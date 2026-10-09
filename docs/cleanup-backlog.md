# Cleanup backlog

Styling left in place by the 2026-10-08 orphan audit, to review and clean up soon. Each item is unused by both books (Field Guide, Design Guide) but still reachable, so removing it is a decision rather than a deletion. Grep evidence for every line is in the audit report that accompanied PR #6.

## 1. Inset-sidebar rail rules

`.dc-sidebar.inset hr`, `hr + p`, `hr ~ p` and `.dc-sidebar.inset > p:last-child:not(:first-of-type)` (`styles/components/images.css`), with their tokens `--dc-sidebar-callout-accent` and `--dc-sidebar-callout-bg`. The design guide's one inset sidebar has no `---` in it, so none of these fire.

Kept pending a trial of @sidebar-box / sidebars in the Field Guide (owner, 2026-10-09).

## Kept as documented options (reviewed 2026-10-09)

Unused combinations left in place on purpose: `.dc-flush` on `.dc-stickers`, `.section > h2:first-child + table` (shares a selector with the live h3 half), `.dc-block h3/h4`, `.dc-sidebar-box > h3:first-child` and `p + p`, per-card `.dc-skill-card.dc-two-col .dc-card-inner table`/`ul > li`, and `.dc-card-pull`.
