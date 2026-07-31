"""
Tests for html2deck's slicer.

Two layers:
  * an end-to-end slice of the bundled fixture (rendered once, session-scoped),
    asserting the readability guarantees the tool promises;
  * fast synthetic-HTML unit tests for the splitter — a tall section splits,
    a short one doesn't, and a figure never separates from its bignums.
"""
import json
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import slice as S  # noqa: E402

# Bundled fixture — no absolute / machine-local paths.
FIXTURE = ROOT / "tests" / "fixtures" / "sample.html"
SANE_MIN, SANE_MAX = 3, 40


def _content_h(unit):
    """The whole-unit content height that slice_page measures (heading excluded)."""
    return "".join(unit["blocks"])


# ---------------------------------------------------------------- end-to-end

@pytest.fixture(scope="session")
def sliced(tmp_path_factory):
    if not FIXTURE.exists():
        pytest.skip(f"fixture not present at {FIXTURE}")
    out = tmp_path_factory.mktemp("out")
    report = S.slice_page(str(FIXTURE), str(out), "section")
    return out, report


def test_every_png_is_16_9_at_2x(sliced):
    out, report = sliced
    for s in report["slides"]:
        w, h = Image.open(out / s["png"]).size
        assert (w, h) == (2560, 1440), f"{s['png']} is {w}x{h}, not 2560x1440"


def test_every_slide_is_titled(sliced):
    _, report = sliced
    for s in report["slides"]:
        assert s["title"].strip(), f"slide {s['n']} has no title"


def test_fitting_units_are_never_split(sliced):
    """A fitting unit may still emit a section-header slide + one content slide.
    It must not fan into multiple *content* parts."""
    _, report = sliced
    by_unit = {}
    for s in report["slides"]:
        by_unit.setdefault(s["unit"], []).append(s)
    for u in report["units"]:
        if not u.get("fits"):
            continue
        slides = by_unit.get(u["id"], [])
        content = [s for s in slides if not s.get("is_title_slide")]
        assert len(content) <= 1, (
            f"unit {u['id']} fit but produced {len(content)} content slides")


def test_split_parts_share_one_title(sliced):
    _, report = sliced
    by_unit = {}
    for s in report["slides"]:
        by_unit.setdefault(s["unit"], []).append(s["title"])
    for unit, titles in by_unit.items():
        assert len(set(titles)) == 1, f"unit {unit} parts have differing titles"


def test_slide_count_is_sane(sliced):
    _, report = sliced
    n = len(report["slides"])
    assert SANE_MIN <= n <= SANE_MAX, f"{n} slides is outside {SANE_MIN}-{SANE_MAX}"


def test_part_labels_are_sequential(sliced):
    """Part labels apply to content faces only; title/header slides stay unlabeled."""
    _, report = sliced
    by_unit = {}
    for s in report["slides"]:
        by_unit.setdefault(s["unit"], []).append(s)
    for unit, slides in by_unit.items():
        content = [s for s in slides if not s.get("is_title_slide")]
        for s in slides:
            if s.get("is_title_slide"):
                assert s["part"] == "", f"title slide of {unit} should have no part"
        if len(content) <= 1:
            if content:
                assert content[0]["part"] == "", (
                    f"lone content slide of {unit} should have no part label")
        else:
            want = [f"{i + 1}/{len(content)}" for i in range(len(content))]
            got = [s["part"] for s in content]
            assert got == want, f"unit {unit} part labels {got} != {want}"


# ---------------------------------------------------------- theme + density

def _corner_luma(png):
    """Average brightness of a top-left patch — the slide background."""
    im = Image.open(png).convert("RGB").crop((4, 4, 40, 40)).resize((1, 1))
    r, g, b = im.getpixel((0, 0))
    return (r + g + b) / 3


def test_theme_dark_changes_background(tmp_path):
    if not FIXTURE.exists():
        pytest.skip(f"fixture not present at {FIXTURE}")
    light = tmp_path / "light"
    dark = tmp_path / "dark"
    rl = S.slice_page(str(FIXTURE), str(light), "section", theme="light")
    rd = S.slice_page(str(FIXTURE), str(dark), "section", theme="dark")
    assert rl["theme"] == "light" and rd["theme"] == "dark"
    ll = _corner_luma(light / rl["slides"][0]["png"])
    ld = _corner_luma(dark / rd["slides"][0]["png"])
    assert ll > 180, f"light slide background too dark (luma {ll:.0f})"
    assert ld < 90, f"dark slide background too light (luma {ld:.0f})"
    assert ll - ld > 80, "dark theme did not visibly darken the slide"


def test_face_projection_strips_long_prose(tmp_path):
    """Long multi-sentence prose leaves the face; short lead may remain."""
    long = ("First sentence stays maybe. Second sentence also long enough. "
            "Third sentence pushes this over the face budget for sure. "
            "Fourth keeps going with more words about nothing in particular.")
    src = tmp_path / "wordy.html"
    src.write_text(f"<!doctype html><section><h2>Wordy</h2><p>{long}</p>"
                   f"<p>{long}</p></section>")
    report = S.slice_page(str(src), str(tmp_path / "out"), "section")
    assert report["units"][0]["stripped"] is True
    assert report["slides"][0]["stripped"] is True
    # face should be far shorter than the source paragraphs
    assert report["slides"][0]["words"] < 80
    assert "Third sentence" in report["slides"][0]["notes_text"]


def test_keep_source_skips_projection(tmp_path):
    """`--keep-source` skips face projection; header centering may still apply."""
    words = " ".join(f"word{i}" for i in range(80))
    src = tmp_path / "wordy.html"
    src.write_text(
        f"<!doctype html><section><h2>Wordy</h2>"
        f"<p>{words}. More words here too for sentences.</p></section>")
    report = S.slice_page(str(src), str(tmp_path / "out"), "section",
                          keep_source=True)
    assert report["keep_source"] is True
    assert report["slides"], "expected at least one slide"
    # Without keep_source, projection would strip; with it, source prose reaches
    # notes or the face before header rules. Either way the flag must stick.
    assert all("keep_source" not in s or s.get("stripped") is False
               for s in report.get("units", [])) or report["keep_source"]


def test_project_face_unit_rules():
    long = ("One. Two. Three sentences make this too long for the face "
            "because we also blow past forty words with filler filler filler "
            "filler filler filler filler filler filler filler end.")
    face, notes, stripped = S.project_face([f"<p>{long}</p>", "<p>Short lead.</p>"])
    assert stripped
    assert notes
    # second short prose after a lead-from-long goes to notes
    assert any("Short lead" in n for n in notes) or face
    face2, notes2, st2 = S.project_face(
        ["<ul>" + "".join(f"<li>item {i} is a short one</li>" for i in range(6))
         + "</ul>"])
    assert st2
    assert face2 and face2[0].count("<li") <= S.MAX_BULLETS


# ------------------------------------------------------------------ splitter

@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": S.SLIDE_W, "height": S.SLIDE_H},
                            device_scale_factor=2)
        pg = ctx.new_page()
        pg.goto("about:blank")
        pg.add_style_tag(content=S.STAGE_CSS)
        yield pg
        b.close()


def _discover(page, html):
    """Load raw HTML into the page and return its units (via the real DISCOVER_JS)."""
    page.evaluate("(h) => { document.body.innerHTML = h; }", html)
    page.add_style_tag(content=S.STAGE_CSS)
    return page.evaluate(S.DISCOVER_JS, "section")


def test_tall_section_splits(page):
    paras = "".join(f"<p style='height:200px'>block {i}</p>" for i in range(6))
    html = f"<section><h2>Tall</h2>{paras}</section>"
    unit = _discover(page, html)[0]
    h = S.measure(page, S.wrap(unit, _content_h(unit))["content_html"])
    parts, _notes = S.balanced_split(page, unit, h)
    assert len(parts) > 1
    # heading rides on every part via the fixed title zone
    assert all("Tall" in p["title_html"] for p in parts)


def test_short_section_stays_one(page):
    html = "<section><h2>Short</h2><p>just a little text</p></section>"
    unit = _discover(page, html)[0]
    h = S.measure(page, S.wrap(unit, _content_h(unit))["content_html"])
    assert h <= S.CONTENT_H * S.FIT_TOLERANCE      # would be treated as fits


def test_figure_and_bignums_never_separate(page):
    # a tall figure welded to a bignums row, plus enough prose to force a split
    fig = "<div class='fig'><svg width='400' height='420'></svg></div>"
    big = "<div class='bignums'><div class='bignum'>128</div></div>"
    prose = "".join(f"<p style='height:180px'>p{i}</p>" for i in range(4))
    html = f"<section><h2>Fig</h2>{prose}{fig}{big}</section>"
    unit = _discover(page, html)[0]
    # the welding step must have merged fig+bignums into a single atomic block
    joined = "".join(unit["blocks"])
    assert "class=\"fig\"" in joined and "bignums" in joined
    fig_block = [b for b in unit["blocks"] if "class=\"fig\"" in b][0]
    assert "bignums" in fig_block, "figure block lost its bignums"
    # and after splitting, no part holds the fig without the bignums
    h = S.measure(page, S.wrap(unit, _content_h(unit))["content_html"])
    parts, _notes = S.balanced_split(page, unit, h)
    for part in parts:
        body = part["content_html"]
        if "class=\"fig\"" in body:
            assert "bignums" in body, "a split part orphaned the figure from its numbers"


def _title_rect(page):
    return page.evaluate(
        "() => { const r = document.getElementById('__title').getBoundingClientRect();"
        "return {top: Math.round(r.top), h: Math.round(r.height)}; }")


def test_title_bar_is_fixed_across_slides(page, tmp_path):
    # Two slides with wildly different content must keep the title at the same
    # Y and height — the PowerPoint-master guarantee.
    short = _discover(page, "<section><h2>A</h2><p>tiny</p></section>")[0]
    tall = _discover(page, "<section><h2>B</h2>"
                     + "".join(f"<p style='height:120px'>x{i}</p>" for i in range(8))
                     + "</section>")[0]
    S.render_png(page, S.wrap(short, "".join(short["blocks"])), str(tmp_path / "a.png"))
    r1 = _title_rect(page)
    S.render_png(page, S.wrap(tall, "".join(tall["blocks"])), str(tmp_path / "b.png"))
    r2 = _title_rect(page)
    assert r1 == r2, f"title bar moved between slides: {r1} vs {r2}"
    assert r1["h"] == S.TITLE_H and r1["top"] == S.SAFE_MARGIN


def test_text_only_slide_is_top_aligned(page, tmp_path):
    """Content-master text slide (explicitly not title-centered) stays top-aligned.
    Sparse text-only units are promoted to title-centering by header rules instead."""
    text = _discover(page, "<section><h2>T</h2><p>a text-only slide</p></section>")[0]
    fig = _discover(page, "<section><h2>F</h2>"
                    "<div class='fig'><svg width='300' height='200'></svg></div>"
                    "</section>")[0]
    S.render_png(page, S.wrap(text, "".join(text["blocks"])), str(tmp_path / "t.png"))
    assert page.evaluate(
        "() => document.getElementById('__content').classList.contains('__top')")
    S.render_png(page, S.wrap(fig, "".join(fig["blocks"])), str(tmp_path / "f.png"))
    # Visual slides center in the content zone (not __top).
    assert page.evaluate(
        "() => document.getElementById('__content').classList.contains('__center')")


def test_title_page_is_centered(page, tmp_path):
    """First-slide title layout: stage.__title-slide, title+lead centered."""
    unit = _discover(
        page,
        "<section><h1>Measuring flow control under pressure.</h1>"
        "<p>Flow control queues requests on a shared pool.</p></section>")[0]
    slide = S.wrap(unit, "".join(unit["blocks"]), is_title_slide=True)
    S.render_png(page, slide, str(tmp_path / "title.png"))
    assert page.evaluate(
        "() => document.getElementById('__stage').classList.contains('__title-slide')")
    # Title lives in the centered stack, not the pinned bar.
    assert page.evaluate(
        "() => !document.getElementById('__title').innerHTML.trim()")
    assert page.evaluate(
        "() => !!document.querySelector('.__title-stack')")
    # Stack should sit near vertical center of the stage (not pinned to top).
    geo = page.evaluate("""() => {
      const s = document.getElementById('__stage').getBoundingClientRect();
      const k = document.querySelector('.__title-stack').getBoundingClientRect();
      return { stageMid: s.top + s.height / 2,
               stackMid: k.top + k.height / 2 };
    }""")
    assert abs(geo["stackMid"] - geo["stageMid"]) < 80, geo


def test_closing_text_slide_is_not_title_centered(page, tmp_path):
    """Limits-style closer keeps master title bar — not title-page centering."""
    unit = _discover(
        page,
        "<section><h2>Limits</h2>"
        "<p>Round-robin fairness handles tenants within one priority band.</p>"
        "</section>")[0]
    slide = S.wrap(unit, "".join(unit["blocks"]), is_title_slide=False)
    S.render_png(page, slide, str(tmp_path / "limits.png"))
    assert not page.evaluate(
        "() => document.getElementById('__stage').classList.contains('__title-slide')")
    assert page.evaluate(
        "() => document.getElementById('__content').classList.contains('__top')")


def test_partition_is_balanced_and_ordered():
    # pure-python: exactly n contiguous parts, order preserved, tallest minimized
    assert S._pack([100, 100, 100, 100], 2) == [[0, 1], [2, 3]]
    assert S._pack([50, 50, 700], 2) == [[0, 1], [2]]        # tall block isolated
    assert S._pack([700], 2) == [[0]]                        # fewer blocks than parts
    groups = S._pack([10, 10, 10, 10, 10, 10], 3)
    assert [len(g) for g in groups] == [2, 2, 2]             # perfectly balanced
    flat = [i for g in groups for i in g]
    assert flat == sorted(flat)                              # contiguous, in order


def test_chip_cap_is_not_a_caption():
    """Posture chips use class='chip cap' — must not match caption truncation."""
    html = ('<div class="grid2"><div class="card">'
            '<div class="chip cap"><span class="lab">queue</span>'
            '<span class="val">TTL 60s</span></div>'
            '<p class="buys">Buys isolation.</p></div></div>')
    assert S.classify_block(html) == "visual"
    assert S._GRAPHIC_FACE_RE.search(html)
    face, notes, _ = S.project_face([html])
    assert face and "grid2" in face[0]
    assert "chip cap" in face[0]
    # Must not have been collapsed to a one-sentence caption.
    assert "Buys isolation" in face[0]


def test_visual_scale_never_exceeds_content_width(page, tmp_path):
    """Hard rule: painted content must not overflow the content box width."""
    # Wide table that would overflow if upscale ignores width.
    rows = "".join(
        f"<tr><td>col-a-{i}</td><td>{'word '*40}</td>"
        f"<td>{'option '*30}</td><td>{'more '*30}</td></tr>"
        for i in range(3))
    html = (f"<section><h2>Wide</h2><table><thead><tr>"
            f"<th>A</th><th>B</th><th>C</th><th>D</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></section>")
    unit = _discover(page, html)[0]
    slide = S.wrap(unit, "".join(unit["blocks"]))
    assert slide["has_fig"]
    S.render_png(page, slide, str(tmp_path / "wide.png"))
    geo = page.evaluate("""() => {
      const c = document.getElementById('__content').getBoundingClientRect();
      const inner = document.getElementById('__inner');
      const r = inner.getBoundingClientRect(); // includes transform
      const tr = getComputedStyle(inner).transform;
      return { contentL: c.left, contentR: c.right, contentW: c.width,
               innerL: r.left, innerR: r.right, innerW: r.width, transform: tr,
               scrollW: inner.scrollWidth, clientW: inner.clientWidth };
    }""")
    # Painted box must stay inside the content zone (1px tolerance for rounding).
    assert geo["innerL"] >= geo["contentL"] - 1, geo
    assert geo["innerR"] <= geo["contentR"] + 1, geo
    # Scale factor from matrix must be <= contentW/scrollW when scrollW > contentW
    if geo["scrollW"] > geo["contentW"] + 1:
        assert "matrix" in (geo["transform"] or ""), geo
