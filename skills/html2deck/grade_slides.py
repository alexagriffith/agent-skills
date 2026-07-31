#!/usr/bin/env python3
"""External visual grader for html2deck slides — Gemini (not Grok).

Paid-expert rubric: FORMAT + LOOK only. Target: every slide ≥ 9.
"""
from __future__ import annotations

import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent / "_out-current"
SLIDES = OUT / "slides"
REPORT = OUT / "slice-report.json"
MODEL = os.environ.get("HTML2DECK_GRADER_MODEL", "gemini-2.5-pro")
API = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
BATCH = 6
MAX_EDGE = 1280  # downscale for API


SYSTEM = """You are a paid presentation-design expert people hire for state-of-the-art
PowerPoint / Keynote / pitch decks (Duarte, Presentation Zen, McKinsey/BCG craft,
Linear/Vercel/Stripe product decks). Grade FORMAT and LOOK only — not factual accuracy.

Rubric (integer 1–10):
1–3 broken/unreadable/amateur
4–6 usable but awkward (sparse, cramped, text wall, bad hierarchy, postage-stamp content)
7–8 solid professional, minor polish left
9–10 A-grade: would ship in a paid client deck / conference keynote

Check: title-page centering; master title bar consistency; visual primacy; ~70% fill
when content exists (not floating orphans, not jammed); short captions; readable tables;
intentional N/M splits; margins/alignment/hierarchy.

Be harsh. No praise padding. Return ONLY valid JSON matching the schema."""


def _key() -> str:
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        sys.exit("GEMINI_API_KEY not set")
    return k


def _encode(png: Path) -> str:
    im = Image.open(png).convert("RGB")
    w, h = im.size
    scale = min(1.0, MAX_EDGE / max(w, h))
    if scale < 1:
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=82, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def _call(parts: list) -> dict:
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }
    req = urllib.request.Request(
        f"{API}?key={_key()}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                raw = json.load(r)
            text = raw["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:400]
            if e.code in (429, 503, 500) and attempt < 3:
                time.sleep(2 ** attempt * 2)
                continue
            raise SystemExit(f"Gemini HTTP {e.code}: {err}") from e
        except json.JSONDecodeError:
            if attempt < 3:
                time.sleep(2)
                continue
            raise


def grade_batch(items: list[dict]) -> list[dict]:
    """items: [{n, title, part, path}]"""
    schema_hint = {
        "slides": [
            {
                "n": 1,
                "score": 7,
                "why": "one line",
                "fixes": ["concrete fix if score < 9", "..."],
            }
        ]
    }
    meta = "\n".join(
        f"- slide {it['n']:02d}: {it['title']}"
        + (f" · {it['part']}" if it.get("part") else "")
        for it in items
    )
    parts = [
        {
            "text": (
                "Grade each attached slide image. Titles:\n"
                f"{meta}\n\n"
                "Return JSON exactly like:\n"
                f"{json.dumps(schema_hint)}\n"
                "One object per slide, same n. fixes=[] when score>=9."
            )
        }
    ]
    for it in items:
        parts.append({"text": f"IMAGE slide-{it['n']:02d}.png"})
        parts.append(
            {"inline_data": {"mime_type": "image/jpeg", "data": _encode(it["path"])}}
        )
    result = _call(parts)
    return result.get("slides", [])


def main() -> None:
    rep = json.loads(REPORT.read_text())
    by_n = {s["n"]: s for s in rep["slides"]}
    paths = sorted(SLIDES.glob("slide-*.png"))
    if not paths:
        sys.exit(f"no slides in {SLIDES}")

    items = []
    for p in paths:
        n = int(p.stem.split("-")[1])
        meta = by_n.get(n, {})
        items.append(
            {
                "n": n,
                "title": meta.get("title", p.stem),
                "part": meta.get("part", ""),
                "path": p,
            }
        )

    all_scores = []
    for i in range(0, len(items), BATCH):
        batch = items[i : i + BATCH]
        print(f"grading slides {batch[0]['n']}–{batch[-1]['n']} via {MODEL}…", flush=True)
        scored = grade_batch(batch)
        # align by n
        by = {s["n"]: s for s in scored}
        for it in batch:
            s = by.get(it["n"])
            if not s:
                s = {"n": it["n"], "score": 0, "why": "MISSING from grader", "fixes": ["re-grade"]}
            s["title"] = it["title"]
            s["part"] = it["part"]
            all_scores.append(s)
        time.sleep(1)

    avg = sum(int(s["score"]) for s in all_scores) / len(all_scores)
    fails = [s for s in all_scores if int(s["score"]) < 9]
    out = {
        "model": MODEL,
        "slides": all_scores,
        "average": round(avg, 2),
        "below_9": len(fails),
        "verdict": "PASS" if not fails else f"FAIL ({len(fails)} below 9)",
    }
    dest = OUT / "grade-report.json"
    dest.write_text(json.dumps(out, indent=2))

    print("\n### Scores")
    print("| # | title | score | why |")
    print("|---|---|---|---|")
    for s in all_scores:
        t = s["title"][:40] + (f" · {s['part']}" if s.get("part") else "")
        print(f"| {s['n']:02d} | {t} | {s['score']} | {s.get('why','')} |")
    print(f"\n### Deck average\n{out['average']}")
    print(f"\n### Verdict\n{out['verdict']}")
    if fails:
        print("\n### Failures (< 9)")
        for s in fails:
            print(f"\n**Slide {s['n']:02d} — {s['score']}/10** — {s.get('why','')}")
            for f in s.get("fixes") or []:
                print(f"- {f}")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
