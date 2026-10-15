@chapter #ch-reference .reference .dg-guide ch="10"

@page .dg-doc

Chapter 10 {.dg-kicker}

# Reference

Every marker on one page, the options they take, the classes you can add, and the token each component exposes. The chapters before this one show each in use. {.dg-lede}


## Structure (Gutterpress core)

| Marker | Closes | Notes |
|---|---|---|
| `@chapter [word] #id ch="N" [head="Name"]` | next `@chapter` / EOF | `ch` prints the footer; `head` names the chapter in the running head (else its `#` title, else "Chapter N"). Words: `rules` `lore` `citizen-file` `specialty` set the chapter's section colour; any other word is the label |
| `@page [word] [.class…]` | next `@page` | Words: `chapter-start` `intro` `credits` `contents` `citizen-file` `specialty-catalog`, plus core's `blank` and `full-bleed`: [Page Templates](#ch-templates) |
| `@spread` | next `@spread` / `@page` | Two facing pages |
| `@section [word] [.class…]` | `@end-section` | A region; bare = core's plain box. Words: `panel` `flat` `catalog`, the kinds of text (`reference` `lore` `dm` `choose`) and the component words (`npc` `fiction` `walkthrough` `cards` `flaws` `ideals` `dreams`) |
| `@columns N` | `@end-columns` | `N` is 1 to 5. The one way to set content in columns; `@column-break` inside it starts the next column |
| `@page-break` · `@column-break` | — | Forced breaks |

## Components (this package)

| Marker | Closes | Options |
|---|---|---|
| `@lede` | `@end-lede` | — |
| `> [!TYPE]` | end of blockquote | `NOTE` `WARNING` `DM` `VIBE` `ORIGIN` `VISIT` `FLAVOR` `PULLQUOTE` |
| `@callout` | `@end-callout` | a variant word: `note` `warning` `dm` `vibe` `origin` `visit` `example` (`@callout vibe`); `label="…"`; `.dc-sidebar` floats it |
| `@dm-note` | `@end-dm-note` | `label="…"` (it is `@callout dm`) |
| `@block` | `@end-block` | `.dc-panel` `.dc-slate` `.dc-shard`, `label="…"` |
| `@definition [lucid\|surreal]` | `@end-definition` | a term, a run of `#### Term` entries (a glossary), or `####` + `---` + body; `lucid` and `surreal` are the two roll states, set as opposites |
| `@faction` | `@end-faction` | a kind word: `megacorp` `cabal` `cult` `enforcer`; `label="…"` |
| `@roll-table` | `@end-roll-table` | `die=d20`, `label="…"`; a pipe table inside |
| `@procedure` | `@end-procedure` | an ordered list |
| `@outcome` | `@end-outcome` | `flush`; rows `roll \| name \| text` |
| `@card` | `@end-card` | inside `@flaws` / `@ideals` / `@dreams` |
| `@card-grid` | `@end-card-grid` | a run of `@specialty` / `@specialty-card` inside `@columns 2` |
| `@citizen-walkthrough` | `@end-citizen-walkthrough` | `####` field names and prose; `@columns 2` inside sets two fields side by side |
| `@fiction-excerpt` | `@end-fiction-excerpt` | prose; the first image floats |
| `@npc-stat` | `@end-npc-stat` | `####` name, `>` flavor, stat lines, `#####` labels; `@columns 2` inside sets the entries in columns |
| `@flaws` · `@ideals` · `@dreams` | `@end-flaws` · `@end-ideals` · `@end-dreams` | a run of `@card` blocks |
| `@gear` | `@end-gear` | a kind word (`augment` `treasure` `vehicle` `drug`; none is general gear); `####` name, `>` tagline, body, field lines; the next `@gear` closes it |
| `@field` | `@end-field` | a variant word (`specs` `traits` `equipment` `effects` `side-effects` `requires`); `label="…"` |
| `@toc` | `@end-toc` | an ordered list of `[title](#id) — blurb` |
| `@specialty` | `@end-specialty` / next `@specialty` / `@page` / `@section` / `@chapter` | `augmerc` … `generalist`, as a word or a `.class` |
| `@specialty-intro` | `@end-specialty-intro` | `##` name, `###` spec tweak |
| `@specialty-art` | `@end-specialty-art` | one image |
| `@specialty-card` | `@end-specialty-card` | `#id`; `###` name, image, `>` tagline, pitch |
| `@learning-path` | `@end-learning-path` / next `@learning-path` / end of its specialty | `###` title, `>` subtitle, `- skills`, `**Augment:**` |
| `@skill` | `@end-skill` / next `@skill` / end of its path | `id="…"`, `{.dc-avoid-split}`; `#### Name \| Tier`; `@columns 2` around part of the body |
| `@continue` | — | inside a skill: continuation card |


## Classes you can add

| Class | Goes on | Effect |
|---|---|---|
| `.dc-avoid-split` | `@section`, `@skill`, `@faction`, `@npc-stat` | Keep the box whole: it moves to the next page rather than splitting (all split by default but a creature). It sets the keep-whole tokens below |
| `.dc-snug` | `@section`, `@page` | Tighten the space under paragraphs and list items; it sets `--dc-flow-gap` to 0.04in |
| `.gp-no-break` | `@section` | Core's never-split class |
| `.gp-break-before` | a heading | New page before it |
| `.dc-page-chapter-start` · `.dc-page-intro` · `.dc-page-credits` · `.dc-page-contents` · `.dc-page-citizen-file` · `.dc-page-specialty-catalog` | `@page` | What the page words write. The old raw pairs (`.page-chapter-start .dc-chapter-start`, `.page-credits .dc-credits`, `.page-intro`, `.page-toc`, `.dc-citizen-file-page`) are no longer styled |
| `.dc-chapter-rules` · `.dc-chapter-lore` · `.dc-chapter-citizen-file` · `.dc-chapter-specialty` | `@chapter` | What the chapter words write |
| `.dc-section-panel` · `.dc-section-flat` | `@section` | What `@section panel` and `flat` write |
| `.dc-section-reference` · `.dc-section-lore` · `.dc-section-dm` · `.dc-section-choose` | `@section` | What `@section reference`, `lore`, `dm` and `choose` write (with `.dc-section-panel`) |
| `.dc-npc-compact` | `@section` | What `@npc-stat compact` writes |
| `.dc-sidebar` | a callout | Float it right, text wrapping on its left |
| `.dc-catalog` | `@section` | What `@section catalog` writes (with `.dc-section-panel`) |
| `.dc-entry` · `.dc-gear` `.dc-augment` `.dc-treasure` `.dc-vehicle` `.dc-drug` | `@gear` and its kind words | The entry card family; the kind class sets its tokens |
| `.dc-field` · `.dc-field-<variant>` · `.dc-field-label` | `@field` | What `@field` and a `**Label:**` paragraph in a card write |
| `.dc-npc-stat` | `@section` | What `@npc-stat` and `@section npc` write (with `.dc-section-panel`) |
| `.dc-fiction-excerpt` | `@section` | What `@fiction-excerpt` and `@section fiction` write: an aged page sunk into a torn hole in the wall, narrative typography, auto art float |
| `.dc-citizen-walkthrough` | `@section` | What `@citizen-walkthrough` writes (with `.dc-section-panel`) |
| `.dc-card-grid` | `@section` | Density for a run of specialty cards (set in `@columns 2`); no chrome |
| `.dc-flaws` · `.dc-ideals` · `.dc-dreams` | `@section` of `@card` | The kind of choice (flaw, ideal, dream): colour, silhouette and chip per step |
| `.dc-chevron` | `#` heading | Chevron banner |
| `.dc-spray` | `##` heading | Spray banner |
| `.dc-spec-tweak` · `.dc-no-top` | `###` heading | Spec-tweak rule; no top margin |
| `.dc-img-float-left` · `.dc-img-float-right` | an image | Float at 44% width |
| `.dc-flush` | tape, stat block, stickers | Edge to edge |

## Inline HTML

| You write | Renders |
|---|---|
| `<span class="dc-tag">Melee</span>` | keyword chip |
| `<span class="dc-classtag augmerc">Augmerc</span>` | specialty identity pill |
| `<span class="dc-ap">2 AP</span>` · `.free` · `.var` | AP chip in prose |
| `<div class="dc-tape dc-flush">Label</div>` | tape, edge to edge |
| `<div class="dc-stat [dc-flush]">…</div>` | four-cell stat grid ([Panels, Cards & Data](#ch-panels)) |
| `<div class="dc-at-a-glance-card">…</div>` in `@columns 3` | label band over a value, as a tile |
| `<div class="dc-sidebar"><div class="dc-human-callout">…` | floated contact card |


## Tokens by component

Reset any of these in a book's own sheet, at `:root` or at a chapter id. Defaults live in the package's `styles/dc-component-defaults.css`; shapes are `polygon(…)` clip-paths.

| Component | Tokens |
|---|---|
| Section chassis | `--dc-section-bg` `--dc-section-accent` |
| Keep whole (`avoid` or `auto`) | `--dc-section-break-inside` (with `--dc-section-edge: 0px`) `--dc-catalog-break-inside` `--dc-npc-stat-break-inside` `--dc-skill-card-break-inside` `--dc-faction-break-inside` |
| Space under paragraphs and list items | `--dc-flow-gap` (unset by default) |
| Art by context | `--dc-entry-art-width` `--dc-credits-art-height` |
| Lede | `--dc-intro-bg` `--dc-intro-accent` `--dc-intro-color` `--dc-intro-size` `--dc-intro-weight` `--dc-intro-style` `--dc-intro-rail` `--dc-intro-rule` `--dc-intro-ink` |
| Flavor | `--dc-flavor-accent` `--dc-flavor-accent-width` `--dc-flavor-color` `--dc-flavor-bg` |
| Pull quote | `--dc-pullquote-accent` `--dc-pullquote-accent-soft` `--dc-pullquote-bg` |
| Alerts, callout, DM note | `--dc-alert-bg` `--dc-alert-border` `--dc-alert-fg` `--dc-alert-label-color` `--dc-alert-border-width` `--dc-alert-label-size` `--dc-alert-body-size` `--dc-alert-frame` `--dc-alert-label-bg` `--dc-alert-label-pad` |
| Tape | `--dc-tape-bg` `--dc-tape-border` `--dc-tape-color` `--dc-tape-shape` |
| Tag (inline chip) | `--dc-tag-bg` `--dc-tag-fg` `--dc-tag-border` |
| Chevron · Spray | `--dc-chevron-bg` `--dc-chevron-color` `--dc-chevron-font-size` · `--dc-spray-bg` `--dc-spray-color` `--dc-spray-stencil` |
| Class tag | `--dc-classtag-color` |
| Roll the die | `--dc-accent-ink` |
| Block | `--dc-block-bg` `--dc-block-fg` `--dc-block-accent` `--dc-block-title-bg` `--dc-block-title-fg` `--dc-block-title-rule` `--dc-block-tag` `--dc-block-tag-edge` |
| Section chip (`dm`, `choose`) | `--dc-section-tab` `--dc-section-tab-bg` `--dc-section-tab-fg` |
| Roll table | `--dc-roll-table-accent` `--dc-roll-table-surface` `--dc-roll-table-head-bg` |
| Faction | `--dc-faction-accent` `--dc-faction-badge-fg` `--dc-faction-shape` `--dc-faction-surface` `--dc-faction-band` `--dc-faction-band-height` `--dc-faction-title` |
| Choice card (set by `@flaws` `@ideals` `@dreams`) | `--dc-choice-accent` `--dc-choice-surface` `--dc-choice-tint` `--dc-choice-kind` `--dc-choice-edge` `--dc-choice-band` `--dc-choice-rail` `--dc-card-shape` |
| Entry card (`@gear` and its kinds) | `--dc-entry-accent` `--dc-entry-ink` `--dc-entry-surface` `--dc-entry-shape` `--dc-entry-radius` `--dc-entry-ornament` `--dc-entry-orn-inset` `--dc-entry-orn-bg` `--dc-entry-orn-border` `--dc-entry-orn-clip` `--dc-entry-orn-z` `--dc-entry-frame` `--dc-entry-badge-bg` `--dc-entry-badge-fg` `--dc-entry-badge-shape` `--dc-entry-badge-radius` |
| Field | `--dc-field-surface` `--dc-field-fg` `--dc-field-label-fg` `--dc-field-edge-width` `--dc-field-edge-style` |
| Procedure | `--dc-steps-accent` `--dc-steps-surface` |
| At-a-glance tile | `--dc-at-a-glance-accent` `--dc-at-a-glance-value` |
| Stat strip | `--dc-stat-strip-accent` `--dc-stat-strip-value` |
| Definition | `--dc-definition-block-surface` `--dc-definition-block-accent` `--dc-definition-block-term` `--dc-definition-block-accent-width` `--dc-definition-block-rule-bottom` `--dc-definition-block-shape` `--dc-definition-block-fg` `--dc-definition-block-style` `--dc-definition-block-frame` `--dc-definition-block-pad` |
| Outcome ladder | `--dc-outcomes-surface` `--dc-outcomes-border` `--dc-outcomes-inner-border` `--dc-outcomes-label-bg` `--dc-outcomes-label-color` `--dc-outcome-key-color` `--dc-outcome-name-color` `--dc-outcome-name-opacity` `--dc-outcome-key-col` |
| NPC stat block | `--dc-npc-stat-primary` `--dc-npc-stat-secondary` `--dc-npc-stat-label-color` `--dc-npc-stat-rule` `--dc-npc-stat-rule-width` |
| Fiction excerpt | `--dc-fiction-bg` `--dc-fiction-depth` `--dc-fiction-depth-bg` `--dc-fiction-cavity` `--dc-fiction-lip` `--dc-fiction-rim` `--dc-fiction-rule` `--dc-fiction-shadow` `--dc-fiction-shape` `--dc-fiction-hole` `--dc-fiction-line-height` `--dc-fiction-art-float` `--dc-fiction-art-width` `--dc-fiction-art-outline` `--dc-fiction-art-shadow` |
| Specialty wrapper | `--spec-accent` `--spec-mid` `--spec-dark` `--spec-band` `--spec-on-band` `--spec-chip-bg` `--spec-chip-fg` `--spec-chip-edge` `--dc-skill-tab-shape` `--dc-skill-body-shape` `--dc-path-title-shape` `--dc-path-shell-clip` `--dc-specialty-card-shell-shape` `--dc-specialty-intro-title-shape` `--dc-specialty-intro-clip` |
| Specialty intro | `--dc-specialty-intro-bg` `--dc-specialty-intro-title-bg` `--dc-specialty-intro-title-color` |
| Title band (path banner, intro title) | `--dc-band-rule` `--dc-band-rule-h` `--dc-band-tick` `--dc-band-tick-style` `--dc-band-tick-w` `--dc-band-rule-skew` `--dc-band-rule-bleed` `--dc-band-facet` `--dc-band-facet-width` `--dc-band-facet-clip` `--dc-band-rim` `--dc-band-reg` |
| Specialty card | `--dc-specialty-card-bg` `--dc-specialty-card-border` `--dc-specialty-card-accent` `--dc-specialty-card-fg` `--dc-specialty-card-media-height` `--dc-specialty-card-media-width` `--dc-specialty-card-title-align` `--dc-specialty-card-band-height` `--dc-specialty-card-shadow` `--dc-specialty-card-title-color` `--dc-specialty-card-display` `--dc-specialty-card-media-order` `--dc-specialty-card-media-float` `--dc-specialty-card-media-margin` `--dc-specialty-card-media-shape` `--dc-specialty-card-media-mat` `--dc-specialty-card-name-size` `--dc-specialty-card-index` `--dc-card-grid-display` `--dc-card-grid-item-display` `--dc-card-grid-row` `--dc-card-grid-gap` |
| Learning path | `--dc-path-title-bg` `--dc-path-title-color` `--dc-path-code-bg` `--dc-path-code-fg` `--dc-path-chip-bg` `--dc-path-chip-fg` `--dc-path-chip-edge` `--dc-path-note-rail` `--dc-path-accent` `--dc-path-shell-padding-top` `--dc-path-shell-padding-bottom` `--dc-arrow-color` |
| Skill card | `--dc-card-accent` `--dc-card-surface` `--dc-card-tab-bg` `--dc-card-tab-title-color` `--dc-card-body-mark` `--dc-card-gap` `--dc-card-tab-shadow` `--dc-tier-bg` `--dc-tier-fg` `--dc-tier-edge` |
| AP chip | `--dc-ap-bg` `--dc-ap-fg` `--dc-ap-border` |

The brand tokens — `--crimson`, `--orange`, `--rust`, `--amber`, `--blood`, `--hud-blue`, `--hud-magenta`, `--paper-cream`, `--paper-aged`, `--ink`, `--ink-smoke`, `--bg`, and the `--font-*` family — are in [Color](#ch-palette) and [Typography](#ch-typography). The machine-readable catalog of every component, with the DOM it emits and the sheet that owns it, is the package's `components.yaml`.
