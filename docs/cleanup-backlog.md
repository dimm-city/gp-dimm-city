# Cleanup backlog

Styling left in place by the 2026-10-08 orphan audit, to review and clean up soon. Each item is unused by both books (Field Guide, Design Guide) but still reachable, so removing it is a decision rather than a deletion. Grep evidence for every line is in the audit report that accompanied PR #6.

## Kept as documented options (reviewed 2026-10-09)

Unused combinations left in place on purpose: `.dc-flush` on `.dc-stickers`, `.section > h2:first-child + table` (shares a selector with the live h3 half), `.dc-block h3/h4`, `.dc-sidebar-box > h3:first-child` and `p + p`, and `.dc-card-pull`.

## Dead-selector review (2026-10-12, 1.6.3)

Every selector in the stylesheets was matched against the rendered design guide and both books (Field Guide, SysOps). 94 matched nothing in the two books; 79 of those are used by the design guide, where `10-reference.md` documents them (`.dc-stat*`, `.dc-tape`, `.dc-spec-tweak`, `.dc-npc-compact`, `.dc-img-float-*`, `.dc-sidebar`, `.dc-human-callout`, `.dc-ap.<kind>`, the `blockquote + p` stat lines of `@npc-stat`, and others), so they stay. Of the 15 that match nothing at all, 2 are deleted (`.dc-skill-card:only-child`, `.dc-sidebar:empty`). The rest stay on purpose: element baselines (`body`, `kbd`, `samp`, `figure`), the rule that hides a stray `---` in a catalog or at the end of an entry (a test asserts it), the loose-list halves of selectors whose tight-list half is live (`.dc-alert li > p:first-child::before`, `.dc-section-choose li > p:first-child::before`), `.dc-specialty-intro > ol` beside its `ul`, and the options kept above.

## Still considering (owner, 2026-10-09)

Parked decisions. Nothing here is scheduled.

- **Field Guide sidebar areas.**
  - "Breaking the Lane" (chapter 2) is now a `@sidebar-box`, as a trial.
  - Still to decide: which other passages become sidebars. (The full-height inset rail was removed 2026-10-12.)
- **Specialty-card page redesign.** This is the Field Guide's "Choose a Specialty" catalog cards and the design guide's card-grid pages. CSS cleanup may change these pages in the meantime.
- **Configurable chapter prefix** (`css-roadmap.md`, review item 15). The design guide would then drop its six restated `@page` blocks and four chip resets.
- **Offset tokens** (`css-roadmap.md`, review item 14). `--dc-outline`, `--dc-chrome-bleed` and `--dc-z-*`, so that the offset literals are derived.
