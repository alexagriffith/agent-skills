# html2deck

Turn an HTML page into 16:9 presentation slides by **measuring** rendered
height and splitting overflowing sections at safe child boundaries — never
shrinking text below a readability floor, and never painting past the content
box width.

Good for a benchmark walkthrough, a written explainer, or any long HTML page
where charts, tables, and numbers must stay intact and legible.

## How it works

1. **`slice.py`** — render each unit in headless Chromium at 1280×720, project a
   visual-first face (excess prose → speaker notes), fit-or-split at child
   boundaries. Output: `_out/slides/*.png` + `slice-report.json`.
2. **`contact_sheet.py`** — thumbnail grid for human approval.
3. **`build.py`** — assemble PNGs into `.pptx` and `.pdf` (full-bleed image per
   slide; unit prose in speaker notes).

Optional: **`layout.py`** (programmatic recipe masters), **`grade_slides.py`**
(Gemini visual grader; needs `GOOGLE_API_KEY`).

## Bootstrap

```bash
./scripts/bootstrap.sh
# or:
pip install playwright python-pptx Pillow pytest
python -m playwright install chromium
```

If Chromium is already cached elsewhere:

```bash
export PLAYWRIGHT_BROWSERS_PATH="$HOME/Library/Caches/ms-playwright"
```

## Quick start

```bash
python3 slice.py path/to/page.html --unit-selector section --theme light
python3 contact_sheet.py _out          # open _out/contact-sheet.html
python3 build.py _out --pptx --pdf --name my-deck
```

## Options

- `slice.py <src> [--out DIR] [--unit-selector CSS] [--theme light|dark]
  [--keep-source]` — face projection is on by default; `--keep-source` skips it.
- `build.py <out_dir> [--pptx] [--pdf] [--name NAME]`

## Layout rules (summary)

- Fixed title bar on content slides (PowerPoint master style).
- Title / section-header slides: text-only, centered — never a graphic.
- Text-only remnants (no image/table/card grid): centered title + lead.
- Visuals may grow to fill the content box; **never exceed content width**.
- See `SKILL.md` for the full contract.

## Tests

```bash
python -m pytest tests/
```

Uses a bundled HTML fixture under `tests/fixtures/` (no machine-local paths).
