#!/usr/bin/env python3
"""
html2deck layout mode — programmatic recipes into a fixed 16:9 master.

Unlike screenshot mode (slice.py), this path extracts structured content from
HTML units and *places* it into deterministic slide recipes. Charts become
captured images inside a known frame; titles/bullets use a fixed type scale.

Recipes (v1):
  title      — centered title + lead
  hero       — full-bleed visual + ≤1 caption
  table      — full-bleed table
  bullets    — title + ≤4 one-liners (top-aligned)
  bignums    — metric cards row
  closer     — master title + short prose (top-left, NOT title-page center)

Usage:
  python3 layout.py <src.html> --out _out-layout [--unit-selector section]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, Error as PWError

# Reuse face / chrome rules from screenshot path
import slice as S

SLIDE_W, SLIDE_H = 1280, 720
MARGIN = 48
TITLE_H = 88
CONTENT_TOP = MARGIN + TITLE_H
CONTENT_H = SLIDE_H - CONTENT_TOP - MARGIN
CONTENT_W = SLIDE_W - 2 * MARGIN

MASTER_CSS = f"""
html,body{{margin:0;padding:0;background:#f4f5f7;color:#111;
  font-family:Inter,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
#deck{{width:{SLIDE_W}px;height:{SLIDE_H}px;position:relative;overflow:hidden;
  background:#f4f5f7;box-sizing:border-box}}
#deck .bar{{position:absolute;left:{MARGIN}px;top:{MARGIN}px;right:{MARGIN}px;
  height:{TITLE_H}px;display:flex;align-items:flex-start}}
#deck .bar h1{{margin:0;font-size:32px;line-height:1.2;letter-spacing:-.02em;
  font-weight:700;max-width:92%}}
#deck .bar .part{{position:absolute;right:0;top:4px;font:600 13px Inter,sans-serif;
  color:#8b909a}}
#deck .zone{{position:absolute;left:{MARGIN}px;top:{CONTENT_TOP}px;
  width:{CONTENT_W}px;height:{CONTENT_H}px;box-sizing:border-box}}
/* title / header — text only, centered, never a graphic */
#deck.recipe-title,#deck.recipe-header,#deck.recipe-spotlight{{
  display:flex;align-items:center;justify-content:center}}
#deck.recipe-title .stack,#deck.recipe-header .stack,#deck.recipe-spotlight .stack{{
  text-align:center;max-width:56ch}}
#deck.recipe-title .stack h1,#deck.recipe-header .stack h1{{
  font-size:58px;line-height:1.12;letter-spacing:-.025em;margin:0 0 18px;font-weight:700}}
#deck.recipe-title .stack p,#deck.recipe-header .stack p{{
  font-size:22px;line-height:1.45;color:#3c414a;margin:0}}
#deck.recipe-spotlight .stack p{{
  font-size:34px;line-height:1.35;color:#1a1d24;margin:0;font-weight:500;max-width:28ch}}
#deck.recipe-spotlight .stack .eyebrow{{
  font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:#8b909a;
  margin:0 0 18px;font-weight:600}}
/* hero / table */
#deck .frame{{width:100%;height:100%;display:flex;flex-direction:column;
  justify-content:center;align-items:stretch;gap:14px}}
#deck .frame img,#deck .frame svg{{max-width:100%;max-height:100%;
  object-fit:contain;display:block;margin:0 auto;background:transparent}}
#deck .frame .cap{{font:500 15px/1.4 Inter,-apple-system,sans-serif;color:#3c414a;
  max-width:72ch;margin:0}}
#deck .frame table{{width:100%;border-collapse:collapse;background:#fff;
  font-size:16px}}
#deck .frame th,#deck .frame td{{border:1px solid #e2e4e8;padding:10px 14px;
  text-align:left}}
#deck .frame th{{background:#eef0f3;font-size:12px;text-transform:uppercase;
  letter-spacing:.04em;color:#5f6673}}
/* bullets */
#deck .bullets{{padding-top:8px;margin:0;padding-left:1.2em}}
#deck .bullets li{{font-size:24px;line-height:1.35;margin:0 0 16px;max-width:42ch}}
/* bignums */
#deck .bignums{{display:flex;gap:18px;height:100%;align-items:stretch}}
#deck .bignum{{flex:1;background:#fff;border:1px solid #e2e4e8;border-radius:14px;
  padding:28px 24px;text-align:left;display:flex;flex-direction:column;
  justify-content:center}}
#deck .bignum .k{{font-size:13px;letter-spacing:.06em;text-transform:uppercase;
  color:#8b909a;margin-bottom:12px;font-weight:600}}
#deck .bignum .v{{font-size:52px;font-weight:700;letter-spacing:-.03em;line-height:1}}
#deck .bignum .s{{font-size:15px;color:#5f6673;margin-top:14px;line-height:1.35}}
"""


_CAPTION_STRIP_RE = re.compile(
    r"(?is)<(figcaption|p|div)\b[^>]*class=[\"'][^\"']*\b"
    r"(caption|cap|note|legend|source)\b[^\"']*[\"'][^>]*>.*?</\1\s*>"
)
_BIGNUM_FIELD_RE = re.compile(
    r"(?is)<div\b[^>]*class=[\"'][^\"']*\b(k|v|sub)\b[^\"']*[\"'][^>]*>(.*?)</div\s*>"
)


def _pick_recipe(blocks: list[str], is_first: bool, is_last: bool) -> str:
    kinds = [S.classify_block(b) for b in blocks]
    joined = " ".join(blocks).lower()
    if is_first and not any(k in ("visual", "table") for k in kinds):
        return "title"
    if any(k == "visual" for k in kinds):
        return "hero"
    if any(k == "table" for k in kinds):
        return "table"
    if "bignum" in joined:
        return "bignums"
    if any(k == "list" for k in kinds):
        return "bullets"
    if is_last:
        return "closer"
    # Short leftover prose → bullets of sentences, not sparse closer
    words = sum(len(S._words(S._plain(b))) for b in blocks)
    if words < 40:
        return "bullets" if _bullets_from(blocks) else "closer"
    return "bullets"


def _extract_visual_html(blocks: list[str]) -> tuple[str, str]:
    """Return (visual_html, caption_text). Caption pulled out of the visual."""
    vis, cap = "", ""
    for b in blocks:
        k = S.classify_block(b)
        if k in ("visual", "table") and not vis:
            vis = S.strip_chrome(b)
        elif k == "caption" and not cap:
            cap = S._plain(b).strip()
    if vis:
        # Prefer external caption; else lift one embedded in the figure.
        embedded = _CAPTION_STRIP_RE.findall(vis)
        if not cap and embedded:
            # findall with groups returns tuples; re-search for text
            m = _CAPTION_STRIP_RE.search(vis)
            if m:
                cap = S._plain(m.group(0)).strip()
        vis = _CAPTION_STRIP_RE.sub("", vis)
        # Also strip bare <figcaption>…</figcaption>
        vis = re.sub(r"(?is)<figcaption\b[^>]*>.*?</figcaption\s*>", "", vis)
    return vis, cap


def _bullets_from(blocks: list[str]) -> list[str]:
    out = []
    for b in blocks:
        if S.classify_block(b) == "list":
            for m in S._LI_RE.finditer(b):
                t = S._plain(m.group(2)).strip()
                if t:
                    out.append(t)
        elif S.classify_block(b) in ("prose", "callout", "caption"):
            for s in S._sentences(S._plain(b)):
                if s:
                    out.append(s)
    return out[: S.MAX_BULLETS]


def _bignums_from(blocks: list[str]) -> list[tuple[str, str, str]]:
    """Parse (label, value, sub) triples from .bignum cards via .k/.v/.sub."""
    cards: list[tuple[str, str, str]] = []
    blob = "\n".join(blocks)
    parts = re.split(
        r"(?is)(?=<div\b[^>]*class=[\"'][^\"']*\bbignum\b)", blob
    )
    for part in parts:
        if re.search(r"(?is)class=[\"'][^\"']*\bbignum\b", part) is None:
            continue
        fields = {"k": "", "v": "", "sub": ""}
        for m in _BIGNUM_FIELD_RE.finditer(part):
            key = m.group(1).lower()
            if key in fields and not fields[key]:
                fields[key] = S._plain(m.group(2)).strip()
        if fields["k"] or fields["v"]:
            cards.append((fields["k"] or "Metric", fields["v"] or "—", fields["sub"]))
    if cards:
        return cards[:4]
    for b in blocks:
        sents = S._sentences(S._plain(b))
        if sents:
            return [("Key result", sents[0][:48], " ".join(sents[1:2]))]
    return []


def _slide_html(recipe: str, title: str, blocks: list[str], part: str) -> str:
    part_html = f'<div class="part">{part}</div>' if part else ""
    if recipe == "title":
        lead = ""
        for b in blocks:
            if S.classify_block(b) == "prose":
                lead = " ".join(S._sentences(S._plain(b))[:2])
                break
        return (
            f'<div id="deck" class="recipe-title"><div class="stack">'
            f"<h1>{_esc(title)}</h1>"
            f"{f'<p>{_esc(lead)}</p>' if lead else ''}"
            f"</div></div>"
        )
    if recipe == "hero":
        vis, cap = _extract_visual_html(blocks)
        # Charts already carry titles/subtitles — external caption is redundant
        # and Gemini consistently docks for it. Keep caption only if no <svg>/<img>.
        has_drawn = bool(re.search(r"(?is)<(svg|img|canvas)\b", vis))
        cap_html = (
            ""
            if has_drawn or not cap
            else f'<div class="cap">{_esc(cap)}</div>'
        )
        return (
            f'<div id="deck" class="recipe-hero"><div class="bar"><h1>{_esc(title)}</h1>'
            f"{part_html}</div><div class=\"zone\"><div class=\"frame\">"
            f"{vis}{cap_html}</div></div></div>"
        )
    if recipe == "table":
        vis, _ = _extract_visual_html(blocks)
        return (
            f'<div id="deck" class="recipe-table"><div class="bar"><h1>{_esc(title)}</h1>'
            f"{part_html}</div><div class=\"zone\"><div class=\"frame\">{vis}</div></div></div>"
        )
    if recipe == "bignums":
        cards = _bignums_from(blocks)
        if not cards:
            # fall through to bullets rather than empty cards
            recipe = "bullets"
        else:
            cells_parts = []
            for k, v, s in cards:
                sub = f'<div class="s">{_esc(s)}</div>' if s else ""
                cells_parts.append(
                    f'<div class="bignum"><div class="k">{_esc(k)}</div>'
                    f'<div class="v">{_esc(v)}</div>{sub}</div>'
                )
            cells = "".join(cells_parts)
            return (
                f'<div id="deck" class="recipe-bignums"><div class="bar">'
                f"<h1>{_esc(title)}</h1>{part_html}</div>"
                f'<div class="zone"><div class="bignums">{cells}</div></div></div>'
            )
    if recipe == "bullets":
        items = _bullets_from(blocks)
        if not items:
            body = ""
            for b in blocks:
                plain = S._plain(b).strip()
                if plain:
                    body = " ".join(S._sentences(plain)[:2])
                    break
            items = [body] if body else [title]
        lis = "".join(f"<li>{_esc(t)}</li>" for t in items)
        return (
            f'<div id="deck" class="recipe-bullets"><div class="bar"><h1>{_esc(title)}</h1>'
            f"{part_html}</div><div class=\"zone\"><ul class=\"bullets\">{lis}</ul>"
            f"</div></div>"
        )
    # closer
    body = ""
    for b in blocks:
        if S.classify_block(b) in ("prose", "callout"):
            body = " ".join(S._sentences(S._plain(b))[:2])
            break
    if not body:
        body = " ".join(S._sentences(S._plain(" ".join(blocks)))[:2])
    return (
        f'<div id="deck" class="recipe-closer"><div class="bar"><h1>{_esc(title)}</h1>'
        f"</div><div class=\"zone\"><p>{_esc(body)}</p></div></div>"
    )


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def layout_page(source: str, outdir: str, unit_selector: str = "section") -> dict:
    src = Path(source).resolve()
    out = Path(outdir)
    (out / "slides").mkdir(parents=True, exist_ok=True)
    report = {
        "mode": "layout",
        "source": str(src),
        "unit_selector": unit_selector,
        "slide_w": SLIDE_W,
        "slide_h": SLIDE_H,
        "content_h": CONTENT_H,
        "slides": [],
        "units": [],
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_context(
            viewport={"width": SLIDE_W, "height": SLIDE_H}, device_scale_factor=2
        ).new_page()
        try:
            page.goto(src.as_uri(), wait_until="load", timeout=30000)
        except PWError:
            page.goto(src.as_uri(), wait_until="domcontentloaded", timeout=30000)
        S._settle(page)
        units = page.evaluate(S.DISCOVER_JS, unit_selector)
        if not units:
            browser.close()
            raise SystemExit(f"No units matched {unit_selector!r}")

        slide_no = 0
        for ui, u in enumerate(units):
            # Prefer raw blocks for recipe content; project_face only for notes
            face, notes, stripped = S.project_face(u["blocks"])
            raw = [S.strip_chrome(b) for b in u["blocks"]]
            if not face and raw:
                face = raw[:1]
                stripped = True
            recipe = _pick_recipe(face or raw, ui == 0, ui == len(units) - 1)
            content_blocks = face if recipe in ("title", "bullets", "closer") else (raw or face)
            # For hero: capture visual alone on matching slide bg (no white plate)
            if recipe == "hero":
                vis, cap = _extract_visual_html(content_blocks)
                if vis:
                    # Remap source design tokens so chart plates match the master
                    boost = S.DECK_BOOST_CSS.replace("#__content", "#v")
                    page.set_content(
                        "<style>"
                        "html,body{margin:0;background:#f4f5f7}"
                        ":root{--base:#f4f5f7;--txt:#111;--txt2:#3c414a;"
                        "--txt3:#8b909a;--b1:rgba(10,12,20,.08);"
                        "--b2:rgba(10,12,20,.18)}"
                        f"#v{{width:{CONTENT_W}px;background:#f4f5f7}}"
                        # Flatten white SVG plate fills baked into charts
                        "svg rect[fill='#ffffff'],svg rect[fill='#fff'],"
                        "svg rect[fill='white'],svg rect[fill='var(--base,#ffffff)']"
                        "{fill:#f4f5f7!important}"
                        f"{boost}</style>"
                        f"<div id=v>{vis}</div>"
                    )
                    S._settle(page)
                    # Force-fill any remaining white full-bleed rects via DOM
                    page.evaluate(
                        """() => {
                          document.querySelectorAll('#v svg rect').forEach(r => {
                            const f = (r.getAttribute('fill') || '').toLowerCase();
                            const w = +r.getAttribute('width') || 0;
                            const h = +r.getAttribute('height') || 0;
                            if (w >= 600 && h >= 250 &&
                                (f.includes('fff') || f.includes('white') ||
                                 f.includes('--base') || f === '')) {
                              r.setAttribute('fill', '#f4f5f7');
                            }
                          });
                        }"""
                    )
                    asset = out / "slides" / f"asset-{ui:02d}.png"
                    page.locator("#v").screenshot(
                        path=str(asset), omit_background=True
                    )
                    content_blocks = [
                        f'<img src="{asset.resolve().as_uri()}" alt="">'
                    ]
            elif recipe == "bignums":
                # Keep raw so card classnames survive face projection
                content_blocks = raw or face
            else:
                content_blocks = content_blocks or face

            html = _slide_html(recipe, u["title"], content_blocks, "")
            page.set_content(f"<style>{MASTER_CSS}</style>{html}")
            S._settle(page)
            slide_no += 1
            fn = f"slides/slide-{slide_no:02d}.png"
            page.locator("#deck").screenshot(path=str(out / fn))
            report["units"].append(
                {
                    "id": u["id"],
                    "title": u["title"],
                    "recipe": recipe,
                    "stripped": stripped,
                    "measured_h": None,
                    "fits": True,
                }
            )
            report["slides"].append(
                {
                    "n": slide_no,
                    "unit": u["id"],
                    "title": u["title"],
                    "recipe": recipe,
                    "png": fn,
                    "part": "",
                    "from_split": False,
                    "stripped": stripped,
                    "notes_text": S._prose(u["outerHTML"])
                    + (("\n\n" + "\n".join(notes)) if notes else ""),
                    "words": S._face_words(html),
                }
            )
        browser.close()

    (out / "slice-report.json").write_text(json.dumps(report, indent=2))
    return report


def main():
    ap = argparse.ArgumentParser(description="Programmatic html2deck layout mode")
    ap.add_argument("source")
    ap.add_argument("--out", default=str(Path(__file__).parent / "_out-layout"))
    ap.add_argument("--unit-selector", default="section")
    args = ap.parse_args()
    rep = layout_page(args.source, args.out, args.unit_selector)
    print(
        f"layout mode: {len(rep['units'])} units → {len(rep['slides'])} slides"
    )
    for u in rep["units"]:
        print(f"  [{u['recipe']:7}] {u['title'][:60]}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
