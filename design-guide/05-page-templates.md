@chapter #ch-templates .templates .dg-guide ch="2"

# Page Templates

@lede

Named page types control margin geometry, footer chrome, and running headers. The geometry pages (`.page`, `.front-matter`, `.dc-chapter-start`, `.chapter-end`, `.dc-full-page`, `.dc-citizen-file-page`) each map to a `@page` rule in the package's `styles/page-rules.css`. A `page-*`-prefixed class must map to a real rule: that prefix is reserved for templates that do work, so a rule-less one is indistinguishable from a working one and reads as a promise the CSS does not keep. Unprefixed **topic slugs** are the sanctioned exception — they are acknowledged no-ops naming one spread, and are described under the table below. The templates that follow identify, for each page type, the geometry class or `@section` component that actually does the work.

@end-lede

---

## Page Geometry

Dimensions for DC Field Guide print output — declared in `manifest.yaml`, US Letter, perfect-bound.

| Dimension | Value | Notes |
|-----------|-------|-------|
| Trim size | 8.5 × 11 in | US Letter |
| Bleed | 0.125 in | All sides — extend backgrounds to edge |
| Top margin | 0.5 in | Body pages; chapter-start uses 0.75 in |
| Bottom margin | 0.70 in | Footer sits in this space |
| Binding gutter | 0.75 in | Inner margin — swaps left↔right per recto/verso |
| Outside margin | 0.5 in | |

Extend any full-bleed background or image by 0.125 in past each edge so trimming variation doesn't leave a white sliver.

## Named Page Types

The DC print system uses named page types to control margin geometry, footer chrome, and running headers. Each class below maps to a `@page` rule in the package's `styles/page-rules.css`. A page that carries none of them gets the default body geometry.

| Class | Key behavior |
|-------|--------------|
| `.page` | Default body. Footer: `p.N` + `c.N` opposing corners |
| `.front-matter` | Footers suppressed — credits, TOC, intro |
| `.dc-chapter-start` | Footer-free chapter opener spread |
| `.chapter-end` | Declared but unused — footers suppressed (see note below) |
| `.dc-full-page` | Zero margins, no footers — full-bleed art |
| `.dc-citizen-file-page` | Running header "Citizen File" — NPC records |

> **`.chapter-end` prints no footer, and nothing uses it.** `@page chapter-end` declares `@bottom-left { content: "C." counter(chapter) }` and `@bottom-right { content: "P." counter(page) }`, but `@page chapter-end:left` and `@page chapter-end:right` both override those boxes to `content: none`, and the `:left`/`:right` blocks win, so the declared content never paints. Treat `.chapter-end` as a footer-free page until that is deliberately changed.
>
> It is also **declared-but-unexercised**, not established practice: `chapter-end` appears in zero Field Guide source files, and in this guide only in prose — no build of either book produces a single `chapter-end` page. Do not cite it as a Field Guide pattern.

Beyond these, a `@page` directive may carry a **per-spread topic slug** (`.vibe`, `.call-home`, `.dream`, `.da-devil`, `.ideal`, `.flaw`, `.choose-specialty`, `.colophon`, `.end-of-book`). Slugs name one specific spread and are styling no-ops today — they exist as stable targets for per-spread tuning. Do **not** invent `page-*`-prefixed classes for this: that prefix is already used by templates with real rules (`.page-toc`, `.page-credits`, `.page-intro`, `.page-chapter-start`), so a rule-less `page-*` class is indistinguishable from a working one and reads as a promise the CSS does not keep.

Named pages are declared in the markdown source using the `@page` directive:

```markdown
@page .dc-chapter-start
```

Legacy `--- {page ...}` fences remain supported for compatibility, but the design guide treats `@page` as the canonical authoring form.

---

## Book Page Templates

These templates cover every DC Field Guide page type. Use the minimal examples as starting skeletons.

---

### Front Matter Pages

@lede

This section shows how the Table of Contents, Credits, and Introduction pages look in the actual Dimm City Field Guide, rendered using real book content. These are the first pages a reader encounters — `page-toc`, `page-credits`, and `page-intro` templates applied to the `chapter-00` content.

@end-lede

@section .gp-columns-2 .dc-column-panel

Front matter sets the emotional contract with the reader. Before they see a single rule, a map, or a stat block, the TOC, Credits, and Introduction tell them what kind of book this is.

| Page | Template class | Design purpose |
|------|---------------|----------------|
| Table of Contents | `page-toc` | Dense chapter listing with `.dc-toc` numbered rows |
| Credits | `page-credits` | Short credits block anchored by a full-bleed illustration |
| Introduction | `page-intro` | Pull-quote opener, narrative fiction, setting primer |

@column-break

All three use the `chapter-00` class selector in `page-rules.css`, which drives the pre-chapter margin and header treatment. The `@toc` and `@end-toc` macros emit the `.dc-toc-row` structure for the Contents page. The pull-quote band on the Introduction page uses `> [!PULLQUOTE]` — the same alert component used elsewhere in the book.

Front matter pages exist outside the main chapter numbering system. They do not have chapter code badges or specialty color blocks. Their job is to establish voice and brand before the system content begins.

@end-section

---

### Chapter Cover

Full-page specialty chapter cover. Footers suppressed. One per specialty chapter. **Page class:** `@page .page-chapter-start .dc-chapter-start`.

**Components:** `.dc-cover-bg` (full-bleed tint) · `.dc-cover-num` ("— Ch N / Name —") · `.dc-cover-bigword` (H1 display title) · `.dc-cover-strap` (strap line, ≤15 words) · `.dc-cover-body` (1–2 onboarding sentences) · `.dc-cover-meta-row` (3-column PATHS / ABILITIES / PAGES grid)

```html
@page .page-chapter-start .dc-chapter-start

<div class="dc-cover-page dc-cover-layout">
  <div class="dc-cover-bg"></div>
  <div class="dc-cover-num">— Chapter 01 / Specialty Name —</div>
  <h1 class="dc-cover-bigword">Display<br>Title</h1>
  <p class="dc-cover-strap">One punchy strap line — keep it under fifteen words.</p>
  <div class="dc-cover-body">
    A short onboarding sentence. A second sentence on when to read this chapter.
  </div>
  <div class="dc-cover-meta-row">
    <div>PATHS<b>4</b></div>
    <div>ABILITIES<b>18</b></div>
    <div>PAGES<b>p.001 — p.032</b></div>
  </div>
</div>
```

---
@chapter #ch-tpl-chapter-opener .example-chapter-opener .chapter-03 .dg-guide ch="3"

### Chapter Opener — Real-World Example {.dc-chevron}

@lede

This section shows how chapter-start spreads look in the actual Dimm City Field Guide, rendered using real book content. The chapter opener uses the `page-chapter-start` page template to create a two-column layout: fiction narrative on the left, rules or character content on the right, separated by a column break.

@end-lede

---

#### About Chapter Opener Spreads

@section .gp-columns-2 .dc-column-panel

A chapter opener spread is the reader's first encounter with each chapter's world. DC openers are always two-column: the left column carries a short fiction vignette establishing the vibe and stakes of the chapter, and the right column launches directly into the rules or character creation content.

| Element | Authoring pattern | Rendered as |
|---------|------------------|-------------|
| Chapter badge | *(none — automatic)* | Stacked chapter code + large number overlay, generated from the chapter's `@chapter C.NN` label on its first page |
| Left column | Fiction vignette + art | Narrative prose with inline image |
| Column break | `---{.column-break}` | Layout split between columns |
| Right column | Rules intro + content | Standard heading hierarchy |

@column-break

The two-column split is authored with a `---{.column-break}` marker. Everything before the column break flows into the left column; everything after flows into the right. There is no `@chapter-opener` macro — the chapter number badge is markup-driven, generated automatically for the first page of a `@chapter C.NN`-labeled chapter (see `plugins/macros.md`).

The `page-chapter-start` template lives in the package's `styles/page-templates.css` (its `@page` wiring in `styles/page-rules.css`); chapter-specific accent and art overrides are applied via the `chapter-01`, `chapter-02` class selectors in the field guide's own `fg-overrides.css`.

@end-section

---

### Chapter Opener

Two-column rules opener for non-specialty chapters. Left: badge + spray banner + fiction. Right: chevron + rules prose + Dream Master callout. Footers suppressed. **Page class:** `@page .page-chapter-start .dc-chapter-start`

**Components:** chapter badge (automatic, from the `@chapter C.NN` label — no macro) · `## Title {.dc-spray}` (banner) · `---{.column-break}` (split) · `# Title {.dc-chevron}` (right-col opener) · `> [!DM]` (callout)

```markdown
@page .page-chapter-start .dc-chapter-start

## Chapter Title {.dc-spray}

Fiction paragraphs fill the left column. Keep each under 80 words.
Continue fiction until the column is comfortably full.

---{.column-break}

# How It Works {.dc-chevron}

Rules prose fills the right column.

> [!DM]
> Facilitator guidance goes here.
```

---
@chapter #ch-tpl-specialty-overview .example-specialty-overview .chapter-03 .dg-guide ch="3"

# Specialty Overview — Real-World Example {.dc-chevron}

@lede

This section shows how the "Choose a Specialty" spread looks in the actual Dimm City Field Guide, rendered using real book content. It covers two page types: a chapter-start opener with fiction and ability primer, followed by a specialty overview spread with the specialty card grid.

@end-lede

---

## About These Pages

@section .gp-columns-2 .dc-column-panel

The specialty section of the Field Guide has two distinct spreads. The chapter-start spread (Chapter 02) pairs an opening fiction vignette with the ability primer — the rules overview for how the whole system works. The specialty overview spread (the `card-grid` template) follows it with the 8 specialty cards side by side.

| Page | Template | Purpose |
|------|----------|---------|
| Chapter opener | `page-chapter-start .chapter-02` | Fiction left, ability rules right |
| Specialty grid | `card-grid` | 8 specialty cards in two-column layout |

@column-break

The two-column structure on both pages is deliberate: the reader gets fiction and mechanics together on the opener, then a clean visual grid for the specialty choices. Every specialty gets equal visual weight in the card grid.

The `@specialty-card` macro inside a `@specialty .name` wrapper sets accent color, silhouette shape, and card layout for each of the 8 specialties. The card grid is fully authored in markdown — no HTML needed.

@end-section

---

### Specialty Opener

Two-page spread: left page has chevron H1 + prose + spec-tweak H3 + class tag chips; right page is full-bleed art. Always footer-free on a visual-left page.

**Page classes:** left: `@page .page-chapter-start .dc-chapter-start` · right: `@page .dc-full-page`

**Components:** `# Name {.dc-chevron}` · `### Spec Tweak {.dc-spec-tweak}` · `<span class="dc-classtag [specialty]">` · `.specialty-art` wrapper

```markdown
@spread .specialty-opener

@page .page-chapter-start .dc-chapter-start

# Specialty Name {.dc-chevron}

3–4 prose paragraphs: who this specialist is, their approach, quick-start picks.
Keep each block under 60 words.

### Spec Tweak: Built for the Job {.dc-spec-tweak}

Spec-tweak body prose — conditions and assumptions the specialty carries into jobs.

<p><span class="dc-classtag augmerc"><span class="dc-classtag-dot"></span>Specialty Name</span></p>

@page .dc-full-page

@section .specialty-art

![Character art](https://placehold.co/1349x842/png?text=Character+Art)

@end-section
```

**Section/macro equivalents** — the specialty grid is now page-template-owned, while card content uses the DC plugin's `@` macros:

| Marker | Purpose |
|--------|---------|
| `@lede` | Intro panel — prose and class tag chips |
| `@section .specialty-art` | Full-bleed art plate (right page) |
| `@specialty .augmerc` | Wraps cards in a specialty palette; child cards inherit shape and accent |

---
@chapter #ch-tpl-specialty-profile .example-specialty-profile .chapter-03 .dg-guide ch="3"

# Specialty Profile — Real-World Example {.dc-chevron}

@lede

This section shows how a full specialty profile looks in the actual Dimm City Field Guide, rendered using real book content from the Augmerc chapter. A specialty profile combines the `@specialty` macro, intro block, art panel, `@learning-path` macro, and a sequence of `@skill` cards — all live DC components.

@end-lede

---

## About Specialty Profile Pages

@section .gp-columns-2 .dc-column-panel

Every specialty in the Field Guide gets a two-page spread: the specialty intro block on the first page, followed by learning paths and skill cards flowing across as many pages as needed. The structure is always the same, but the silhouette shapes, accent colors, and ability content differ for each specialty.

| Component | Macro / class | Renders as |
|-----------|---------------|------------|
| Specialty wrapper | `@specialty .augmerc` | Parent container with accent + shape tokens |
| Intro block | `@specialty-intro` / `@end-specialty-intro` | Title banner + definition + spec tweak |
| Path header | `@learning-path` | Path shell with path title, skill list, signature augment |
| Skill cards | `@skill` (one per ability) | Tabbed card with tier, flavor, and AP options |

@column-break

The `@specialty .augmerc` wrapper defines all 7 shape variables (`--dc-skill-tab-shape`, `--dc-skill-body-shape`, `--dc-path-title-shape`, `--dc-path-shell-clip`, `--dc-specialty-card-shell-shape`, `--dc-specialty-intro-title-shape`, `--dc-specialty-intro-clip`). Every nested component inherits these through CSS custom property cascade — the component base rules use `var(--token, fallback)` so that specialty shapes override without requiring new selectors.

**Macros used:** `@specialty`, `@specialty-intro`, `@specialty-art`, `@learning-path`, `@skill`. See [Components](#ch-components) for the full reference.

@end-section

---

## Specialty Intro Block

**Macros** — `@specialty .augmerc` wraps the entire specialty section and applies specialty-scoped CSS. `@specialty-intro` holds the name, definition, and Spec Tweak. `@learning-path` injects the path header and path sequence list. Each `@skill` card follows the path declaration. See [Components](#ch-components) for the full macro reference.

---

### Specialty Listing

2–3 specialty entries per page: portrait, class tag chip, prose description, flavor quote. Separated by tape dividers. **Page class:** normal body page, no break marker needed.

**Status:** *deprecated 2026-05-24.* The `@class-entry` macro and the
`.section.dc-class-entry` CSS were parked in the since-deleted `css/deprecated.css` after zero
live usage was found in any Part 2 example file. A parser-state bug in the
multi-entry path made revival expensive for a never-used feature. If the
"specialty roster" format is needed in a future spread, design it from the
cascade principle: `@section .dc-class-entry` as the wrapper, with structural
elements inside. The structure below is preserved for reference only.

**Reference emitted structure (deprecated):** `<div class="section dc-class-entry">` (outer) · `.dc-portrait > img` (frame component, direct child) · `.dc-content-col` (body column) > `<h3>` (styled by `.section.dc-class-entry h3`) + `.dc-tag-row > .dc-classtag` (generic tag-row primitive) + body `<p>` + `.dc-flavor` · followed by `<div class="dc-tape">— § —</div>` separator

```html
<div class="section dc-class-entry">
  <div class="dc-portrait">
    <img src="images/specialty.png" alt="Specialty Name">
  </div>
  <div class="dc-content-col">
    <h3>Specialty Name</h3>
    <div class="dc-tag-row">
      <span class="dc-classtag augmerc">Specialty Name</span>
    </div>
    <p>Description paragraph one.</p>
    <p>Description paragraph two — when to choose this specialty.</p>
    <p class="dc-flavor">"Flavor quote."<br><em>— Operator Name, Role, District</em></p>
  </div>
</div>

<div class="dc-tape">— § —</div>
```

---

### Learning Path

Specialty spread with spray banner, sticker chain, signature augment, and `@skill` cards. Use the standard specialty spread layout and let the learning-path and skill-card shells manage their own chrome.

**Components:** `@specialty .<slug>` (parent container) · `@learning-path` (opens block) · `### Path Name` (spray banner) · `> Subtitle` (lede) · bullet list (sticker chain) · `<div class="dc-tape">` (divider) · `@skill id="…"` / `@end-skill` · `<span class="dc-ap">N AP</span>`. Silhouette and accent come from the `@specialty` parent — no `variant=` needed.

```markdown
@specialty .augmerc

@learning-path

### Path Name

> One punchy subtitle line.

- Skill Title One
- Skill Title Two
- Skill Title Three

**Signature Augment Name:** Description of the passive augment — what it enables and where it lives.

<div class="dc-tape">— Signature Augment / Augment Name —</div>

@skill id="skill-unique-id"
**Skill Title**
Flavor line. Operator voice.
Ability body text. When the trigger fires, you may:
**Option Alpha:** Description. ROLL THE DIE!
Active | <span class="dc-ap">2 AP</span>
@end-skill

@end-specialty
```

---

### Ability Spread

Facing-page spread. Left: spray banner + path subtitle + `@skill` cards. Right: field notes + pull quote + DM callout + tape divider + class tags.

**Components:** `## Title {.dc-spray}` · `<div class="dc-path-subtitle">` · `@skill` / `@end-skill` · `---{.column-break}` · `### Field Notes {.dc-spec-tweak .dc-no-top}` · `> [!PULLQUOTE]` · `> [!DM]` · `<div class="dc-tape">` · `<span class="dc-classtag">`

```markdown
## Skill Title {.dc-spray}

<div class="dc-path-subtitle">— SP1 · Path Name —</div>

@skill id="skill-id"
**Skill Title**
Flavor line.
Ability body and options.
Stance | <span class="dc-ap">0 AP</span>–<span class="dc-ap">2 AP</span>
@end-skill

---{.column-break}

### Field Notes {.dc-spec-tweak .dc-no-top}

Tactical context and table guidance. Two to three short paragraphs.

> [!PULLQUOTE]
> Pull quote — one resonant line.
>
> Attribution

> [!DM]
> Facilitator note.

<div class="dc-tape">— § —</div>

<p><span class="dc-classtag augmerc"><span class="dc-classtag-dot"></span>Specialty Name</span></p>
```

---

### Bestiary Entry

Two-column creature/NPC entry. Left: chevron banner + lede + stat block + encounter notes. Right: aged-paper portrait + tape label + caption. **Page class:** `@page .page`

**Components:** `@section .gp-columns-2 .dc-column-panel` (two-col split in a column-panel card) · `# Title {.dc-chevron}` · `@lede` (≤20 words) · `.dc-stat` · `.dc-portrait` · `.dc-tape`

> [!WARNING]
> `.dc-stamp` is **deprecated** — it has zero live usage and no CSS in the build. Its rules were parked in the since-deleted `css/deprecated.css`. Do not use it; it will not render.

> [!NOTE]
> This template previously showed `@page .page .chapter-end`. It does not use `.chapter-end` — nothing in this repo does. See the `.chapter-end` note under [Named Page Types](#ch-templates); the rendered Dream Master example in Part 2 is a plain `@page`.

```markdown
@page .page

@section .gp-columns-2 .dc-column-panel

# Creature Name {.dc-chevron}

@lede
One punchy atmospheric line. Under twenty words.
@end-lede

Flavor prose — appearance, behavior, threat type.

<div class="dc-stat">
  <div class="dc-stat-head">
    <div class="dc-stat-name">Creature Name, Variant</div>
    <div class="dc-stat-class">— Threat 2 · Category —</div>
  </div>
  <div class="dc-stat-grid">
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">HP</div><div class="dc-stat-cell-val">18</div></div>
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">DEF</div><div class="dc-stat-cell-val">12</div></div>
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">AP</div><div class="dc-stat-cell-val">3</div></div>
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">DMG</div><div class="dc-stat-cell-val">d20</div></div>
  </div>
  <div class="dc-stat-line"><strong>Signature Attack:</strong> Description.</div>
</div>

**Encounter Notes**

Encounter guidance for the Dream Master.

---{.column-break}

![Creature Name](https://placehold.co/600x800/png?text=Creature){.dc-img-float-right}

<div class="dc-tape dc-margin-sm">— Field Plate —</div>

Caption text.
```

---

### Table of Contents

Front-matter TOC: chevron banner + lede + structured rows with `target-counter()`-resolved page numbers. Footers suppressed. Each `<a href="#id">` resolves to its page number at layout time. **Page class:** `@page .page .front-matter`

**Components:** `# Contents {.dc-chevron}` · `<div class="dc-intro">` · `<div class="dc-toc">` (container) · `<div class="dc-toc-row">` (one per entry) · `<div class="dc-toc-no">` (zero-padded ch#) · `<div class="dc-toc-title">` (with `<small>` subtitle) · `<div class="dc-toc-page">` (resolved number)

```html
@page .page .front-matter

# Contents {.dc-chevron}

<div class="dc-intro">Orienting sentence about what this book contains.</div>

<div class="dc-toc mt">
  <div class="dc-toc-row">
    <div class="dc-toc-no">01</div>
    <div class="dc-toc-title">Chapter One Title <small>Brief description.</small></div>
    <div class="dc-toc-page"><a href="#ch-one-id">p.007</a></div>
  </div>
  <div class="dc-toc-row">
    <div class="dc-toc-no">02</div>
    <div class="dc-toc-title">Chapter Two Title <small>Brief description.</small></div>
    <div class="dc-toc-page"><a href="#ch-two-id">p.015</a></div>
  </div>
</div>
```

Each `href` must point to an `id` on a heading or `<span id="…">` anchor. Page numbers resolve automatically at render time.

---

### Procedure Page

Numbered procedure with two-column layout: steps list left, callout + pull quote right. Tape divider introduces closing prose. **Page class:** normal body page, no break marker needed.

**Components:** `# Title {.dc-chevron}` · `@lede` · `@procedure` (ordered list rendered as `<ol class="dc-steps">`) · `@sidebar` · `> [!PULLQUOTE]` · `<div class="dc-tape">`

```markdown
# Procedure Title {.dc-chevron}

@lede
One orienting sentence — what this procedure produces and roughly how long it takes.
@end-lede

@procedure

1. **Step One.** Description. One outcome only.
2. **Step Two.** Description. Reference step one where relevant.
3. **Step Three.** Description. Name any tables or rolls explicitly.

@end-procedure

@sidebar
### Sidebar

Guidance for common mistakes or variant rules.

@end-sidebar

> [!PULLQUOTE]
> A resonant line capturing the procedure's purpose.
>
> Source attribution

<div class="dc-tape">— Variant rules begin overleaf —</div>

Optional closing prose for variant rules or table preferences.
```

---

### Fiction / Narrative Prose

Full-column narrative for chapter openers, vignettes, dream intros. Prose + floated art + pull quote only — no structural UI. First-line indent applied by print CSS. **Page class:** normal body page, no break marker needed.

**Components:** `### Scene Label {.dc-spec-tweak .dc-no-top}` (optional) · `*italic opener*` · `![alt](https://placehold.co/1349x842/png?text=Scene){.dc-img-float-right}` (or `.dc-img-float-left`) · `> [!PULLQUOTE]`

```markdown
### Scene Label {.dc-spec-tweak .dc-no-top}

*Italic opener — one sentence that sets tone before the prose begins.*

Narrative prose body. Keep paragraphs short and sensory — what the
operator sees, hears, or smells. Each paragraph earns the next.

![Alt text](https://placehold.co/1349x842/png?text=Scene){.dc-img-float-right}

Continued prose with the floated image wrapping left.

> [!PULLQUOTE]
> A resonant line that closes the scene.
>
> Field debrief, post-run
```

---

### Default Body Page

Standard body page for rules and prose sections such as Vibe, Origins, Dreams, and the DA Devil mechanic. It declares no geometry class at all, so it takes the default `@page :left`/`:right` geometry and keeps both footer counters (`p.N` + `c.N`). Use it for any in-chapter content page that is plain prose, tables, and callouts with no special grid layout. **Page class:** `@page .<section-slug> .chapter-NN`

The section slug (`.vibe`, `.call-home`, `.dream`, `.da-devil`) is an authoring hook for per-spread overrides — these slugs have no dedicated CSS, so they are styling no-ops today and exist as stable targets for future per-section tuning. Do not add a `page-*` marker class here: the default body page is defined by the *absence* of a geometry class, and giving it a second name would create a competing definition of the book's most common page.

> **What `.chapter-NN` does and does not do:** it is a styling hook, and only `fg-overrides.css` uses it — for per-chapter opener art, matching both the unpadded `.page.chapter-1` and the zero-padded `.page.chapter-01`. It resets no counter; no stylesheet defines a `chapter` counter at all. It supplies no accent color; there is no accent rule keyed to it. And it is *not* what paints the `c.N` footer: the body footers read `string(guideSection, first)`, which comes from `@chapter … ch="N"` via `div.chapter[data-ch]`. Per [constitution.md](https://github.com/dimm-city/gp-dimm-city/blob/main/docs/constitution.md), declare `@chapter` and let `markers.js` stamp `.chapter-N` for you rather than hand-writing the padded form.

```markdown
@page .vibe .chapter-01

## 2. Vibe {#c2-style}

They don't know your name.
They don't know what you are.
They know enough.

Something lingers after you leave the room. A pressure change. A silence
that didn't used to be there.

That's your vibe. It doesn't grant bonuses or bend the rules — it's the
signal you broadcast just by existing in the city.

@callout variant="vibe"

DM tip: Ask each Dreamer for one vibe cue, then echo it back in the first NPC reaction.

@end-callout
```

---

### Citizen-File Walkthrough Page

Companion page inside the Citizen File walkthrough. The `.dc-citizen-file-page` geometry class prints the amber **"Citizen File"** running header in the top corner and shifts the binding margin per recto/verso. `@page citizen-file` does not override the bottom margin boxes, so the default body footers (`p.N` + `c.N`) are **retained**. The content is a two-column `@section .dc-citizen-walkthrough` that guides the reader through each field of the character profile. Use it for the character-creation walkthrough pages where field prompts sit beside an origin callout. **Page class:** `@page .dc-citizen-file-page .chapter-NN`

All of the page-level behavior comes from `.dc-citizen-file-page`; the two-column layout comes from the `@section` component. There is no separate sidebar page class — a page carrying one would be indistinguishable from this.

```markdown
@page .dc-citizen-file-page .chapter-01

@section .dc-citizen-walkthrough

## Citizen File {#c2-character-profile}

This chapter will guide you through all the choices you need to make to
fill in the blanks and create a unique and interesting character.

### Image Is Everything {#c2-first-impressions}

Before reputation comes recognition. Before recognition comes a glance.
Dimmers speed-read bodies like text: names, scars, size, and stance all
scanned in a heartbeat.

@column-break

@callout variant=origin label="Image Is Everything"

**Before You Fill Anything In:**

Don't start with numbers. Start with a body, a vibe, and a reason you're
still breathing in Dimm City.

@end-callout

@end-section
```

---

### Choice-Card Page

Choice grid for the **Ideal** and **Flaw** steps of character creation. Takes default body geometry and footers; the page carries only the `.ideal` or `.flaw` topic slug plus `.chapter-NN`. The page holds a sequence of `@card` blocks (each an Ideal/Flaw option) inside a `@section .dc-ideals` or `@section .dc-flaws` wrapper — the section class tints the card accent border (blue for Ideals, blood-red for Flaws). Use it whenever a step offers a set of pickable, equally-weighted options with a heading, prose, and a flavor quote each. **Page class:** `@page .ideal .chapter-NN` (or `.flaw`)

These cards are a single-column stack, not a grid — identical structure per option is what makes the choices comparable. If a step run needs a visual break, use a `.dc-tape` divider between steps rather than a page-level layout. Any column treatment would belong to the `@section`, never the page: per the columns-ownership rule in [css-architecture.md](https://github.com/dimm-city/gp-dimm-city/blob/main/docs/css-architecture.md), `columns:N` lives only in `page-templates.css`, and a column context on the page above the section would nest multicol inside multicol.

```markdown
@page .ideal .chapter-01

@section .dc-ideals

## 4. Ideal {#c2-ideal}

> **What do you stand for when the city bares its teeth?**

Your **Ideal** is the belief you fall back on when things get loud, ugly,
or expensive. Choose one below, or carve your own into the concrete.

@card

### Information Freedom

You value the free flow of information and advocate for digital privacy,
encryption, and the right to access unrestricted knowledge.

> "If knowledge is locked away, it's already being abused."

@end-card

@card

### Honor

You believe in a code, and it's your duty to uphold it.

> "I made a promise to help those in need, and I must fulfill it at all costs."

@end-card

@end-section
```

---

### Ability-Catalog Page

The **Choose a Specialty** catalog — a grid of all eight starting specialties, each a tappable preview card. Takes default body geometry and footers; the page carries only the `.choose-specialty` topic slug plus `.chapter-NN`. Content is a `@section .dc-card-grid` — which owns the two-column layout in `page-templates.css` — holding one `@specialty .<slug>` / `@specialty-card` per specialty; the specialty slug sets the card's accent color and silhouette. Use it for any overview page that surveys a full catalog of specialties or abilities as preview cards before the detailed profiles. **Page class:** `@page .choose-specialty .chapter-NN`

Keep these cards uniform. Identical card chrome is what makes the eight specialties comparable at a glance — `docs/field-guide-visual-diversity-review.md` lists this page in its explicit do-NOT-vary set. A per-page catalog template would only invite varying it.

```markdown
@page .choose-specialty .chapter-01

@section .dc-card-grid

## 1. Choose a Specialty {#c2-choose-a-role}

Every dreamer's got a sharp edge — your specialty is where it starts.
Here's a quick hit on the first eight specialties, each broken down in
full in this chapter:

@specialty .augmerc

@specialty-card #specialty-augmerc

### Augmerc

![Augmerc](https://placehold.co/300x300/png?text=Augmerc)

> Cybernetic Commando

Heavily armed and wired for war, Augmercs are the blunt force of any
squad. Combat-born, augged to kill, and never outgunned.

@end-specialty-card

@end-specialty

@specialty .proxy

@specialty-card #specialty-proxy

### Proxy

![Proxy](https://placehold.co/300x300/png?text=Proxy)

> Militant Monolith

Marked by something higher — god, ghost, code, or conviction — Proxies
walk the line between zealot and judge.

@end-specialty-card

@end-specialty

@end-section
```

---

### Colophon Page

End-of-book closing page. Carries the `.colophon` and `.end-of-book` topic slugs. Neither carries a `@page` rule, so the page inherits the **default** `p.N` + `c.N` footers — they are **retained**, not suppressed. (If a footer-free sign-off is wanted, add `.dc-suppress-footer` to the page, which maps to `@page clean`.) Content is a single `@section` with the closing transmission, edition/imprint metadata, and thanks. Use it once, as the last content page of the book. **Page class:** `@page .colophon .end-of-book`

> **Known gap:** as authored, this page renders as ordinary body prose — after ~290 pages the ending looks like any other spread. The system already ships a treatment that would suit it: `.page.page-credits .section.credits-colophon` in `page-templates.css` gives an accent-rail substrate, poster shadow, two-column colophon grid, and turns bold lead-ins (`**Edition:**`, `**Imprint:**`) into mono uppercase role labels. The existing copy is already in the shape that rule expects.
>
> **It cannot simply be reused, despite appearances.** Every one of those rules is scoped `.page.page-credits .section.credits-colophon` (the package's `styles/page-templates.css`), and `.page.page-credits` maps to `page: front-matter` (`page-rules.css:202`), whose `@page front-matter` block sets `@bottom-left`/`@bottom-right` to `content: none` (`page-rules.css:178`). Re-authoring the colophon onto `@page .page-credits` would therefore **suppress the very footers this page is documented to retain**. Unscoping the rule from `.page-credits` so the colophon can share it is new CSS and a real design decision — not a free re-author. Left open deliberately.

```markdown
@page .colophon .end-of-book

@section

## End of Transmission

"The streets keep score. The Dream keeps the rest."

You made it to the back of the book. The city kept the receipts.

This is the **Dimm City Field Guide** — a living document for a living
sprawl. Rules bend. Lore drifts. Every table runs Dimm City its own way,
and that's the point.

**Edition:** First printing.
**Imprint:** Dimm City Press.

**Thanks** to the playtesters who broke the rules so we could fix them,
the artists who gave the alley its glow, and every Citz who ever rolled a
1 and laughed about it.

Now close the book. Lace up. The Dream is waiting.

**— End. —**

@end-section
```

---

# Rules Pages — Real-World Example {.dc-chevron}

@lede

This section shows how core rules pages look in the actual Dimm City Field Guide, rendered using real book content from chapter 03. Rules pages use standard prose, outcome tables, status condition tables, and rule-break callouts. No special macros — clean prose layout with DC typography.

@end-lede

---

## About Rules Page Layouts

@section .gp-columns-2 .dc-column-panel

Rules pages are the workhorse of any RPG book. In Dimm City they follow a consistent structure across three page templates:

| Template | Chapter class | Contents |
|----------|--------------|----------|
| `page-chapter-start` | `.chapter-03` | Chapter opener fiction + intro prose (two-column) |
| `the-players` | `.chapter-03` | Dreams, Dreamers, Dream Master + ROLL A DIE! section |
| bare `@page` | `.chapter-03` | Status conditions table, AP rules, outcome ladder |

@column-break

Rules prose in DC uses a deliberately aggressive voice. The Dream Master section, for instance, isn't a neutral referee description — it's confrontational, second-person, and assumes the reader is ready to run something rough. The tone is part of the system.

The status conditions table uses standard GFM `|---|---|` syntax — the package's component sheets apply alternating row backgrounds universally. The outcome ladder uses the `@outcome … @end-outcome` macro for tiered DC styling (crit/hit/mixed/miss/fail row colors). Table header color is determined by page-class context: reference/system pages use HUD blue, dramatic/rules pages keep the default crimson.

@end-section

---

### Rules Reference

Workhorse template for mechanics chapters. H2 banners, H3 sub-headings, body prose, note callouts, tape dividers, and roll/option tables (standard GFM pipe tables, auto-styled by dc-core). **Page class:** normal body page, no break marker needed.

**Components:** `## ◈ Title {.dc-chevron}` (◈ optional) · `### Sub-Heading` · `**MECHANIC NAME**` · `ROLL THE DIE!` (automatic `.dc-roll-the-die`) · `<span class="dc-roll-lucid">ROLL LUCID.</span>` · `<span class="ability-name">Name</span>` · `> [!NOTE]` / `> [!DM]` · `<div class="dc-tape">— § —</div>` · `@outcome` macro

```markdown
## ◈ Rule Category {.dc-chevron}

### Mechanic Term

A **MECHANIC TERM** is a defined element of play with a resolution path.
When an ability says ROLL THE DIE!, roll d20.

> [!NOTE]
> Inverse condition note — common edge case or clarification.

<div class="dc-tape">— § —</div>

## ◈ Resolution Table {.dc-chevron}
```

```markdown
@outcome

#### 20 | Crit
Automatic success plus additional benefit of the DM's choice.

#### 11–19 | Hit
Success — the action works as intended.

#### 6–10 | Mixed
Partial success — the action works but with a cost or complication.

#### 2–5 | Miss
Failure — the action does not succeed.

#### 1 | Catastrophe
Fail, and something else goes wrong.

@end-outcome
```

---

# DM & NPC Pages — Real-World Example {.dc-chevron}

@lede

This section shows how Dream Mastery and NPC pages look in the actual Dimm City Field Guide, rendered using real book content from chapter 04. DM pages combine prose, callout blocks, and example sidebars. NPC pages use the stat block format: type line, HP/Damage, Traits, Equipment, and Cybernetics sections.

@end-lede

---

## About DM and NPC Pages

@section .gp-columns-2 .dc-column-panel

The Dream Mastery chapter of the Field Guide is written entirely in second-person directed at the DM. It's the most voice-forward section of the book — not a neutral referee guide, but a manifesto for how to run Dimm City. The layout reflects this: long-form prose with frequent subheadings, bullet-list guidance blocks, and callout boxes for specific techniques.

NPC pages use a consistent three-tier format:

| Tier | HP | Damage | Role |
|------|----|--------|------|
| **Fodder** | 2 | 1 | Cannon fodder, civilian threats, mob encounters |
| **Operator** | 4 | 2 | Skilled grunts, tactical support, mini-bosses |
| **Master** | 10 | 4 | Main antagonists, unique threats, boss encounters |

@column-break

Each NPC entry follows the same structure: a blockquote flavor line (in-world voice), a type/size designation, then H5 subsections for Traits, Equipment, and Cybernetics. The `---` dashed rule separates individual NPC entries within a tier. The tier headers are H3, individual NPC names are H4.

The stat block format is intentionally minimal — no special macro required. The package's component sheets style H4/H5 headings inside the NPC sections automatically using the `chapter-04` page class.

@end-section

---

# Gear & Tech — Real-World Example {.dc-chevron}

@lede

This section shows how gear and cybernetics pages look in the actual Dimm City Field Guide, rendered using real book content from chapter 05. This example focuses on the rules-heavy reference page pattern and standard gear prose.

@end-lede

---

## About Gear & Tech Pages

@section .gp-columns-2 .dc-column-panel

Gear pages in the Field Guide follow a consistent structure: an in-world voice opener (blockquote), a mechanical explanation in plain prose, then a reference table. The pattern repeats for every subsystem — cybernetics, weapons, utilities.

| Pattern | Element | Authoring |
|---------|---------|----------|
| Voice opener | `> blockquote` | In-world character speaking about the gear |
| Mechanical rules | Standard prose | Bold key terms, inline code for mechanic names |
| Reference table | GFM table | Standard `|---|---|` — no class needed for alternating rows |
| Inline code | \`SysChk\` | Game-mechanic terms that are also keywords appear in code style |

@column-break

**Prose + table pattern** — This is the most common rules-page structure in the Field Guide: a section opener in bold flavour prose, a `> blockquote` for an in-world voice line, body prose explaining the mechanic, then a reference table. The Ego Points table is pure GFM markdown — no class attributes needed for basic alternating-row styling (the package's component sheets apply it universally).

**Inline code in prose** — `SysChk` rendered as inline code is intentional for game-mechanic terms that double as class names or keywords. The package's inline code style (orange text, faint orange background) reads clearly against cream body text at 12pt body size.

@end-section

---

## Running Headers and Footers

Two markers in opposing bottom corners of every body page: **`p.N`** (page number) and **`c.N`** (chapter label). Recto: `p.N` bottom-left · `c.N` bottom-right. Verso: swapped. `.dc-chapter-start` and `.front-matter` suppress all footer chrome.

`p.N` is `counter(page)`. `c.N` is **not** a counter — it is a named string, produced by the `@chapter` wrapper and consumed in the `@page` margin boxes:

```css
/* page-rules.css — producer (one rule, all chapters) */
div.chapter[data-ch] { string-set: guideSection attr(data-ch); }

/* page-rules.css — consumers */
@page :left  { @bottom-right { content: "C." string(guideSection, first); } }
@page :right { @bottom-left  { content: "C." string(guideSection, first); } }
```

So the footer number comes from `@chapter … ch="N"` at the top of each chapter file. A chapter split across several source files repeats the marker in every file — `markers.js` renders one file at a time and drains its frame stack at EOF, so one wrapper cannot span files.

In a **book** (as opposed to this guide), write `@chapter ch="N"` and nothing else. this guide's own `styles/guide.css` styles `div.chapter.dg-guide hr` / `pre` / `code` as documentation specimens, and only this guide's own markers carry `.dg-guide`, so a book inherits none of that chrome. Omit any bare label — a label makes `markers.js` inject a visible `.chapter-opener` element into the chapter's first page.

The same `ch="N"` also stamps a `.chapter-N` class onto every page of the chapter. That class is a styling hook — `fg-overrides.css` uses it for per-chapter opener art — not a counter. There is no chapter counter in any stylesheet.

---

## See It In Action

These examples show the above page templates rendered with actual Dimm City Field Guide content.

- [Front Matter & TOC](#ch-example-front-matter) — front-matter page class, TOC template, credits page structure
- [Chapter Openers](#ch-example-chapter-opener) — chapter-start page class, chapter opener template in context
- [Specialty Overview](#ch-example-specialty-overview) — specialty listing, choose-specialty catalog page
- [Specialty Profile](#ch-example-specialty-profile) — specialty opener spread (left + full-page art), learning path template, ability spread
- [Rules & Mechanics](#ch-example-rules) — standard body pages, procedure page, rules reference template
- [Dream Master Pages](#ch-example-dm-npcs) — bestiary entry, citizen-file page class, info sidebar template
- [Gear & Tech](#ch-example-gear-tech) — gear and tech pages, rules tables, cybernetics reference
