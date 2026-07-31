#!/usr/bin/env python3
"""Build a contact sheet (thumbnail grid) from a slice-report.json so a human
can approve the slicing at a glance. Pure HTML, self-contained, opens anywhere.

Works for both screenshot mode (units have measured_h/fits) and layout mode
(units have recipe)."""
import sys, json, base64
from pathlib import Path

outdir = Path(sys.argv[1] if len(sys.argv) > 1 else "_out")
rep = json.loads((outdir / "slice-report.json").read_text())
mode = rep.get("mode", "screenshot")

cards = []
for s in rep["slides"]:
    png = (outdir / s["png"]).read_bytes()
    b64 = base64.b64encode(png).decode()
    part = f' · {s["part"]}' if s.get("part") else ""
    badges = ""
    if s.get("from_split"):
        badges += ' <span class="split">split</span>'
    if s.get("stripped"):
        badges += ' <span class="stripped">stripped</span>'
    if s.get("recipe"):
        badges += f' <span class="recipe">{s["recipe"]}</span>'
    cards.append(f"""<figure>
      <img src="data:image/png;base64,{b64}" alt="slide {s['n']}">
      <figcaption><b>{s['n']:02d}</b> {s['title']}{part}{badges}</figcaption>
    </figure>""")

units = rep.get("units") or []
if mode == "layout":
    units_rows = "".join(
        f"<tr><td>{u['title'][:60]}</td><td>{u.get('recipe','')}</td>"
        f"<td>{'stripped' if u.get('stripped') else '—'}</td></tr>"
        for u in units
    )
    units_head = "<tr><td><b>Unit</b></td><td><b>Recipe</b></td><td><b>Face</b></td></tr>"
    sub_bits = [Path(rep["source"]).name, f"{len(rep['slides'])} slides"]
else:
    units_rows = "".join(
        f"<tr><td>{u['title'][:60]}</td>"
        f"<td style='text-align:right'>{u.get('measured_h','?')}px</td>"
        f"<td>{'one slide' if u.get('fits') else 'split'}"
        f"{' · stripped' if u.get('stripped') else ''}</td></tr>"
        for u in units
    )
    units_head = (
        "<tr><td><b>Unit</b></td><td style='text-align:right'><b>Measured</b></td>"
        "<td><b>Result</b></td></tr>"
    )
    sub_bits = [
        Path(rep["source"]).name,
        f"each slide is {rep.get('slide_w','?')}×{rep.get('slide_h','?')} (16:9)",
        f"content budget {rep.get('content_h','?')}px",
    ]

html = f"""<!doctype html><meta charset=utf-8>
<title>{'Layout' if mode=='layout' else 'Slice'} mockup — {Path(rep['source']).name}</title>
<style>
 body{{font:14px/1.5 Inter,-apple-system,sans-serif;margin:32px;background:#0d0f13;color:#e8eaf0}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#9aa0ad;margin:0 0 24px}}
 table{{border-collapse:collapse;margin:0 0 28px;font-size:13px}}
 td{{padding:4px 14px;border-bottom:1px solid #1c1f26}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px}}
 figure{{margin:0;background:#12151b;border:1px solid #1c1f26;border-radius:10px;overflow:hidden}}
 figure img{{width:100%;display:block;aspect-ratio:16/9;object-fit:contain;background:#fff}}
 figcaption{{padding:8px 11px;font-size:12px;color:#c3c8d2}}
 .split{{color:#f0a35b;font-size:10px;border:1px solid #f0a35b55;border-radius:4px;padding:1px 5px;margin-left:4px}}
 .stripped{{color:#7eb8ff;font-size:10px;border:1px solid #7eb8ff55;border-radius:4px;padding:1px 5px;margin-left:4px}}
 .recipe{{color:#9ad67a;font-size:10px;border:1px solid #9ad67a55;border-radius:4px;padding:1px 5px;margin-left:4px}}
</style>
<h1>{'Layout' if mode=='layout' else 'Slice'} mockup · {len(rep['slides'])} slides from {len(units)} units</h1>
<p class=sub>{' · '.join(sub_bits)}</p>
<table>{units_head}{units_rows}</table>
<div class=grid>{''.join(cards)}</div>
"""
(outdir / "contact-sheet.html").write_text(html)
print(f"wrote {outdir/'contact-sheet.html'}  ({len(rep['slides'])} slides)")
