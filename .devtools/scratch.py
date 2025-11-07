import requests
from bs4 import BeautifulSoup


def collect_day_urls() -> list[str]:
    all_urls = set()
    for page in range(1, 13):
        page_url = f"https://www.kaged.com/blogs/12-week-lean-muscle-trainer/tagged/week-{page}"
        html = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30).text
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a[href*='leanmuscle-day']"):
            href = a.get("href")
            if not href:
                continue
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = "https://www.kaged.com" + href
            href = href.split("?")[0]
            all_urls.add(href)
    return sorted(all_urls)


def parse_article(url: str) -> None:
    response = requests.get(url, timeout=30)
    print(f"Requested: {url}\nFinal URL: {response.url}\nStatus: {response.status_code}")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("h1")
    print(f"TITLE: {title.get_text(strip=True) if title else 'NA'}")
    content = soup.select_one(".article__content") or soup.select_one("article")
    if not content:
        print("No article content found")
        return
    for heading in content.find_all(["h2", "h3"]):
        print(f"HEADING: {heading.get_text(strip=True)}")
    tables = content.find_all("table")
    print(f"Found {len(tables)} tables")


def collect_links(page_url: str) -> list[str]:
    html = requests.get(page_url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.select("a[href*='lean-muscle-trainer']"):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = "https://www.kaged.com" + href
        if "/blogs/" not in href:
            continue
        if "tagged" in href:
            continue
        links.add(href.split("?")[0])
    return sorted(links)


if __name__ == "__main__":
    urls = collect_day_urls()
    for url in urls:
        print(url)
    numbers = sorted(int(url.rsplit("day", 1)[1]) for url in urls if "day" in url)
    missing = [n for n in range(1, 85) if n not in numbers]
    print(f"\nFound {len(numbers)} day pages. Missing: {missing}\n")
    if urls:
        print("\nSample parse of first workout:\n")
        parse_article(urls[1])

