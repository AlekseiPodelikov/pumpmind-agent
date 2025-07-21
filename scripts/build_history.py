#!/usr/bin/env python3
"""1 commit per green cell from scripts/plan_pixels.txt (user plan image)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIXELS_FILE = ROOT / "scripts" / "plan_pixels.txt"
AUTHOR_NAME = "Aleksei Podelikov"
AUTHOR_EMAIL = "294050723+AlekseiPodelikov@users.noreply.github.com"
AUTHOR = f"{AUTHOR_NAME} <{AUTHOR_EMAIL}>"
GRAPH_END = date(2026, 6, 16)

COMMIT_MSGS = [
    "chore: sync activity log",
    "feat: tune narrative scorer",
    "fix: ws reconnect",
    "docs: architecture",
    "refactor: signal router",
]

TOUCH_FILES = [
    "packages/core/src/types.ts",
    "packages/agent/src/planner.ts",
    "packages/scraper/src/pumpfun-ws.ts",
    "packages/signals/src/router.ts",
    "packages/api/src/server.ts",
    "README.md",
]


def load_pixels() -> list[tuple[int, int]]:
    text = PIXELS_FILE.read_text(encoding="utf-8")
    pixels = [tuple(map(int, m)) for m in re.findall(r"\((\d+),\s*(\d+)\)", text)]
    extra = (52, 1)  # current-week dot on plan
    if extra not in pixels:
        pixels.append(extra)
    return sorted(set(pixels))


def run(cmd: list[str], env: dict | None = None) -> None:
    subprocess.run(cmd, cwd=ROOT, env=env, check=True, capture_output=True, text=True)


def sunday_on_or_before(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1) % 7)


def grid_start(end: date) -> date:
    return sunday_on_or_before(end) - timedelta(weeks=52)


def cell_date(start: date, col: int, row: int) -> date:
    return start + timedelta(weeks=col, days=row)


def preview(pixels: set[tuple[int, int]]) -> None:
    w = max(c for c, _ in pixels) + 1
    print("Plan preview (7 rows, 0=Sun):")
    for row in range(7):
        print(f"{row}|" + "".join("#" if (c, row) in pixels else "." for c in range(w)))


def wipe() -> None:
    import shutil
    import time

    for name in ("history", ".git"):
        p = ROOT / name
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
    time.sleep(0.5)


def init_repo() -> None:
    run(["git", "init", "-b", "main"])
    run(["git", "config", "user.name", AUTHOR_NAME])
    run(["git", "config", "user.email", AUTHOR_EMAIL])


def commit_on(day: date, msg: str, touch: Path) -> None:
    env = os.environ.copy()
    ts = f"{day.isoformat()}T12:00:00 +0000"
    env["GIT_AUTHOR_DATE"] = ts
    env["GIT_COMMITTER_DATE"] = ts

    log = ROOT / "history" / "activity.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"date": day.isoformat(), "msg": msg}) + "\n")

    text = touch.read_text(encoding="utf-8")
    touch.write_text(text + f"\n// {day.isoformat()}\n", encoding="utf-8")
    run(["git", "add", "-A"], env=env)
    run(["git", "commit", "-m", msg, "--author", AUTHOR], env=env)


def main() -> None:
    wipe()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "scaffold_project.py")], check=True)
    init_repo()

    pixels = load_pixels()
    preview(set(pixels))
    start = grid_start(GRAPH_END)

    dates: list[date] = []
    for col, row in pixels:
        d = cell_date(start, col, row)
        if d <= GRAPH_END:
            dates.append(d)
        else:
            print(f"skip ({col},{row}) -> {d}")

    dates = sorted(dates)
    print(f"{len(dates)} commits: {dates[0]} .. {dates[-1]}")

    for i, d in enumerate(dates):
        commit_on(d, COMMIT_MSGS[i % len(COMMIT_MSGS)], ROOT / TOUCH_FILES[i % len(TOUCH_FILES)])
    print("Done.")


if __name__ == "__main__":
    main()
