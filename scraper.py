"""
Parsing menu
"""

import re
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

PRICE_RE = re.compile(r"^\$\d+(?:\.\d{2})?$")

FOOD_SECTIONS = {
    "brekkie time", "all day", "bowls", "salads", "pasta",
    "burgers", "sides", "sweets",
}

SKIP_SECTIONS = {"drinks", "coffee and tea", "seasonal specials",
                 "smoothies", "cocktails", "beer & wine"}


@dataclass
class ScrapedDish:
    name: str
    description: str = ""
    price: str = ""
    category: str = "All Day"


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def scrape(url: str) -> tuple[str, list[ScrapedDish]]:
    resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    restaurant = "Ruby's Cafe"
    title = soup.find("title")
    if title:
        restaurant = "Ruby's Cafe"

    for tag in soup(["nav", "footer", "script", "style", "noscript"]):
        tag.decompose()

    dishes: list[ScrapedDish] = []
    current_section = "All Day"
    in_food_section = True

    for el in soup.find_all(["h2", "li"]):
        if el.name == "h2":
            heading = _clean(el.get_text()).lower()
            if heading in FOOD_SECTIONS:
                current_section = _clean(el.get_text()).title()
                in_food_section = True
            elif heading in SKIP_SECTIONS:
                in_food_section = False
            continue

        if not in_food_section:
            continue

        strongs = el.find_all("strong")
        if not strongs:
            continue

        name = _clean(strongs[0].get_text())
        if not name or PRICE_RE.match(name) or len(name) < 3:
            continue

        if name.lower() in {"add ons", "make it gf", "sides", "add-ons"}:
            continue

        price = ""
        for s in strongs:
            txt = _clean(s.get_text())
            if PRICE_RE.match(txt):
                price = txt

        for s in el.find_all("strong"):
            s.decompose()
        description = _clean(el.get_text())
        description = re.sub(r"\s*(add\s+\w.*|two\s+\w.*|\w+\s+\$\d+.*)", "", description, flags=re.I).strip()

        if name and price:
            dishes.append(ScrapedDish(
                name=name,
                description=description,
                price=price,
                category=current_section,
            ))

    seen: set[str] = set()
    unique = []
    for d in dishes:
        key = d.name.lower()
        if key not in seen:
            seen.add(key)
            unique.append(d)

    if not unique:
        raise ValueError("No dishes found — page structure may have changed.")

    return restaurant, unique
