@chapter #ch-components .dg-guide ch="1"

# Components

@lede

The full Dimm City component catalog, organized by role: prose & typography, alerts & callouts, block enclosures, sidebars, tables, the specialty system, gear/stat blocks, and dividers & reference. Base prose and callout components work in all chapter types without a specialty or learning-path wrapper; the DC-specific chrome (ability cards, banners, stat blocks, path chains) gives the Field Guide its look.

@end-lede

> **Cross-references:** Marker grammar (open/close semantics, worked examples for `@skill`, `@continue`, `@learning-path`, `@procedure`, `@sidebar`, `@sidebar-box`, `@definition`) and the authoritative alert type → class → label table live in `07-markdown-reference.md`. The exhaustive class inventory and the macro → emitted-class cross-reference live in `https://github.com/dimm-city/gp-dimm-city/blob/main/docs/components-and-palette-reference.md`. This chapter is the authored-component catalog — it describes each component's visual role and authoring path; it does not restate marker grammar or the full class list.

---

# 1. Prose & Typography

Base prose and heading components. Standard markdown elements inherit the DC type scale automatically; banners and headers add the spray-paint and chevron chrome.

---

## Body Prose

Default text style for all narrative and rules content. Standard markdown paragraphs automatically inherit the DC type scale, leading, and color — no class or wrapper required.

```markdown
When an enemy falters, you may trigger one of the following counters.
**Backbiters** are simply part of what makes an Augmerc dangerous.
```

---

## Intro Lede

Slightly larger opening paragraph at the top of a chapter or major section. **Syntax** — `@lede` … `@end-lede` → `.dc-intro`

```markdown
@lede
An Augmerc is muscle for hire. Street thugs, corporate bodyguards,
deniable enforcers — the difference is gear, grafts, and how much
of them is still original.
@end-lede
```

---

## Flavor Text

Italic in-world voice for card flavor and atmospheric lines. Inside `@skill` cards the `>` blockquote line is auto-styled; for standalone flavor paragraphs use `> [!FLAVOR]` → `.dc-alert.dc-flavor`.

```markdown
> [!FLAVOR]
> See an opening, ya take it. Best time to hit 'em is when they think it's over.
```

---

## Pull Quote

Large-format excerpt with accent rules above and below. Use sparingly — one per chapter. **Syntax** — `> [!PULLQUOTE]` → `.dc-pullquote.dc-flush`

```markdown
> [!PULLQUOTE]
> The rig braces and answers every swing.
>
> Field manual, second draft
```

> [!PULLQUOTE]
> The rig braces and answers every swing.
>
> Field manual, second draft

---

## Blockquote

Epigraphs and attributed in-world text with accent-alt left border and italic body. **Syntax** — standard markdown `>` blockquote

```markdown
> Every city has a language. Dimm City's is neon, static, and the sound
> of someone's implants glitching at 3am.
>
> — Hollis Vance, *Street Anthropology Vol. 4*
```

---

## Code Blocks

Fenced code blocks with orange left border, cream background, and Tomorrow monospace. **Syntax** — triple-backtick fenced block with optional language hint

````markdown
```css
.dc-note {
  border-left: 3pt solid var(--color-accent);
}
```
````

---

## Banners & Headers

@section .gp-columns-2 .dc-column-panel

| Element | Syntax | Role |
|---|---|---|
| Chevron Banner | `# Title {.dc-chevron}` | Primary H1 opener — once per chapter, replaces plain `#` |
| Spray Banner | `## Title {.dc-spray}` | H2 opener for learning paths and major topic breaks |
| Spec Tweak Rule | `### Title {.dc-spec-tweak .dc-no-top}` | H3 for optional mechanics; `.dc-no-top` removes top margin |

```
# Augmerc {.dc-chevron}
## Biting Distance {.dc-spray}
### Spec Tweak: Wired to Kill {.dc-spec-tweak .dc-no-top}
```

@end-section

---

# 2. Alerts & Callouts

`.dc-alert` is the alert shell. `dc-note`, `dc-vibe-callout`, `dc-origin-callout`, `dc-visit-callout`, `dc-gear-callout`, and `dc-dm-note` are thin variants layered on top of that shell, overriding only the properties that actually change.

### Callout Decision Tree

Use this to choose the right callout type before reaching for a class name.

```
1. Who sees it?
   └── GM only → dc-dm-note
   └── Player-facing → continue ↓

2. What register?
   └── Atmosphere / narrative → dc-vibe-callout
   └── World / setting lore  → dc-origin-callout
   └── Gear & equipment      → dc-gear-callout
   └── Rules / mechanics     → continue ↓

3. How urgent?
   └── Caution / warning          → dc-note.warning
   └── Informational              → dc-note
   └── General rules callout      → dc-alert
```

> **Choosing `@callout` vs `> [!NOTE]`:** the authoritative guidance on when to use the inline GFM alert form versus the multi-paragraph `@callout` block, and the canonical alert type → class → label mapping, live in `07-markdown-reference.md`. Reference that table rather than duplicating it here.

---

## Note

Boxed rules clarification with a labeled header and left-border accent. **Syntax** — `> [!NOTE]` → `.dc-note`

```markdown
> [!NOTE]
> Free counters trigger only once per round. Pick the one that hurts most.
```

> [!NOTE]
> Free counters trigger only once per round. Pick the one that hurts most.

---

## Warning

High-visibility callout in amber for rules with critical consequences. **Syntax** — `> [!WARNING]` → `.dc-note.warning`

```markdown
> [!WARNING]
> Trauma Patches stabilize a dying character but do not restore HP. A character
> at 0 HP with a Patch applied is still incapacitated.
```

> [!WARNING]
> Trauma Patches stabilize a dying character but do not restore HP. A character
> at 0 HP with a Patch applied is still incapacitated.

---

## Vibe Callout

Full-width atmospheric block for in-world voice at the top of a chapter or faction entry. **Syntax** — `> [!VIBE]` → `.dc-vibe-callout`

```markdown
> [!VIBE]
> The Gutterdruid doesn't fight because they have to — they fight because
> something feral in them still remembers what it felt like to be free.
```

> [!VIBE]
> The Gutterdruid doesn't fight because they have to — they fight because
> something feral in them still remembers what it felt like to be free.

---

## Origin Callout

Second-person backstory block addressing the reader as their character. **Syntax** — `> [!ORIGIN]` → `.dc-origin-callout`

```markdown
> [!ORIGIN]
> You didn't choose the street — the street chose you. Before the grafts,
> before the crew, there was just hunger and the particular talent for
> surviving what should have killed you.
```

> [!ORIGIN]
> You didn't choose the street — the street chose you. Before the grafts,
> before the crew, there was just hunger and the particular talent for
> surviving what should have killed you.

---

## Visit Callout

In-world location description in present tense, placed before encounter content. **Syntax** — `> [!VISIT]` → `.dc-visit-callout`

```markdown
> [!VISIT]
> The Neon Bazaar doesn't close. Day shift workers and third-shift scavengers
> brush shoulders between stalls selling augment cartridges, black-market
> permits, and fried synthetic crab.
```

> [!VISIT]
> The Neon Bazaar doesn't close. Day shift workers and third-shift scavengers
> brush shoulders between stalls selling augment cartridges, black-market
> permits, and fried synthetic crab.

---

## Gear Callout

Named equipment block for weapons, armor, and notable items. **Syntax** — `> [!GEAR]` → `.dc-gear-callout`

```markdown
> [!GEAR]
> **Ripper Blades (Mk II)**
>
> Melee. Damage 1d8+STR. *Serrated:* on a critical hit, the target bleeds
> for 1d4 damage at the start of their next turn.
```

> [!GEAR]
> **Ripper Blades (Mk II)**
>
> Melee. Damage 1d8+STR. *Serrated:* on a critical hit, the target bleeds
> for 1d4 damage at the start of their next turn.

---

## Dream Master Note

Dream Master–addressed instruction block for GM guidance and scene hooks, visually distinct from player-facing notes. **Syntax** — `> [!DM]` → `.dc-dm-note`

```markdown
> [!DM]
> If a player hasn't chosen their starting gear by the end of session zero,
> hand them a Scavenger Pack and move on.
```

> [!DM]
> If a player hasn't chosen their starting gear by the end of session zero,
> hand them a Scavenger Pack and move on.

---

## Block Callout Macros

Multi-paragraph versions of GFM alert types. Use `@callout variant="…"` when the note needs multiple paragraphs, lists, or nested content. **Syntax** — `@callout variant="note|warning|dm|vibe|origin|visit|gear"` → `.dc-alert` + variant

```markdown
@callout variant="warning"
**Trauma Patches** stabilize a dying character but do not restore HP.

A character at 0 HP with a Patch applied is still incapacitated. Apply Injury
Track consequences at the end of the scene, not immediately.
@end-callout
```

@callout variant="warning"

**Trauma Patches** stabilize a dying character but do not restore HP.

A character at 0 HP with a Patch applied is still incapacitated. Apply Injury Track consequences at the end of the scene, not immediately.

@end-callout

---

## DM Note block

`@dm-note` is the block form of `> [!DM]` → `.dc-dm-note`.

```markdown
@dm-note label="Scene Hook"
The contact doesn't know the job is a setup.

If players investigate further before accepting, they can discover the trap with a
Streetwise roll DC 14.
@end-dm-note
```

@dm-note label="Scene Hook"

The contact doesn't know the job is a setup.

If players investigate further before accepting, they can discover the trap with a Streetwise roll DC 14.

@end-dm-note

---

## Callout Class Names — Field Guide vs Design Guide

Use the design-guide forms documented in this chapter: `.dc-alert` is the alert shell, and dc-prefixed variants such as `.dc-vibe-callout`, `.dc-origin-callout`, `.dc-gear-callout`, and `.dc-dm-note` layer on top of it. Avoid unprefixed legacy callout names in new guide examples. If a field-guide page still needs book-specific treatment such as a forced full-height gear box, add that as a book-level rule rather than switching back to a legacy class.

```markdown
> [!GEAR]
> **Ripper Blades (Mk II)**
>
> Melee. Damage 1d8+STR.
```

> **Class-inventory note (docs-only):** `.dc-alert-label` (alert label chip) and `.dc-callout` (generic callout) exist in the CSS inventory but have no dedicated authored component section. They are listed in the consolidated quick-reference at the end of this chapter.

---

# 3. Block Variants (dc-block family)

Four reusable card-like enclosures for text content sections. Each variant has a distinct clip-path geometry, surface color, and accent that signals a different content register. `.dc-block` is the base container; `.dc-panel`, `.dc-slate`, `.dc-shard`, and `.dc-codex` are variants layered on top.

@section .gp-columns-2 .dc-column-panel

@block .dc-panel label="Panel — HUD Tactical"

Structured data, mission briefings, system documentation. Left accent strip in dark teal. Hex corner cuts. Title band has diagonal right cut.

Use for player-facing rules summaries and structured information blocks.

@end-block

@block .dc-slate label="Slate — Dark Authority"

Key rules, Dream Master directives, critical definitions. Dark near-black surface with magenta title band. Top-left step cut.

Use for authoritative rulings and high-importance content.

@end-block

@block .dc-shard label="Shard — Zine Cut"

Flavor, atmosphere, setting detail, narrative asides. Warm aged-paper surface, rust title band. Aggressive bottom-right diagonal slash.

Use for fiction, vibe, and atmospheric content blocks.

@end-block

@block .dc-codex label="Codex — Reference"

Tables, compendium entries, rules lookups. Pale cyan surface. Symmetric octagon corner cuts. Clean data-register aesthetic.

Use for reference tables and encyclopedia-style entries.

@end-block

@end-section

### Block Authoring Syntax

All four variants use the unified `@block` macro with class syntax:

```
@block .dc-panel label="Title"
Content here (any markdown)...
@end-block

@block .dc-codex label="Custom Title"
Also works with any of the four variants.
@end-block
```

The `label` attribute is optional — omit it to render without a title band.

---

# 4. Sidebars & Panels

`.dc-prose-panel` is the small shared shell for compact prose boxes in this family. `.dc-definition-block` and `.dc-sidebar-box` are thin concrete variants layered on top of it. `.dc-sidebar` and `.dc-human-callout` remain separate components with their own layout/content rules.

@section .gp-columns-2 .dc-column-panel

## Sidebar

Floated reference panel. **Syntax** — `@sidebar` … `@end-sidebar` → `.dc-sidebar` (add `.inset` for the inset variant → `.dc-sidebar.inset`). Marker open/close semantics are documented in `07-markdown-reference.md`.

## Definitions & Glossaries

**Preferred — standard markdown definition lists.** Definitions and glossaries use the standard PHP-Markdown-Extra / Pandoc **definition-list** syntax: a `Term` line, then a `: definition` line. It renders on-brand (orange-tint substrate + HUD-blue rail + bold terms) via the base `dl/dt/dd` rules in `dc-core.css` — no class or macro required. **Use:** term glossaries, NPC type summaries, item category descriptions, ability class definitions.

```markdown
Tick / Tic
: A very short, indefinite period of time.

Reach
: Close enough to touch. Adjacent.
```

**Legacy — `@definition` macro.** The styled-panel macro below still works but is **superseded** by the deflist syntax above (the raw-HTML `.dc-terms` glossary is likewise legacy). Migrate opportunistically. It emits `.dc-prose-panel.dc-definition-block` — a 1–3 sentence italic callout, warm-cream background + red left border.

```markdown
@definition
Augmercs are muscle for hire. Street enforcers, deniable contractors,
close-combat specialists — the difference is gear, grafts, and how much
of them is still original flesh.
@end-definition
```

@end-section

## Sidebar Box

Callout with H4 heading + internal dashed divider + cream background. **Syntax** — `@sidebar-box` … `@end-sidebar-box` → `.dc-prose-panel.dc-sidebar-box`. **Use:** rules etiquette, standalone reference blocks, any callout needing its own visual boundary. (Distinct from `dc-note` — no heading; `dc-pullquote` — decorative only.) H4 at top, then `---`, then body:

```markdown
@sidebar-box
#### Dice Etiquette

---

Roll your dice in the open. Both players should be able to see every
roll clearly — hidden dice undermine the shared fiction. If a die
lands off the table, reroll it.
@end-sidebar-box
```

## Human Callout (NPC Sidebar)

Compact NPC stat block inside a `.dc-sidebar` float. **Syntax** — raw HTML `.dc-sidebar > .dc-human-callout`

```html
<div class="dc-sidebar">
  <div class="dc-human-callout">
    <p><strong>Rennick "Two-Tab" Farrow</strong></p>
    <p>Fixer. HP 8 | DEF 11 | Intimidate +4.</p>
  </div>
</div>
```

---

# 5. Tables

## Table

Standard markdown tables receive DC styling automatically: colored header row, alternating fills, small type scale. **Syntax** — standard markdown pipe table

```markdown
| Augment          | Slot   | Effect                              |
|------------------|--------|-------------------------------------|
| Reflex Booster   | Legs   | +2 to initiative rolls              |
| Subdermal Plating| Torso  | Reduce incoming damage by 1         |
| Optic Splice     | Head   | Ignore darkness penalties           |
| Neural Tap       | Head   | +1 die on Hack and Interface checks |
```

---

# 6. Specialty System

The `@specialty .<name>` container is the **parent scope** for the specialty chrome. It emits `.dc-specialty.<name>` and drives the silhouette and accent color of every `@skill`, `@learning-path`, and card nested inside it — the Contextual Cascade Principle. Authors never set a `variant=` attribute on a card; the variant flows from the parent context. The marker-semantics statement for `@specialty` is owned by `07-markdown-reference.md`; this section owns the visual/role description.

> **Component pattern:** `.dc-skill-card`, `.dc-path-shell`, and `.dc-specialty-card` are distinct components. They may share some visual language, but each owns its own shell, spacing, break behavior, and layout rules. Do not collapse them into one broad variable-driven family.

**Specialty families** (`.dc-specialty.<name>` variants): `augmerc`, `proxy`, `streetwarden`, `gutterdruid`, `cybersurgeon`, `wirephreak`, `technosorcerer`, `etherlock`, `dualist`, `generalist`.

---

## Ability / Skill Card

The `@skill` macro generates the full card HTML automatically → `.dc-skill-card`. The next `@skill` or `@end-skill` closes the current card. **The card's silhouette and accent color come from the `@specialty .<name>` parent container** — no per-card variant attribute is needed. Wrap a section in `@specialty .augmerc` and every `@skill` inside inherits the augmerc shape; wrap in `@specialty .wirephreak` and every `@skill` inherits that family's shape.

**Macro syntax** — H4 title, blockquote flavor, ordered list abilities, optional H5 sub-header (full marker grammar and worked examples in `07-markdown-reference.md`):

```
@skill
#### Ability Title | AUG1.1
> Flavor line.
1. **0 AP** *Action Name:* Effect description.
2. **2 AP** *Action Name:* Effect description.
##### Sub-header text
@end-skill
```

**Tier badge** — Inside `@learning-path` the tab tier (`AUG1.1`, `AUG1.2`, …) is auto-generated. For standalone cards or custom labels, append ` | Badge` to the H4.

**Optional attributes** — `id="slug"` sets the card's `name` for anchor links. For long abilities, use `@continue`.

**Card variants (docs-only):** `.dc-skill-card.dc-two-col` and `.dc-skill-card.dc-highlight` exist in the class inventory but have no dedicated authored macro path. The plugin also emits these sub-elements (authors never write them directly): `.dc-card-tab`, `.dc-tab-title`, `.dc-tab-tier`, `.dc-flavor`, `.dc-ability` / `.dc-ability-text`, `.dc-card-body`, `.dc-card-inner`.

---

## Skill Card Continuation

When an ability is too long for one card, use `@continue` inside the active `@skill` block → `.dc-skill-card.dc-skill-card-cont`. It closes the current card and opens a new continuation card with the same variant and a `▸` suffix on the tab title.

`@continue` must appear between `@skill` and `@end-skill`. The next `@skill`, `@end-skill`, or end of file closes the continuation automatically.

```
@skill
#### Deep Scan | AUG2.4
> Every system has a back door. Yours is already open.
1. **0 AP** *Passive Sweep:* Detect networked devices within Near at scene start.
2. **2 AP** *Root Access:* Read all signals on one target until your next turn.
@continue
3. **3 AP** *Kill Switch:* Shut down one networked device in Near range.
4. **VAR AP** *Cascade Wipe:* Extend Kill Switch across linked targets (2 AP each).
##### Every door has a hinge. You are the hinge.
@end-skill
```

---

## AP Chip Variants

Inline HTML spans inside `@skill` ability text. Variants signal cost type at a glance:

| Class | Example | Meaning |
|---|---|---|
| `dc-ap free` | `<span class="dc-ap free">0 AP</span>` | Free action — crimson fill |
| `dc-ap` | `<span class="dc-ap">2 AP</span>` | Standard cost — HUD green |
| `dc-ap var` | `<span class="dc-ap var">VAR</span>` | Variable cost — magenta fill |

**Additional AP variants (docs-only):** the class inventory also lists `.dc-ap.reduced`, `.dc-ap.increased`, `.dc-ap.standard`, and `.dc-ap.special` — they exist in CSS but have no dedicated authored example here.

---

## Learning Path

A learning path wraps skill cards under a named spray banner with a sticker chain and flavor line → `.dc-path-shell` + `.dc-learning-path`. Use `@learning-path` after `@specialty .classname` — the path index and specialty code (e.g., `AUG1`) are auto-computed. Tab tiers (`AUG1.1`, `AUG1.2`, …) are generated automatically from position; use `#### Skill Name | Custom` only to override. The emitted path shell is its own component (`.dc-path-shell`) with its own notched shape and spacing rules; `.dc-path-block` is only the structural section hook. Marker grammar lives in `07-markdown-reference.md`.

@section .gp-columns-2 .dc-column-panel

**Macro syntax:**

```
@specialty .augmerc

@learning-path
### Path Title
> Path flavor line.
- Skill A
- Skill B
- Skill C

@skill
#### Skill Name
> Skill flavor.
1. **0 AP** *Action:* Effect.
2. **2 AP** *Action:* Effect.
@end-skill

@end-learning-path
```

## Learning Path Variants — driven by the parent specialty

The learning-path shell and its spray-banner title each have a distinct clip-path silhouette per specialty family. The shape is **assigned by the parent `@specialty .<name>` container**, not by an attribute on `@learning-path` itself.

```markdown
@specialty .augmerc
@learning-path
### Biting Distance
- subtitle
@end-learning-path
@end-specialty
```

The CSS rule `.dc-specialty.augmerc .dc-path-shell { clip-path: … }` picks the silhouette. Drop the same `@learning-path` into `@specialty .wirephreak` and it inherits the wirephreak shape automatically — no syntax change needed.

@end-section

| Parent specialty | Shell silhouette |
|---|---|
| `.dc-specialty.augmerc` | Default corner-notched shell with diagonal spray banner |
| `.dc-specialty.wirephreak` | Sharp angular shell with clipped-corner banner |
| `.dc-specialty.proxy` | Asymmetric stepped shell with left-cut banner |
| `.dc-specialty.gutterdruid` | Soft angular shell with shallow-corner banner |
| `.dc-specialty.cybersurgeon` | Pinched shell with centered-notch banner |
| `.dc-specialty.streetwarden`, `.technosorcerer`, `.etherlock` | Additional family-specific silhouettes |

---

## Clip-Path Card Shapes — assigned by parent specialty

Each specialty family also has a distinct skill-card silhouette. Like the path shell above, the shape is **read from the `@specialty .<name>` parent container** — authors never set a `variant=` attribute on `@skill`. (Card and path shell are different shells, but both follow the same parent-cascade rule described in the group intro above.)

@section .gp-columns-2 .dc-column-panel

```markdown
@specialty .augmerc
@skill
#### Punishing Counter
> Flavor line.
1. **0 AP** *Steel Says No:* …
@end-skill
@end-specialty
```

The CSS rule `.dc-specialty.augmerc .dc-skill-card { clip-path: … }` defines the augmerc card silhouette. Eight specialty families exist, each with its own card shape and tab silhouette:

| Specialty | Card silhouette |
|-----------|-----------------|
| `.dc-specialty.augmerc` | Default right-diagonal tab, bottom-right notch body |
| `.dc-specialty.wirephreak` | Sharp angular — diagonal cuts on all four tab corners |
| `.dc-specialty.proxy` | Asymmetric tech — top-left step on tab, large diagonal on body |
| `.dc-specialty.gutterdruid` | Soft angular — shallow corner cuts |
| `.dc-specialty.cybersurgeon` | Scooped futuristic — center notch on tab |
| `.dc-specialty.streetwarden`, `.technosorcerer`, `.etherlock` | Family-specific variants |

To add a new specialty, define `.dc-specialty.<name> .dc-skill-card { clip-path: … }` in the package's `styles/components/*.css`. All skill cards inside `@specialty .<name>` automatically pick up the silhouette.

@end-section

---

## Stickers & Path Chains

Slightly skewed paper labels connected by orange chevron arrows. The active step renders in crimson with a harder rotation — no fade, instant state flip.

@section .gp-columns-2 .dc-column-panel

### Path Step Chain

Horizontal chain of skill-name stickers auto-generated by `@learning-path` from the bullet list; first sticker gets `.active`. Never author manually inside chapter content.

**Syntax** — auto-generated by `@learning-path`; raw HTML fallback: `<div class="dc-stickers dc-flush">` with `<span class="dc-sticker">` and `<span class="dc-arrow">»</span>` separators

```html
<div class="dc-stickers dc-flush">
  <span class="dc-sticker active">Punishing Counter</span>
  <span class="dc-arrow">»</span>
  <span class="dc-sticker">Rage Hit</span>
  <span class="dc-arrow">»</span>
  <span class="dc-sticker">Pain Compliance</span>
</div>
```

### Path Subtitle & Sub-header Sticker

Both are auto-generated from the `@learning-path` / `@skill` macros. Author manually only for standalone use.

```html
<!-- Path Subtitle — auto from @learning-path blockquote line -->
<div class="dc-path-subtitle dc-flush">— Path · Choose your specialty —</div>

<!-- Sub-header Sticker — auto from @skill H5 line -->
<div class="dc-sub-header dc-flush">Stance · Free counter · Once per round</div>
```

@end-section

### DC Path Sticker

Badge inside learning-path spray headers. **Syntax** — `<span class="dc-path-sticker">AUG1</span>` → `.dc-path-sticker`

```html
<span class="dc-path-sticker">AUG1</span>
```

---

## Specialty Intro, Art & Card

These three specialty-page components are emitted by their respective markers; the parent `@specialty .<name>` drives their accent.

- **Specialty Intro** — `@specialty-intro` → `.dc-specialty-intro`. Title-banded intro panel for a specialty's opening page.
- **Specialty Art** — `@specialty-art` → `.dc-specialty-art`. Full-bleed art panel.
- **Specialty Card** — `@specialty-card` → `.dc-specialty-card`. Individual specialty entry card (portrait + accent band).

**Classtag (docs-only):** `.dc-classtag` + specialty variant (class-identity dots) exists in the class inventory but has no dedicated authored macro path here.

---

## Chapter Opener Number

> **Retired — do not use.** `.dc-chapter-opener-no` has no rule in any loaded
> stylesheet and no macro emits it: the plugin never referenced it, and its CSS
> was deleted when the legacy `@chapter-opener` macro was retired (see the note at
> the package's `styles/components/*.css`). The live badge is the `.chapter-opener`
> element that `markers.js` injects for a labelled `@chapter` — see the
> Chapter Opener template in `05-page-templates.md`. The markup and slug table
> below are kept for historical reference only; they render unstyled.

```html
<div class="dc-chapter-opener-no">AUG1</div>
```

| Specialty | Slug | Specialty | Slug |
|---|---|---|---|
| Augmerc | `AUG1` | Cybersurgeon | `CYB1` |
| Proxy | `PRX1` | Wirephreak | `WPK1` |
| Streetwarden | `SWD1` | Technosorcerer | `TCS1` |
| Gutterdruid | `GDR1` | Etherlock | `ETH1` |
| Non-specialty | `C.01`, `C.02`, … | | |

---

## At-a-Glance Cards

Quick stat grid for character sheets, specialty summaries, and creature previews → `.dc-at-a-glance-cards` / `.dc-at-a-glance-card`. Each card holds one label and one value.

```html
<div class="dc-at-a-glance-cards">
  <div class="dc-at-a-glance-card"><h4>HP</h4><p>14</p></div>
  <div class="dc-at-a-glance-card"><h4>Speed</h4><p>Near</p></div>
  <div class="dc-at-a-glance-card"><h4>Edge</h4><p>+2</p></div>
</div>
```

---

# 7. Gear, Stat Blocks & NPCs

## Gear Entry

H3 item name (crimson display font) + italic tagline + mechanics prose → `.dc-card.dc-gear`. Entries separated by `---`. **Syntax** — `@gear` … `@end-gear`. Tagline paragraph must be purely italic (`*...*`). **Use:** appendices, gear chapters, weapon lists.

```markdown
@gear
### Ripper Blades Mk.II

*Melee. Cyberware implant. Pair.*

Damage 1d8+STR. On a crit, the target bleeds for 1d4 at the start of
their next turn. Retractable — no visible profile when sheathed.
Requires Cybersurgeon installation.
@end-gear

---

@gear
### Ghost-Wire Whip

*Melee. Monofilament. Reach 2.*

Damage 1d6+AGI. Ignores armor on a roll of 5+. Folding grip —
concealable under a jacket. Cuts non-powered barriers on a hit of 10+.
@end-gear
```

---

## Stat Blocks

Both block types use the same `.dc-stat` structure. Creature blocks use combat stats (HP / DEF / AP / DMG); NPC blocks use social stats (REP / HEAT / FEE / TURN). Add `.dc-flush` to remove default side margins.

> **Narrative vs numeric (docs-only):** the class inventory distinguishes `.dc-npc-stat` (narrative enemy/ally entries with flavor quotes and trait sections) from `.dc-stat-grid` (compact at-a-glance numerical stat grids). These are **separate components, not variants of each other**. The HTML examples below use the `.dc-stat` / `.dc-stat-grid` numeric form.

### Creature Stat Block

**Syntax** — raw HTML

```html
<div class="dc-stat dc-flush">
  <div class="dc-stat-head">
    <div class="dc-stat-name">Wirewolf, Pack-Beta</div>
    <div class="dc-stat-class">— Threat · Hunter —</div>
  </div>
  <div class="dc-stat-grid">
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">HP</div>
      <div class="dc-stat-cell-val">22</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">DEF</div>
      <div class="dc-stat-cell-val">14</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">AP</div>
      <div class="dc-stat-cell-val">3</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">DMG</div>
      <div class="dc-stat-cell-val">d20</div>
    </div>
  </div>
  <div class="dc-stat-line">
    <strong>Pack Tactic:</strong> While 2+ wirewolves
    are in reach, all gain advantage.
  </div>
</div>
```

### NPC Stat Block — social stats variant

```html
<div class="dc-stat dc-flush">
  <div class="dc-stat-head">
    <div class="dc-stat-name">Doc Solenn</div>
    <div class="dc-stat-class">— Contact · Fixer —</div>
  </div>
  <div class="dc-stat-grid">
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">REP</div>
      <div class="dc-stat-cell-val">4</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">HEAT</div>
      <div class="dc-stat-cell-val">2</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">FEE</div>
      <div class="dc-stat-cell-val">×1.5</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">TURN</div>
      <div class="dc-stat-cell-val">−1</div>
    </div>
  </div>
  <div class="dc-stat-line">
    <strong>Patch Job:</strong> Treat wounds between
    scenes. Costs FEE × severity.
  </div>
</div>
```

---

## Card Entries & Distance Tags (docs-only)

The class inventory references these classes; they have no dedicated authored component section in this catalog (listed here for completeness, not added as new authored components):

- **Card entries** — `.dc-card` is the base card referenced via the `@gear` quick-reference; flaws / ideals / dreams card variants build on it.
- **Distance tags** — `.dc-distance-tags` / `.dc-dist-tag` / `.dc-dist-name` / `.dc-dist-ap` for range/AP labels.

---

# 8. Dividers & Reference

## Tape Divider

Horizontal section break styled as a torn-tape strip → `.dc-tape.dc-flush`. `.dc-flush` extends edge to edge. **Syntax** — `<div class="dc-tape dc-flush">…</div>`

```html
<div class="dc-tape dc-flush">Section Break</div>
```

---

## Dashed Rule Divider

Red dashed `<hr>` for gear lists, NPC blocks, and rules section breaks → `.dc-dashed-rule`. CSS applies the style globally to all `<hr>` elements. **Syntax** — `---`. **Use:** gear entries, NPC separators, rules section breaks.

```markdown
Field Rations × 3
---
Trauma Kit
---
Signal Jammer (single-use)
```

---

## Class Tag

Inline pill for specialty names and cost labels. **Syntax** — `<span class="dc-tag">Label</span>` → `.dc-tag`

```html
<span class="dc-tag">Augmerc</span>
```

---

## Glossary / Term List

Definition list of game terms rendered as a styled block → `.dc-terms` / `.dc-terms-item`. **Syntax** — raw HTML `.dc-terms` wrapper

```html
<div class="dc-terms">
  <div class="dc-terms-item">
    <strong>Augmerc</strong>
    <p>A specialist who combines cybernetic augmentation with close-range combat training.</p>
  </div>
  <div class="dc-terms-item">
    <strong>Hard Choice</strong>
    <p>A roll result where the fiction advances but at a cost.</p>
  </div>
</div>
```

---

## Numbered Procedure

Zero-padded ordered list for sequential rules → `.dc-steps`. **Syntax** — `@procedure` … `@end-procedure` with a standard ordered list inside (marker semantics in `07-markdown-reference.md`)

```markdown
@procedure
1. **Pick a Spec.** Augmerc, Proxy, Streetwarden — one of eight.
2. **Spend 6 Spec Points.** Distribute across paths.
3. **Take a Signature Augment.** Free at character creation.
@end-procedure
```

---

## Outcome Ladder

Five-rung d20 result table for all rolls → `.dc-outcomes`. Each row is color-coded by result severity. **Syntax** — `@outcome` … `@end-outcome` macro; columns: `roll | name | description`. Row variants: `.hit`, `.miss`, `.crit`, `.fail`, `.mixed`.

```
@outcome
20 | Crit | You flow. Automatic success — no further roll needed.
11–19 | Hit | You succeed at what you were trying to do without a hitch.
6–10 | Hard Choice | You succeed, but at a cost.
2–5 | Miss | You fail. The only consequence is what you had riding on the roll.
1 | Catastrophe | Dark. Automatic fail with a severe setback.
@end-outcome
```

> **Sub-element classes (docs-only):** the plugin emits `.dc-outcome-row` (`.hit` / `.miss` / `.crit` / `.fail` / `.mixed`), `.dc-outcomes-label`, `.dc-outcome-key`, and `.dc-outcome-text`. Authors do not write these directly.

---

## Stamps *(deprecated)*

Rotated monospaced label chips for content status (draft, deprecated, classified, DM-only) → `.dc-stamp` / `.dc-classified`. Parked in the since-deleted `css/deprecated.css` on 2026-05-24 — zero live usage and the only authoring path was raw HTML, which violates the no-HTML-in-markdown rule. If revived, the cascade-correct shape is `@section .dc-stamp` containing the label text, with `.dc-classified` as a variant on the section.

---

## Roll Lucid / Roll Surreal Badges

In-world dice badges → `.dc-roll-lucid` / `.dc-roll-surreal`. No current authoring path — the CSS exists, awaiting a section-component wrapper. The plugin automatically wraps the canonical Markdown text `ROLL THE DIE!` with `.dc-roll-the-die`; code and raw HTML are excluded.

---

# 9. Front Matter, Images & Layout (docs-only)

These components are emitted by templates and the plugin (cover page, table of contents, image placement helpers, and multi-card layout grids) rather than written directly by chapter authors. The class inventory references them; they are listed here for completeness, not as new authored markdown components.

---

## Cover Page (docs-only)

The book cover template emits the cover furniture. Authors do not write these classes directly — they are produced by the front-matter cover template.

- **Page shell** — `.dc-cover-page` wraps the whole cover; `.dc-cover-layout` is the inner layout grid and `.dc-cover-body` holds the stacked title block.
- **Title typography** — `.dc-cover-bigword` is the oversized title word; `.dc-cover-num` is the edition / volume number; `.dc-cover-strap` is the strapline / subtitle.
- **Metadata** — `.dc-cover-meta-row` renders a row of cover metadata (imprint, edition, year).

---

## Table of Contents (docs-only)

The TOC template emits the contents furniture. Authors do not write these classes directly — they are produced by the front-matter TOC template.

- **Page shell** — `.dc-toc-page` is the TOC page wrapper; `.dc-toc` is the contents list container.
- **Rows** — `.dc-toc-row` is a single contents entry; `.dc-toc-title` is the entry's title text (paired with its page-number leader).

---

## Images (docs-only)

Image-placement helper classes referenced by the class inventory. They position and frame art within prose; no dedicated authored macro path in this catalog.

- **Floats** — `.dc-img-float-left` / `.dc-img-float-right` float an image to the named side with prose wrapping around it.
- **Portrait framing** — `.dc-portrait` frames a portrait-orientation character image.
- **Bottom art** — `.dc-art-bottom` anchors decorative art to the bottom of a page or section.

---

## Card Grid (docs-only)

`.dc-card-grid` is a multi-column grid container for laying out cards side by side. It exists in the class inventory but has no dedicated authored macro path here.

---

## Citizen Walkthrough

Field-walkthrough section that guides a reader through filling out each field of the Citizen File (character profile). It is the **instructional walkthrough chapter**, not the filled-form artifact. Each `@section .dc-citizen-walkthrough` is one step or field group — the reader works top to bottom through Handle, Designation, age, size, eyes, skin, species, and the remaining character-creation prompts. The section rides the standard `.section` chassis (clipped-corner accent stripe + substrate); tune its accent or substrate by overriding `--dc-section-accent` / `--dc-section-bg` at the chapter id in `fg-overrides.css` rather than adding bespoke rules. Add `.gp-columns-2 .dc-column-panel` for a side-by-side field split (e.g. Handle next to Designation) — heading height is normalized so both columns' body text starts on the same baseline. **Syntax** — `@section .dc-citizen-walkthrough` … `@end-section`, paired with the `@page .dc-citizen-file-page` topic page for the running header.

```markdown
@page .dc-citizen-file-page .chapter-01

@section .dc-citizen-walkthrough

## Citizen File

This chapter will guide you through all the choices you need to make to
help you fill in the blanks and create a unique and interesting character.
Don't worry about making mistakes — just try to have fun with it and let
your imagination do the work.

#### What's Yr Handle?

Choose a name. It can come from any culture, any language, or straight out
of your imagination. Pull it from a book, a show, a half-remembered dream,
or invent something that sounds right for the city.

#### Designation

Let others know how to refer to you. She/her, he/him, they/them, or
something else entirely. Names and pronouns matter when life itself is
constantly trying to strip both away.

@end-section
```

> **Class-inventory note (docs-only):** `.dc-citizen-walkthrough.gp-columns-2` is the two-column variant; apply it as `@section .dc-citizen-walkthrough .gp-columns-2 .dc-column-panel` to split a step into paired fields.

---

## Fiction Excerpt

Narrative-fiction opener that wraps in-world prose — chapter-opening vignettes, in-character tales, and story interludes — with narrative typography, orphan/widow control, and **automatic art placement**. Drop a placeholder or final image anywhere in the prose flow and the section floats it (left by default) at roughly 3 inches wide with a hard drop-shadow and outline, wrapping the body text around it; authors never add a per-image float class. The float side is set via `--dc-fiction-art-float` and the surface tint via `--dc-fiction-bg`, both overridable per chapter in `fg-overrides.css`. **Syntax** — `@section .dc-fiction-excerpt` … `@end-section`, paired with the `@page .dc-chapter-start` opener page.

```markdown
@page .page-chapter-start .dc-chapter-start .chapter-01

@section .dc-fiction-excerpt

# Who Do You Dream to Be?

"It's hard being me, but I guess it's the same for anyting sentient in the
monoverse, ay?! Tag's Thump, an I'm a rabbit outta dee EntD here in Dimm
City. Lemme post ya a tale about life here in da middle 'o dee ether.

I wuz tearin down an alley, lungs burnin, heart jackhammering like it
wanted out. Da cauldron wuz right on mai heels now, wings chopping da air,
close enough I could smell da oil an blood on 'em.

Streets don't care how clever you are. Dey only care what you live through."

![Lil Thump](https://placehold.co/600x400/png?text=Lil+Thump)

@end-section
```

---

# Consolidated Quick Reference

The single authoritative author-syntax → emitted-class map for this chapter. This consolidates what were previously three separate named tables — the **Component Token Reference** (Core), the **Component Authoring Quick Reference** (DC Component Library), and the **Component Authoring Quick Reference** (Field Guide Components) — into one grouped table; the per-class rows from each are preserved under the grouped headings below. For the exhaustive class inventory and the canonical macro → class cross-reference, see `https://github.com/dimm-city/gp-dimm-city/blob/main/docs/components-and-palette-reference.md`. Rows tagged *(class exists / no authored section)* are surfaced for completeness — the class is in the CSS but has no dedicated authored component in this catalog.

**Prose & typography**

| Component | Authoring method | CSS class(es) |
|-----------|-----------------|-----------|
| Body Prose | Plain markdown paragraph | *(auto)* |
| Intro Lede | `@lede` … `@end-lede` | `.dc-intro` |
| Flavor Text | `> [!FLAVOR]` blockquote | `.dc-alert`, `.dc-flavor` |
| Pull Quote | `> [!PULLQUOTE]` | `.dc-pullquote.dc-flush` |
| Blockquote | Standard markdown `>` | *(auto)* |
| Code Block | Triple-backtick fenced block | *(auto)* |
| Chevron Banner | `# Title {.dc-chevron}` | `dc-chevron` |
| Spray Banner | `## Title {.dc-spray}` | `dc-spray` |
| Spec Tweak Rule | `### Title {.dc-spec-tweak .dc-no-top}` | `dc-spec-tweak`, `dc-no-top` |

**Alerts & callouts**

| Component | Authoring method | CSS class(es) |
|-----------|-----------------|-----------|
| Note | `> [!NOTE]` | `.dc-note` |
| Warning | `> [!WARNING]` | `.dc-note.warning` |
| Vibe Callout | `> [!VIBE]` | `.dc-vibe-callout` |
| Origin Callout | `> [!ORIGIN]` | `.dc-origin-callout` |
| Visit Callout | `> [!VISIT]` | `.dc-visit-callout` |
| Gear Callout | `> [!GEAR]` | `.dc-gear-callout` |
| Dream Master Note | `> [!DM]` | `.dc-dm-note` |
| Block Callout | `@callout variant="…"` … `@end-callout` | `.dc-alert` + variant |
| DM Note block | `@dm-note label="…"` … `@end-dm-note` | `.dc-dm-note` |
| Alert label chip | *(class exists / no authored section)* | `.dc-alert-label` |
| Generic callout | *(class exists / no authored section)* | `.dc-callout` |

**Block variants (dc-block family)**

| Component | Authoring method | CSS class(es) |
|-----------|-----------------|-----------|
| Panel Enclosure | `@block .dc-panel label="…" … @end-block` | `dc-block dc-panel` |
| Slate Enclosure | `@block .dc-slate label="…" … @end-block` | `dc-block dc-slate` |
| Shard Enclosure | `@block .dc-shard label="…" … @end-block` | `dc-block dc-shard` |
| Codex Enclosure | `@block .dc-codex label="…" … @end-block` | `dc-block dc-codex` |

**Sidebars & panels**

| Component | Authoring method | CSS class(es) |
|-----------|-----------------|-----------|
| Sidebar | `@sidebar … @end-sidebar` | `dc-sidebar` (`.inset` variant) |
| Sidebar Box | `@sidebar-box … @end-sidebar-box` | `dc-prose-panel dc-sidebar-box` |
| Definition Block | `@definition … @end-definition` | `dc-prose-panel dc-definition-block` |
| Human Callout / NPC Sidebar | Raw HTML inside `.dc-sidebar` | `.dc-human-callout` |
| Shared prose-panel shell | *(class exists / shared shell)* | `.dc-prose-panel` |

**Tables**

| Component | Authoring method | CSS class(es) |
|-----------|-----------------|-----------|
| Table | Standard markdown pipe table | *(auto)* |

**Specialty system**

| Component | Authoring method | CSS class(es) |
|-----------|-----------------|-----------|
| Specialty wrapper | `@specialty .<name>` … `@end-specialty` | `.dc-specialty` + variant |
| Skill Card (outer) | `@skill … @end-skill` macro | `dc-skill-card` |
| Skill Card Continuation | `@continue` inside `@skill` block | `dc-skill-card dc-skill-card-cont` |
| Skill Card variants | *(class exists / no authored section)* | `.dc-skill-card.dc-two-col`, `.dc-skill-card.dc-highlight` |
| Card Tab / Title / Tier | Generated by macro | `dc-card-tab`, `dc-tab-title`, `dc-tab-tier` |
| Flavor (in card) | Generated by macro | `dc-flavor` |
| Ability Row | Generated by macro | `dc-ability`, `dc-ability-text` |
| Generated card sub-elements | Generated by macro | `dc-card-body`, `dc-card-inner` |
| AP Chip — Free | `<span class="dc-ap free">` | `dc-ap free` |
| AP Chip — Standard | `<span class="dc-ap">` | `dc-ap` |
| AP Chip — Variable | `<span class="dc-ap var">` | `dc-ap var` |
| AP Chip — others | *(class exists / no authored section)* | `dc-ap reduced`, `dc-ap increased`, `dc-ap standard`, `dc-ap special` |
| Learning Path | `@learning-path … @end-learning-path` macro | `dc-learning-path`, `dc-path-block` (structural), `dc-path-shell` (visual shell) |
| Path Step Chain | auto via `@learning-path`; raw HTML fallback | `dc-stickers`, `dc-sticker`, `dc-sticker.active`, `dc-arrow` |
| Path Subtitle | auto via `@learning-path`; raw HTML fallback | `dc-path-subtitle`, `flush` |
| Sub-header Sticker | auto via `@skill`; raw HTML fallback | `dc-sub-header`, `flush` |
| DC Path Sticker | `<span class="dc-path-sticker">AUG1</span>` | `dc-path-sticker` |
| Card silhouette | Driven by `@specialty .<name>` parent | `.dc-specialty.<name> .dc-skill-card` |
| Specialty Intro | `@specialty-intro` | `dc-specialty-intro` |
| Specialty Art | `@specialty-art` | `dc-specialty-art` |
| Specialty Card | `@specialty-card` | `dc-specialty-card` |
| Classtag | *(class exists / no authored section)* | `dc-classtag` + specialty variant |
| Chapter Opener Number | Auto via labelled `@chapter` (`dc-chapter-opener-no` is retired — no CSS, no emitter) | `chapter-opener` |
| At-a-Glance Cards | Raw HTML | `dc-at-a-glance-cards`, `dc-at-a-glance-card` |

**Gear, stat blocks & NPCs**

| Component | Authoring method | CSS class(es) |
|-----------|-----------------|-----------|
| Gear Entry | `@gear … @end-gear` | `dc-card dc-gear` |
| Creature Stat Block | Raw HTML | `dc-stat`, `dc-stat-head`, `dc-stat-grid`, `dc-stat-cell`, `dc-stat-cell-key`, `dc-stat-cell-val`, `dc-stat-line`, `dc-stat-name`, `dc-stat-class` |
| NPC Stat Block (numeric) | Raw HTML (social stats) | `dc-stat`, `dc-stat-grid` |
| NPC Stat Block (narrative) | *(class exists / no authored section)* | `dc-npc-stat` |
| Card entries (flaws/ideals/dreams) | *(class exists / no authored section)* | `dc-card` variants |
| Distance tags | *(class exists / no authored section)* | `dc-distance-tags`, `dc-dist-tag`, `dc-dist-name`, `dc-dist-ap` |

**Dividers & reference**

| Component | Authoring method | CSS class(es) |
|-----------|-----------------|-----------|
| Tape Divider | `<div class="dc-tape dc-flush">Label</div>` | `dc-tape`, `flush` |
| Dashed Rule Divider | `---` | `dc-dashed-rule` |
| Class Tag | `<span class="dc-tag">Label</span>` | `dc-tag` |
| Glossary / Term List | Raw HTML `.dc-terms` wrapper | `dc-terms`, `dc-terms-item` |
| Numbered Procedure | `@procedure … @end-procedure` | `dc-steps` |
| Outcome Ladder | `@outcome … @end-outcome` | `dc-outcomes`; rows `.hit`/`.miss`/`.crit`/`.fail`/`.mixed` |
| Outcome sub-elements | Generated by macro | `dc-outcome-row`, `dc-outcomes-label`, `dc-outcome-key`, `dc-outcome-text` |
| Stamp — Default *(DEPRECATED — do not use)* | None — no CSS in the build; will not render | `dc-stamp` |
| Stamp — Classified *(DEPRECATED — do not use)* | None — no CSS in the build; will not render | `dc-stamp`, `dc-classified` |
| Roll Lucid badge | (no current authoring path) | `dc-roll-lucid` |
| Roll Surreal badge | (no current authoring path) | `dc-roll-surreal` |
| Roll the Die | Canonical `ROLL THE DIE!` text (automatic) | `dc-roll-the-die` |

**Front matter, images & layout (docs-only)**

| Component | Authoring method | CSS class(es) |
|-----------|-----------------|-----------|
| Cover Page | Emitted by cover template | `dc-cover-page`, `dc-cover-layout`, `dc-cover-body`, `dc-cover-bigword`, `dc-cover-num`, `dc-cover-strap`, `dc-cover-meta-row` |
| Table of Contents | Emitted by TOC template | `dc-toc`, `dc-toc-page`, `dc-toc-row`, `dc-toc-title` |
| Images | *(class exists / no authored section)* | `dc-img-float-left`, `dc-img-float-right`, `dc-portrait`, `dc-art-bottom` |
| Card Grid | *(class exists / no authored section)* | `dc-card-grid` |
| Citizen Walkthrough | `@section .dc-citizen-walkthrough … @end-section` | `dc-citizen-walkthrough` (`.gp-columns-2 .dc-column-panel` variant) |
| Fiction Excerpt | `@section .dc-fiction-excerpt … @end-section` | `dc-fiction-excerpt` |

---

# See It In Action

These examples show the above components rendered in real book pages using actual Dimm City Field Guide content.

- [Front Matter & TOC](#ch-example-front-matter) — credits, TOC, intro pages
- [Chapter Openers](#ch-example-chapter-opener) — chapter start spreads, chevron banners
- [Specialty Overview](#ch-example-specialty-overview) — chapter-02 specialty intro pages with vibe callouts, origin blocks, class tags, definition blocks, and specialty listing cards
- [Specialty Profile](#ch-example-specialty-profile) — full specialty spread: flavor text, pull quotes, spray banners, sticker chains, skill cards with AP chips and clip-path variants
- [Rules & Mechanics](#ch-example-rules) — outcome ladder, notes, warnings, numbered procedures, sidebar boxes, and dashed rule dividers in context
- [Dream Master Pages](#ch-example-dm-npcs) — DM notes, creature and NPC stat blocks, definition blocks for NPC summaries, encounter hooks
- [Gear & Tech](#ch-example-gear-tech) — gear callouts, gear entries, tables, dashed rule separators, and cybernetics rules
