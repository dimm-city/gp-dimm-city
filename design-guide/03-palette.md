@chapter #ch-palette .palette .dg-guide ch="1"

# Color Palette

@lede

Two accent registers on cream substrate. Creaturepunk fire (crimson, rust, orange, amber) for printed content. HUD digital (blue, magenta) for cybernetics and tech. The page is never black.

@end-lede

@page

> [!NOTE]
> **Register rule:** Use fire palette (crimson, orange, rust) for printed lore, ability text, and danger. Use HUD digital (blue, magenta) for cybernetics, tech overlays, and system chrome. Never mix fire and HUD on the same UI element.

## Paper & Ink

<div class="dc-palette-grid">
  <div class="dc-palette-swatch border on-light"><strong>BG</strong><code>#c8c5bf</code><code>--bg</code></div>
  <div class="dc-palette-swatch border on-light"><strong>Paper Cream</strong><code>#f0eee9</code><code>--paper-cream</code></div>
  <div class="dc-palette-swatch border on-light"><strong>Paper Light</strong><code>#e2ded7</code><code>--paper-light</code></div>
  <div class="dc-palette-swatch border on-light"><strong>Paper Aged</strong><code>#c8c2b8</code><code>--paper-aged</code></div>
  <div class="dc-palette-swatch bg-ink on-dark"><strong>Ink</strong><code>#1a1512</code><code>--ink</code></div>
  <div class="dc-palette-swatch bg-ink-smoke on-dark"><strong>Ink Smoke</strong><code>#4d4339</code><code>--ink-smoke</code></div>
  <div class="dc-palette-swatch bg-ink-dust on-light"><strong>Ink Dust</strong><code>#665b4e</code><code>--ink-dust</code></div>
</div>

## Creaturepunk Fire

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-crimson on-dark"><strong>Crimson</strong><code>#e1261c</code><code>--crimson</code></div>
  <div class="dc-palette-swatch bg-blood on-dark"><strong>Blood</strong><code>#901a12</code><code>--blood</code></div>
  <div class="dc-palette-swatch bg-orange on-dark"><strong>Orange</strong><code>#d4500a</code><code>--orange</code></div>
  <div class="dc-palette-swatch bg-rust on-dark"><strong>Rust</strong><code>#b23a12</code><code>--rust</code></div>
  <div class="dc-palette-swatch bg-amber on-light"><strong>Amber</strong><code>#7a5a20</code><code>--amber</code></div>
  <div class="dc-palette-swatch bg-deep-rust on-dark"><strong>Deep Rust</strong><code>#6a1a08</code><code>--deep-rust</code></div>
</div>

## HUD Digital

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-hud-blue on-dark"><strong>HUD Blue</strong><code>#1f6f94</code><code>--hud-blue</code></div>
  <div class="dc-palette-swatch bg-hud-blue-bright on-light"><strong>HUD Bright</strong><code>#00bcd4</code><code>--hud-blue-bright</code></div>
  <div class="dc-palette-swatch bg-hud-blue-dim border on-light"><strong>HUD Dim</strong><code>#7ab8d0</code><code>--hud-blue-dim</code></div>
  <div class="dc-palette-swatch bg-hud-magenta on-dark"><strong>HUD Magenta</strong><code>#c026d3</code><code>--hud-magenta</code></div>
</div>

@section .gp-columns-2 .dc-column-panel

## Surface Tokens

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-hud-panel border on-light"><strong>HUD Panel</strong><code>#eeece8</code><code>--hud-panel</code></div>
  <div class="dc-palette-swatch bg-surface-tint-3 border on-light"><strong>Surface 3</strong><code>#f2f0ec</code><code>--surface-tint-3</code></div>
  <div class="dc-palette-swatch bg-surface-orange-tint border on-light"><strong>Orange Tint</strong><code>#d8cfb4</code><code>--surface-orange-tint</code></div>
</div>

## Border Tokens

<div class="dc-palette-grid">
  <div class="dc-palette-swatch bg-border-hairline on-light"><strong>Hairline</strong><code>#c8b898</code><code>--border-hairline</code></div>
</div>

Additional border values come directly from ink-scale tokens (`--ink`, `--ink-smoke`, `--ink-dust`) — no dedicated border aliases for those.

> [!NOTE]
> `--paper-stain` (`#b0a89c`) and `--border-hairline` (`#c8b898`) are distinct: `--paper-stain` is for textured-background fills; `--border-hairline` is for rule lines. Use each semantically.

@end-section

@section .gp-columns-2 .dc-column-panel

## Spacing Token Notes

> [!NOTE]
> `--gutter` is the structural two-column gap (`0.15in`). `--space-2xl` remains the `0.25in` spacing-scale step. Keep them separate: gutter changes reflow layouts, spacing-scale changes adjust component rhythm.

## Usage Rules

- Crimson is the dominant accent. One crimson element per composition; stack additional emphasis with orange.
- HUD blue and magenta signal cybernetic or tech-flavored content. Never mix fire and HUD accents on the same UI element.
- Paper surfaces are for raised elements (cards, callouts). The page background (`--bg`) is the canvas; cream is the surface.

@end-section

@page

## Page Background & Brick Texture

The page background uses `--bg: #c8c5bf` — a light cool gray that contrasts cream paper surfaces (cards, callouts, panels). The Dimm City aesthetic adds an aged-brick texture over it. One `@page` rule paints both across the whole sheet — the content box, plus every margin box carrying no content of its own:

```css
/* dc-native.css (page-rules.css sets the bare color) */
@page {
  background: var(--bg) url("../images/brick-bg-01.png") repeat;
  background-size: 1.5in auto;
  background-blend-mode: multiply;
}
```

Keep the `url()` **local and repo-relative**: the build stages and preloads every image your stylesheets reference, and that preload is what makes an `@page` background paint at all. A remote `url(https://…)` is never staged, so the sheet prints the color alone. Needs Gutterpress 0.10.2-alpha.1+ — before it, a `url()` reached only from `@page` printed nothing, which is why older DC CSS put the wall on a wrapper element.

| Token | Value | Purpose |
|---|---|---|
| `--bg` | `#c8c5bf` | Page background — set on `@page` to control page surface color in both preview and PDF |

---

## CMYK Notes

CMYK approximations for the four primary colors:

| Color | Hex | CMYK |
|---|---|---|
| Crimson | #e1261c | ~0/95/90/0 |
| Orange | #d4500a | ~0/62/95/17 |
| HUD Blue | #1f6f94 | ~79/25/0/42 |
| Ink | #1a1512 | ~0/15/29/90 |

Keep total ink coverage under 280% for coated stock and under 240% for uncoated stock. RGB-to-CMYK conversion is not one-to-one for saturated colors — request a physical proof before the full print run.

---

## Token → Component map

Every component in `components/*.css` exposes its theming surface as `--dc-*`
custom properties declared in `styles/dc-component-defaults.css`. To re-theme a component for a
chapter or a whole project, override the token — set it at `:root` (project-wide)
or at a chapter-id scope (e.g. `#ch-gear { --dc-flavor-accent: var(--orange-deep); }`)
in your book's own sheet. Do **not** edit the component rules; the cascade resolves
your override automatically. The defaults below match each component's shipped look,
so an unset token renders exactly as before.

| Component | Public `--dc-*` token(s) | Default | Overriding it… |
|---|---|---|---|
| `.dc-ap` arrow | `--dc-arrow-color` | `var(--blood)` | recolors the AP-cost arrow glyph |
| `.dc-chevron` banner | `--dc-chevron-bg` · `--dc-chevron-color` · `--dc-chevron-font-size` | `var(--brand-magenta-deep)` · `var(--paper-cream)` · `var(--fs-h1)` | retheme the chevron banner fill, text color, and title size |
| `.dc-classtag` | `--dc-classtag-color` | `var(--orange)` | recolors the inline class tag |
| `.dc-card-tab` | `--dc-card-tab-shadow` | `none` | adds/removes the skill-card tab shadow |
| Cover meta | `--dc-cover-meta-border` | `rgba(201, 214, 226, 0.35)` | retints the cover metadata divider |
| `.dc-definition-block` | `--dc-definition-block-accent` · `--dc-definition-block-accent-width` · `--dc-definition-block-surface` | `var(--hud-blue-bright)` · `4px` · `var(--surface-orange-tint)` | recolors the rail, sets its width, and swaps the panel surface |
| `.dc-dist-*` table | `--dc-dist-ap-color` · `--dc-dist-name-color` · `--dc-dist-tag-border` · `--dc-dist-tag-surface` | `var(--ink)` · `var(--hud-blue)` · `var(--hud-blue-dim)` · `var(--paper-light)` | retheme distribution-table text, name color, and tag chrome |
| `.dc-fiction` | `--dc-fiction-art-float` | `left` | flips the inline fiction-art float side |
| `.dc-flavor` | `--dc-flavor-accent` · `--dc-flavor-accent-width` · `--dc-flavor-color` | `var(--orange)` · `3px` · `var(--ink-smoke)` | recolors the flavor rail, sets its width, and the body text color |
| `.dc-intro` | `--dc-intro-accent` · `--dc-intro-bg` | `var(--orange)` · `var(--paper-stain)` | recolors the intro accent and panel background |
| `.dc-npc-stat-*` block | `--dc-npc-stat-label-color` · `--dc-npc-stat-primary` · `--dc-npc-stat-secondary` · `--dc-npc-stat-rule` · `--dc-npc-stat-rule-width` | `var(--hud-blue-dark)` · `var(--hud-blue-dark)` · `var(--ink-smoke)` · `var(--rust)` · `2pt` | retheme NPC stat-block label, primary/secondary text, and divider rule |
| `.dc-outcomes` table | `--dc-outcomes-surface` · `--dc-outcomes-border` · `--dc-outcomes-inner-border` · `--dc-outcomes-label-bg` · `--dc-outcomes-label-color` · `--dc-outcome-key-color` · `--dc-outcome-name-color` · `--dc-outcome-name-opacity` | `var(--paper-cream)` · `var(--ink)` · `var(--paper-aged)` · `var(--ink-dark)` · `var(--paper-cream)` · `var(--paper-cream)` · `var(--paper-cream)` · `0.85` | retheme the outcomes table surface, borders, header band, and key/name text |
| `.dc-path-shell` | `--dc-path-shell-clip` · `--dc-path-shell-padding-top` · `--dc-path-shell-padding-bottom` · `--dc-path-title-shape` | `polygon(…)` · `0` · `0` · `polygon(…)` | reshapes the path-shell clip silhouette, its vertical padding, and the title tag shape |
| Portrait | `--dc-portrait-border` · `--dc-portrait-surface` | `var(--paper-aged)` · `var(--paper-cream)` | retheme the portrait frame border and mat |
| `.dc-pullquote` | `--dc-pullquote-accent` · `--dc-pullquote-accent-soft` · `--dc-pullquote-bg` | `var(--hud-magenta)` · `rgba(230, 0, 122, 0.15)` · `var(--concrete-pale)` | recolors the pull-quote accent, its soft tint, and panel background |
| Roll / die callout | `--dc-roll-lucid-color` · `--dc-roll-surreal-color` · `--dc-roll-the-die-color` · `--dc-roll-the-die-border` | `var(--hud-blue-dark)` · `var(--hud-magenta)` · `var(--blood)` · `var(--hud-magenta)` | retheme lucid/surreal roll colors and the "roll the die" chip |
| `.dc-sidebar-box` | `--dc-sidebar-box-surface` · `--dc-sidebar-box-border` · `--dc-sidebar-box-accent` · `--dc-sidebar-box-rail` | `var(--paper-cream)` · `var(--border-hairline)` · `var(--hud-blue-dark)` · `4px` | retheme the boxed-sidebar surface, border, accent rail color and width |
| `.dc-sidebar-callout` | `--dc-sidebar-callout-accent` · `--dc-sidebar-callout-bg` | `var(--hud-blue)` · `rgba(42, 106, 138, 0.08)` | recolors the sidebar-callout accent and background tint |
| `.dc-skill-card` shape | `--dc-skill-body-shape` · `--dc-skill-tab-shape` | `polygon(…)` · `polygon(…)` | reshapes the skill-card body and tab clip silhouettes |
| `.dc-specialty-card` extra | `--dc-specialty-card-shadow` · `--dc-specialty-card-shell-shape` · `--dc-specialty-card-title-color` | `none` · `polygon(…)` · `var(--dc-specialty-card-accent)` | adds a card shadow, reshapes the shell, and recolors the title (defaults to the card accent) |
| `.dc-specialty-intro` shape | `--dc-specialty-intro-clip` · `--dc-specialty-intro-title-shape` | `polygon(…)` · `polygon(…)` | reshapes the specialty-intro panel and its title tag |
| `.dc-spray` banner | `--dc-spray-bg` · `--dc-spray-color` | `var(--hud-magenta)` · `var(--paper-cream)` | retheme the spray-paint banner fill and text |
| `.dc-tape` | `--dc-tape-bg` · `--dc-tape-border` · `--dc-tape-color` | `var(--paper-aged)` · `rgba(212, 18, 0, 0.60)` · `var(--ink-dust)` | retheme the tape strip surface, border, and text |

> [!NOTE]
> Components that already exposed their tokens at `:root` before this map — `.dc-alert`,
> `.dc-skill-card` colors, `.dc-specialty-intro` colors, `.dc-path-shell` colors,
> `.dc-specialty-card` colors, `.dc-block`, `.dc-section`, and the chapter-opener
> composite — keep their existing public-API blocks in `dc-component-defaults.css`. A handful of
> component-scoped tokens (e.g. `--dc-ap-bg`, `--dc-sidebar-accent`,
> `--dc-fiction-bg`) are deliberately *not* in this map: they are assigned per
> modifier/variant inside the component rule and have no single global default.

---

@section .gp-columns-2 .dc-column-panel

## Font Size Token Notes

> [!NOTE]
> Pull quotes use `--fs-h2` directly. They are intentionally set at section-heading weight rather than a separate display scale.

> [!NOTE]
> Chevron banners use `--fs-h1` directly. This keeps banner headings and body H1s on the same display scale.

## See It In Action

These examples show the DC palette applied to real book pages using actual Dimm City Field Guide content.

- [Front Matter & TOC](#ch-example-front-matter) — cream paper and ink-dust on credits and TOC pages
- [Chapter Openers](#ch-example-chapter-opener) — crimson chevron banners and brick-texture background in context
- [Specialty Overview](#ch-example-specialty-overview) — specialty palette in action across intro pages
- [Specialty Profile](#ch-example-specialty-profile) — fire palette on skill cards and spray banners
- [Rules & Mechanics](#ch-example-rules) — HUD blue on outcome tables and roll chips
- [Dream Master Pages](#ch-example-dm-npcs) — amber warnings and ink-smoke secondary text
- [Gear & Tech](#ch-example-gear-tech) — fire-palette rules tables and cybernetics reference

> [!NOTE]
> **Ink coverage cap:** Keep total CMYK coverage under 280 % for coated stock and under 240 % for uncoated. Saturated fire palette colors run high — request a physical proof before full print run.

@end-section
