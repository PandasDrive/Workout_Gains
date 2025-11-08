from __future__ import annotations

import json
import math
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://www.kaged.com"
TAG_URL = f"{BASE_URL}/blogs/8-week-hardcore-trainer/tagged/trainer-day"
RAW_JSON = Path(".devtools/hardcore_raw.json")
STRUCTURED_JSON = Path(".devtools/hardcore_structured.json")
WEEKS_JS = Path(".devtools/hardcore_weeks_js.txt")

USER_AGENT = {"User-Agent": "Mozilla/5.0 (compatible; WorkoutGainsBot/1.0)"}


@dataclass
class Exercise:
    name: str
    info: str
    sets: Optional[int]
    reps: str
    rest: str
    section: Optional[str]
    subsection: Optional[str]


@dataclass
class DayPlan:
    day_number: int
    title: str
    cardio: str
    notes: List[str]
    exercises: List[Exercise]
    url: str
    video: Optional[str]


def normalise_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    replacements = {
        "\xa0": " ",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
        "•": "-",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    value = re.sub(r" w hat", " what", value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s+([!,?.;:])", r"\1", value)
    return value.strip()


def collect_day_urls() -> List[str]:
    urls: List[str] = []
    seen = set()
    page = 1
    while True:
        page_url = TAG_URL if page == 1 else f"{TAG_URL}?page={page}"
        response = requests.get(page_url, headers=USER_AGENT, timeout=30)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, "html.parser")
        new_links = 0
        for a in soup.find_all('a'):
            href = a.get('href')
            if not href or 'tagged' in href or '/blogs/8-week-hardcore-trainer/' not in href:
                continue
            full = href if href.startswith('http') else BASE_URL + href
            full = full.split('?')[0]
            if full not in seen:
                seen.add(full)
                urls.append(full)
                new_links += 1
        if new_links == 0:
            break
        page += 1
        if page > 20:
            break
    urls.sort(key=lambda u: extract_day_number(u))
    return urls


def extract_day_number(url: str) -> int:
    match = re.search(r"day-(\d+)", url)
    if match:
        return int(match.group(1))
    return 0


def parse_day(url: str) -> DayPlan:
    response = requests.get(url, headers=USER_AGENT, timeout=30)
    response.raise_for_status()
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    main_grid = soup.select_one('article main > div.grid')
    if not main_grid:
        raise ValueError(f"Unable to locate main grid for {url}")
    content_main = main_grid.select_one('main')
    if not content_main:
        raise ValueError(f"Unable to locate main content for {url}")

    children = list(content_main.children)
    collecting = True
    section = None
    subsection = None
    cardio_parts: List[str] = []
    notes: List[str] = []
    exercises: List[Exercise] = []
    title = ""

    for child in children:
        if isinstance(child, Tag):
            name = child.name.lower()
            text = normalise_text(child.get_text(' ', strip=True))
            if name == 'h2':
                if 'related' in text.lower():
                    break
                section = text
                subsection = None
            elif name == 'h3':
                section = text
                subsection = None
            elif name == 'h4':
                if 'cardio' in text.lower():
                    cardio_parts.append(text)
                else:
                    subsection = text
            elif name == 'h1' and not title:
                title = text
            elif name == 'p':
                if text and not text.lower().startswith('this content cannot be found'):
                    notes.append(text)
            elif name == 'table' and 'daypages' in child.get('class', []):
                exercise = parse_exercise_table(child, section, subsection)
                exercises.append(exercise)

    if not title:
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else f"Day {extract_day_number(url)}"

    cardio_text = '; '.join(dict.fromkeys(cardio_parts)) if cardio_parts else ''

    video_url = None
    for iframe in soup.select('iframe[src]'):
        src = iframe.get('src')
        if not src:
            continue
        lowered = src.lower()
        if 'youtube.com' in lowered or 'youtu.be' in lowered or 'vimeo.com' in lowered:
            video_url = src
            break

    return DayPlan(
        day_number=extract_day_number(url),
        title=title,
        cardio=cardio_text,
        notes=deduplicate_notes(notes),
        exercises=exercises,
        url=url,
        video=video_url,
    )


def parse_exercise_table(table: Tag, section: Optional[str], subsection: Optional[str]) -> Exercise:
    rows = table.find_all('tr')
    primary_name = ''
    primary_info = ''
    for row in rows:
        cells = row.find_all(['th', 'td'])
        if not cells:
            continue
        name_cell = normalise_text(cells[0].get_text(' ', strip=True))
        if not name_cell:
            continue
        info_cell = normalise_text(cells[1].get_text(' ', strip=True)) if len(cells) > 1 else ''
        primary_name = name_cell
        primary_info = info_cell
        break
    clean_name = clean_exercise_name(primary_name)
    sets, reps, rest = parse_exercise_info(primary_info)
    return Exercise(
        name=clean_name,
        info=primary_info,
        sets=sets,
        reps=reps,
        rest=rest,
        section=section,
        subsection=subsection,
    )


def clean_exercise_name(name: str) -> str:
    name = normalise_text(name)
    name = re.sub(r"^\d+[a-d]?\.?\s*", "", name)
    name = name.replace(' *', '').strip()
    return name


def parse_exercise_info(info: str) -> Tuple[Optional[int], str, str]:
    info = normalise_text(info)
    if not info:
        return None, '', ''
    sets = None
    rest = ''
    reps = info
    match = re.search(r"(\d+)\s*Sets?", info, re.IGNORECASE)
    if match:
        sets = int(match.group(1))
        remainder = info[match.end():].strip()
        remainder = re.sub(r"^[xX\-\–\u00d7\s]+", "", remainder)
        reps = remainder or info
    rest_match = re.search(r"(Rest[^.,;]*)", reps, re.IGNORECASE)
    if rest_match:
        rest = rest_match.group(1).strip()
        reps = reps.replace(rest_match.group(0), '').strip(' ,;-')
    return sets, reps, rest


def deduplicate_notes(notes: List[str]) -> List[str]:
    cleaned = []
    seen = set()
    for note in notes:
        note = normalise_text(note)
        if not note:
            continue
        if note.lower().startswith('related products') or note.lower().startswith('related articles'):
            continue
        if note not in seen:
            seen.add(note)
            cleaned.append(note)
    return cleaned


def build_weeks(days: List[DayPlan]) -> List[Dict]:
    by_week: Dict[int, List[DayPlan]] = {}
    for day in days:
        week_number = (day.day_number - 1) // 7 + 1
        by_week.setdefault(week_number, []).append(day)
    weeks = []
    for week in sorted(by_week):
        week_days = sorted(by_week[week], key=lambda d: d.day_number)
        weeks.append({
            "week": week,
            "task": "",
            "days": [
                {
                    "day": ((day.day_number - 1) % 7) + 1,
                    "title": day.title,
                    "cardio": day.cardio,
                    "notes": day.notes,
                    "url": day.url,
                    "video": day.video,
                    "exercises": [
                        {
                            "name": exercise.name,
                            "section": exercise.section,
                            "subsection": exercise.subsection,
                            "info": exercise.info,
                            "sets": exercise.sets,
                            "reps": exercise.reps,
                            "rest": exercise.rest,
                        }
                        for exercise in day.exercises
                    ]
                }
                for day in week_days
            ]
        })
    return weeks


def main() -> None:
    urls = collect_day_urls()
    days = [parse_day(url) for url in urls if extract_day_number(url)]
    days.sort(key=lambda d: d.day_number)

    raw_payload = {
        "source": TAG_URL,
        "count": len(days),
        "urls": urls,
    }
    RAW_JSON.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    structured = {
        "program": "Kaged 8 Week Hardcore Trainer",
        "days": [
            {
                "day_number": day.day_number,
                "title": day.title,
                "cardio": day.cardio,
                "notes": day.notes,
                "url": day.url,
                "video": day.video,
                "exercises": [asdict(ex) for ex in day.exercises],
            }
            for day in days
        ]
    }
    STRUCTURED_JSON.write_text(json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8")

    weeks = build_weeks(days)
    js_content = json.dumps(weeks, ensure_ascii=False, indent=2)
    WEEKS_JS.write_text("  hardcore8: {\n    title: \"Kris Gethin 8-Week Hardcore\",\n    weeks: " + js_content.replace('\n', '\n    ') + "\n  }\n", encoding="utf-8")


if __name__ == "__main__":
    main()
