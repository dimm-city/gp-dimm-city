@chapter #ch-palette .palette .dg-guide ch="3"

@page .dg-doc

Chapter 3 {.dg-kicker}

# Color

Cream paper, dark ink, and two accent registers. Creaturepunk **fire** — crimson, orange, rust, amber — for printed lore, ability text, and danger. **HUD digital** — blue and magenta — for cybernetics, tech, and system chrome. The page is never black, and fire and HUD never share one element. {.dg-lede}


## Paper & ink

<div class="dc-palette-grid">
  <div class="dc-palette-swatch border on-light"><strong>BG</strong><code>#c8c5bf</code><code>--bg</code><code>21/17/21/5</code></div>
  <div class="dc-palette-swatch border on-light"><strong>Paper Cream</strong><code>#f0eee9</code><code>--paper-cream</code><code>6/5/7/0</code></div>
  <div class="dc-palette-swatch border on-light"><strong>Paper Light</strong><code>#e2ded7</code><code>--paper-light</code><code>12/10/14/0</code></div>
  <div class="dc-palette-swatch border on-light"><strong>Paper Aged</strong><code>#c8c2b8</code><code>--paper-aged</code><code>20/18/25/6</code></div>
  <div class="dc-palette-swatch bg-ink on-dark"><strong>Ink</strong><code>#1a1512</code><code>--ink</code><code>42/49/45/99</code></div>
  <div class="dc-palette-swatch bg-ink-smoke on-dark"><strong>Ink Smoke</strong><code>#4d4339</code><code>--ink-smoke</code><code>32/47/55/100</code></div>
  <div class="dc-palette-swatch bg-ink-dust on-dark"><strong>Ink Dust</strong><code>#665b4e</code><code>--ink-dust</code><code>27/44/62/99</code></div>
</div>

The page background (`--bg`) is the wall; a brick texture is painted over it by the package's `@page` rule. Paper surfaces are what sits on the wall — cards, callouts, panels. Components are posters and displays hung on the wall: hard edges, decisive separation, never a soft tint that lets the texture through.

## Creaturepunk fire

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-crimson on-dark"><strong>Crimson</strong><code>#e1261c</code><code>--crimson</code><code>0/95/100/17</code></div>
  <div class="dc-palette-swatch bg-blood on-dark"><strong>Blood</strong><code>#901a12</code><code>--blood</code><code>0/92/100/45</code></div>
  <div class="dc-palette-swatch bg-orange on-dark"><strong>Orange</strong><code>#d4500a</code><code>--orange</code><code>0/75/100/24</code></div>
  <div class="dc-palette-swatch bg-rust on-dark"><strong>Rust</strong><code>#b23a12</code><code>--rust</code><code>0/83/100/40</code></div>
  <div class="dc-palette-swatch bg-amber on-light"><strong>Amber</strong><code>#7a5a20</code><code>--amber</code><code>1/29/100/80</code></div>
  <div class="dc-palette-swatch bg-deep-rust on-dark"><strong>Deep Rust</strong><code>#6a1a08</code><code>--deep-rust</code><code>0/84/91/63</code></div>
</div>

## HUD digital

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-hud-blue on-dark"><strong>HUD Blue</strong><code>#1f6f94</code><code>--hud-blue</code><code>100/28/0/46</code></div>
  <div class="dc-palette-swatch bg-hud-blue-bright on-light"><strong>HUD Bright</strong><code>#00bcd4</code><code>--hud-blue-bright</code><code>100/0/13/0</code></div>
  <div class="dc-palette-swatch bg-hud-blue-dim border on-light"><strong>HUD Dim</strong><code>#7ab8d0</code><code>--hud-blue-dim</code><code>60/11/9/5</code></div>
  <div class="dc-palette-swatch bg-hud-magenta on-dark"><strong>HUD Magenta</strong><code>#c026d3</code><code>--hud-magenta</code><code>38/100/0/5</code></div>
</div>

## Surfaces & borders

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-hud-panel border on-light"><strong>HUD Panel</strong><code>#eeece8</code><code>--hud-panel</code><code>7/5/7/0</code></div>
  <div class="dc-palette-swatch bg-surface-tint-3 border on-light"><strong>Surface 3</strong><code>#f2f0ec</code><code>--surface-tint-3</code><code>5/4/6/0</code></div>
  <div class="dc-palette-swatch bg-surface-orange-tint border on-light"><strong>Orange Tint</strong><code>#d8cfb4</code><code>--surface-orange-tint</code><code>15/14/32/3</code></div>
  <div class="dc-palette-swatch bg-border-hairline on-light"><strong>Hairline</strong><code>#c8b898</code><code>--border-hairline</code><code>17/20/45/11</code></div>
</div>

`--paper-stain` (`#b0a89c`) is a textured fill; `--border-hairline` is a rule line. Other rules use the ink scale directly.

## Usage rules

- Crimson is the dominant accent — one crimson element per composition. Stack further emphasis with orange.
- HUD blue and magenta mean cybernetics or tech. Never mix fire and HUD on the same element.
- Paper is for raised elements. The wall is the canvas; cream is the surface.
- Keep CMYK coverage under 280% on coated stock and 240% on uncoated. The fire palette runs hot — proof on paper before a print run.

Running text goes on a paper surface, never straight on the wall: the brick texture under body type cuts its contrast and breaks up the letterforms.

Don't {.dg-dont-label}

<div class="dg-stage dg-dont">

Dimm City twitches like a clamped nerve at the edge of existence. Nothing here is safe, and nothing here is free.

</div>

Do {.dg-result}

<div class="dg-stage">

@section

Dimm City twitches like a clamped nerve at the edge of existence. Nothing here is safe, and nothing here is free.

@end-section

</div>


## Retheming a book

Every component exposes its colors and shapes as `--dc-*` custom properties, with defaults in the package's `styles/dc-component-defaults.css`. A book never edits the package: it lists one sheet of its own under `styles:` and resets tokens there, either for the whole book at `:root` or for one chapter at the chapter's id. The book's sheet is unlayered and the package sits in its own cascade layer, so the override wins at any specificity.

```css
/* my-book/styles/overrides.css */
:root {
  --dc-flavor-accent: var(--hud-blue);        /* every flavor rail, whole book */
}

#ch-gear {
  --dc-section-accent: var(--amber);          /* section chrome in one chapter */
  --dc-alert-border: var(--rust);
}
```

The brand tokens themselves — `--crimson`, `--hud-blue`, `--paper-cream`, the fonts — live in `styles/dc-palette.css` and reset the same way. The full token-to-component map is in [Reference](#ch-reference).

Do not write bare `.dc-*` rules in a book to change a component; that fights the package on every update. Reset the component's tokens on a context selector instead.

## CMYK

Each swatch's third line is its CMYK build (C/M/Y/K, percent), converted from the hex through CGATS21_CRPC1 — the coated press profile gutterpress embeds in a PDF/X build — with relative colorimetric intent. Treat them as starting points: RGB to CMYK is not one-to-one for saturated colors, so request a physical proof before the full print run.
