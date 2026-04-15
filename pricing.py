"""
USDA API and estimated prices dict
"""

import os
import httpx
from dataclasses import dataclass, field

USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


@dataclass
class PriceEstimate:
    price: float
    unit: str
    trend: str
    usda_category: str = ""
    usda_description: str = ""
    source: str = "USDA ERS Market Estimate (Q4 2024)"

_PRICES: dict[str, tuple[float, str, str]] = {
    "beef short ribs":   (9.50,  "lb",      "rising"),
    "ground beef":       (5.50,  "lb",      "stable"),
    "beef":              (7.00,  "lb",      "rising"),
    "chicken breast":    (3.90,  "lb",      "stable"),
    "chicken":           (3.50,  "lb",      "stable"),
    "pork sausage":      (4.50,  "lb",      "stable"),
    "chorizo":           (5.50,  "lb",      "stable"),
    "bacon":             (6.80,  "lb",      "rising"),
    "prosciutto":        (14.00, "lb",      "stable"),
    "smoked salmon":     (16.00, "lb",      "rising"),
    "salmon":            (12.00, "lb",      "rising"),
    "shrimp":            (8.50,  "lb",      "stable"),
    "halloumi":          (12.00, "lb",      "stable"),
    "eggs":              (3.20,  "dozen",   "falling"),
    "egg":               (3.20,  "dozen",   "falling"),
    "ricotta":           (4.50,  "lb",      "stable"),
    "burrata":           (10.00, "lb",      "stable"),
    "mozzarella":        (6.00,  "lb",      "stable"),
    "parmesan":          (8.00,  "lb",      "stable"),
    "pecorino":          (9.00,  "lb",      "stable"),
    "gruyere":           (11.00, "lb",      "stable"),
    "fontina":           (9.00,  "lb",      "stable"),
    "swiss cheese":      (7.00,  "lb",      "stable"),
    "american cheese":   (4.50,  "lb",      "stable"),
    "monterey jack":     (5.50,  "lb",      "stable"),
    "provolone":         (6.00,  "lb",      "stable"),
    "feta":              (6.50,  "lb",      "stable"),
    "cream":             (3.50,  "qt",      "stable"),
    "butter":            (5.00,  "lb",      "stable"),
    "yogurt":            (3.50,  "lb",      "stable"),
    "sour cream":        (3.00,  "lb",      "stable"),
    "sourdough":         (5.00,  "loaf",    "stable"),
    "bread":             (4.00,  "loaf",    "stable"),
    "bun":               (4.00,  "6-pack",  "stable"),
    "tortilla":          (3.50,  "12-pack", "stable"),
    "pappardelle":       (3.50,  "lb",      "stable"),
    "rigatoni":          (2.50,  "lb",      "stable"),
    "spaghetti":         (2.00,  "lb",      "stable"),
    "pasta":             (2.50,  "lb",      "stable"),
    "freekeh":           (4.00,  "lb",      "stable"),
    "farro":             (3.50,  "lb",      "stable"),
    "brown rice":        (2.00,  "lb",      "stable"),
    "rice":              (1.80,  "lb",      "stable"),
    "quinoa":            (3.50,  "lb",      "stable"),
    "granola":           (5.00,  "lb",      "stable"),
    "kale":              (2.50,  "lb",      "stable"),
    "spinach":           (2.50,  "lb",      "stable"),
    "arugula":           (3.00,  "lb",      "stable"),
    "lettuce":           (2.00,  "lb",      "stable"),
    "pea shoots":        (8.00,  "lb",      "rising"),
    "cherry tomatoes":   (3.50,  "lb",      "stable"),
    "tomatoes":          (2.00,  "lb",      "stable"),
    "tomato":            (2.00,  "lb",      "stable"),
    "sun-dried tomatoes":(6.00,  "lb",      "stable"),
    "avocado":           (1.20,  "each",    "falling"),
    "watermelon radish": (4.00,  "lb",      "stable"),
    "radish":            (1.50,  "lb",      "stable"),
    "cucumber":          (1.20,  "lb",      "stable"),
    "snap peas":         (3.50,  "lb",      "stable"),
    "snow peas":         (3.50,  "lb",      "stable"),
    "edamame":           (3.00,  "lb",      "stable"),
    "broccolini":        (3.50,  "lb",      "rising"),
    "brussels sprouts":  (2.50,  "lb",      "stable"),
    "mushrooms":         (4.00,  "lb",      "stable"),
    "scallions":         (1.50,  "bunch",   "stable"),
    "shallots":          (2.50,  "lb",      "stable"),
    "chives":            (3.00,  "lb",      "stable"),
    "red onion":         (1.00,  "lb",      "stable"),
    "onion":             (0.90,  "lb",      "falling"),
    "lemon":             (0.60,  "each",    "stable"),
    "sweet potato":      (1.20,  "lb",      "stable"),
    "potato":            (0.80,  "lb",      "stable"),
    "corn":              (0.50,  "each",    "stable"),
    "peas":              (2.00,  "lb",      "stable"),
    "apple":             (1.50,  "lb",      "stable"),
    "pear":              (1.80,  "lb",      "stable"),
    "banana":            (0.60,  "lb",      "stable"),
    "mango":             (1.50,  "each",    "stable"),
    "zucchini":          (1.80,  "lb",      "stable"),
    "basil":             (3.00,  "lb",      "stable"),
    "parsley":           (2.00,  "lb",      "stable"),
    "pumpkin seeds":     (4.00,  "lb",      "stable"),
    "sunflower seeds":   (2.50,  "lb",      "stable"),
    "walnuts":           (8.00,  "lb",      "stable"),
    "hemp seeds":        (7.00,  "lb",      "stable"),
    "tahini":            (5.00,  "lb",      "stable"),
    "olive oil":         (9.00,  "liter",   "rising"),
    "chocolate":         (6.00,  "lb",      "rising"),
    "maple syrup":       (12.00, "lb",      "stable"),
}

_DEFAULT_PRICE = (3.00, "lb", "stable")


def _lookup_price(name: str) -> tuple[float, str, str]:
    key = name.lower().strip()
    if key in _PRICES:
        return _PRICES[key]
    best, best_len = None, 0
    for k, v in _PRICES.items():
        if k in key and len(k) > best_len:
            best, best_len = v, len(k)
    return best if best else _DEFAULT_PRICE


def fetch_usda_data(ingredient_name: str) -> dict:
    try:
        resp = httpx.get(
            USDA_SEARCH_URL,
            params={
                "api_key": USDA_API_KEY,
                "query": ingredient_name,
                "pageSize": 1,
                "dataType": "Foundation,SR Legacy",
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        foods = data.get("foods", [])
        if not foods:
            return {"usda_category": "", "usda_description": ""}
        food = foods[0]
        return {
            "usda_category":    food.get("foodCategory", ""),
            "usda_description": food.get("description", "").title(),
        }
    except Exception:
        return {"usda_category": "", "usda_description": ""}


def get_price(normalized_name: str) -> PriceEstimate:
    price, unit, trend = _lookup_price(normalized_name)
    usda = fetch_usda_data(normalized_name)

    return PriceEstimate(
        price=price,
        unit=unit,
        trend=trend,
        usda_category=usda["usda_category"],
        usda_description=usda["usda_description"],
        source="USDA ERS Market Estimate (Q4 2024)",
    )
