#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi

load_dotenv()


@dataclass(frozen=True)
class CompetitionInfo:
    ref: str
    title: str
    url: str
    category: str | None = None
    deadline: str | None = None
    reward: str | None = None


KEYWORDS = [
    "audio",
    "sound",
    # "speech",
    "acoustic",
    "music",
    # "signal",
    # "sensor",
    # "time series",
    # "accelerometer",
]

CATEGORIES = [
    "featured",
    "research",
    "playground",
    # "community",
]

STATE_PATH = Path(os.getenv("STATE_PATH", "kaggle_seen_competitions.json"))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
NOTIFY_ON_FIRST_RUN = os.getenv("NOTIFY_ON_FIRST_RUN", "0") == "1"


def load_seen_refs(path: Path) -> set[str]:
    if not path.exists():
        return set()

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    seen_refs = data.get("seen_refs", [])
    if not isinstance(seen_refs, list):
        raise ValueError(f"Invalid state file format: {path}")

    return {normalize_ref(str(ref)) for ref in seen_refs}


def save_seen_refs(path: Path, refs: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"seen_refs": sorted(set(refs))}

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_attr(obj, name: str) -> str | None:
    value = getattr(obj, name, None)
    if value is None:
        return None
    return str(value)


def normalize_ref(ref: str) -> str:
    value = ref.strip()
    parsed = urlparse(value)

    if parsed.netloc.endswith("kaggle.com"):
        parts = [part for part in parsed.path.split("/") if part]
        if "competitions" in parts:
            index = parts.index("competitions")
            if len(parts) > index + 1:
                return parts[index + 1]

    return value


def competition_url(comp) -> str:
    url = get_attr(comp, "url")
    if url:
        return url

    raw_ref = get_attr(comp, "ref")
    ref = normalize_ref(raw_ref) if raw_ref else None
    if not ref:
        return "https://www.kaggle.com/competitions"

    return f"https://www.kaggle.com/competitions/{ref}"


def iter_competitions(response) -> Iterable[object]:
    if response is None:
        return ()

    if isinstance(response, list):
        return response

    competitions = getattr(response, "competitions", None)
    if competitions is None:
        raise TypeError(f"Unexpected competitions_list response: {type(response)}")

    return competitions


def fetch_competitions(api: KaggleApi) -> dict[str, CompetitionInfo]:
    found: dict[str, CompetitionInfo] = {}

    for keyword in KEYWORDS:
        for category in CATEGORIES:
            try:
                response = api.competitions_list(
                    search=keyword,
                    category=category,
                    page=1,
                )
                competitions = iter_competitions(response)
            except Exception as exc:
                print(
                    "[WARN] failed to fetch competitions: "
                    f"keyword={keyword}, category={category}, error={exc}"
                )
                continue

            for comp in competitions:
                raw_ref = get_attr(comp, "ref")
                if not raw_ref:
                    continue

                ref = normalize_ref(raw_ref)
                title = get_attr(comp, "title") or ref

                found[ref] = CompetitionInfo(
                    ref=ref,
                    title=title,
                    url=competition_url(comp),
                    category=get_attr(comp, "category"),
                    deadline=get_attr(comp, "deadline"),
                    reward=get_attr(comp, "reward"),
                )

    return found


def post_to_slack(new_items: list[CompetitionInfo]) -> None:
    if not new_items:
        return

    if not SLACK_WEBHOOK_URL:
        raise RuntimeError("SLACK_WEBHOOK_URL is not set")

    lines = [
        ":bell: *New Kaggle competitions matched your watch keywords*",
        "",
    ]

    for item in new_items:
        lines.append(f"• *<{item.url}|{item.title}>*")
        lines.append(f"  ref: `{item.ref}`")
        if item.category:
            lines.append(f"  category: {item.category}")
        if item.deadline:
            lines.append(f"  deadline: {item.deadline}")
        if item.reward:
            lines.append(f"  reward: {item.reward}")
        lines.append("")

    payload = {"text": "\n".join(lines)}

    response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=15)
    response.raise_for_status()


def main() -> None:
    api = KaggleApi()
    api.authenticate()

    seen_refs = load_seen_refs(STATE_PATH)
    first_run = not STATE_PATH.exists()

    current = fetch_competitions(api)
    current_refs = set(current.keys())

    new_refs = sorted(current_refs - seen_refs)
    new_items = [current[ref] for ref in new_refs]

    print(f"[INFO] matched competitions: {len(current_refs)}")
    print(f"[INFO] known competitions: {len(seen_refs)}")
    print(f"[INFO] new competitions: {len(new_items)}")

    if new_items and (NOTIFY_ON_FIRST_RUN or not first_run):
        post_to_slack(new_items)
        print("[INFO] Slack notification sent")
    elif new_items and first_run:
        print("[INFO] First run: initialized state without notification")
    else:
        print("[INFO] No new competitions")

    save_seen_refs(STATE_PATH, seen_refs | current_refs)


if __name__ == "__main__":
    main()
