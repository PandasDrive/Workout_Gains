"""Scrape ThenX featured workouts metadata for personal use."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://app.thenx.com"
FEATURED_URL = f"{BASE_URL}/featured-workouts"
OUTPUT_JSON = Path(".devtools/thenx_workouts.json")
OUTPUT_JS = Path("data/thenx-workouts.js")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WorkoutGainsBot/1.0)"
}


@dataclass
class Workout:
    title: str
    focus: List[str]
    url: str
    likes: Optional[int]
    comments: Optional[int]
    date: Optional[str]
    image: Optional[str]


def normalise_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def parse_likes_comments(text: str) -> Dict[str, Optional[int]]:
    likes = comments = None
    like_match = re.search(r"(\d+)\s+likes", text, re.IGNORECASE)
    comment_match = re.search(r"(\d+)\s+comments", text, re.IGNORECASE)
    if like_match:
        likes = int(like_match.group(1))
    if comment_match:
        comments = int(comment_match.group(1))
    return {"likes": likes, "comments": comments}


def parse_workout_card(card) -> Optional[Workout]:
    href = card.get("href")
    if not href or "/featured-workouts/" not in href:
        return None
    url = href if href.startswith("http") else BASE_URL + href

    badges = [normalise_text(span.get_text()) for span in card.select(".badge")]

    title_el = card.select_one("h5")
    title = normalise_text(title_el.get_text()) if title_el else ""

    date_el = card.select_one("small")
    date = normalise_text(date_el.get_text()) if date_el else None

    summary_el = card.select("small")
    likes = comments = None
    if summary_el:
        last_small_text = normalise_text(summary_el[-1].get_text())
        metrics = parse_likes_comments(last_small_text)
        likes = metrics["likes"]
        comments = metrics["comments"]
        if date and normalise_text(summary_el[0].get_text()) != date:
            date = normalise_text(summary_el[0].get_text())

    img = card.find("img")
    image = img.get("src") if img else None

    if not title:
        return None

    return Workout(
        title=title,
        focus=badges,
        url=url,
        likes=likes,
        comments=comments,
        date=date,
        image=image,
    )


def fetch_page(page: int) -> List[Workout]:
    url = FEATURED_URL if page == 1 else f"{FEATURED_URL}?page={page}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    workouts: List[Workout] = []
    for card in soup.select("a.card[href*='/featured-workouts/']"):
        workout = parse_workout_card(card)
        if workout:
            workouts.append(workout)
    return workouts


def main() -> None:
    workouts: List[Workout] = []
    page = 1
    while True:
        page_workouts = fetch_page(page)
        if not page_workouts:
            break
        workouts.extend(page_workouts)
        page += 1
        if page > 5:
            break

    payload = {
        "source": FEATURED_URL,
        "count": len(workouts),
        "workouts": [asdict(workout) for workout in workouts],
    }

    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    js_payload = {
        "source": FEATURED_URL,
        "updatedAt": datetime.utcnow().isoformat() + "Z",
        "workoutCount": len(workouts),
        "workouts": payload["workouts"],
    }

    OUTPUT_JS.write_text(
        "window.thenxWorkouts = " + json.dumps(js_payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

