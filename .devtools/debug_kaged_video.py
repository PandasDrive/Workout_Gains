from __future__ import annotations

import requests
from bs4 import BeautifulSoup

URL = "https://www.kaged.com/blogs/8-week-hardcore-trainer/day-1-hct"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WorkoutGainsBot/1.0)"
}


def main() -> None:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    iframes = soup.find_all("iframe")
    if not iframes:
        print("No iframe found")
        return
    for idx, iframe in enumerate(iframes, 1):
        print(f"Iframe {idx}: {iframe.get('src')}")


if __name__ == "__main__":
    main()

