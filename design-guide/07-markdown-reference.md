@chapter #ch-reference .reference .dg-guide ch="2"

# Markdown Reference

@lede

Syntax-table reference for all markdown-it features and DC authoring markers.

@end-lede

> [!NOTE]
> This chapter is a **syntax** reference only — it lists every macro, marker, and attribute. For full component documentation (what each one renders, when to use it, examples), see **[Components](#ch-components)** and the **DC Component Library**.

@page

## Page Layout Markers

The `@` marker system controls page flow and generates semantic HTML wrappers. Markers accept `#id`, `.class`, and `key=value` attributes, enabling chapter-scoped CSS rules without touching global selectors.

**Full attribute syntax** — `@marker #id .class key=value`

| Marker | HTML emitted | Purpose |
|--------|-------------|---------|
| `@chapter #id .class` | `<div class="chapter [class]" id="id">` | Wraps all following content until next `@chapter` |
| `@page #id .class` | `<div class="page [class]" id="id">` | Explicit page container with a named CSS target |
| `@end-section` | (no output) | Closes nearest open `@section` |
| `@page-break` | `<div class="md-page-break" aria-hidden="true"></div>` | Force a hard page break without a wrapper |
| `@section #id .class` | `<div class="region [class]" id="id">` | Region block — groups content, avoids page split |
| `@spread #id .class` | `<div class="spread [class]" id="id">` | Two-page spread — keeps left and right pages paired |

```markdown
@chapter #ch-augmerc .augmerc   → <div class="chapter augmerc" id="ch-augmerc">
@page #pg-skills .skills        → <div class="page skills" id="pg-skills">
@section #sec-counters .counters → <div class="region counters" id="sec-counters">
```

Chapter IDs enable precise CSS scoping without specificity battles: `.chapter#ch-augmerc table { table-layout: fixed; }`

@page

## Dimm City Plugin Markers

The Dimm City plugin (`plugin.js` in the `gp-dimm-city` package) extends the `@` marker system with game-specific block wrappers. These markers auto-close any previously open block of the same type. See **[Components](#ch-components)** for what each block renders.

| Marker | Closes on | Emits / Purpose |
|--------|-----------|-----------------|
| `@sidebar class="…"` | `@end-sidebar` | `.dc-sidebar` aside (`class="inset"` → `.dc-sidebar.inset`, full-height rail; requires an `@page .page-sidebar` host) |
| `@sidebar-box` | `@end-sidebar-box` | `.dc-prose-panel.dc-sidebar-box` callout |
| `@definition` | `@end-definition` | `.dc-prose-panel.dc-definition-block` callout |
| `@procedure` | `@end-procedure` | `.dc-steps` (wraps an ordered list) |
| `@specialty .classname` | Next `@specialty` / `@end-specialty` | `.dc-specialty` + variant (`.augmerc` → `AUG`) |
| `@specialty-intro` | `@end-specialty-intro` | `.dc-specialty-intro` panel |
| `@specialty-art` | `@end-specialty-art` | `.dc-specialty-art` full-page plate |
| `@specialty-card` | `@end-specialty-card` | `.dc-specialty-card` summary card |
| `@learning-path` | Next `@learning-path` / `@end-learning-path` | `.dc-path-shell` + `.dc-learning-path` |
| `@skill` | Next `@skill` / `@end-skill` | `.dc-skill-card` |
| `@continue` | — | `.dc-skill-card.dc-skill-card-cont` continuation card |
| `@gear` | `@end-gear` | `.dc-card.dc-gear` entry |
| `@block .dc-<variant> label=…` | `@end-block` | `.dc-block` + variant (`.dc-panel` / `.dc-slate` / `.dc-shard` / `.dc-codex`) |
| `@outcome` | `@end-outcome` | `.dc-outcomes` ladder |
| `@callout variant="…"` | `@end-callout` | `.dc-alert` + variant (block-level, multi-paragraph) |
| `@dm-note label=…` | `@end-dm-note` | `.dc-dm-note` box |

**Specialty parent-container model** — Card silhouette and accent color come from the `@specialty .<name>` wrapper, not from `variant=` attributes. Wrap a full specialty section in `@specialty .augmerc` and every card inside inherits the augmerc shape and color automatically.

**Optional `@skill` attributes** — `id="slug"` sets an anchor on the card wrapper. `{.dc-allow-split}` allows tall cards to split across pages. For long abilities, use `@continue`.

**Specialty variant classes** — `augmerc`, `proxy`, `streetwarden`, `gutterdruid`, `cybersurgeon`, `wirephreak`, `technosorcerer`, `etherlock`, `dualist`, `generalist`.

@page

## Marker Blocks

`@`-prefixed markers open a wrapped block; matching `@end-X` (or `@end-section`) closes it. Attributes use the same grammar as `@page` / `@section`: `name .class #id key=val key="quoted val"`.

| Marker | Effect |
|--------|--------|
| `@section .gp-columns-2` … `@end-section` | Two equal CSS columns (Gutterpress core vocabulary) |
| `@section .gp-columns-3` … `@end-section` | Three narrow columns — best for short reference entries |
| `@section .gp-columns-2 .dc-column-panel` | The same run inside the DC column-panel card — substrate, top/bottom rules, and a full-width spanning bar for the leading H2/H3 |
| `@column-break` | Hard column break inside a multi-column `@section` |
| `@sidebar` … `@end-sidebar` | Right-floated aside at 38% width |
| `@callout variant="…"` … `@end-callout` | Styled alert box (block-level, multi-paragraph) |
| `@dm-note` … `@end-dm-note` | Dream Master note box (multi-paragraph) |
| `> [!TYPE]` | Inline GFM alert — preferred for single-paragraph callouts |

**Alert type values** for `@callout variant="…"` and `> [!TYPE]`:

| Type | Class | Label |
|------|-------|-------|
| `note` | `dc-note` | Note |
| `warning` | `dc-note warning` | Warning |
| `dm` | `dc-dm-note` | Dream Master Note |
| `vibe` | `dc-vibe-callout` | Vibe |
| `origin` | `dc-origin-callout` | Origin |
| `visit` | `dc-visit-callout` | Visit |
| `gear` | `dc-gear-callout` | Gear |
| `pullquote` | `dc-pullquote flush` | Pull Quote |
| `flavor` | `dc-flavor` | Flavor Text |

> **Choosing between `@callout` and `> [!NOTE]`:** Use `> [!TYPE]` for single short paragraphs — it's shorter and reads naturally in source. Use `@callout` when you need multiple paragraphs, lists, or nested content that can't cleanly fit in a blockquote.

## The `.dc-allow-split` Modifier

By default DC card and section components are **atomic** — `break-inside: avoid` keeps each one whole on a single page. `.dc-allow-split` is the escape hatch: it sets `break-inside: auto` so the element is permitted to break across a page boundary instead of being pushed whole to the next page.

Add it as a class on the component: `@skill {.dc-allow-split}` (skill cards, via `.dc-specialty .dc-skill-card.dc-allow-split`) or `@section .dc-allow-split` (a long section wrapper). It does **not** force a break — it only removes the keep-together constraint so the layout engine may break there if it needs to.

**When to use it.** Reach for `.dc-allow-split` only when an atomic element is genuinely taller than the printable area, or when keeping it whole forces a large dead zone (most of a page left blank) before it. Apply it to the *one* oversized element, not as a blanket habit — splitting a card or section mid-content trades a clean paper object for recovered space, so it's a deliberate trade. Prefer first splitting the content at a logical authoring boundary (e.g. `@continue` for a long ability); use `.dc-allow-split` only when that isn't enough.

```markdown
@skill {.dc-allow-split}
#### Deep Scan | AUG2.4
> Every system has a back door. Yours is already open.
1. **0 AP** *Passive Sweep:* Detect networked devices within Near at scene start.
2. **2 AP** *Root Access:* Read all signals on one target until your next turn.
3. **3 AP** *Kill Switch:* Shut down one networked device in Near range.
@end-skill
```

@page

@section .gp-columns-2 .dc-column-panel

## Element Attributes

`markdown-it-attrs` adds `{#id .class attr="value"}` to most elements. Attribute block must immediately follow the element with no space.

```markdown
## Section Heading {#my-anchor .custom-class}
![Alt text](image.png){.dc-img-float-right}
This sentence has a **key term**{.custom-span} highlighted.
```

## Standard Markdown

All GFM features are available. Smart typography is enabled by default.

**Inline:** `**bold**` · `*italic*` · `***bold italic***` · `` `code` ``

**Headings:** `# H1` (chapter title) · `## H2` (section, accent border) · `### H3` (sub-section) · `#### H4` (item heading, uppercase small)

```markdown
- Unordered list item      1. Ordered list item
  - Nested item               2. Second item

> Blockquote text.         | Col A | Col B |
> — Attribution            |-------|-------|
                           | A     | B     |
```

````markdown
```language
Fenced code block.
```
````

**Definition lists** — standard PHP-Markdown-Extra / Pandoc syntax (a `Term` line, then a `: definition` line). This is the **preferred** way to author definitions and glossaries; it renders on-brand via the base `dl/dt/dd` rules (no class or macro). Supersedes the legacy `@definition` macro and the raw-HTML `.dc-terms` glossary.

```markdown
Tick / Tic
: A very short, indefinite period of time.

Reach
: Close enough to touch. Adjacent.
```

@end-section

@section .gp-columns-2 .dc-column-panel

## Smart Typography

Auto-converts common ASCII sequences to proper typographic characters. No manual Unicode entry required.

| Input | Output | Name |
|-------|--------|------|
| `--` | – | En dash |
| `---` | — | Em dash |
| `...` | … | Ellipsis |
| `"text"` | "text" | Curly double quotes |
| `'text'` | 'text' | Curly single quotes |

## Footnotes

Footnotes are supported via `markdown-it-footnote`. References appear inline at the point of use; definitions can be placed anywhere in the file and render at the end of the content flow.

**Syntax** — `[^label]` inline + `[^label]: definition` anywhere in the file.

```markdown
Here is a sentence with a footnote.[^fn-1]

A second sentence references a different note.[^fn-2]

[^fn-1]: The footnote definition. Can go anywhere in the source file.
[^fn-2]: A second, independent footnote. Labels can be numbers, words, or abbreviations.
```

@end-section

## See It In Action

These examples show the above markdown syntax and plugin markers used in real book pages using actual Dimm City Field Guide content.

- [Front Matter & TOC](#ch-example-front-matter) — page markers, `@chapter`, front-matter class
- [Chapter Openers](#ch-example-chapter-opener) — `@chapter` label, `@specialty`, two-column with column-break
- [Specialty Profile](#ch-example-specialty-profile) — `@learning-path`, `@skill`, `@continue` in context
- [Rules & Mechanics](#ch-example-rules) — container blocks, element attributes, outcome macro
- [Dream Master Pages](#ch-example-dm-npcs) — `@section`, sidebar containers, NPC stat block authoring
