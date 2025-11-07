from __future__ import annotations

import requests
from bs4 import BeautifulSoup

HTML = requests.get(
    "https://app.thenx.com/featured-workouts",
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30,
).text

soup = BeautifulSoup(HTML, "html.parser")

link = soup.select_one("a[href*='/featured-workouts/']")
if link:
    print(link.prettify())


