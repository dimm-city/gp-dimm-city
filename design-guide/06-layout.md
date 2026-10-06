@chapter #ch-layout .layout .dg-guide ch="2"

# Layout & Composition

@lede

Multi-column splits, floated art, sidebar wrappers, and page-break utilities.

@end-lede

@page

## Layout Utilities Reference

| Syntax | Effect | Notes |
|--------|--------|-------|
| `@section .gp-columns-2` … `@end-section` | Two equal columns with column rule | Gutterpress core vocabulary — columns and nothing else |
| `@section .gp-columns-3` … `@end-section` | Three narrow columns | Best for short reference entries |
| `+ .dc-column-panel` | Wrap the run in the DC column-panel card | Substrate + top/bottom rules; the leading H2/H3 becomes a full-width spanning bar and its first paragraph a shared preamble |
| `@sidebar` … `@end-sidebar` | Right-floated aside at 38% width | Emits `.dc-sidebar`; add `class="inset"` inside an `@page .page-sidebar` for the full-height rail |
| `@column-break` | Force next column | Use inside `@section .gp-columns-2` / `.gp-columns-3` |
| `![]{.dc-img-float-right}` | Float image right, 44% width | Text wraps left |
| `![]{.dc-img-float-left}` | Float image left, 44% width | Text wraps right |
| `@section .gp-no-break` | Prevent block splitting across pages | — |
| `## Heading {.gp-break-before}` | Force new page before element | — |

@section .gp-columns-2 .dc-column-panel

**Two-column behavior:** text fills the left column top-to-bottom and overflows right automatically. A two-column block can break across pages — wrap in `@section .gp-no-break` to keep it together.

**Image float behavior:** floated image occupies 44% of column width; after the float clears, text returns to full width. Add a blank line below the float to clear it explicitly if following content crowds the image.

**Sidebar wrapper:** `@sidebar` emits `.dc-sidebar`. Use `@sidebar class="inset"` for the full-height rail — it must sit inside an `@page .page-sidebar` page, which is what reserves the column the rail stands in. Used on an ordinary page it falls back to the plain floated sidebar rather than covering the body text. Use raw HTML only when you need a structure the sidebar contains, not to author the sidebar shell itself.

@end-section

@section .gp-columns-2 .dc-column-panel

```markdown
@section .gp-columns-2 .dc-column-panel

Left column content.

@column-break

Right column content.

@end-section
```

```markdown
@sidebar
> [!NOTE]
> Free counters trigger only once per round.

@end-sidebar

Body text wraps to the left of the sidebar automatically.
```

@end-section

@section .gp-columns-2 .dc-column-panel

```markdown
@page .page-sidebar
Body text for this page stops at the rail's edge.

@sidebar class="inset"
### Sidebar

Inset sidebar content for page templates like rules references.
@end-sidebar
@page
```

```markdown
@section .gp-no-break
Content that must not split across a page break.
@end-section

## New Section {.gp-break-before}
```

@end-section

---

## See It In Action

These examples show the above layout utilities applied to real book pages using actual Dimm City Field Guide content.

- [Chapter Openers](#ch-example-chapter-opener) — two-column opener layout with column-break between fiction and rules columns
- [Specialty Profile](#ch-example-specialty-profile) — two-column ability spreads and image floats alongside skill cards
- [Rules & Mechanics](#ch-example-rules) — sidebar wrappers with rules callouts beside body prose
- [Dream Master Pages](#ch-example-dm-npcs) — sidebar float with portrait and field notes in citizen-file pages
- [Gear & Tech](#ch-example-gear-tech) — three-column gear tables and floated art plates
