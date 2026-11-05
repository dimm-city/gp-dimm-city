@chapter #ch-palette .palette .dg-guide ch="3"

@page .dg-doc

Chapter 3 {.dg-kicker}

# Color

Cream paper, dark ink, and two accent registers. Creaturepunk **fire** --- crimson, orange, rust, amber --- for printed lore, ability text, and danger. **HUD digital** --- blue and cyan --- for rules, look-ups, cybernetics and system chrome, with magenta kept for display punch. The page is never black, and fire and HUD never share one element. {.dg-lede}


## Paper & ink

<div class="dc-palette-grid">
  <div class="dc-palette-swatch border on-light"><strong>BG</strong><code>#c8c5bf</code><code>--bg</code><code>18/15/18/2<br>53%</code></div>
  <div class="dc-palette-swatch border on-light"><strong>Paper Cream</strong><code>#ffffff</code><code>--paper-cream</code><code>0/0/0/0<br>0%</code></div>
  <div class="dc-palette-swatch border on-light"><strong>Paper Light</strong><code>#ffffff</code><code>--paper-light</code><code>0/0/0/0<br>0%</code></div>
  <div class="dc-palette-swatch border on-light"><strong>Paper Aged</strong><code>#dcdad5</code><code>--paper-aged</code><code>12/9/12/0<br>33%</code></div>
  <div class="dc-palette-swatch bg-ink on-dark"><strong>Ink</strong><code>#1e1d1c</code><code>--ink</code><code>44/38/37/92<br>211%</code></div>
  <div class="dc-palette-swatch bg-ink-dark on-dark"><strong>Ink Dark</strong><code>#2f2622</code><code>--ink-dark</code><code>39/38/38/87<br>202%</code></div>
  <div class="dc-palette-swatch bg-ink-smoke on-dark"><strong>Ink Smoke</strong><code>#4d4339</code><code>--ink-smoke</code><code>32/33/39/71<br>175%</code></div>
  <div class="dc-palette-swatch bg-ink-dust on-dark"><strong>Ink Dust</strong><code>#665b4e</code><code>--ink-dust</code><code>31/31/41/53<br>156%</code></div>
</div>

The page background (`--bg`) is the wall; a brick texture is painted over it by the package's `@page` rule. Paper surfaces are what sits on the wall --- cards, callouts, panels. Components are posters and displays hung on the wall: hard edges, decisive separation, never a soft tint that lets the texture through.

## Creaturepunk fire

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-crimson on-dark"><strong>Crimson</strong><code>#e1261c</code><code>--crimson</code><code>0/100/100/6<br>206%</code></div>
  <div class="dc-palette-swatch bg-blood on-dark"><strong>Blood</strong><code>#901a12</code><code>--blood</code><code>2/92/65/48<br>207%</code></div>
  <div class="dc-palette-swatch bg-orange on-dark"><strong>Orange</strong><code>#d4500a</code><code>--orange</code><code>0/71/100/13<br>184%</code></div>
  <div class="dc-palette-swatch bg-rust on-dark"><strong>Rust</strong><code>#b23a12</code><code>--rust</code><code>0/80/100/30<br>210%</code></div>
  <div class="dc-palette-swatch bg-amber on-light"><strong>Amber</strong><code>#7a5a20</code><code>--amber</code><code>17/33/75/52<br>177%</code></div>
  <div class="dc-palette-swatch bg-deep-rust on-dark"><strong>Deep Rust</strong><code>#70200e</code><code>--deep-rust</code><code>11/73/58/65<br>207%</code></div>
</div>

## HUD digital

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-hud-blue on-dark"><strong>HUD Blue</strong><code>#1f6f94</code><code>--hud-blue</code><code>78/29/8/24<br>139%</code></div>
  <div class="dc-palette-swatch bg-hud-blue-bright on-light"><strong>HUD Bright</strong><code>#00bcd4</code><code>--hud-blue-bright</code><code>67/0/11/0<br>78%</code></div>
  <div class="dc-palette-swatch bg-hud-blue-dim border on-light"><strong>HUD Dim</strong><code>#7ab8d0</code><code>--hud-blue-dim</code><code>46/9/8/3<br>66%</code></div>
  <div class="dc-palette-swatch bg-hud-magenta on-dark"><strong>HUD Magenta</strong><code>#cf217e</code><code>--hud-magenta</code><code>2/100/1/12<br>115%</code></div>
</div>

## Surfaces & borders

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-hud-panel border on-light"><strong>HUD Panel</strong><code>#dcdad5</code><code>--hud-panel</code><code>12/9/12/0<br>33%</code></div>
  <div class="dc-palette-swatch bg-surface-tint-3 border on-light"><strong>Surface 3</strong><code>#f2f0ec</code><code>--surface-tint-3</code><code>4/4/5/0<br>13%</code></div>
  <div class="dc-palette-swatch bg-surface-orange-tint border on-light"><strong>Orange Tint</strong><code>#d8cfb4</code><code>--surface-orange-tint</code><code>13/12/26/1<br>52%</code></div>
  <div class="dc-palette-swatch bg-border-hairline on-dark"><strong>Hairline</strong><code>#1e1d1c</code><code>--border-hairline</code><code>44/38/37/92<br>211%</code></div>
</div>

There are three substrates: white paper, one light grey (`--concrete-pale`, `#dcdad5`) and the wall. The other paper names are aliases of them: `--paper-light` and `--paper-form` (the `choose` form's sheet) are white; `--paper-zine` (no component uses it: the fiction excerpt and the shard block are white), `--paper-aged` (chips, `code`, outcome rows) and `--hud-panel` are the light grey. Callouts, sections, cards and entries are white: a component's colour is in its rail, frame, title bar and label, never in a tinted body. `--paper-stain` (`#b0a89c`) is a dark inset well and label strip: it never carries body text, and neither does any fill darker than the wall. `--border-hairline` is the column and table rule, in ink. Every hairline is at least 1pt, in `--ink` or a tint that prints in one ink. `--surface-tint-3` is only here for its swatch; no component uses it.

## What each colour means

Colour is a job, not a mood. A reader flipping pages should know what kind of content a box holds from its silhouette, its edge and its label before reading a word, and the same has to hold in a grayscale proof, so every variant also differs in shape, edge weight or label: never in hue alone. Text reads on white; the colour is in the rail, the frame, the title bar and the label.

| Colour | Means | Used by |
|---|---|---|
| Magenta | Display punch: the loudest thing on the page, never a category | Chapter chevrons, spray titles, pull quotes, `ROLL THE DIE!`, the VAR chip, the default panel accent |
| HUD blue, pale cyan | A rule or a look-up, for the player | Note alert, reference section, definitions, megacorp faction, ideals |
| Cyan on ink | The Dream Master only | `dm` alert and section, the Dream Master chip |
| Hazard yellow with ink | Danger, consequence, a choice you must make | Warning alert, enforcer faction, the *Choose* stamp, vehicle gear |
| Blood, rust, crimson | Harm, cost, cult, a binding ruling | Slate block, flaws, cult faction, origin stamp, side effects |
| Violet, amethyst | The world and the arcane | Vibe alert, lore section, dreams, cabal faction, treasure |
| Fungi green | The living city: organic, toxic | Visit alert, drug gear, Gutterdruid |
| Paper versus ink | Reading surface or display | White paper holds reading text, whoever it is for. An ink-dark fill is a display element: title bars, tabs, badges, label chips, the slate block and the Surreal definition |

## Usage rules

- Crimson is the dominant accent --- one crimson element per composition. Stack further emphasis with orange.
- HUD blue means a rule or a look-up; magenta is display punch, not a category. Never mix fire and HUD on the same element.
- Paper is for raised elements. The wall is the canvas; cream is the surface.
- Total ink stays under 240%: the CGATS21_CRPC1 profile a `pdfx` build converts through cannot put down more, and no colour here comes near it. Small text is set in `--ink`, the one dark that prints in black alone. Magenta, crimson and fungi green shift most on press --- proof on paper before a print run.

Running text goes on a paper surface, never straight on the wall: the brick texture under body type cuts its contrast and breaks up the letterforms.

Don't {.dg-dont-label}

<div class="dg-stage dg-dont">

Dimm City twitches like a clamped nerve at the edge of existence. Nothing here is safe, and nothing here is free.

</div>

Do {.dg-result}

<div class="dg-stage">

@section panel

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

The brand tokens themselves --- `--crimson`, `--hud-blue`, `--paper-cream`, the fonts --- live in `styles/dc-palette.css` and reset the same way. The full token-to-component map is in [Reference](#ch-reference).

Do not write bare `.dc-*` rules in a book to change a component; that fights the package on every update. Reset the component's tokens on a context selector instead.

## CMYK

Each swatch's third line is its CMYK build (C/M/Y/K, percent) and total ink, converted from the hex the way a `pdfx` build converts it: through Ghostscript with CGATS21_CRPC1 --- the newsprint-class press profile DriveThruRPG specifies and gutterpress embeds in a PDF/X build --- at Ghostscript's default intent, relative colorimetric with black-point compensation (`scripts/measure-palette-crpc1.py` in the gp-dimm-city repository runs a swatch of each colour through that conversion and reads the operands back). The figures are the build's to the digit. CRPC1 is a small gamut, so the purples are chosen to print close to how they look on screen and well apart from each other. Treat the figures as starting points and request a physical proof before the full print run.
