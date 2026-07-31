#!/usr/bin/env python3
"""
html2deck — slice an HTML page into 16:9 slides by MEASURING, not guessing.

Core idea: a slide is 1280x720. Walk the page's top-level "units" (each
`--unit-selector` match). Project a visual-first face (excess prose → speaker
notes), then render each unit alone on a 1280x720 stage in headless Chromium
and measure its real height. If it fits under the readable budget (with a
small overflow tolerance), it is one slide. If it is genuinely taller, split
it at safe child boundaries into balanced parts, repeating the heading on
each part — never shrinking text below the readability floor.

Content grouping is respected: a figure (svg/img/figure/.fig) is welded to an
adjacent caption or bignums row so a chart never lands on a different slide
from the numbers that explain it.

Composition fit (best-fit equation in SKILL.md) prefers ~72% fill at scale
≥0.90, visual primacy when a chart exists, and strip/split over scale.

Output (always): _out/slides/*.png and _out/slice-report.json. Feed the report
to contact_sheet.py for an approval grid and to build.py for the .pptx/.pdf.

Usage:
    python3 slice.py <source.html> [--out DIR] [--unit-selector CSS]
                     [--theme light|dark] [--keep-source]
"""
import sys, json, argparse, math, re, html as _html
from pathlib import Path
from playwright.sync_api import sync_playwright, Error as PWError

SLIDE_W, SLIDE_H = 1280, 720           # 16:9
SAFE_MARGIN = 48                        # px breathing room on all sides
TITLE_H = 96                            # pinned top zone for the heading (master-style)
TITLE_GAP = 16                          # hard gap between title bar and content
CONTENT_H = SLIDE_H - 2 * SAFE_MARGIN - TITLE_H - TITLE_GAP
FIT_TOLERANCE = 1.10                    # keep whole on one slide within +10% of budget

# Face / composition contract (see SKILL.md "Layout contract")
MAX_PROSE_SENTENCES = 2                 # per prose/callout block on the face
MAX_PROSE_WORDS = 40                    # per prose/callout block on the face
MAX_BULLETS = 4
MAX_BULLET_WORDS = 12
MAX_CAPTION_SENTENCES = 1
MAX_LEAD_SENTENCES = 1
FILL_MIN, FILL_MAX, FILL_SWEET = 0.50, 0.92, 0.72
FILL_SIGMA = 0.12
FILL_VISUAL = 0.95                     # visual slides: grow into nearly all of CONTENT_H
MAX_UPSCALE = 1.85                      # grow under-filled visuals; never past content box
VISUAL_SHARE_MIN = 0.55                 # when a visual is present
PROSE_SHARE_MAX = 0.30                  # when a visual is present
FACE_WORD_SANITY = 60                   # residual whole-face flag after projection
WORD_BUDGET = FACE_WORD_SANITY          # alias kept for tests / stderr copy
EMPTY_FACE_WORDS = 12                   # drop slides with no visual below this
MERGE_PART_H = int(CONTENT_H * 0.55)    # merge undersized parts below this
SPARSE_TABLE_WORDS = 55                 # small tables must merge, not own a slide

# Alignment equation (content slides):
#   CONTENT_H = SLIDE_H − 2·MARGIN − TITLE_H − TITLE_GAP
#   s_fit     = min(1, CONTENT_H / h, CONTENT_W / w)  # never overflow
#   s_fill    = min(MAX_UPSCALE, FILL_VISUAL·CONTENT_H / h)  # grow visuals
#   s         = s_fit if h > CONTENT_H else (s_fill if visual else 1)
# Visual slides: content is vertically centered in the content zone.
# Title zone is z-stacked above content; content is clipped to CONTENT_H.
# Prefer strip/split over scale. Ordinary packings target s ≥ PREFERRED_FIT_SCALE;
# a single unsplittable block may go below that at render — fit always wins.
PREFERRED_FIT_SCALE = 0.90
EMERGENCY_FIT_SCALE = 0.80
MIN_FIT_SCALE = PREFERRED_FIT_SCALE

# Visual-slide chrome (more canvas for the graph under a shorter title bar).
VISUAL_TITLE_H = 56
VISUAL_TITLE_GAP = 4
VISUAL_SAFE_MARGIN = 28
VISUAL_CONTENT_H = SLIDE_H - 2 * VISUAL_SAFE_MARGIN - VISUAL_TITLE_H - VISUAL_TITLE_GAP

# One unit on a 1280x720 canvas, on the page's own background/styles.
# Layout is a fixed grid: a pinned title zone of TITLE_H at the top (same Y and
# height on EVERY slide, like a PowerPoint master) and a content zone below it.
# The content zone alone is scaled to fit; the title never moves or resizes.
STAGE_CSS = f"""
  html,body{{margin:0;padding:0;background:transparent}}
  #__stage{{width:{SLIDE_W}px;height:{SLIDE_H}px;overflow:hidden;position:relative;
    display:flex;flex-direction:column;box-sizing:border-box;padding:{SAFE_MARGIN}px}}
  #__title{{flex:0 0 {TITLE_H}px;height:{TITLE_H}px;overflow:hidden;position:relative;
    z-index:5;display:flex;flex-direction:column;justify-content:flex-start;
    background:#fafafa;isolation:isolate;flex-shrink:0}}
  #__title > *{{margin:0}}
  #__gap{{flex:0 0 {TITLE_GAP}px;height:{TITLE_GAP}px;flex-shrink:0;
    background:#fafafa;z-index:5;position:relative}}
  #__content{{flex:1 1 auto;min-height:0;height:{CONTENT_H}px;max-height:{CONTENT_H}px;
    position:relative;width:100%;overflow:hidden;z-index:1;
    display:flex;flex-direction:column;justify-content:flex-start;
    contain:paint}}
  #__content.__top{{justify-content:flex-start}}
  #__content.__center{{justify-content:center;align-items:center}}
  #__fit{{width:100%;height:100%;overflow:hidden;position:relative;
    transform-origin:top center;contain:paint}}
  #__fit.__center{{display:flex;align-items:center;justify-content:center;
    transform-origin:center center}}
  #__fit > *, #__inner, #__inner > .__face{{max-width:100%;width:100%;box-sizing:border-box;
    margin:0!important;box-shadow:none!important}}
  /* Kill page-card chrome that bleeds into the title (section shadows, etc.) */
  #__inner section, #__inner .hero, #__inner .__face,
  #__inner .card, #__inner .wide, #__inner article{{
    box-shadow:none!important;margin-top:0!important;margin-bottom:0!important;
    position:static!important;top:auto!important}}
  #__content img,#__content svg{{max-height:100%}}
  /* Visual slides: shorter title bar, more canvas for the graph */
  #__stage.__visual{{padding:{VISUAL_SAFE_MARGIN}px}}
  #__stage.__visual #__title{{flex:0 0 {VISUAL_TITLE_H}px;height:{VISUAL_TITLE_H}px}}
  #__stage.__visual #__gap{{flex:0 0 {VISUAL_TITLE_GAP}px;height:{VISUAL_TITLE_GAP}px}}
  #__stage.__visual #__content{{height:{VISUAL_CONTENT_H}px;max-height:{VISUAL_CONTENT_H}px}}
  #__stage.__visual #__title h1,#__stage.__visual #__title h2,
  #__stage.__visual #__title h3{{font-size:clamp(24px,2.2vw,32px)!important;line-height:1.15}}
  /* PowerPoint-style title slide ONLY (first slide of the deck).
     Standard 16:9 title type is ~44–54pt; we sit slightly large for 1280 canvas. */
  #__stage.__title-slide{{justify-content:center;align-items:center}}
  #__stage.__title-slide #__title,
  #__stage.__title-slide #__gap{{display:none;flex:0;height:0;overflow:hidden}}
  #__stage.__title-slide #__content{{flex:0 0 auto;width:100%;max-width:100%;
    height:auto;max-height:none;overflow:visible;
    justify-content:center;align-items:center}}
  #__stage.__title-slide #__content.__top{{justify-content:center}}
  #__stage.__title-slide .__title-stack{{display:flex;flex-direction:column;
    align-items:center;justify-content:center;text-align:center;width:100%;
    gap:22px;box-sizing:border-box}}
  #__stage.__title-slide .__title-stack > *{{text-align:center;margin-left:auto;
    margin-right:auto;max-width:56ch;width:auto}}
  #__stage.__title-slide .__title-stack h1,
  #__stage.__title-slide .__title-stack h2,
  #__stage.__title-slide .__title-stack h3{{text-align:center;width:auto;
    font-size:clamp(48px,5.2vw,68px)!important;line-height:1.12;
    letter-spacing:-0.025em}}
  #__stage.__title-slide .__title-stack p{{font-size:clamp(20px,1.85vw,26px)!important;
    line-height:1.45;opacity:.88;max-width:44ch}}
  #__stage.__title-slide hr,
  #__stage.__title-slide .rule,
  #__stage.__title-slide .divider{{display:none!important}}
  /* Title / section-header slides: NEVER a graphic, card, table, or figure.
     Source <section> chrome (shadow, plate, stripe) is stripped. */
  #__stage.__title-slide .__title-stack section,
  #__stage.__title-slide .__title-stack article,
  #__stage.__title-slide .__title-stack .card,
  #__stage.__title-slide .__title-stack [class*="panel"],
  #__stage.__title-slide .__title-stack [class*="signal"],
  #__stage.__title-slide .__title-stack table,
  #__stage.__title-slide .__title-stack figure,
  #__stage.__title-slide .__title-stack img,
  #__stage.__title-slide .__title-stack svg,
  #__stage.__title-slide .__title-stack .assetcard,
  #__stage.__title-slide .__title-stack .fig{{
    background:transparent!important;box-shadow:none!important;
    border:none!important;border-radius:0!important;padding:0!important;
    margin:0!important;width:auto!important;max-width:44ch!important}}
  #__stage.__title-slide .__title-stack table,
  #__stage.__title-slide .__title-stack figure,
  #__stage.__title-slide .__title-stack img,
  #__stage.__title-slide .__title-stack svg,
  #__stage.__title-slide .__title-stack .assetcard,
  #__stage.__title-slide .__title-stack .fig,
  #__stage.__title-slide .__title-stack .signal-list,
  #__stage.__title-slide .__title-stack .run-groups,
  #__stage.__title-slide .__title-stack .setup-grid{{display:none!important}}
  /* Content-slide master title: larger than body, not title-page scale */
  #__title h1,#__title h2,#__title h3{{font-size:clamp(28px,2.6vw,36px)!important;
    line-height:1.2;letter-spacing:-0.02em}}
"""


# INTERIM (stopgap, remove once svgchart drives themed charts): on a dark slide,
# a chart that is still a baked light-background image reads as a raw white
# rectangle. Until charts re-render from a dark palette, wrap those light plates
# in a soft neutral figure-plate card (rounded, subtle border, gentle padding)
# so they read as an intentional inset rather than a broken white box. Applied
# only under --theme dark; a natively themed chart is the real fix.
FIGURE_PLATE_CSS = """
  #__content img,
  #__content figure,
  #__content .assetcard,
  #__content [class*="chart"]{
    background:#f4f5f7;border:1px solid rgba(255,255,255,.14);
    border-radius:14px;padding:14px;box-shadow:0 1px 3px rgba(0,0,0,.35)}
"""

# Deck-facing boost: page CSS often leaves charts/tables as narrow cards on a
# wide canvas (postage stamps). Force face content to use the content zone.
DECK_BOOST_CSS = """
  /* Full-bleed content: cut L/R gutter from page cards; shrink-wrap height
     (no empty belly). Upscale is transform-only when still under fill. */
  #__content{font-size:122%}
  #__content > *{width:100%;max-width:100%;box-sizing:border-box}
  #__content .assetcard,
  #__content figure,
  #__content .fig,
  #__content [class*="chart"],
  #__content .tblwrap,
  #__content .card,
  #__content [class*="panel"]{
    width:100%!important;max-width:100%!important;
    margin-left:0!important;margin-right:0!important;
    box-sizing:border-box;
    padding:6px 8px!important;
    /* shrink-wrap — never invent empty vertical space inside the card */
    min-height:0!important;height:auto!important}
  #__content table{width:100%!important;max-width:100%!important;
    font-size:0.95em;table-layout:fixed!important}
  #__content table th,#__content table td{
    word-wrap:break-word;overflow-wrap:anywhere;hyphens:auto}
  #__content .assetcard img,
  #__content figure img,
  #__content .fig img,
  #__content .assetcard svg,
  #__content figure svg,
  #__content .fig svg{width:100%!important;height:auto!important;
    max-height:none!important;min-height:0;display:block}
  /* Visual slides: give the chart the vertical room; hide redundant fig chrome */
  #__stage.__visual #__content .assetcard > figcaption,
  #__stage.__visual #__content figure > figcaption{display:none!important}
  #__content p.caption,
  #__content .caption,
  #__content figcaption,
  #__content .src{display:none!important}
"""

# Injected once; discovers units and returns each unit's atomic split blocks.
# An atomic block = one or more consecutive children that must stay together
# (a figure welded to an adjacent caption/bignums row). Heading is separated so
# it can be repeated on every part.
DISCOVER_JS = r"""
(sel) => {
  const isFig = el => /(^|\s)(fig|figure|chart|assetcard)(\s|$)/i.test(el.className)
    || ['svg','img','figure','picture'].includes(el.tagName.toLowerCase())
    || !!el.querySelector('svg,img,figure,canvas');
  const isCap = el => /(^|\s)(bignum|bignums|caption|cap|note|legend|source)(\s|$)/i.test(el.className);
  // One-level expand so tall group wrappers can split into atomic parts.
  const isExpand = el => /(^|\s)(run-groups|signal-list|collection-record|setup-grid|chart-pair|metric-visuals|visual-grid)(\s|$)/i
    .test(el.className || '');
  const outer = el => el.outerHTML;
  const nodes = [...document.querySelectorAll(sel)];
  return nodes.map((n, i) => {
    const heading = n.querySelector('h1,h2,h3,h4');
    const headHTML = heading ? heading.outerHTML : '';
    const title = heading ? heading.innerText.trim().replace(/\s+/g, ' ')
                          : (n.id || ('Slide ' + (i + 1)));
    // block-level children, heading excluded, welded into atomic groups
    const kids = [...n.children].filter(c => c !== heading);
    const blocks = [];
    for (let j = 0; j < kids.length; j++) {
      const c = kids[j];
      if (isExpand(c) && c.children.length >= 2) {
        for (const sub of [...c.children]) blocks.push(outer(sub));
        continue;
      }
      let group = [outer(c)];
      // weld a figure to the caption/bignums that immediately follows it
      if (isFig(c) && kids[j + 1] && isCap(kids[j + 1])) {
        group.push(outer(kids[++j]));
      // weld a caption/bignums to the figure that immediately precedes it
      } else if (isCap(c) && kids[j - 1] && isFig(kids[j - 1]) && blocks.length) {
        blocks[blocks.length - 1] += outer(c);
        continue;
      }
      blocks.push(group.join(''));
    }
    return {
      idx: i, id: n.id || ('unit' + i), title,
      tag: n.tagName.toLowerCase(), cls: n.className || '',
      headHTML, blocks, outerHTML: n.outerHTML
    };
  });
}
"""


def _settle(page):
    """Best-effort wait for fonts + images to finish so measurement is real."""
    try:
        page.wait_for_function(
            "() => document.fonts ? document.fonts.status === 'loaded' : true",
            timeout=2000)
    except PWError:
        pass
    try:
        page.evaluate("""() => Promise.all(
          [...document.images].filter(i => !i.complete)
            .map(i => new Promise(r => { i.onload = i.onerror = r; }))
        )""")
    except PWError:
        pass
    page.wait_for_timeout(80)


def _ensure_zones(page):
    """Create the fixed #__title / #__gap / #__content zones inside the stage once."""
    page.evaluate("""() => {
      let s = document.getElementById('__stage');
      if (!s) { s = document.createElement('div'); s.id = '__stage';
        document.body.innerHTML = ''; document.body.appendChild(s); }
      if (!document.getElementById('__title')) {
        s.innerHTML = '<div id="__title"></div><div id="__gap"></div><div id="__content"></div>';
      } else if (!document.getElementById('__gap')) {
        const t = document.getElementById('__title');
        const g = document.createElement('div'); g.id = '__gap';
        t.after(g);
      }
    }""")


def measure(page, content_html):
    """Render content_html at content-zone width; return its unclipped height.

    Uses an off-stage probe so flex layout on #__content cannot stretch a short
    block to the full slide height (which broke sparse-part detection)."""
    _ensure_zones(page)
    return page.evaluate("""(html) => {
      const probe = document.createElement('div');
      probe.id = '__measure_probe';
      probe.style.cssText = 'position:absolute;left:-12000px;top:0;width:1184px;'
        + 'height:auto;overflow:visible;pointer-events:none;';
      probe.innerHTML = html;
      document.body.appendChild(probe);
      const h = Math.ceil(probe.scrollHeight);
      probe.remove();
      return h;
    }""", content_html)



def render_png(page, slide, out_path):
    """Render one slide at exactly 1280x720 (2x device scale) and screenshot it.

    Alignment equation (content slides):
        CONTENT_H = SLIDE_H − 2·MARGIN − TITLE_H
        s_fit = min(1, CONTENT_H/h, CONTENT_W/w)   # hard: never overflow
        s_fill = min(MAX_UPSCALE, FILL_SWEET·CONTENT_H/h)  # optional grow
        s = s_fit if h>CONTENT_H else (s_fill if visual else 1)

    Title is z-stacked above a clipped content box. Fit always wins over the
    preferred/emergency readability floors (those guide split decisions only).
    Title/spotlight (`is_title_slide`): centered PowerPoint title layout."""
    _ensure_zones(page)
    # Opaque title/gap/stage backgrounds — never transparent (box-shadows show through).
    page.evaluate("""() => {
      const s = document.getElementById('__stage');
      const t = document.getElementById('__title');
      const g = document.getElementById('__gap');
      if (!s || !t) return;
      const sample = document.createElement('div');
      sample.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;z-index:-1';
      document.body.appendChild(sample);
      let bg = getComputedStyle(document.body).backgroundColor;
      // Ignore fully transparent
      if (!bg || bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent') {
        const theme = document.documentElement.getAttribute('data-theme');
        bg = theme === 'dark' ? '#0e1014' : '#fafafa';
      }
      sample.remove();
      t.style.background = bg;
      s.style.background = bg;
      if (g) g.style.background = bg;
    }""")
    page.evaluate(f"""(sl) => {{
      const s = document.getElementById('__stage');
      const t = document.getElementById('__title');
      const c = document.getElementById('__content');
      const visual = !!sl.has_fig && !sl.is_title_slide;
      const contentH = visual ? {VISUAL_CONTENT_H} : {CONTENT_H};
      const contentW = visual
        ? {SLIDE_W - 2 * VISUAL_SAFE_MARGIN}
        : {SLIDE_W - 2 * SAFE_MARGIN};
      const fitInto = (host, html, availH, availW, allowUp, center) => {{
        host.innerHTML = '<div id="__fit"><div id="__inner">' + html + '</div></div>';
        const fit = host.querySelector('#__fit');
        const inner = host.querySelector('#__inner');
        fit.style.height = availH + 'px';
        fit.style.width = '100%';
        fit.style.overflow = 'hidden';
        fit.classList.toggle('__center', !!center);
        inner.style.transform = '';
        inner.style.width = '100%';
        inner.style.maxWidth = '100%';
        const needH = Math.max(1, inner.scrollHeight);
        const needW = Math.max(1, inner.scrollWidth);
        let scale = Math.min(1, availH / needH, availW / needW);
        if (allowUp && center) {{
          // Visuals: grow toward content-box height, but NEVER past width.
          // Width overflow (clipped columns / cut-off table text) is a hard fail.
          const fillH = availH / needH;
          const fillW = availW / needW;
          if (needH <= availH * 1.12 && fillW >= 0.999) {{
            scale = Math.min({MAX_UPSCALE}, Math.max(scale, fillH), fillW);
          }} else {{
            scale = Math.min(1, fillH, fillW);
          }}
        }} else if (allowUp && scale >= 0.999 && needH < availH * {FILL_SWEET}) {{
          scale = Math.min({MAX_UPSCALE}, (availH * {FILL_SWEET}) / needH,
                           availW / needW);
        }}
        // Hard clamp — painted size must fit the content box on BOTH axes.
        scale = Math.min(scale, availH / needH, availW / needW, {MAX_UPSCALE});
        if (Math.abs(scale - 1) > 0.005) {{
          inner.style.transformOrigin = center ? 'center center' : 'top center';
          inner.style.transform = 'scale(' + scale + ')';
        }}
        return scale;
      }};
      s.classList.toggle('__title-slide', !!sl.is_title_slide);
      s.classList.toggle('__visual', visual);
      if (sl.is_title_slide) {{
        t.innerHTML = '';
        c.classList.remove('__top', '__center');
        c.style.height = 'auto';
        c.style.maxHeight = 'none';
        c.style.overflow = 'visible';
        c.innerHTML = '<div class="__title-stack">' + (sl.title_html || '')
          + (sl.content_html || '') + '</div>';
        const stack = c.firstElementChild;
        const avail = s.clientHeight - {2 * SAFE_MARGIN};
        if (stack && stack.scrollHeight > avail) {{
          const sc = Math.min(1, avail / stack.scrollHeight);
          stack.style.transformOrigin = 'center center';
          stack.style.transform = 'scale(' + sc + ')';
        }}
        return;
      }}
      t.innerHTML = sl.title_html + (sl.part_label
        ? '<div style="position:absolute;top:0;right:0;'
          + 'font:600 13px system-ui,sans-serif;opacity:.45">'
          + sl.part_label + '</div>'
        : '');
      c.classList.toggle('__top', !visual);
      c.classList.toggle('__center', visual);
      c.style.height = contentH + 'px';
      c.style.maxHeight = contentH + 'px';
      c.style.overflow = 'hidden';
      fitInto(c, sl.content_html || '', c.clientHeight || contentH,
              c.clientWidth || contentW, !!sl.has_fig, visual);
    }}""", {**slide, "emergency_scale": bool(slide.get("emergency_scale")),
            "is_title_slide": bool(slide.get("is_title_slide")),
            "has_fig": bool(slide.get("has_fig"))})
    _settle(page)
    page.locator("#__stage").screenshot(path=out_path)


# ---------------------------------------------------------------------------
# Face projection + composition scoring
# ---------------------------------------------------------------------------

_VISUAL_RE = re.compile(
    r"(?is)(<svg\b|<img\b|<figure\b|<canvas\b|<picture\b|"
    r"class=[\"'][^\"']*\b(fig|figure|chart|assetcard|grid2|grid3|card-grid)\b)")
_TABLE_RE = re.compile(
    r"(?is)(<table\b|class=[\"'][^\"']*\b(tblwrap|datatable|table)\b)")
# Do NOT match bare `\bcap\b` — posture chips use `class="chip cap"` and must
# stay on the face as a card grid, not get truncated as captions.
_CAPTION_RE = re.compile(
    r"(?is)class=[\"'][^\"']*\b(bignum|bignums|caption|note|legend|source)\b")
_LIST_RE = re.compile(r"(?is)^<(ul|ol)\b")
_CALLOUT_RE = re.compile(
    r"(?is)class=[\"'][^\"']*\b(callout|aside|call-out|note-box|notice|tip|warn)\b")
_LI_RE = re.compile(r"(?is)(<li\b[^>]*>)(.*?)(</li>)")
# Web-page chrome that must never become a slide face (links, action bars, rules).
_CHROME_PATTERNS = [
    # Collapsed "View the data" disclosure — full table lives in notes, not a chip slide.
    re.compile(
        r"(?is)<details\b[^>]*class=[\"'][^\"']*\bviewdata\b[^\"']*[\"'][^>]*>.*?</details>"),
    re.compile(r"(?is)<a\b[^>]*>\s*(?:<[^>]+>\s*)*View the data\s*(?:[^<]*|<\s*/?\w+[^>]*>)*\s*</a>"),
    re.compile(r"(?is)<button\b[^>]*>.*?View the data.*?</button>"),
    re.compile(r"(?is)<hr\b[^>]*/?>"),
    re.compile(
        r"(?is)<(div|nav|p|span)\b[^>]*class=[\"'][^\"']*\b("
        r"actions|toolbar|permalink|data-link|view-data|asset-link|chip-row"
        r")\b[^\"']*[\"'][^>]*>.*?</\1>"),
]


def strip_chrome(html_fragment):
    """Remove web-page chrome (View the data, hr, action bars) from a block."""
    out = html_fragment
    for pat in _CHROME_PATTERNS:
        out = pat.sub("", out)
    # drop empties left behind
    out = re.sub(r"(?is)<(div|p|span|section)\b[^>]*>\s*</\1>", "", out)
    return out.strip()


def _block_is_empty(html_fragment):
    """True when a block has no visual and almost no face text (after chrome strip)."""
    cleaned = strip_chrome(html_fragment)
    if not cleaned:
        return True
    if classify_block(cleaned) in ("visual", "table"):
        return False
    return len(_words(_plain(cleaned))) < 3


def _plain(html_fragment):
    """Markup → plain text (no script/style/svg guts)."""
    txt = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", html_fragment)
    txt = re.sub(r"(?s)<[^>]+>", " ", txt)
    return _html.unescape(txt)


def _words(text):
    return [w for w in text.split() if w]


def _sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p for p in parts if p.strip()]


def classify_block(html_fragment):
    """Classify one atomic block for face rules / composition scoring."""
    if _TABLE_RE.search(html_fragment):
        return "table"
    if _VISUAL_RE.search(html_fragment):
        return "visual"
    if _CAPTION_RE.search(html_fragment):
        return "caption"
    if _LIST_RE.match(html_fragment.strip()):
        return "list"
    if _CALLOUT_RE.search(html_fragment):
        return "callout"
    return "prose"


def _first_n_sentences_html(html_fragment, n):
    """Keep the opening tag wrapper but replace body with the first n sentences
    of its plain text. Crude but deterministic — long HTML prose becomes a
    short face line; full text is already captured for notes."""
    text = _plain(html_fragment).strip()
    kept = " ".join(_sentences(text)[:n]).strip()
    if not kept:
        return html_fragment
    m = re.match(r"(?is)^(<([a-z0-9]+)(\s[^>]*)?>)(.*)(</\2\s*>)$",
                 html_fragment.strip(), re.DOTALL)
    if not m:
        return f"<p>{_html.escape(kept)}</p>"
    return f"{m.group(1)}{_html.escape(kept)}{m.group(5)}"


def _project_list(html_fragment):
    """Keep ≤MAX_BULLETS short one-liner <li>s; return (face_html|None, notes)."""
    notes = []
    kept = []
    for m in _LI_RE.finditer(html_fragment):
        open_t, body, close_t = m.group(1), m.group(2), m.group(3)
        text = _plain(body).strip()
        sents, wcount = _sentences(text), len(_words(text))
        if len(kept) >= MAX_BULLETS or len(sents) > 1 or wcount > MAX_BULLET_WORDS:
            if text:
                notes.append(text)
            continue
        kept.append(f"{open_t}{body}{close_t}")
    if not kept:
        return None, notes
    # rebuild list with original outer tag
    outer = re.match(r"(?is)^<(ul|ol)(\b[^>]*)>", html_fragment.strip())
    tag, attrs = (outer.group(1), outer.group(2)) if outer else ("ul", "")
    return f"<{tag}{attrs}>{''.join(kept)}</{tag}>", notes


def project_face(blocks, keep_source=False):
    """Apply face rules to a unit's atomic blocks.

    Returns (face_blocks, stripped_note_lines, did_strip).
    When keep_source=True, face_blocks == blocks and nothing is stripped.
    """
    if keep_source or not blocks:
        return list(blocks), [], False

    face, notes = [], []
    lead_used = False
    did_strip = False

    for raw0 in blocks:
        raw = strip_chrome(raw0)
        if raw != raw0:
            did_strip = True
        if _block_is_empty(raw0) or (raw and _block_is_empty(raw)) or not raw:
            # chrome-only / empty block — never a face
            text = _plain(raw0).strip()
            if text:
                notes.append(text)
                did_strip = True
            continue

        kind = classify_block(raw)
        text = _plain(raw).strip()
        sents, wcount = _sentences(text), len(_words(text))

        # Signal / scenario cards are graphics for title-page purposes —
        # never land on a title slide; move to notes (or a later content slide
        # via header rules if kept on face elsewhere).
        if re.search(r"(?is)class=[\"'][^\"']*\b(signal-list|signal-item)\b", raw):
            notes.append(text)
            did_strip = True
            continue

        if kind in ("visual", "table"):
            face.append(raw)
            continue

        if kind == "caption":
            # Chart cards already carry their own subtitle — external captions
            # under a visual become redundant footer text. Move to notes.
            under_visual = bool(face) and classify_block(face[-1]) == "visual"
            if under_visual:
                notes.append(text)
                did_strip = True
                continue
            if sents and len(sents) > MAX_CAPTION_SENTENCES:
                face.append(_first_n_sentences_html(raw, MAX_CAPTION_SENTENCES))
                notes.append(text)
                did_strip = True
            else:
                face.append(raw)
            continue

        if kind == "list":
            rebuilt, dropped = _project_list(raw)
            if dropped:
                notes.extend(dropped)
                did_strip = True
            if rebuilt:
                # lists under a visual → notes (chart owns the face)
                if face and classify_block(face[-1]) in ("visual", "table"):
                    notes.append(_plain(rebuilt).strip() or text)
                    did_strip = True
                else:
                    face.append(rebuilt)
            elif text:
                notes.append(text)
                did_strip = True
            continue

        # Under a visual/table, prose is notes — the chart owns the face.
        if (face and classify_block(face[-1]) in ("visual", "table")
                and kind in ("prose", "callout")):
            notes.append(text)
            did_strip = True
            continue

        # prose / callout
        too_long = len(sents) > MAX_PROSE_SENTENCES or wcount > MAX_PROSE_WORDS
        if too_long:
            if not lead_used and sents:
                face.append(_first_n_sentences_html(raw, MAX_LEAD_SENTENCES))
                lead_used = True
                notes.append(text)
                did_strip = True
            else:
                notes.append(text)
                did_strip = True
            continue

        if kind == "prose" and not lead_used:
            face.append(raw)
            lead_used = True
            continue

        if kind == "callout" and len(sents) <= 1 and wcount <= MAX_BULLET_WORDS:
            face.append(raw)
            continue

        if not too_long and wcount <= MAX_PROSE_WORDS and len(sents) <= MAX_PROSE_SENTENCES:
            if lead_used:
                notes.append(text)
                did_strip = True
            else:
                face.append(raw)
                lead_used = True
            continue

        notes.append(text)
        did_strip = True

    return face, notes, did_strip


def _part_is_sparse(part_blocks, h):
    """True when a part should not own a slide alone (tiny table / thin prose)."""
    html = "".join(part_blocks)
    words = len(_words(_plain(html)))
    has_chart = bool(re.search(
        r"(?is)(<svg\b|<img\b|<canvas\b|class=[\"'][^\"']*\b(chart|assetcard|fig)\b)",
        html))
    has_table = bool(_TABLE_RE.search(html))
    rows = len(re.findall(r"(?is)<tr\b", html))
    # Div-grid "tables" (tblwrap) often have no <tr> — treat low word count as small.
    if has_chart:
        return h < MERGE_PART_H * 0.7
    if has_table and (words <= SPARSE_TABLE_WORDS or (rows and rows <= 4)):
        return True
    if not has_chart and not has_table and words < 40:
        return True
    return h < MERGE_PART_H


def _face_is_droppable(body):
    """True for near-empty faces (button-only leftovers, orphan captions)."""
    if body.get("has_fig"):
        return False
    words = _face_words(body.get("content_html", ""))
    return words < EMPTY_FACE_WORDS


def composition_metrics(page, unit, blocks, heights=None):
    """Compute h, scale s, fill φ, visual share V, prose share for packing B."""
    if not blocks:
        return {"h": 0, "s": 1.0, "phi": 0.0, "V": 0.0, "tau_prose": 0.0,
                "prose_words": 0, "kinds": []}
    if heights is None:
        heights = [measure(page, wrap(unit, b)["content_html"]) for b in blocks]
    h = sum(heights)
    s = 1.0 if h <= 0 else min(1.0, CONTENT_H / h)
    # preferred floor for scoring; emergency handled elsewhere
    phi = (s * h) / CONTENT_H if CONTENT_H else 0.0
    kinds = [classify_block(b) for b in blocks]
    vis_h = sum(ht for ht, k in zip(heights, kinds) if k in ("visual", "table"))
    prose_h = sum(ht for ht, k in zip(heights, kinds)
                  if k in ("prose", "callout", "list"))
    V = (vis_h / h) if h else 0.0
    tau_prose = (prose_h / h) if h else 0.0
    prose_words = sum(len(_words(_plain(b))) for b, k in zip(blocks, kinds)
                      if k in ("prose", "callout", "list"))
    return {"h": h, "s": s, "phi": phi, "V": V, "tau_prose": tau_prose,
            "prose_words": prose_words, "kinds": kinds, "heights": heights}


def composition_score(m):
    """Soft score from SKILL.md best-fit equation. Higher is better."""
    s, phi, V, pw = m["s"], m["phi"], m["V"], m["prose_words"]
    no_scale = 1.0 if s >= 0.999 else s
    fill = math.exp(-((phi - FILL_SWEET) ** 2) / (2 * FILL_SIGMA ** 2))
    return no_scale + fill + 0.5 * V - (pw / 40.0)


def composition_ok(m):
    """Hard constraints from the layout contract (scale floor deferred to
    single-block emergency). Sparse empty slides (phi < FILL_MIN) are allowed
    when content is intentionally short — only flag jam / prose-dominance."""
    has_visual = m["V"] > 0.05 or any(k in ("visual", "table") for k in m["kinds"])
    if m["s"] < PREFERRED_FIT_SCALE and len(m["kinds"]) > 1:
        return False
    if m["phi"] > FILL_MAX:
        return False
    if has_visual and m["tau_prose"] > PROSE_SHARE_MAX:
        return False
    if has_visual and m["V"] < VISUAL_SHARE_MIN and m["tau_prose"] > 0.15:
        return False
    return True


def _strip_prose_from_blocks(blocks):
    """Drop prose/callout/list blocks when a visual needs primacy; return
    (kept, notes, stripped)."""
    kinds = [classify_block(b) for b in blocks]
    has_visual = any(k in ("visual", "table") for k in kinds)
    if not has_visual:
        return blocks, [], False
    kept, notes, stripped = [], [], False
    for b, k in zip(blocks, kinds):
        if k in ("prose", "callout", "list"):
            notes.append(_plain(b).strip())
            stripped = True
        else:
            kept.append(b)
    return (kept or blocks), notes, stripped


def wrap(unit, blocks_html, part_label="", emergency_scale=False,
         is_title_slide=False):
    """Build one slide's render spec: the heading for the fixed title zone, the
    content blocks in a neutral face wrapper (never the page <section> card —
    that shadow/plate paints into the title), and whether the content carries a
    visual (drives upscale). Title/header slides use centered PowerPoint layout."""
    has_fig = ("<svg" in blocks_html or "<img" in blocks_html
               or "<table" in blocks_html or "<figure" in blocks_html
               or "<canvas" in blocks_html or "<picture" in blocks_html
               or bool(re.search(
                   r"(?is)class=[\"'][^\"']*\b(signal-list|run-group|assetcard|"
                   r"fig|scenario-viz|grid2|grid3|card-grid)\b",
                   blocks_html)))
    if is_title_slide:
        return {
            "title_html": unit["headHTML"],
            "content_html": blocks_html or "",
            "part_label": "",
            "has_fig": False,
            "emergency_scale": False,
            "is_title_slide": True,
        }
    # Neutral wrapper — do NOT re-use <section class=…> from the page; those
    # cards carry box-shadow / negative margins that bleed into the title bar.
    return {
        "title_html": unit["headHTML"],
        "content_html": f'<div class="__face">{blocks_html}</div>',
        "part_label": part_label,
        "has_fig": has_fig,
        "emergency_scale": emergency_scale,
        "is_title_slide": False,
    }


_GRAPHIC_FACE_RE = re.compile(
    r"(?is)(<svg\b|<img\b|<table\b|<figure\b|<canvas\b|<picture\b|"
    r"class=[\"'][^\"']*\b(signal-list|signal-item|run-group|run-groups|"
    r"setup-grid|collection-record|assetcard|fig|tblwrap|grid2|grid3|"
    r"card-grid)\b)")


def _plain_lead_html(blocks) -> tuple[str, list[str]]:
    """At most one short lead <p> for a title/header slide; rest → notes."""
    lead, notes = "", []
    for b in blocks:
        if _GRAPHIC_FACE_RE.search(b):
            t = _plain(b).strip()
            if t:
                notes.append(t)
            continue
        kind = classify_block(b)
        text = _plain(b).strip()
        if not text:
            continue
        if kind in ("prose", "callout") and not lead:
            kept = " ".join(_sentences(text)[:MAX_LEAD_SENTENCES]).strip()
            if kept:
                lead = f"<p>{_html.escape(kept)}</p>"
            if text != kept:
                notes.append(text)
        else:
            notes.append(text)
    return lead, notes


def _face_is_graphic_heavy(blocks) -> bool:
    if not blocks:
        return False
    return any(_GRAPHIC_FACE_RE.search(b) for b in blocks)


def _as_header_slide(unit, lead_html=""):
    """Title-page layout reused as a section header: title (+ optional lead)."""
    return wrap(unit, lead_html, is_title_slide=True)


def _apply_title_and_header_rules(unit, bodies, is_deck_title: bool,
                                  face_blocks=None):
    """Enforce: title/header slides are text-only; heavy openers get a header
    slide first, then content under the master title bar.

    Returns (bodies, extra_notes).
    """
    notes = []
    if not bodies:
        return bodies, notes

    face_blocks = list(face_blocks or [])

    if is_deck_title:
        # Deck opener: title alone. Lead and any graphic → notes (or a following
        # content slide only when a graphic remains on the face).
        lead, more = _plain_lead_html(face_blocks)
        if lead:
            more = [_plain(lead)] + more
        notes.extend(more)
        header = _as_header_slide(unit, "")  # title alone — no lead card
        rest = []
        if _face_is_graphic_heavy(face_blocks):
            graphic = [b for b in face_blocks if _GRAPHIC_FACE_RE.search(b)]
            if graphic:
                rest.append(wrap(unit, "".join(graphic), part_label=""))
            for b in bodies[1:]:
                b["is_title_slide"] = False
                rest.append(b)
        out = [header] + rest
        content_slides = [s for s in out if not s.get("is_title_slide")]
        if len(content_slides) > 1:
            for j, s in enumerate(content_slides):
                s["part_label"] = f"{j + 1} / {len(content_slides)}"
        elif content_slides:
            content_slides[0]["part_label"] = ""
        return out, notes

    # Non-deck units: if the opener is graphic-heavy, reuse title-page layout
    # as a section header, then put the graphic on the next slide(s).
    first = bodies[0]
    has_graphic = (
        any(b.get("has_fig") for b in bodies)
        or _face_is_graphic_heavy(face_blocks)
        or any(_GRAPHIC_FACE_RE.search(b.get("content_html") or "") for b in bodies)
    )
    if has_graphic and (
            first.get("has_fig")
            or _GRAPHIC_FACE_RE.search(first.get("content_html") or "")):
        prose = [b for b in face_blocks if not _GRAPHIC_FACE_RE.search(b)]
        graphic = [b for b in face_blocks if _GRAPHIC_FACE_RE.search(b)]
        lead, more = _plain_lead_html(prose)
        notes.extend(more)
        header = _as_header_slide(unit, lead)
        if not graphic:
            return [header], notes
        if len(bodies) == 1:
            content = wrap(unit, "".join(graphic), part_label="")
            return [header, content], notes
        for b in bodies:
            b["is_title_slide"] = False
        out = [header] + bodies
        content_slides = [s for s in out if not s.get("is_title_slide")]
        if len(content_slides) > 1:
            for j, s in enumerate(content_slides):
                s["part_label"] = f"{j + 1} / {len(content_slides)}"
        return out, notes

    # Text-only (no image/table/card grid): never leave a lonely paragraph under
    # the pinned master title. Center title + lead like Batch isolation.
    if not has_graphic:
        lead, more = _plain_lead_html(face_blocks)
        notes.extend(more)
        if not lead:
            listish = [b for b in face_blocks
                       if classify_block(b) in ("list", "prose", "callout", "caption")]
            if listish:
                lead = listish[0]
                notes.extend(_plain(b).strip() for b in listish[1:] if _plain(b).strip())
        return [_as_header_slide(unit, lead)], notes

    # has_graphic but some body slides are text-only remnants → center those.
    out = []
    for b in bodies:
        if b.get("is_title_slide") or b.get("has_fig"):
            out.append(b)
            continue
        words = _face_words(b.get("content_html") or "")
        if words <= 40:
            out.append(_as_header_slide(unit, b.get("content_html") or ""))
        else:
            out.append(b)
    return out, notes


def _pack(heights, n):
    """Partition contiguous block heights into exactly `n` parts that minimize
    the tallest part (classic linear-partition DP). Contiguity keeps document
    order and never breaks an atomic block. Returns `n` non-empty index groups
    (fewer only when there are fewer blocks than parts)."""
    m = len(heights)
    n = min(n, m)
    if n <= 1:
        return [list(range(m))]
    # dp[i][k] = min achievable max-part over heights[i:] using k parts
    INF = float("inf")
    suffix = [0] * (m + 1)
    for i in range(m - 1, -1, -1):
        suffix[i] = suffix[i + 1] + heights[i]
    dp = [[INF] * (n + 1) for _ in range(m + 1)]
    cut = [[m] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][1] = suffix[i] - suffix[m]           # one part = sum of the rest
    for k in range(2, n + 1):
        for i in range(m - 1, -1, -1):
            best, run = INF, 0
            for j in range(i, m - (k - 1)):        # first part = heights[i:j+1]
                run += heights[j]
                cand = max(run, dp[j + 1][k - 1])
                if cand < best:
                    best, cut[i][k] = cand, j + 1
            dp[i][k] = best
    # reconstruct
    groups, i, k = [], 0, n
    while k > 1:
        j = cut[i][k]
        groups.append(list(range(i, j)))
        i, k = j, k - 1
    groups.append(list(range(i, m)))
    return groups


def _pack_scored(page, unit, blocks, heights, n):
    """Like _pack, but among partitions with the same max-height, prefer the
    one with the higher mean composition_score."""
    groups = [g for g in _pack(heights, n) if g]
    # DP already minimized tallest; score is a soft preference recorded for report
    scores = []
    for g in groups:
        bs = [blocks[i] for i in g]
        hs = [heights[i] for i in g]
        scores.append(composition_score(composition_metrics(page, unit, bs, hs)))
    return groups, (sum(scores) / len(scores) if scores else 0.0)


def balanced_split(page, unit, unit_h, blocks=None):
    """
    Split one over-budget unit into balanced parts at atomic-block boundaries.

    Part count is amortized: ceil(unit_h / CONTENT_H), so the repeated heading
    is charged once, not once per part — a unit ~2x the budget yields 2 parts,
    not 3. Blocks are then distributed to minimize the tallest part rather than
    greedily filling part 1. Soft composition score breaks ties. The heading
    rides on every part. A single block taller than the budget still becomes
    its own (unavoidably tall) part and may use emergency scale.

    Returns (slides, extra_notes).
    """
    blocks = list(blocks if blocks is not None else unit["blocks"])
    if not blocks:
        return [wrap(unit, "")], []

    heights = [measure(page, wrap(unit, b)["content_html"]) for b in blocks]
    n = min(len(blocks), max(2, -(-max(unit_h, 1) // CONTENT_H)))  # amortized ceil
    groups, _ = _pack_scored(page, unit, blocks, heights, n)
    extra_notes = []

    def refine(groups_):
        refined_, notes_ = [], []
        for g in groups_:
            part_blocks = [blocks[i] for i in g]
            hs = [heights[i] for i in g]
            m = composition_metrics(page, unit, part_blocks, hs)
            if not composition_ok(m):
                kept, notes, _ = _strip_prose_from_blocks(part_blocks)
                notes_.extend(n for n in notes if n)
                part_blocks = kept
                m = composition_metrics(page, unit, part_blocks)
            emergency = (len(part_blocks) == 1
                         and m["h"] > CONTENT_H * PREFERRED_FIT_SCALE)
            refined_.append((part_blocks, emergency, m["h"]))
        # Merge sparse parts (tiny tables / thin prose) into a neighbor.
        merged = []
        for part_blocks, emergency, h in refined_:
            sparse = _part_is_sparse(part_blocks, h)
            if sparse and merged:
                prev_b, prev_e, prev_h = merged[-1]
                if prev_h + h <= CONTENT_H * FIT_TOLERANCE * 1.25:
                    merged[-1] = (prev_b + part_blocks, prev_e, prev_h + h)
                    continue
            if (merged and _part_is_sparse(merged[-1][0], merged[-1][2])
                    and h + merged[-1][2] <= CONTENT_H * FIT_TOLERANCE * 1.25):
                prev_b, prev_e, prev_h = merged[-1]
                merged[-1] = (prev_b + part_blocks, emergency, prev_h + h)
            else:
                merged.append((part_blocks, emergency, h))
        return [(b, e) for b, e, _h in merged], notes_

    refined, notes = refine(groups)
    extra_notes.extend(notes)

    need_more = any(
        len(pb) > 1 and composition_metrics(page, unit, pb)["s"] < PREFERRED_FIT_SCALE
        for pb, _ in refined)
    if need_more and n < len(blocks):
        groups, _ = _pack_scored(page, unit, blocks, heights, min(len(blocks), n + 1))
        refined, notes = refine(groups)
        extra_notes.extend(notes)

    total_parts = len(refined)
    slides = []
    for p, (part_blocks, emergency) in enumerate(refined):
        label = f"{p + 1} / {total_parts}" if total_parts > 1 else ""
        slides.append(wrap(unit, "".join(part_blocks), label,
                           emergency_scale=emergency))
    return slides, extra_notes


def _bodies_for_unit(page, u, face_blocks, keep_source):
    """Measure → fit-or-split → composition enforce. Returns
    (bodies, measured_h, fits, extra_notes, any_extra_strip)."""
    extra_notes = []
    any_extra = False
    whole = wrap(u, "".join(face_blocks))
    h = measure(page, whole["content_html"])
    m = composition_metrics(page, u, face_blocks)

    if not keep_source and not composition_ok(m):
        kept, notes, more = _strip_prose_from_blocks(face_blocks)
        if more:
            face_blocks = kept
            extra_notes.extend(notes)
            any_extra = True
            whole = wrap(u, "".join(face_blocks))
            h = measure(page, whole["content_html"])
            m = composition_metrics(page, u, face_blocks)

    fits = h <= CONTENT_H * FIT_TOLERANCE
    if fits:
        if len(face_blocks) == 1 and m["h"] > CONTENT_H * PREFERRED_FIT_SCALE:
            whole["emergency_scale"] = True
        return [whole], h, True, extra_notes, any_extra

    bodies, split_notes = balanced_split(page, u, h, face_blocks)
    extra_notes.extend(split_notes)
    return bodies, h, False, extra_notes, any_extra or bool(split_notes)


def slice_page(source, outdir, unit_selector, theme="light", keep_source=False):
    src = Path(source).resolve()
    outdir = Path(outdir)
    (outdir / "slides").mkdir(parents=True, exist_ok=True)

    report = {"source": str(src), "unit_selector": unit_selector, "theme": theme,
              "keep_source": keep_source,
              "slide_w": SLIDE_W, "slide_h": SLIDE_H, "content_h": CONTENT_H,
              "units": [], "slides": []}

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": SLIDE_W, "height": SLIDE_H},
                                  device_scale_factor=2)
        page = ctx.new_page()
        try:
            page.goto(src.as_uri(), wait_until="load", timeout=30000)
        except PWError:
            page.goto(src.as_uri(), wait_until="domcontentloaded", timeout=30000)
        # Stamp the requested theme on the root so every slice/render inherits
        # the page's own light/dark tokens (the page reads data-theme).
        page.evaluate("(t) => document.documentElement.setAttribute('data-theme', t)",
                      theme)
        _settle(page)
        page.add_style_tag(content=STAGE_CSS)
        page.add_style_tag(content=DECK_BOOST_CSS)
        if theme == "dark":
            page.add_style_tag(content=FIGURE_PLATE_CSS)
            page.add_style_tag(content="""
              #__stage,#__title,#__gap{background:#0e1014!important}
            """)

        units = page.evaluate(DISCOVER_JS, unit_selector)
        if not units:
            browser.close()
            raise SystemExit(f"No units matched selector {unit_selector!r} in {src.name}")

        slide_no = 0
        heavy = []
        for ui, u in enumerate(units):
            face_blocks, stripped_notes, unit_stripped = project_face(
                u["blocks"], keep_source=keep_source)
            if not face_blocks and u["blocks"]:
                face_blocks = [u["blocks"][0]]
                unit_stripped = True

            bodies, h, fits, extra_notes, extra_strip = _bodies_for_unit(
                page, u, face_blocks, keep_source)
            stripped = unit_stripped or extra_strip

            # Title-page purity + section-header reuse + text-only centering.
            # Run before droppable so a short prose-only unit becomes a centered
            # title slide instead of being discarded as an empty face.
            bodies, header_notes = _apply_title_and_header_rules(
                u, bodies, is_deck_title=(ui == 0), face_blocks=face_blocks)
            if header_notes:
                stripped = True
                stripped_notes = list(stripped_notes) + header_notes

            # Drop chrome-only / near-empty content faces (never title slides).
            kept_bodies = []
            for b in bodies:
                if b.get("is_title_slide"):
                    kept_bodies.append(b)
                    continue
                if _face_is_droppable(b):
                    stripped = True
                    continue
                kept_bodies.append(b)
            bodies = kept_bodies
            if not bodies:
                if ui == 0:
                    bodies = [_as_header_slide(u, "")]
                    stripped = True
                else:
                    report["units"].append({"id": u["id"], "title": u["title"],
                                            "measured_h": h, "fits": True,
                                            "blocks": 0,
                                            "source_blocks": len(u["blocks"]),
                                            "stripped": True, "dropped": True})
                    continue

            # Re-stamp part labels on content faces after drops.
            content_faces = [b for b in bodies if not b.get("is_title_slide")]
            if len(content_faces) > 1:
                for j, b in enumerate(content_faces):
                    b["part_label"] = f"{j + 1} / {len(content_faces)}"
            elif content_faces:
                content_faces[0]["part_label"] = ""

            report["units"].append({"id": u["id"], "title": u["title"],
                                    "measured_h": h, "fits": fits,
                                    "blocks": len(face_blocks),
                                    "source_blocks": len(u["blocks"]),
                                    "stripped": stripped})

            unit_notes = _prose(u["outerHTML"])
            stripped_blob = "\n".join(dict.fromkeys(
                ln for ln in (stripped_notes + extra_notes) if ln))
            notes_text = unit_notes
            if stripped_blob and stripped_blob not in unit_notes:
                notes_text = (unit_notes + "\n\n" + stripped_blob).strip()

            for j, body in enumerate(bodies):
                slide_no += 1
                fn = f"slides/slide-{slide_no:02d}.png"
                render_png(page, body, str(outdir / fn))
                words = _face_words(body["title_html"], body["content_html"])
                if words > FACE_WORD_SANITY:
                    heavy.append((slide_no, words))
                    print(f"slide {slide_no} is text-heavy ({words} words) — "
                          f"shorten or move to speaker notes", file=sys.stderr)
                # rough composition on the rendered face blob
                m = composition_metrics(page, u, [body["content_html"]])
                report["slides"].append({
                    "n": slide_no, "unit": u["id"], "title": u["title"],
                    "part": ("" if body.get("is_title_slide")
                             else (body.get("part_label") or "").replace(" / ", "/")),
                    "png": fn, "from_split": (not body.get("is_title_slide")
                                             and len([x for x in bodies
                                                      if not x.get("is_title_slide")]) > 1),
                    "words": words,
                    "stripped": stripped,
                    "is_title_slide": bool(body.get("is_title_slide")),
                    "phi": round(m["phi"], 3), "V": round(m["V"], 3),
                    "score": round(composition_score(m), 3),
                    "notes_text": notes_text})
        browser.close()
    report["text_heavy"] = heavy

    (outdir / "slice-report.json").write_text(json.dumps(report, indent=2))
    return report


def _face_words(*html_parts):
    """Count the words actually shown on a slide face (title + content text),
    ignoring markup."""
    txt = " ".join(html_parts)
    txt = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", txt)
    txt = re.sub(r"(?s)<[^>]+>", " ", txt)
    txt = _html.unescape(txt)
    return len(txt.split())


def _prose(unit_html):
    """Plain-text prose of a unit, for speaker notes (headings + paragraphs)."""
    txt = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", unit_html)
    txt = re.sub(r"(?is)</(p|div|li|h[1-6]|figcaption)>", "\n", txt)
    txt = re.sub(r"(?s)<[^>]+>", " ", txt)
    txt = _html.unescape(txt)
    lines = [ln.strip() for ln in txt.splitlines()]
    return "\n".join(dict.fromkeys(ln for ln in lines if ln)).strip()


def main():
    ap = argparse.ArgumentParser(description="Slice an HTML page into 16:9 slides.")
    ap.add_argument("source", help="path to the source .html file")
    ap.add_argument("--out", default=str(Path(__file__).parent / "_out"))
    ap.add_argument("--unit-selector", default="section",
                    help="CSS selector for top-level slide units (default: section)")
    ap.add_argument("--theme", default="light", choices=["light", "dark"],
                    help="stamp data-theme on the page before rendering (default: light)")
    ap.add_argument("--keep-source", action="store_true",
                    help="skip face projection (warn-only); debug the source HTML")
    args = ap.parse_args()

    report = slice_page(args.source, args.out, args.unit_selector, args.theme,
                        keep_source=args.keep_source)
    print(f"units: {len(report['units'])}  ->  slides: {len(report['slides'])}"
          f"  (theme: {report['theme']}"
          f"{', keep-source' if report.get('keep_source') else ''})")
    for u in report["units"]:
        flag = "OK   " if u["fits"] else "SPLIT"
        strip = " stripped" if u.get("stripped") else ""
        print(f"  [{flag}] {u['measured_h']:>4}px  {u['title'][:60]}{strip}")
    heavy = report.get("text_heavy", [])
    if heavy:
        print(f"\n{len(heavy)} text-heavy slide(s) (> {FACE_WORD_SANITY} words after "
              f"projection): " + ", ".join(f"#{n} ({w}w)" for n, w in heavy))
    stripped_n = sum(1 for s in report["slides"] if s.get("stripped"))
    if stripped_n:
        print(f"{stripped_n} slide(s) had face text moved to speaker notes")
    print(f"\nwrote {len(report['slides'])} slide PNGs + slice-report.json to {args.out}")


if __name__ == "__main__":
    main()
