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
| `> [!NOTE]` | GFM alert | `.dc-note` |
| `> [!WARNING]` | GFM alert | `.dc-note.warning` |

---

## Supported Components

### Callouts & Notes
- `.dc-alert` — warning/info callout block
- `.dc-alert-label` — label chip on alerts
- `.dc-note` / `.dc-note.warning`
- `.dc-vibe-callout`, `.dc-human-callout`, `.dc-origin-callout`
- `.dc-dm-note`
- `.dc-prose-panel`

#### Callout Decision Tree

Use this to choose the right callout type before reaching for a class name.

```
1. Who sees it?
   └── GM only → dc-dm-note
   └── Player-facing → continue ↓

2. What register?
   └── Atmosphere / narrative → dc-vibe-callout
   └── World / setting lore  → dc-origin-callout
   └── Rules / mechanics     → continue ↓

3. How urgent?
   └── Caution / warning          → dc-note.warning
   └── Informational              → dc-note
   └── General rules callout      → dc-alert
```

### Block Components (via `@block panel`, `slate`, `shard`)
- `.dc-block` — base block container
- `.dc-block.dc-panel` — data/rules panel (a `@block` register; the general card is `@section panel`)
- `.dc-block.dc-slate` — authority/authority-voice
- `.dc-block.dc-shard` — flavor/atmosphere

### Sections
- `.dc-section-panel` — the card: cream substrate, accent rail, clipped corner, title bar
- `.dc-section-flat` — the rail on a plain host
- `.dc-section-reference`, `.dc-section-lore`, `.dc-section-dm`, `.dc-section-choose` — panels that say what kind of text they hold (a look-up, the world, advice for the Dream Master, a choice)
- `.dc-npc-stat`, `.dc-citizen-walkthrough`, `.dc-flaws`, `.dc-ideals`, `.dc-dreams` — panels that carry their own class
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
- `.dc-skill-card` / `.dc-skill-card.dc-highlight`
- `.dc-skill-card-cont` — card container
- `.dc-ability` / `.dc-ability-text`
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
- `.dc-chevron` — chevron banner heading
- `.dc-spray` — spray-paint heading style
- `.dc-sub-header`
- `.dc-pullquote`
- `.dc-intro` — lede/intro text panel
- `.dc-flavor` — italic flavor text
- `.dc-tape` — adhesive tape label
- `.dc-sticker` / `.dc-sticker-ref` / `.dc-stickers`
- `.dc-definition-block` — a term, a glossary run, or a boxed note with a divider
- `.dc-steps`

### Gear
- `.dc-card.dc-entry` with `.dc-gear` (or `.dc-augment`, `.dc-treasure`, `.dc-vehicle`, `.dc-drug`) — `@gear [kind]`
- `.dc-field.dc-field-specs` — the SPECS box (`@field specs`, or a `**SPECS:**` paragraph in an entry)

### Layout Helpers
- `.dc-card-grid`
- `.dc-at-a-glance-card` (three across in `@columns 3`)
- `.dc-citizen-walkthrough` (two fields side by side in `@columns 2`)

Note: there are no `.dc-accent-X` utility classes. Retheme a chapter by setting the component tokens at its id (`#chapter-03 { --dc-section-accent: var(--rust); }`).

### Inline Markers
- `.dc-arrow`
- `.dc-tag`
- `.dc-roll-the-die`

### Images
- `.dc-img-float-left` / `.dc-img-float-right`

### TOC
- `.dc-toc` (a plain list inside it)

---

## Color Palette Pillars

Tokens are organized in layers. New projects override the pillar layer only where brand identity differs; everything else inherits automatically.

### Surface / Paper
| Token | Value | Role |
|---|---|---|
| `--bg` | `#c8c5bf` | Ash-concrete page background |
| `--concrete-pale` | `#dcdad5` | Pale concrete — cold-grey panels |
| `--paper-cream` | `#f0eee9` | Light flyer-stock — primary text surface |
| `--paper-light` | `#e2ded7` | Secondary layered panel surface |
| `--paper-aged` | `#c8c2b8` | Weathered grey — decay register |
| `--paper-stain` | `#b0a89c` | Deep stain — dark inset wells |

### Ink / Text
| Token | Value | Role |
|---|---|---|
| `--ink` | `#1a1512` | Near-black with red bias |
| `--ink-dark` | `#2b231d` | Secondary heading weight |
| `--ink-smoke` | `#4d4339` | Body emphasis mid-tone |
| `--ink-dust` | `#665b4e` | Muted body/captions |

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
| `--deep-rust` | `#6a1a08` | Shadow rust |

### Brand Cyber
| Token | Value | Role |
|---|---|---|
| `--brand-magenta` | `#c026d3` | Dimm.city signature cyber-magenta |
| `--brand-magenta-deep` | `#8a0a9a` | Small-text-on-fill safe version |
| `--brand-cyan` | `#00bcd4` | Neon-cyan — signal/wire |
| `--brand-yellow` | `#ffd700` | Brand radiant gold |
| `--brand-violet` | `#7030b8` | Cyber-violet — ritual+tech |

### HUD / Interface
| Token | Value | Role |
|---|---|---|
| `--hud-blue` | `#1f6f94` | Teal-cyan mid HUD |
| `--hud-blue-dark` | `#14516e` | Deep teal — borders, H2 text |
| `--hud-blue-bright` | `→ --brand-cyan` | Neon accent alias (5 consumers) |
| `--hud-blue-dim` | `#7ab8d0` | Visible cream panel tint |
| `--hud-magenta` | `→ --brand-magenta` | Brand-magenta alias (29 consumers) |
| `--hud-panel` | `#eeece8` | Neutral cream — callouts, note bars |

### Ecological / Organic
| Token | Value | Role |
|---|---|---|
| `--fungi-glow` | `#c8e040` | Bioluminescent yellow-green |
| `--fungi-rot` | `#2a4015` | Deep moldering green — large fill only |

### Crystal / Mineral
| Token | Value | Role |
|---|---|---|
| `--crystal-amethyst` | `#6a3a8a` | Deep mineral violet |
| `--crystal-aqua` | `#4a98a8` | Pale crystalline aquamarine |

### Shadows & Utility
| Token | Value | Role |
|---|---|---|
| `--shadow-poster` | `2pt 3pt 0 var(--shadow-ink)` | Card drop shadow: a hard offset |
| `--shadow-ink` | `color-mix(in srgb, #000 28%, transparent)` | Translucent shadow colour, so the wall darkens under it (the source of `--shadow-poster`) |
| `--tint-magenta-rose` | `#e6007a` | Pullquote accent / paper-stain rule mix source |
| `--tint-hud-teal` | `#2a6a8a` | Inset-sidebar callout mix source |
| `--tint-signal-red` | `#d41200` | Tape border mix source |
| `--tint-brick-red` | `#b42828` | Skill-card header wash mix source |

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
| `--dc-alert-bg` | `--hud-blue-dim` | Panel background |
| `--dc-alert-border` | `--hud-blue-dark` | Left-rail border color |
| `--dc-alert-fg` | `--ink` | Body text color |
| `--dc-alert-label-color` | `--ink-dark` | Label chip text |
| `--dc-alert-border-width` | `4px` | Left-rail width |
| `--dc-alert-label-size` | `8pt` | Label chip font size |

### Skill Card (`.dc-skill-card`)
| Token | Default | Role |
|---|---|---|
| `--dc-card-accent` | `--ink` | Default accent (no specialty) |
| `--dc-card-surface` | `--paper-cream` | Card body background |
| `--dc-card-tab-bg` | `--ink-dark` | Tab strip background |
| `--dc-card-tab-title-color` | `--paper-cream` | Tab title text |
| `--dc-card-body-mark` | `--crimson` | Body accent mark |

### Specialty Intro (`.dc-specialty-intro`)
| Token | Default | Role |
|---|---|---|
| `--dc-specialty-intro-title-bg` | `--hud-magenta` | Title bar background |
| `--dc-specialty-intro-title-color` | `--bg` | Title bar text |
| `--dc-specialty-intro-bg` | `--hud-panel` | Panel background |

### Learning Path Shell (`.dc-path-shell`)
| Token | Default | Role |
|---|---|---|
| `--dc-path-title-bg` | `--hud-magenta` | Path header background |
| `--dc-path-title-color` | `--paper-cream` | Path header text |
| `--dc-path-accent` | `--hud-magenta` | Path accent color |

### Specialty Card (`.dc-specialty-card`)
| Token | Default | Role |
|---|---|---|
| `--dc-specialty-card-bg` | `--paper-cream` | Card background |
| `--dc-specialty-card-border` | `--hud-blue` | Card border color |
| `--dc-specialty-card-accent` | `--crimson` | Card accent |
| `--dc-specialty-card-fg` | `--ink` | Card text |
| `--dc-specialty-card-media-height` | `0.85in` | Portrait image height |
| `--dc-specialty-card-media-width` | `0.75in` | Portrait image width |
| `--dc-specialty-card-title-align` | `right` | Name heading alignment |
| `--dc-specialty-card-band-height` | `16pt` | Accent band height |

### Block (`.dc-block`)
| Token | Default | Role |
|---|---|---|
| `--dc-block-bg` | `--paper-light` | Block background |
| `--dc-block-fg` | `--ink` | Block text |
| `--dc-block-accent` | `--hud-blue-dark` | Block accent |
| `--dc-block-title-bg` | `--hud-blue-dark` | Title bar background |
| `--dc-block-title-fg` | `--paper-cream` | Title bar text |

---

## Dimm City Specialty Identity Tokens

Project-specific. A different project using this component library replaces this block with its own identity tokens; the pillar palette and component defaults above remain untouched.

### Specialty Accents
| Specialty | Accent | Mid | Dark |
|---|---|---|---|
| Augmerc | `--brand-magenta` (`#c026d3`) | `#9a1896` | `#8a1a90` |
| Proxy | `--orange` (`#d4500a`) | `#7a3008` | `#3d1a00` |
| Streetwarden | `#4db840` | `#347828` | `#1a3d10` |
| Gutterdruid | `--fungi-glow` (`#c8e040`) | `#4d6020` | `#2a3408` |
| Cybersurgeon | `#a8b4b8` | `#606870` | `#303840` |
| Wirephreak | `--brand-cyan` (`#00bcd4`) | `#006878` | `#003a40` |
| Technosorcerer | `--brand-violet` (`#7030b8`) | `#4a1878` | `#200a38` |
| Etherlock | `--brand-yellow` (`#ffd700`) | `#8a6a00` | `#3d3000` |
| Dualist | `--crystal-aqua` (`#4a98a8`) | `#2a6878` | `#143a4a` |
| Generalist | `--crystal-amethyst` (`#6a3a8a`) | `#503070` | `#1e0e2e` |

### Tier Badges
| Token | Value | Role |
|---|---|---|
| `--tier-bronze` | `#8a5c28` | Tier 1 — salvage |
| `--tier-gold` | `#b8921a` | Tier 2 — tarnished brass |
| `--tier-silver` | `#a8b4b8` | Tier 3 — cyan-tinged chrome |
