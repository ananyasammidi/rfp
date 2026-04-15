"""
Extracting ingredients from menu descriptions using Regex
"""

import re
from dataclasses import dataclass


@dataclass
class Ingredient:
    raw_name: str
    normalized_name: str
    quantity: float
    unit: str

ALIASES: dict[str, str] = {
    "avo":              "avocado",
    "evoo":             "olive oil",
    "l.t.o.":           "lettuce, tomato, onion",
    "lto":              "lettuce, tomato, onion",
    "sun dried":        "sun-dried tomatoes",
    "sun-dried":        "sun-dried tomatoes",
    "chili":            "chili pepper",
    "chilli":           "chili pepper",
    "parm":             "parmesan",
    "parm cheese":      "parmesan cheese",
    "prosciutto di parma": "prosciutto",
    "swiss":            "swiss cheese",
    "jack":             "monterey jack cheese",
    "american":         "american cheese",
    "mozz":             "mozzarella",
    "brekkie":          "breakfast",  
    "s&p":              "salt and pepper",
    "e&o":              "olive oil",
    "xo":               "XO sauce",
    "gf":               "gluten-free", 
    "pb":               "peanut butter",
    "df":               "dairy-free",  
}
NON_INGREDIENTS = {
    "housemade", "house-made", "house made", "seasonal", "local",
    "organic", "fresh", "daily", "classic", "signature", "special",
    "ask your server", "contains bacon", "sauce contains bacon",
    "gluten-free", "dairy free", "dairy-free", "vegan", "vegetarian",
    "gf", "df", "vg", "v", "gfo",
    "add", "add ons", "add-ons", "make it gf",
    "brekkie", "breakfast", "lunch", "dinner",
}


QTY_PREFIX_RE = re.compile(
    r"^(\d+(?:\.\d+)?)\s*(oz|lb|lbs|g|kg|ml|cup|cups|tbsp|tsp|piece|pieces|each)?\s*",
    re.IGNORECASE,
)

NUMERIC_RE = re.compile(r"^\$?\d+(?:\.\d+)?$")


def _normalize(token: str) -> str:
    """Apply alias map to a cleaned token."""
    lower = token.lower().strip()
    return ALIASES.get(lower, token.strip())


def _extract_qty(raw: str) -> tuple[float | None, str | None, str]:
    token = raw.strip()
    m = QTY_PREFIX_RE.match(token)
    if m and m.group(1):
        qty = float(m.group(1))
        unit = m.group(2).lower() if m.group(2) else "unit"
        name = token[m.end():].strip()
        if name: 
            return qty, unit, name
    return None, None, token


def _is_valid(token: str) -> bool:
    if not token or len(token) < 2:
        return False
    if NUMERIC_RE.match(token):
        return False
    if token.lower() in NON_INGREDIENTS:
        return False
    if re.match(r"^[^a-zA-Z]+$", token):
        return False
    return True


def extract(dish_name: str, description: str) -> list[Ingredient]:
    if not description or "," not in description:
        sources = [dish_name]
    else:
        raw_tokens = description.split(",")
        sources = []
        for token in raw_tokens:
            parts = re.split(r"\s+&\s+|\s+and\s+", token)
            sources.extend(parts)

    found: list[Ingredient] = []
    seen: set[str] = set()

    for raw in sources:
        raw = raw.strip()
        if not raw:
            continue

        qty, unit, cleaned = _extract_qty(raw)
        normalized = _normalize(cleaned)
        for part in normalized.split(","):
            part = part.strip()
            if not _is_valid(part):
                continue
            key = part.lower()
            if key in seen:
                continue
            seen.add(key)
            found.append(Ingredient(
                raw_name=cleaned,
                normalized_name=part,
                quantity=qty,
                unit=unit,
            ))

    return found
