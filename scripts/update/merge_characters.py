"""Merge scraped agent data with existing characters.json by name matching."""

# ruff: noqa: ANN401

import json
import os
from typing import Any

from agent_scraper import scrape_wiki_chars

MAPPING_FILE = "../../data/name_mapping.json"


def load_json(path: str) -> Any:
    """Load data from a JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    """Save data to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_mapping(path: str) -> dict[str, str]:
    """Load name mapping."""
    if os.path.exists(path):
        return load_json(path)
    return {}


def build_entry(existing_val: dict[str, Any], agent: dict[str, Any]) -> dict[str, Any]:
    """Build a new character entry."""
    return {
        "id": existing_val["id"],
        "name": existing_val.get("name", ""),
        "full_name": agent["name"],
        "element": existing_val.get("element", agent["attribute"]),
        "availability": existing_val.get("availability", ""),
        "specialty": existing_val.get("specialty", agent["specialty"]),
        "attack_type": agent.get("attack_type", ""),
        "faction": agent.get("faction", ""),
        "release_date": agent.get("release_date", ""),
        "role": existing_val.get("role", ""),
    }


def merge_characters(scraped: list[dict[str, Any]]) -> None:
    """Merge scraped agent data with existing characters.json by name matching."""
    base = os.path.dirname(os.path.abspath(__file__))
    chars_path = os.path.join(base, "../../data", "characters.json")
    mapping_path = os.path.join(base, MAPPING_FILE)

    existing: dict[str, Any] = load_json(chars_path)
    mapping: dict[str, str] = load_mapping(mapping_path)

    used_indices: set[int] = set()
    merged: dict[str, Any] = {}

    def match(key: str, agents: list[dict[str, Any]]) -> int | None:
        key_lower = key.lower().strip()
        for i, a in enumerate(agents):
            if i in used_indices:
                continue
            if key_lower == a["name"].lower().strip():
                return i
        for i, a in enumerate(agents):
            if i in used_indices:
                continue
            if key_lower in a["name"].lower():
                return i
        return None

    for existing_key, existing_val in existing.items():
        idx: int | None
        idx = match(existing_key, scraped)

        if idx is not None:
            used_indices.add(idx)
            merged[existing_key] = build_entry(existing_val, scraped[idx])
            continue

        mapped_name: str | None = mapping.get(existing_key)
        if mapped_name is not None:
            for i, a in enumerate(scraped):
                if i in used_indices:
                    continue
                if a["name"].lower().strip() == mapped_name.lower().strip():
                    used_indices.add(i)
                    merged[existing_key] = build_entry(existing_val, a)
                    break
            continue

        unused: list[dict[str, Any]] = [
            a for i, a in enumerate(scraped) if i not in used_indices
        ]

        if len(unused) == 1:
            idx = next(
                i for i, a in enumerate(scraped) if a["name"] == unused[0]["name"]
            )
            used_indices.add(idx)
            merged[existing_key] = build_entry(existing_val, unused[0])
            mapping[existing_key] = unused[0]["name"]
            continue

        print(
            f"\n  UNMATCHED: '{existing_key}' / {existing_val.get('specialty', '?')})",
        )
        print("  Choose which scraped agent it maps to:")
        for n, a in enumerate(unused, 1):
            print(f"    [{n}] {a['name']} ({a['attribute']} / {a['specialty']})")
        while True:
            try:
                choice: str = input(f"  Enter number (1-{len(unused)})").strip()
                n: int = int(choice)
                if 1 <= n <= len(unused):
                    chosen: dict[str, Any] = unused[n - 1]
                    idx = next(
                        i for i, a in enumerate(scraped) if a["name"] == chosen["name"]
                    )
                    used_indices.add(idx)
                    merged[existing_key] = build_entry(existing_val, chosen)
                    mapping[existing_key] = chosen["name"]
                    print()
                    break
            except (ValueError, IndexError):
                pass
            print("  Invalid choice, try again.")

    save_json(mapping_path, mapping)
    save_json(chars_path, merged)


if __name__ == "__main__":
    merge_characters(scrape_wiki_chars())
