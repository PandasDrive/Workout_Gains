"""Parse the 80 Wholefoods PDF into structured recipe data."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict

import PyPDF2

PDF_PATH = Path("food_plans/the-80-wholefoods-mains-to-nourish-3.pdf")
RAW_TEXT_JSON = Path(".devtools/nutrition_data.json")
OUTPUT_JSON = Path(".devtools/nutrition_structured.json")
OUTPUT_JS = Path("data/nutrition-data.js")


@dataclass
class Recipe:
    title: str
    slug: str
    prep_time: str
    prep_minutes: float
    ingredients: List[str]
    calories: float
    fat_g: float
    carbs_g: float
    fiber_g: float
    sugar_g: float
    protein_g: float
    sodium_mg: float
    notes: List[str]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip('-')
    return value or "recipe"


def load_pdf_text(path: Path) -> str:
    reader = PyPDF2.PdfReader(path.open("rb"))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def normalise_line(line: str) -> str:
    line = unicodedata.normalize("NFKC", line)
    line = line.replace("ﬁ", "fi").replace("ﬂ", "fl")
    return line.strip()


def parse_number(value: str) -> float:
    value = value.replace(',', '').strip()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", value)
    return float(match.group(1)) if match else 0.0


def merge_wrapped_lines(lines: List[str], join_condition=None) -> List[str]:
    merged: List[str] = []
    for line in lines:
        if not merged:
            merged.append(line)
            continue
        prev = merged[-1]
        should_join = False
        if join_condition is not None:
            should_join = join_condition(prev, line)
        else:
            if line and (line[0].islower() or prev.endswith(('-', '/', '(', ',')) or not re.search(r'[.!?]$', prev)):
                should_join = True
        if should_join:
            merged[-1] = prev + ' ' + line
        else:
            merged.append(line)
    return [ln.strip() for ln in merged]


def parse_recipe_block(block: str) -> Recipe:
    lines = [normalise_line(ln) for ln in block.splitlines()]
    lines = [ln for ln in lines if ln]
    if len(lines) < 12:
        raise ValueError(f"Recipe block appears too short: {block[:100]}...")

    title = lines[0]
    prep_time = lines[1]
    prep_minutes = parse_number(prep_time)

    idx = 2
    ingredients: List[str] = []
    while idx < len(lines) and not re.match(r"^[0-9]", lines[idx]):
        ingredients.append(lines[idx])
        idx += 1

    def ingredient_join(prev: str, line: str) -> bool:
        starters = ('into', 'for', 'or', 'and', 'plus', 'with', 'to', 'on', 'in', 'at', 'of', ')')
        return bool(line) and (line[0].islower() or line.startswith(starters))

    ingredients = merge_wrapped_lines(ingredients, ingredient_join)

    macros = lines[idx:idx + 10]
    if len(macros) < 10:
        raise ValueError(f"Unexpected macro length for {title}: {macros}")
    calories = parse_number(macros[0])
    fat_g = parse_number(macros[1])
    carbs_g = parse_number(macros[2])
    fiber_g = parse_number(macros[4])
    sugar_g = parse_number(macros[6])
    protein_g = parse_number(macros[7])
    sodium_mg = parse_number(macros[9])

    notes = merge_wrapped_lines(lines[idx + 10:])

    return Recipe(
        title=title,
        slug=slugify(title),
        prep_time=prep_time,
        prep_minutes=prep_minutes,
        ingredients=ingredients,
        calories=calories,
        fat_g=fat_g,
        carbs_g=carbs_g,
        fiber_g=fiber_g,
        sugar_g=sugar_g,
        protein_g=protein_g,
        sodium_mg=sodium_mg,
        notes=notes,
    )


def main() -> None:
    if not PDF_PATH.exists():
        raise SystemExit(f"PDF not found: {PDF_PATH}")

    raw_text = load_pdf_text(PDF_PATH)
    RAW_TEXT_JSON.write_text(json.dumps({"raw_text": raw_text}, ensure_ascii=False, indent=2), encoding="utf-8")

    blocks = [block.strip() for block in raw_text.split("http://www.status8020.com") if block.strip()]
    intro = blocks[0]
    recipe_blocks = blocks[1:]

    recipes = [parse_recipe_block(block) for block in recipe_blocks]

    intro_normalized = "\n".join(normalise_line(line) for line in intro.splitlines() if line.strip())
    payload: Dict[str, object] = {
        "source": str(PDF_PATH).replace("\\", "/"),
        "intro": intro_normalized,
        "recipe_count": len(recipes),
        "recipes": [asdict(recipe) for recipe in recipes],
    }

    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    js_payload = {
        "source": payload["source"],
        "intro": payload["intro"],
        "recipeCount": payload["recipe_count"],
        "recipes": payload["recipes"],
    }
    js_content = "window.nutritionData = " + json.dumps(js_payload, ensure_ascii=False, indent=2) + ";\n"
    OUTPUT_JS.write_text(js_content, encoding="utf-8")


if __name__ == "__main__":
    main()

