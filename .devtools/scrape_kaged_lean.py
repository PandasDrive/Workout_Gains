"""Scrape Kris Gethin's 12-Week Lean Muscle Trainer from kaged.com.

This script collects each day of the program, parses the workout tables,
and emits structured data compatible with the app's `programs` schema.

Outputs:
    - .devtools/kaged_lean_data.json : canonical JSON representation
    - .devtools/kaged_lean_weeks_js.txt : JS snippet ready to paste
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup, Tag


HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; WorkoutGainsBot/1.0)"}
TRANSLATION = str.maketrans({
    "’": "'",
    "“": '"',
    "”": '"',
    "–": "-",
    "—": "-",
    "•": "-",
})
BASE_URL = "https://www.kaged.com"
TAG_URL_TEMPLATE = BASE_URL + "/blogs/12-week-lean-muscle-trainer/tagged/week-{}"
OUTPUT_JSON = Path(".devtools/kaged_lean_data.json")
OUTPUT_JS = Path(".devtools/kaged_lean_weeks_js.txt")


@dataclass
class DayWorkout:
    day_number: int
    week: int
    day: int
    title: str
    cardio: str
    exercises: list[dict]
    url: str


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip().translate(TRANSLATION)


def collect_day_urls() -> list[str]:
    urls: set[str] = set()
    for week in range(1, 13):
        tag_url = TAG_URL_TEMPLATE.format(week)
        response = requests.get(tag_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.select("a[href*='leanmuscle-day']"):
            href = link.get("href")
            if not href:
                continue
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = BASE_URL + href
            href = href.split("?")[0]
            urls.add(href)
    return sorted(urls, key=lambda u: int(re.search(r"day(\d+)", u).group(1)))


def parse_sets_and_reps(text: str) -> tuple[str | int | None, str]:
    text = clean_text(text)
    match = re.search(r"(\d+)[\s-]*Sets?", text, re.IGNORECASE)
    if match:
        sets_val = match.group(1)
        remainder = text[match.end():].strip()
        remainder = remainder.lstrip("/:.- ")
        if remainder.lower().startswith("of "):
            remainder = remainder[3:].strip()
        return sets_val, remainder
    return None, text


def extract_cardio_and_exercises(body: Tag) -> tuple[str, list[dict]]:
    cardio = ""
    exercises: list[dict] = []

    for table in body.find_all("table"):
        first_td = table.find("td")
        if not first_td:
            continue
        raw_text = clean_text(first_td.get_text(" ", strip=True))
        lower_text = raw_text.lower()

        # Cardio tables usually list duration in the first cell
        if raw_text and lower_text.startswith("cardio"):
            lines = [clean_text(p.get_text(" ", strip=True)) for p in first_td.find_all("p")]
            lines = [line for line in lines if line and line.lower() != "cardio"]
            if lines:
                cardio = "; ".join(lines)
            else:
                cardio = clean_text(raw_text[len("cardio"):])
            continue

        # Skip supplement/product tables
        if any(keyword in lower_text for keyword in ["re-kaged", "re kaged", "in-kaged", "supplement", "stack", "protein isolate", "hydra-charge"]):
            continue

        for row in table.find_all("tr"):
            cell = row.find("td")
            if not cell:
                continue

            strong = cell.find("strong")
            name = clean_text(strong.get_text(" ", strip=True)) if strong else ""

            paragraphs = cell.find_all("p")
            info_lines: list[str] = []
            for idx, paragraph in enumerate(paragraphs):
                text_parts = [clean_text(part) for part in paragraph.stripped_strings]
                text_parts = [part for part in text_parts if part]
                if not text_parts:
                    continue
                joined = " ".join(text_parts)
                if idx == 0 and name and joined.startswith(name):
                    remainder = clean_text(joined[len(name):])
                    if remainder:
                        info_lines.append(remainder)
                else:
                    info_lines.append(joined)

            if not name and info_lines:
                # Sometimes the name isn't in a <strong>; use the first line
                name = info_lines.pop(0)

            if not name or name.lower().startswith("cardio"):
                continue
            if "sample stack" in name.lower():
                continue

            sets = ""
            reps = ""
            rest = ""
            notes = ""

            if info_lines:
                sets_guess, reps_guess = parse_sets_and_reps(info_lines[0])
                if sets_guess is not None:
                    sets = sets_guess
                    reps = reps_guess
                else:
                    reps = info_lines[0]
                info_lines = info_lines[1:]

            if info_lines:
                rest = info_lines[0]
                info_lines = info_lines[1:]

            if info_lines:
                notes = " ".join(info_lines)

            if isinstance(sets, str) and sets.isdigit():
                sets = int(sets)

            exercises.append({
                "name": name,
                "sets": sets,
                "reps": reps,
                "rest": rest,
                "notes": notes,
            })

    return cardio, exercises


def derive_cardio_from_text(body: Tag) -> str:
    for paragraph in body.find_all("p"):
        text = clean_text(paragraph.get_text(" ", strip=True))
        if "cardio" in text.lower():
            return text
    return ""


def parse_day(url: str) -> DayWorkout:
    match = re.search(r"day(\d+)", url)
    if not match:
        raise ValueError(f"Could not find day number in URL: {url}")
    day_number = int(match.group(1))
    week = (day_number - 1) // 7 + 1
    day = (day_number - 1) % 7 + 1

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    title_text = soup.title.get_text(strip=True) if soup.title else ""
    title_match = re.search(r"Day\s*\d+\s*:?-?\s*(.+?)(?:\||$)", title_text)
    title = clean_text(title_match.group(1)) if title_match else f"Day {day}"

    body = soup.select_one("article.article div.container main > div.grid > div > main")
    if not body:
        raise ValueError(f"Could not locate article body for {url}")

    cardio, exercises = extract_cardio_and_exercises(body)
    if not cardio:
        cardio = derive_cardio_from_text(body)
    if not cardio:
        cardio = "Use program guidance for cardio."

    # Normalize exercise entries
    normalized_exercises = []
    for entry in exercises:
        sets_val = entry["sets"]
        if sets_val == "":
            sets_val = ""
        normalized_exercises.append({
            "name": entry["name"],
            "sets": sets_val,
            "reps": entry["reps"],
            "rest": entry["rest"],
            "notes": entry["notes"],
        })

    return DayWorkout(
        day_number=day_number,
        week=week,
        day=day,
        title=title,
        cardio=cardio,
        exercises=normalized_exercises,
        url=url,
    )


def build_weeks(days: Iterable[DayWorkout]) -> list[dict]:
    by_week: dict[int, list[DayWorkout]] = {}
    for day in days:
        by_week.setdefault(day.week, []).append(day)

    weeks = []
    for week_number in sorted(by_week):
        week_days = sorted(by_week[week_number], key=lambda d: d.day)
        weeks.append({
            "week": week_number,
            "task": "",
            "days": [
                {
                    "day": day.day,
                    "title": day.title,
                    "cardio": day.cardio,
                    "exercises": day.exercises,
                }
                for day in week_days
            ],
        })
    return weeks


def save_outputs(weeks: list[dict]) -> None:
    program = {
        "title": "Kaged 12-Week Lean Muscle",
        "weeks": weeks,
    }
    OUTPUT_JSON.write_text(json.dumps(program, indent=2, ensure_ascii=False), encoding="utf-8")

    # Create JS snippet similar to existing program data structure
    weeks_json = json.dumps(weeks, indent=4, ensure_ascii=False)
    weeks_lines = weeks_json.splitlines()
    if weeks_lines:
        weeks_lines[0] = "    weeks: " + weeks_lines[0]
        for idx in range(1, len(weeks_lines)):
            weeks_lines[idx] = "    " + weeks_lines[idx]

    js_lines = ["  kagedLean: {", "    title: \"Kaged 12-Week Lean Muscle\","]
    js_lines.extend(weeks_lines)
    js_lines.append("  }")
    OUTPUT_JS.write_text("\n".join(js_lines), encoding="utf-8")


def main() -> None:
    urls = collect_day_urls()
    days = [parse_day(url) for url in urls]
    weeks = build_weeks(days)
    save_outputs(weeks)
    print(f"Collected {len(days)} days across {len(weeks)} weeks.")
    print(f"JSON saved to {OUTPUT_JSON}")
    print(f"JS snippet saved to {OUTPUT_JS}")


if __name__ == "__main__":
    main()

