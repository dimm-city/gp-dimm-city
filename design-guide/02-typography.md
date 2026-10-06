@chapter #ch-typography .typography .dg-guide ch="2"

@page .dg-doc


# Typography

Three faces, each with one job. lixdu is the display face for chapter and section headings and banners; Tomorrow is the mono face for tabs, chips, counters, and code; Titillium Web carries every line of body, flavor, and quote copy. {.dg-lede}

## The type scale

| Element | You write | Size · Face | Role |
|---|---|---|---|
| H1 | `# Title` | 20.7pt bold · lixdu | Chapter and specialty openers |
| H2 | `## Heading` | 17.3pt bold · lixdu | Section breaks, with an accent rule |
| H3 | `### Sub-heading` | 14.4pt · lixdu | Column labels and sub-topics |
| H4 | `#### Item` | small uppercase · lixdu | Skill names, gear names, stat-block names |
| Body | a paragraph | 12pt · Titillium Web | All prose |
| Flavor | `> [!FLAVOR]` | 12pt italic · Titillium Web | In-world voice |
| Chevron banner | `# Title {.dc-chevron}` | H1 scale, angled fill | One per chapter opener |
| Spray banner | `## Title {.dc-spray}` | H2 scale, spray-paint fill | Learning paths, major topic breaks |
| Card tab | emitted by `@skill` | 9pt · Tomorrow | Skill-card tab labels |
| Tag | `<span class="dc-tag">` | 8pt · Tomorrow | Keyword and cost chips |

## Heading hierarchy

Each level rendered at its print size:

<div class="dg-stage">

# Chapter Title

## Section Heading

### Sub-section Label

#### Item Heading

</div>

## Heading chrome

Three classes dress a heading. The chevron opens a chapter, the spray breaks a major topic, and the spec-tweak rule flags an optional mechanic; `.dc-no-top` pulls it tight against whatever is above it.

```markdown
# Augmerc {.dc-chevron}

## Biting Distance {.dc-spray}

### Spec Tweak: Wired to Kill {.dc-spec-tweak .dc-no-top}
```

Result {.dg-result}

<div class="dg-stage">

@section .dc-banner-demo

# Augmerc {.dc-chevron}

## Biting Distance {.dc-spray}

### Spec Tweak: Wired to Kill {.dc-spec-tweak .dc-no-top}

@end-section

</div>

## Body and flavor

<div class="dg-stage">

Twelve-point Titillium Web carries all running narrative. Corporate enforcers earn their grafts in blood and overtime; street muscle runs cheaper and lasts longer than anyone admits. Notice the leading, the x-height, and how weight shifts when a word is **bolded** or *italicized* mid-sentence.

> [!FLAVOR]
> See an opening, ya take it. Best time to hit 'em is when they think it's over.

</div>

Flavor keeps the body size and switches to italic and `--ink-smoke`. Never set flavor in bold italic — it reads as urgency, not voice.

**Column-safe headings:** in a two-column layout use `###` and `####`. `#` and `##` at full print size exceed a 3.5-inch column.

## Smart typography

The renderer converts ASCII shortcuts as you type: `--` is an en dash --, `---` an em dash ---, `...` an ellipsis ..., and "straight quotes" curl. No special syntax, no Unicode entry.

## Font tokens

| Token | Face | Used for |
|---|---|---|
| `--font-display` | lixdu | H1–H3, banners |
| `--font-body` | Titillium Web | Body prose, flavor, quotes |
| `--font-mono` | Tomorrow | Code, counters, tabular data |
| `--font-tab` | Tomorrow | Short label text: card tabs, stat labels |
| `--font-quote` | Titillium Web | Italic quotes and attributions |

The fonts ship in the package and embed in the PDF at build time; a book never installs them.
