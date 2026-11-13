# DC Design Guide — Components & Color Palette Reference

---

## Macro → Class Cross-Reference

This table maps the author-facing syntax to the CSS classes emitted at render time.
Authors write on the left; the right-hand columns show what appears in the DOM.

| Author writes | Macro / trigger | Emitted class(es) |
|---|---|---|
| `@lede … @end-lede` | DC plugin | `.dc-intro` |
| `@section` | marker plugin | `.section` (plain: this package styles nothing on it) |
| `@section panel` | DC section word | `.section.dc-section-panel` |
| `@section flat` | DC section word | `.section.dc-section-flat` |
| `@section reference` · `lore` · `dm` · `choose` | DC section word | `.section.dc-section-panel.dc-section-reference` (`-lore`, `-dm`, `-choose`) |
| `@npc-stat` · `@section npc` | DC section component | `.section.dc-section-panel.dc-npc-stat` (`@npc-stat compact` adds `.dc-npc-compact`) |
| `@citizen-walkthrough` · `@section walkthrough` | DC section component | `.section.dc-section-panel.dc-citizen-walkthrough` |
| `@flaws` / `@ideals` / `@dreams` · `@section flaws` … | DC section component | `.section.dc-section-panel.dc-section-choose.dc-flaws` (`-ideals`, `-dreams`) |
| `@fiction-excerpt` · `@section fiction` | DC section component | `.section.dc-fiction-excerpt` |
| `@card-grid` · `@section cards` | DC section component | `.section.dc-card-grid` |
| `@section … .dc-avoid-split` | modifier | `.dc-avoid-split` (sets the keep-whole tokens `--dc-section-break-inside`, `--dc-skill-card-break-inside`, `--dc-faction-break-inside`, `--dc-npc-stat-break-inside`) |
| `@section … .dc-snug` · `@page .dc-snug` | modifier | `.dc-snug` (sets `--dc-flow-gap`, tighter paragraph and list gaps) |
| `@page chapter-start` | DC page word | `.page.dc-page-chapter-start` |
| `@page intro` · `credits` · `contents` · `citizen-file` | DC page word | `.page.dc-page-intro` · `-credits` · `-contents` · `-citizen-file` |
| `@page full-bleed` · `@page blank` | core page word | `.page.gp-page-full-bleed` · `.page.gp-page-blank` |
| `@chapter rules` · `lore` · `citizen-file` · `specialty` | DC chapter word | `.chapter.dc-chapter-rules` · `-lore` · `-citizen-file` · `-specialty` |
| `@page .NAME` | marker plugin | `.page.NAME` |
| `@block panel` | DC plugin | `.dc-block.dc-panel` |
| `@block slate` | DC plugin | `.dc-block.dc-slate` |
| `@block shard` | DC plugin | `.dc-block.dc-shard` |
| `@faction megacorp` · `cabal` · `cult` · `enforcer` | DC plugin | `.dc-card.dc-faction.dc-faction-<kind>` + `.dc-faction-kind` badge |
| `@gear` · `@gear augment` · `treasure` · `vehicle` · `drug` | DC plugin | `.dc-card.dc-entry.dc-gear` (bare) · `.dc-card.dc-entry.dc-<kind>` |
| `@field specs` · `traits` · `equipment` · `effects` · `side-effects` · `requires`, or a `**SPECS:**` paragraph in an entry | DC plugin | `.dc-field.dc-field-<variant>` + `.dc-field-label` |
| `@roll-table` | DC plugin | `.dc-roll-table` + `.dc-roll-table-caption` over the author's table |
| a table of the five bands | DC plugin (by shape) | `.dc-outcomes` ladder |
| a table with HP and Damage columns | DC plugin (by shape) | `table.dc-stat-strip` |
| `@callout example` | DC plugin | `.dc-alert.dc-example-callout` |
| `@specialty .NAME` | DC plugin | `.dc-specialty.NAME` (scope parent for specialty cards) |
| `@skill … @end-skill` | DC plugin | `.dc-skill-card` |
| `@learning-path … @end-learning-path` | DC plugin | `.dc-path-shell` + `.dc-learning-path` |
| `@chapter NAME` | marker plugin | `<div class="chapter" data-chapter-label="NAME">` (when NAME is not a declared chapter word) |
| `> [!VIBE]` | GFM alert + DC plugin | `.dc-vibe-callout` |
| `> [!DM]` | GFM alert + DC plugin | `.dc-dm-note` |
| `> [!ORIGIN]` | GFM alert + DC plugin | `.dc-origin-callout` |
| `> [!LOCATION]` | GFM alert + DC plugin | `.dc-location-callout` |
| `> [!VISIT]` | GFM alert + DC plugin | `.dc-visit-callout` |
| `> [!NOTE]` | GFM alert | `.dc-note` |
| `> [!WARNING]` | GFM alert | `.dc-note.warning` |

---

## Supported Components

### Callouts & Notes
- `.dc-alert` — the one callout shell: eight registers (note, warning, dm, vibe, origin, location, visit, example), told apart by silhouette, edge and label; every one is a white sheet, its colour in the rail, the frame and the label
- `.dc-alert-label` — label chip on alerts
- `.dc-note` / `.dc-note.warning`
- `.dc-vibe-callout`, `.dc-human-callout` (a contact card: blue ID band, ink strip foot), `.dc-origin-callout`, `.dc-location-callout`, `.dc-visit-callout`, `.dc-example-callout`
- `.dc-dm-note`
- `.dc-prose-panel`

#### Callout Decision Tree

Use this to choose the right callout type before reaching for a class name.

```
1. Who sees it?
   └── Dream Master only → dc-dm-note        (ink label bar in cyan, white sheet, ink ring, cyan rail)
   └── Player-facing → continue ↓

2. What is it? (every callout is bolted: a bolt head in each top corner)
   └── A worked example              → dc-example-callout  (cyan rail and ring, taped-on label)
   └── Atmosphere / narrative voice  → dc-vibe-callout     (violet frame along its diagonals, violet chip, italic)
   └── Backstory, in second person   → dc-origin-callout   (torn edge, rust frame and rail, worn crimson stamp)
   └── A place, written up           → dc-location-callout (torn edge, teal frame and rail, worn teal stamp)
   └── A place, present tense        → dc-visit-callout    (wobbly signpost, fungi-green frame, rail and chip)
   └── Rules / mechanics             → continue ↓

3. How urgent?
   └── A rule with consequences   → dc-note.warning  (hazard-stripe rail, caution-tape label)
   └── Informational              → dc-note          (heavy blue rail, blue ring, blue chip)
```

Every one is a white sheet: the brackets name the rail, frame and label that tell them apart.

### Block Components (via `@block panel`, `slate`, `shard`)
- `.dc-block` — base block container
- `.dc-block.dc-panel` — data/rules panel (a `@block` register; the general card is `@section panel`)
- `.dc-block.dc-slate` — authority voice: ink body, blood band, a stamped Binding tag
- `.dc-block.dc-shard` — flavor/atmosphere: white paper, torn foot, no accent hue

### Sections
- `.dc-section-panel` — the card: cream substrate, accent rail, clipped corner, title bar
- `.dc-section-flat` — the rail on a plain host
- `.dc-section-reference`, `.dc-section-lore`, `.dc-section-dm`, `.dc-section-choose` — boxes that say what kind of text they hold (a look-up, the world, advice for the Dream Master, a choice), each by its own bar over a white sheet: a pale HUD band, a deep violet bar, an ink bar with a cyan rule, and for `choose` a form with no bar (`--paper-form`)
- `.dc-npc-stat`, `.dc-citizen-walkthrough` — panels that carry their own class
- `.dc-flaws`, `.dc-ideals`, `.dc-dreams` — `choose` sections of choice cards: blood with a cracked edge, HUD blue with a steady tablet, violet with a rising edge (the card reads `--dc-choice-*`)
- `.dc-kicker` — a section's last paragraph when it is only a bold run: it never opens a page alone
- `.dc-fiction-excerpt`, `.dc-card-grid` — section components that are not panels
- `.dc-avoid-split`, `.dc-snug` — modifiers

A bare `.section` has no rule. Chrome sits on a variant class; the section accent and background are `--dc-section-accent` and `--dc-section-bg`, and the panel's edge is `--dc-section-clip` and `--dc-section-rail`.

### Locations (page and chapter words)
- `.dc-page-chapter-start`, `.dc-page-intro`, `.dc-page-credits`, `.dc-page-contents`, `.dc-page-citizen-file`
- `.dc-chapter-rules`, `.dc-chapter-lore`, `.dc-chapter-citizen-file`, `.dc-chapter-specialty`

A location sets tokens on the components inside it and draws nothing of its own.

### Floats
- `.dc-sidebar` — float placement: a callout (`@callout note .dc-sidebar`) or a `.dc-human-callout` floated right

### Skill Cards
- `.dc-skill-card`
- `.dc-skill-card-cont` — card container
- `.dc-ability` / `.dc-ability-text`
- `.dc-ability-body` — wraps an ability's text and a nested list when the item has one
- `.dc-ability-title` — a cost row that is only a name (`**3 AP — Butcher Roach**`): the title of the paragraphs after it
- `.dc-card-subhead` — a paragraph whose whole content is one bold run: the card's pseudo-heading (a run-in `**Label:** text` is not one)
- `.dc-lead-in` — a paragraph or cost row whose text ends in a colon: it stays with the block after it
- `.dc-card-signoff` — the card's last paragraph when it is short (under 90 characters): it stays with the block above it
- `.dc-ap` — action point cost (`.free`, `.reduced`, `.increased`, `.var`, `.standard`, `.special`)
- `.dc-outcome-row` (`.hit`, `.miss`, `.crit`, `.fail`, `.mixed`)
- `.dc-outcomes` / `.dc-outcomes-label` / `.dc-outcome-key` / `.dc-outcome-text`

> These sub-elements are emitted by the plugin — authors do not write them directly:
> `dc-card-tab`, `dc-tab-title`, `dc-tab-tier`, `dc-card-body`, `dc-card-inner`

### Specialty System
- `.dc-specialty` + variant (`.augmerc`, `.proxy`, `.streetwarden`, `.gutterdruid`, `.cybersurgeon`, `.wirephreak`, `.technosorcerer`, `.etherlock`, `.dualist`, `.generalist`)
- `.dc-specialty-intro`
- `.dc-specialty-card` — individual specialty entry
- `.dc-specialty-art` — full-bleed art panel
- `.dc-path-shell` — learning path shell
- `.dc-path-block` / `.dc-learning-path.dc-path-block`
- `.dc-path-sticker` / `.dc-path-sep`
- `.dc-classtag` + specialty variant — class identity dots

### NPC / Stat Blocks

`.dc-npc-stat`: for narrative enemy/ally entries with flavor quotes and trait sections.
`.dc-stat-grid`: for compact at-a-glance numerical stat grids.
These are separate components — not variants of each other.

- `.dc-stat` / `.dc-stat-grid` / `.dc-stat-class`
- `.dc-stat-name`
- `.dc-npc-stat`

> These sub-elements are emitted by the plugin — authors do not write them directly:
> `dc-stat-cell`, `dc-stat-cell-key`, `dc-stat-cell-val`, `dc-stat-head`, `dc-stat-line`

### Typography Decorations
- `.dc-chevron` — deep-magenta chevron banner heading
- `.dc-spray` — stencil-tag heading: stepped overspray edge, dashed stencil line
- `.dc-sub-header`
- `.dc-pullquote`
- `.dc-intro` — lede: upright semibold ink type on a light panel, accent rail, ink foot rule
- `.dc-flavor` — italic flavor text with a rail and no box
- `.dc-tape` — a strip of masking tape: tan, torn ends, ink edges, ink label
- `.dc-sticker` / `.dc-sticker-ref` / `.dc-stickers`
- `.dc-definition-block` — a dictionary page for a term or a glossary run: cream, heavy rule over, headword first; `@definition lucid` (`.dc-definition-lucid`: light, machined chamfers, upright) and `@definition surreal` (`.dc-definition-surreal`: dark, skewed, torn, off-register) are the two roll states, set as opposites
- `.dc-steps` — the numbered instruction plate (`@procedure`): ink frame, hard shadow, HUD-blue number strip

### Gear
- `.dc-card.dc-entry` with `.dc-gear` (or `.dc-augment`, `.dc-treasure`, `.dc-vehicle`, `.dc-drug`) — `@gear [kind]`; each kind has its own silhouette, frame, badge and name colour on a white sheet: a hang tag, a spec chip, a gem, an industrial plate, a prescription label
- `.dc-field.dc-field-specs` — the SPECS box (`@field specs`, or a `**SPECS:**` paragraph in an entry)

### Layout Helpers
- `.dc-card-grid`
- `.dc-at-a-glance-card` (three across in `@columns 3`): a reversed label band over a big value
- `.dc-citizen-walkthrough` (two fields side by side in `@columns 2`)

Note: there are no `.dc-accent-X` utility classes. Retheme a chapter by setting the component tokens at its id (`#chapter-03 { --dc-section-accent: var(--rust); }`).

### Inline Markers
- `.dc-arrow`
- `.dc-tag` — an inline keyword chip (hard edge, ink hairline, mono caps)
- `.dc-roll-the-die`

### Images
- `.dc-img-float-left` / `.dc-img-float-right`

### TOC
- `.dc-toc` (a plain list inside it)

---

## Color Palette Pillars

Tokens are organized in layers. New projects override the pillar layer only where brand identity differs; everything else inherits automatically. Each colour's CMYK and total ink through the CGATS21_CRPC1 press profile is in its comment in `styles/dc-palette.css` / `dc-identity.css` and in [constitution §V](./constitution.md); `scripts/measure-palette-crpc1.py` measures them.

### Surface / Paper
| Token | Value | Role |
|---|---|---|
| `--bg` | `#c8c5bf` | Ash-concrete page background |
| `--concrete-pale` | `#dcdad5` | Pale concrete — cold-grey panels |
| `--paper-form` | `→ --paper-cream` | The `choose` form's sheet: white |
| `--paper-cream` | `#ffffff` | White, no ink — the text surface: every sheet that holds reading text |
| `--paper-zine` | `→ --concrete-pale` | The grey printed page — no package rule reads it (the fiction excerpt and shard block are white); kept for books |
| `--paper-light` | `→ --paper-cream` | White, no ink — secondary layered panel surface; the lede |
| `--paper-aged` | `→ --concrete-pale` | Label and chip grounds (field chips, `code`, outcome rows) |
| `--paper-stain` | `#b0a89c` | Deep stain — dark inset wells and label strips; never body text |

### Ink / Text
| Token | Value | Role |
|---|---|---|
| `--ink` | `#1e1d1c` | Near-black with red bias — body and all small text, hairlines |
| `--ink-dark` | `#2f2622` | Fills and heavy rules (not small text: four plates) |
| `--ink-smoke` | `#4d4339` | Mid-tone fills and rails |
| `--ink-dust` | `#665b4e` | Fallback rail; not a text colour |

### Industrial Warm (reds, oranges)
| Token | Value | Role |
|---|---|---|
| `--crimson` | `#e1261c` | PMS Red 032 — POD-safe signal red |
| `--blood` | `#901a12` | Oxidised arterial — primary accent |
| `--orange` | `#d4500a` | Burnt circuit-board |
| `--orange-deep` | `#a03808` | Deeper orange for small text on fill |
| `--rust` | `#b23a12` | Burnt rebar edge |
| `--amber` | `#7a5a20` | Sulfur-scorched brass |
| `--amber-dark` | `#5c3c10` | Charred amber |
| `--deep-rust` | `#70200e` | Shadow rust; public, no package rule reads it |

### Brand Cyber
| Token | Value | Role |
|---|---|---|
| `--brand-magenta` | `#cf217e` | Dimm.city signature magenta, pink and inside the press gamut |
| `--brand-magenta-deep` | `#690045` | Small-text-on-fill safe version |
| `--brand-cyan` | `#00bcd4` | Neon-cyan — signal/wire |
| `--brand-yellow` | `#ffd700` | Brand radiant gold |
| `--brand-violet` | `#662d87` | Cyber-violet — the world (lore, vibe, cabal); no specialty |
| `--signal-indigo` | `#396cb7` | Indigo — wirephreak accent |

### HUD / Interface
| Token | Value | Role |
|---|---|---|
| `--hud-blue` | `#1f6f94` | Teal-cyan mid HUD |
| `--hud-blue-dark` | `#14516e` | Deep teal — borders, H2 text |
| `--hud-blue-bright` | `→ --brand-cyan` | Neon accent alias (5 consumers) |
| `--hud-blue-dim` | `#7ab8d0` | Light cyan — the `reference` band and column heads, roll-table heads, dividers, the reduced AP chip; not a body fill |
| `--hud-magenta` | `→ --brand-magenta` | Brand-magenta alias (29 consumers) |
| `--hud-panel` | `→ --concrete-pale` | The default specialty-intro panel |

### Ecological / Organic
| Token | Value | Role |
|---|---|---|
| `--fungi-glow` | `#c8e040` | Bioluminescent yellow-green |
| `--fungi-rot` | `#30461e` | Deep moldering green — large fill only |

### Crystal / Mineral
| Token | Value | Role |
|---|---|---|
| `--crystal-amethyst` | `#905aa5` | Mineral violet — the amethyst chapter chip |
| `--crystal-slate` | `#52626f` | Cool slate stone — generalist accent |
| `--crystal-aqua` | `#4a98a8` | Pale crystalline aquamarine |

### Shadows & Utility
| Token | Value | Role |
|---|---|---|
| `--shadow-poster` | `2pt 3pt 0 var(--shadow-ink)` | Card drop shadow: a hard offset |
| `--shadow-ink` | `color-mix(in srgb, var(--ink) 28%, transparent)` | Translucent shadow colour, so the wall darkens under it (the source of `--shadow-poster`) |
| `--tint-magenta-rose` | `→ --brand-magenta` | Pullquote accent mix source |
| `--tint-hud-teal` | `→ --hud-blue` | Former mix source (alias) |

---

## Component Public Token Defaults

All component tokens live at `:root` so per-chapter overrides can use the cascade. Set these at chapter id scope in the book's own sheet (unlayered — it beats this package at any specificity) to retheme a section without touching component rules.

### Section (`.section`)
| Token | Default | Role |
|---|---|---|
| `--dc-section-bg` | `--paper-cream` | Section card background |
| `--dc-section-accent` | `--brand-magenta` | Section header accent strip |
| `--dc-section-surface` | `""` | `content` of the `::before` panel layer; `none` removes it |
| `--dc-section-shadow` | `""` | `content` of the `::after` shadow layer; `none` removes it |
| `--dc-section-pad-top` / `-bottom` | `--space-md` | Section padding; the header bar's negative margins follow it |
| `--dc-section-pad-right` / `-left` | `--space-lg` | Same, horizontal |

Variants and templates set these on their own rule (`.dc-section-flat`, the intro and credits pages). The tokens inherit, so do not nest a section inside a flat one.

### Alert / Callout (`.dc-alert`)
| Token | Default | Role |
|---|---|---|
| `--dc-alert-bg` | `--paper-cream` | The sheet: white in every register |
| `--dc-alert-border` | `--hud-blue-dark` | The accent: left rail, frame ring and label chip |
| `--dc-alert-fg` | `--ink` | Body text color |
| `--dc-alert-label-color` | `--paper-cream` | Label chip text (warning: ink on yellow; dm: cyan, `--hud-blue-bright`, on its ink bar) |
| `--dc-alert-border-width` | `8px` | Left-rail width (dm, origin, location, example 6px; vibe 4px; warning 14px) |
| `--dc-alert-label-size` | `10pt` (`--fs-floor`) | Label chip font size |
| `--dc-alert-frame` | `inset 0 0 0 2pt` in `--dc-alert-border` | An inset ring in the accent (warning and dm: ink; vibe, origin, location, visit: `none`, framed by the next token) |
| `--dc-alert-frame-width` | `3pt` | The frame of a callout whose frame follows its outline (vibe, origin, location, visit): the box is filled with the accent under a white copy of its silhouette, this far in from the top, right and foot; the rail is the left side |
| `--dc-alert-label-bg` / `-label-pad` | `--dc-alert-border` / `2px 9px` | The label's chip: the accent, with paper type (warning: yellow tape; dm: `--ink-dark`, the bar across its top; origin, location: paper, a stamp) |
| `--dc-alert-label-shadow` | `--dc-label-shadow` | The chip's raised edge (dm: `none`) |

### Lede (`.dc-intro`)
| Token | Default | Role |
|---|---|---|
| `--dc-intro-bg` | `--paper-cream` | The sheet (white, as every callout) |
| `--dc-intro-accent` | `--orange` | Rail and ring colour |
| `--dc-intro-color` | `--ink` | Type colour |
| `--dc-intro-size` | `--fs-h4` | Type size |
| `--dc-intro-weight` / `-style` | `600` / `normal` | Upright semibold |
| `--dc-intro-rail` / `-ring` | `8px` / `2pt` | Rail width and inset ring width, the callout's (a lede on paper sets the ring to 0) |
| `--dc-intro-shape` | `--dc-alert-shape` | The clip-path silhouette: the note's chamfers and chipped notch (`none` on paper) |

### Inline chips and tape (`.dc-tag`, `.dc-tape`, `.dc-spray`)
| Token | Default | Role |
|---|---|---|
| `--dc-tag-bg` / `-fg` / `-border` | `--paper-cream` / `--ink` / `--ink` | The keyword chip |
| `--dc-tape-bg` | 30% `--brand-yellow` in `--paper-aged` | Masking-tape fill |
| `--dc-tape-border` / `-color` | `--ink` / `--ink` | Tape edges and label |
| `--dc-tape-shape` | torn-end polygon | Tape clip-path |
| `--dc-spray-stencil` | `--ink-dark` | The dashed stencil line along a spray tag's foot |

### Choice Card, Faction, Entry (`.dc-card`, `.dc-faction`, `.dc-entry`)
| Token | Default | Role |
|---|---|---|
| `--dc-choice-accent` / `-surface` / `-tint` / `-kind` | `--ink-dark` / `--paper-cream` / `--paper-cream` / `none` | Rail, top band and title colour; sheet; the closing quote's ground (white in all three); the one-word chip. `@flaws`, `@ideals`, `@dreams` set the accent, the sheet and the chip |
| `--dc-choice-edge` / `-band` / `-rail` | `1.5pt solid --ink-dark` / `5px` / `6px` | The card's border and the weight of its top band and left rail (flaw: 2pt solid, 9px; dream: a 4pt double edge, 3px band) |
| `--dc-faction-surface` / `-band` / `-band-height` / `-title` | `--paper-cream` / HUD-blue band image / `8pt` / `--hud-blue-dark` | A faction's sheet, top band (an image: `linear-gradient(c, c)` for solid) and name colour; each kind sets all of them |
| `--dc-entry-radius` / `-ornament` / `-frame` | `0` / `none` / `none` | An entry kind's corner radius, ornament layer (the vehicle's inner seam) and inset keyline |
| `--dc-entry-badge-bg` / `-fg` / `-shape` / `-radius` | `--ink-dark` / `--paper-cream` / `none` / `0` | The kind badge over the name |
| `--dc-field-edge-width` / `-edge-style` | `0px` / `solid` | The frame on a field's other three sides (effects solid, side effects dashed) |

### Procedure, At-a-glance, Definition, Outcome
| Token | Default | Role |
|---|---|---|
| `--dc-steps-accent` / `-surface` | `--hud-blue-dark` / `--paper-cream` | Number strip; plate |
| `--dc-at-a-glance-accent` / `-value` | `--hud-blue-dark` / `--ink` | Tile frame and label band; the value |
| `--dc-definition-block-accent` / `-accent-width` / `-surface` / `-shape` | `--hud-blue-dark` / `3pt` / `--paper-cream` / `none` | The rules; the rule over the block; page; clip |
| `--dc-definition-block-term` / `-fg` / `-style` / `-frame` / `-rule-bottom` / `-pad` | `--hud-blue-dark` / `--ink` / `italic` / `--shadow-poster` / `1pt` / `8pt 12pt 9pt` | Headword colour; body colour; body style; box-shadow (the hard shadow, or an inset frame); the rule under; padding. `lucid` and `surreal` set them |
| `--dc-outcome-key-col` | `max(130px, 26%)` | Outcome ladder chip column |
| `--dc-fiction-bg` / `-cavity` | `--paper-cream` / `--ink-smoke` | The fiction excerpt's page (white); the broken wall's face round the hole |
| `--dc-fiction-title-size` | `--fs-h2` | The excerpt's `#` title: a story's name, a step under a chapter's |
| `--dc-fiction-hole` / `-shape` | generated polygons | The hole and the page (the hole shrunk by the face), from `scripts/fiction-break.py` |
| `--dc-fiction-line-height` | `1.45` | The fiction excerpt's leading |

### Skill Card (`.dc-skill-card`)
| Token | Default | Role |
|---|---|---|
| `--dc-card-accent` | `--ink` | Default accent (no specialty) |
| `--dc-card-surface` | `--paper-cream` | Card body background |
| `--dc-card-tab-bg` | `--ink-dark` | Tab strip background |
| `--dc-card-tab-title-color` | `--paper-cream` | Tab title text |
| `--dc-bolt` / `-bolt-face` / `-bolt-size` | `--ink` / `--paper-stain` / `10px` | The bolt head on a skill card's top right and bottom left, a callout's two top corners and a `##` slip (the slip's `--dc-page-slip-bolt*` default to these): ring and slot, face, diameter |
| `--dc-skill-foot-bolt-left` / `-bottom` | `4px` / `4px` | Where the card's bottom-left bolt sits, from the left edge and the foot; each specialty sets its own beside its body shape so the bolt clears the foot's cut |
| `--dc-tier-bg` / `-fg` / `-edge` | `--ink-dark` / `--paper-cream` / `--paper-cream` | The tier pill on the tab; each specialty sets its own chip |

### Specialty Intro (`.dc-specialty-intro`)
| Token | Default | Role |
|---|---|---|
| `--dc-specialty-intro-title-bg` | `--hud-magenta` | Title bar background |
| `--dc-specialty-intro-title-color` | `--paper-cream` | Title bar text |
| `--dc-specialty-intro-bg` | `--hud-panel` | Panel background |
| `--dc-specialty-intro-h3-color` | `--blood` | `###` heading text and its underline; each specialty sets its `--spec-ink` |
| `--dc-band-rule` / `-rule-h` / `-rule-art` | `--hud-magenta` / `3px` / `none` | The rule under the band: colour, height, hard-edged pattern |
| `--dc-band-facet` / `-facet-width` / `-facet-clip` | `transparent` / `32%` / polygon | A flat plane at the band's right (magic facet, landfill patch) |
| `--dc-band-rim` | `none` | An inset top highlight (tech bands only) |
| `--dc-band-reg` | `none` | A box-shadow on the rule: a second ink printed 2px off, a misregistered line (tech bands only) |

### Learning Path Shell (`.dc-path-shell`)
| Token | Default | Role |
|---|---|---|
| `--dc-path-title-bg` | `--hud-magenta` | Path header background |
| `--dc-path-title-color` | `--paper-cream` | Path header text |
| `--dc-path-accent` | `--hud-magenta` | Path accent color |
| `--dc-path-code-bg` / `-code-fg` | `--paper-cream` / `--hud-blue-dark` | The path's code chip |
| `--dc-path-chip-bg` / `-chip-fg` / `-chip-edge` | `--ink-dark` / `--paper-cream` / `--hud-blue-dark` | The sticker chain |
| `--dc-path-note-rail` | `--orange` | The subtitle's rail |

### Specialty Card (`.dc-specialty-card`)
| Token | Default | Role |
|---|---|---|
| `--dc-specialty-card-bg` | `--paper-cream` | Card background |
| `--dc-specialty-card-accent` | `--crimson` | Card accent |
| `--dc-specialty-card-fg` | `--ink` | Card text |
| `--dc-specialty-card-media-height` | `0.85in` | Portrait image height |
| `--dc-specialty-card-media-width` | `0.75in` | Portrait image width |
| `--dc-specialty-card-title-align` | `right` | Name heading alignment |
| `--dc-specialty-card-band-bg` | the accent | Name band fill (in a specialty: its banner colour) |
| `--dc-specialty-card-band-fg` | `--paper-cream` | Type on the name band |
| `--dc-specialty-card-band-shape` | `none` | Name band clip (in a specialty: its banner cut) |
| `--dc-specialty-card-shell-shape` | a chamfer | The sheet's silhouette (in a specialty: its banner's) |
| `--dc-specialty-card-pad-x` | `0.18in` | The sheet's side padding (the band bleeds out over it) |

### Block (`.dc-block`)
| Token | Default | Role |
|---|---|---|
| `--dc-block-bg` | `--paper-light` | Block background |
| `--dc-block-fg` | `--ink` | Block text |
| `--dc-block-accent` | `--hud-blue-dark` | Block accent |
| `--dc-block-title-bg` | `--hud-blue-dark` | Title bar background |
| `--dc-block-title-fg` | `--paper-cream` | Title bar text |
| `--dc-block-title-rule` | `none` | A whole `border-bottom` value under the band (slate: 3pt crimson; shard: 2pt solid) |
| `--dc-block-tag` | `none` | A quoted word stamped on the band's right end (slate: "Binding") |
| `--dc-block-tag-edge` | `1.5pt solid --paper-cream` | The tag's border (slate: `3pt double`, a worn stamp) |

### Page text (free-standing headings and prose)
| Token | Default | Role |
|---|---|---|
| `--dc-page-slip-bg` / `-ink` / `-edge` / `-shadow` | `--paper-cream` / `--ink` / `--ink` / `--shadow-poster` | A heading slip's paper, type, ink edge and dashed foot, and hard shadow |
| `--dc-page-slip-bolt` / `-bolt-face` / `-bolt-size` | `--dc-bolt` / `--dc-bolt-face` / `--dc-bolt-size` | The two slotted bolt heads in a `##` slip's top corners: ring and slot, face, diameter. Set one to change the slips only |
| `--dc-page-slip-gap` | `--space-xl` | The space above a slip |
| `--dc-page-slip-foot` | `6pt` | The space below a slip, the same whatever follows it |
| `--dc-page-sheet-pad` | `0.18in` | The side padding of the prose sheet |
| `--dc-page-title-ink` | `--paper-cream` | Type on the page-title banner |


### Rules, page foot and the choose form
| Token | Default | Role |
|---|---|---|
| `--dc-rule` | `--ink` | The colour of the `---` hairline; a skill card sets it to the specialty's mid (the seam between sub-abilities) |
| `--chip-gap` | `0.10in` | The chips' tops below the text block: a full page ends this far above the folio chip |
| `--lh-display` | `1.35` | Heading leading. Not tighter: lixdu's capitals fill the whole em, so at 1.2 two lines of a wrapped heading sit 2pt apart |
| `--dc-choose-stamp-room` | `0px` | The CHOOSE stamp's width reserved on the first block's first lines (a form that opens a page) |
| `--dc-choose-stamp-top` | `0px` | Where the stamp's top edge sits: 0 is on the form's top edge |
| `--dc-choose-stamp-lift` | `-50%` | How far the stamp is lifted over that edge: half its height |

---

## Dimm City Specialty Identity Tokens

Project-specific. A different project using this component library replaces this block with its own identity tokens; the pillar palette and component defaults above remain untouched.

### Specialty Accents
Every specialty also sets `--spec-band` (the title-band fill: the accent, except Proxy's `--brand-magenta-deep`), `--spec-on-band` (ink or cream, at least 4.5:1 on the band) and the tier chip `--spec-chip-bg`, `-fg` and `-edge`.

| Specialty | Accent | Mid | Dark |
|---|---|---|---|
| Augmerc | `--brand-cyan` (`#00bcd4`) | `#006878` | `#003a40` |
| Technosorcerer | `--orange` (`#d4500a`) | `#7a3008` | `#4c290f` |
| Streetwarden | `#4db840` | `#347828` | `→ --fungi-rot` (`#30461e`) |
| Gutterdruid | `--fungi-glow` (`#c8e040`) | `#4d6020` | `→ --fungi-rot` (`#30461e`) |
| Cybersurgeon | `#a8b4b8` | `→ --crystal-slate` (`#52626f`) | `#303840` |
| Wirephreak | `--signal-indigo` (`#396cb7`) | `#093c81` | `#181b45` |
| Proxy | `--brand-magenta` (`#cf217e`) | `#9c0f63` | `→ --brand-magenta-deep` (`#690045`) |
| Etherlock | `--brand-yellow` (`#ffd700`) | `#8a6a00` | `#46360c` |
| Dualist | `--crystal-aqua` (`#4a98a8`) | `→ --augmerc-mid` (`#006878`) | `→ --augmerc-dark` (`#003a40`) |
| Generalist | `--crystal-slate` (`#52626f`) | `#3a4854` | `#212a32` |

