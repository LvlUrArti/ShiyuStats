"""Scrape agent data from the wiki."""

# pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportArgumentType=false

import warnings

from bs4 import BeautifulSoup
from cloudscraper import create_scraper

URL = "https://zenless-zone-zero.fandom.com/wiki/Agent"

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def scrape_wiki_chars() -> list[dict[str, str | int]]:
    """Scrape agent data from the wiki."""
    scraper = create_scraper()
    resp = scraper.get(URL)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    heading = soup.find("span", id="Playable_Agents")
    if heading is None:
        msg = "Could not find 'Playable Agents' heading on the page"
        raise RuntimeError(msg)

    table = heading.find_parent("h3")
    if table is None:
        msg = "Could not find parent h3 for Playable Agents heading"
        raise RuntimeError(msg)

    table = table.find_next_sibling("table")
    if table is None:
        msg = "Could not find agent table after Playable Agents heading"
        raise RuntimeError(msg)

    agents: list[dict[str, str | int]] = []
    for row in table.select("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue

        name = cells[1].get_text(strip=True)

        rank_span = cells[2].find("span", class_="zzw-icon")
        rank_title = rank_span.get("title", "") if rank_span else ""
        if rank_title is None:
            continue
        rank = "S" if "AgentRank S" in rank_title else "A"

        attribute = cells[3].get_text(strip=True)

        specialty = cells[4].get_text(strip=True)

        attack_types = ", ".join(
            a.get_text(strip=True)
            for a in cells[5].find_all("a")
            if a.get_text(strip=True)
        )

        faction = cells[6].get_text(strip=True)

        release_text = cells[7].get_text(strip=True)
        has_date = cells[7].has_attr("data-sort-value") and any(
            m in release_text for m in MONTHS
        )
        release_date: int = int(cells[7]["data-sort-value"]) if has_date else 0

        agents.append(
            {
                "name": name,
                "rank": rank,
                "attribute": attribute,
                "specialty": specialty,
                "attack_type": attack_types,
                "faction": faction,
                "release_date": release_date,
            },
        )

        if not has_date:
            warnings.warn(f"No release date for '{name}'", stacklevel=2)

    return agents
