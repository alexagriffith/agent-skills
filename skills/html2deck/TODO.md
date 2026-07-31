# html2deck — deferred TODOs

## Still open

- [ ] **Native themed charts** — re-render charts for `--theme dark` instead of
      the interim figure-plate wrap for baked light SVGs.
- [ ] **Editable PowerPoint text** — real text boxes for titles/body; charts stay
      images.
- [ ] **Markdown source** — MD → HTML front-end, then the same measure/split path.
- [ ] **Module split** — `slice.py` is large; extract `face.py` / `compose.py` /
      `render.py` when touching it next.
- [ ] **Honest report metrics** — `phi` / `V` / `score` in `slice-report.json`
      should reflect the face blocks, not the wrapped blob.

## Done (kept for history)

- Theme flag, fixed title bar, face projection, composition scoring
- Width hard-clamp (no side overflow), card-grid / `chip cap` face retention
- Text-only centering, visual height-fill under shorter title chrome
- Fixture-based tests (no absolute paths)
- Homepage Export buttons live on flow-control-benchmarks (written + walkthrough)
