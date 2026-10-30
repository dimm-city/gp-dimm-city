@chapter #ch-typography .typography .dg-guide ch="2"

@page .dg-doc

Chapter 2 {.dg-kicker}

# Typography

Three faces, each with one job. lixdu is the display face for chapter and section headings and banners; Tomorrow is the mono face for tabs, chips, counters, and code; Titillium Web carries every line of body, flavor, and quote copy. {.dg-lede}

## The type scale

| Element | You write | Size · Face | Role |
|---|---|---|---|
| H1 | `# Title` | 26pt bold · lixdu | Chapter and specialty openers |
| H2 | `## Heading` | 20pt bold · lixdu | Section breaks, with an accent rule |
| H3 | `### Sub-heading` | 16pt · lixdu | Column labels and sub-topics |
| H4 | `#### Item` | 13pt uppercase · lixdu | Skill names, gear names, stat-block names |
| Body | a paragraph | 12pt · Titillium Web | All prose |
| Flavor | `> [!FLAVOR]` | 11pt italic · Titillium Web | In-world voice |
| Chevron banner | `# Title {.dc-chevron}` | H1 scale, angled fill | One per chapter opener |
| Spray banner | `## Title {.dc-spray}` | H2 scale, a stencilled tag with a stepped edge | Learning paths, major topic breaks |
| Card tab | emitted by `@skill` | 11pt title, 10pt tier pill · Tomorrow | Skill-card tab labels |
| Tag | `<span class="dc-tag">` | 10pt · Tomorrow | Keyword and cost chips |

## The three faces

<div class="dg-face">
<p class="dg-face-meta"><strong>lixdu</strong> &mdash; display · <code>--font-display</code> · headings set uppercase, H1 26pt, leading 1.35, tracking 0.2em</p>
<p class="dg-face-display">ABCDEFGHIJKLM<br>NOPQRSTUVWXYZ<br>0123456789</p>
<p class="dg-face-display dg-face-set">Wired to kill</p>
</div>

<div class="dg-face">
<p class="dg-face-meta"><strong>Titillium Web</strong> &mdash; body · <code>--font-body</code> · 12pt, leading 1.5 (18pt), tracking 0.005em</p>
<p class="dg-face-body">ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 &amp;?!</p>
<p class="dg-face-body dg-face-set">Corporate enforcers earn their grafts in blood and overtime; street muscle runs cheaper and lasts longer than anyone admits. <em>Italic carries the in-world voice,</em> and <strong>bold marks a rule.</strong></p>
</div>

<div class="dg-face">
<p class="dg-face-meta"><strong>Tomorrow</strong> &mdash; labels · <code>--font-mono</code>, <code>--font-tab</code> · tabs, chips and counters at 10pt (the floor), uppercase, tracking 0.08em or wider</p>
<p class="dg-face-tab">ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789</p>
<p class="dg-face-tab dg-face-set">AUG1.3 · 2 AP · SYSCHK 9&ndash;13</p>
</div>

## Heading hierarchy

Each level rendered at its print size:

<div class="dg-stage dg-on-paper">

# Chapter Title

## Section Heading

### Sub-section Label

#### Item Heading

</div>

## Level and look

A heading's level is its place in the outline, and the outline never skips a level: `#` is followed by `##`, never `###`. Gutterpress flags a skip when it builds. When the page needs a smaller label than the outline allows, keep the level and set the look with `.dc-h3`, `.dc-h4`, `.dc-h5` or `.dc-h6`:

```markdown
# Cybernetics, Weapons, and Gear

## Useful Items {.dc-h3}

### Base Reality {.dc-h4}

#### Dreamer {.dc-h5}
```

Result {.dg-result}

<div class="dg-stage dg-on-paper">

## Useful Items {.dc-h3}

### Base Reality {.dc-h4}

#### Dreamer {.dc-h5}

</div>

The look follows the class everywhere: an `##` with `.dc-h3` that opens a section takes the subordinate section bar, and a `###` with `.dc-h4` inside a section takes no accent rule. On a paragraph, the class sets a line in heading type without adding it to the outline.

## Heading chrome

Three classes dress a heading. The chevron opens a chapter, the spray breaks a major topic, and the spec-tweak rule flags an optional mechanic; `.dc-no-top` pulls it tight against whatever is above it.

```markdown
# Augmerc {.dc-chevron}

## Biting Distance {.dc-spray}

### Spec Tweak: Wired to Kill {.dc-spec-tweak .dc-no-top}
```

Result {.dg-result}

<div class="dg-stage">

@section panel

# Augmerc {.dc-chevron}

## Biting Distance {.dc-spray}

### Spec Tweak: Wired to Kill {.dc-spec-tweak .dc-no-top}

@end-section

</div>

## Body and flavor

<div class="dg-stage dg-on-paper">

Twelve-point Titillium Web carries all running narrative. Corporate enforcers earn their grafts in blood and overtime; street muscle runs cheaper and lasts longer than anyone admits. Notice the leading, the x-height, and how weight shifts when a word is **bolded** or *italicized* mid-sentence.

> [!FLAVOR]
> See an opening, ya take it. Best time to hit 'em is when they think it's over.

</div>

Flavor is 11pt italic in `--ink-dark`, with a rail and no box. Never set flavor in bold italic --- it reads as urgency, not voice.

Don't {.dg-dont-label}

<div class="dg-stage dg-dont">

> [!FLAVOR]
> ***See an opening, ya take it. Best time to hit 'em is when they think it's over.***

</div>

**Column-safe headings:** in a two-column layout use `###` and `####`. `#` and `##` at full print size exceed a 3.5-inch column.

## Size floors

There is one floor, `--fs-floor` (10pt), and nothing prints smaller: not a chip, a tab, a tier pill, an AP chip, a folio or a stamp. It is a minimum, not a target; text that already meets it stays as it is.

| Text | Floor |
|---|---|
| All text: body, rules, tables, captions, labels, chips, tabs and badges | 10pt (the book sets running body at 12pt) |

## Smart typography

The renderer converts ASCII shortcuts as you type: `--` is an en dash --, `---` an em dash ---, `...` an ellipsis ..., and "straight quotes" curl. No special syntax, no Unicode entry.

## Font tokens

| Token | Face | Used for |
|---|---|---|
| `--font-display` | lixdu | H1--H3, banners |
| `--font-body` | Titillium Web | Body prose, flavor, quotes |
| `--font-mono` | Tomorrow | Code, counters, tabular data |
| `--font-tab` | Tomorrow | Short label text: card tabs, stat labels |
| `--font-quote` | Titillium Web | Italic quotes and attributions |

The fonts ship in the package and embed in the PDF at build time; a book never installs them.
