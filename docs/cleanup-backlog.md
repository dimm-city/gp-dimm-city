# Cleanup backlog

Styling left in place by the 2026-10-08 orphan audit, to review and clean up soon. Each item is unused by both books (Field Guide, Design Guide) but still reachable, so removing it is a decision rather than a deletion. Grep evidence for every line is in the audit report that accompanied PR #6.

## 1. Distance tags

`.dc-distance-tags`, `.dc-dist-tag`, `.dc-dist-ap`, `.dc-dist-name` (`styles/components/data.css`) and the tokens `--dc-dist-ap-color`, `--dc-dist-name-color`, `--dc-dist-tag-border`, `--dc-dist-tag-surface` (`styles/dc-component-defaults.css`).

The plugin still emits the markup for a `Distance` table inside a skill (`buildDistanceTags` and the `"distance"` branch of `classifyTable` in `plugin.js`, covered by `test/plugin.test.js`). No book has such a table. Decide whether to keep the feature; removing it means removing the plugin code and tests too. Catalog entry: `distance-tags` (`unused`).

## 2. Inset-sidebar rail rules

`.dc-sidebar.inset hr`, `hr + p`, `hr ~ p` and `.dc-sidebar.inset > p:last-child:not(:first-of-type)` (`styles/components/images.css`), with their tokens `--dc-sidebar-callout-accent` and `--dc-sidebar-callout-bg`. The design guide's one inset sidebar has no `---` in it, so none of these fire.

## 3. Combinations no book uses yet

Each class is live on its own, but never in this combination:

- `.dc-flush` on stickers, ledes, sub-headers and procedures (`.dc-stickers.dc-flush`, `.dc-intro.dc-flush`, `.dc-sub-header.dc-flush` in `chrome.css`; `.dc-steps.dc-flush` in `data.css`). `.dc-flush` is an author modifier, so these may be wanted.
- `.dc-intro + .dc-alert` (`chrome.css`): the lede-then-note pattern it was written for is no longer adjacent anywhere.
- `.dc-card-grid > h2`, `> h3`, `> .dc-intro` (`section.css`, `page-templates.css`): the headings and ledes sit outside the grid.
- `.section > h2:first-child + table`, `.section > h2.dc-h3:not(:first-child)`, `.dc-block h3/h4`, `.dc-sidebar-box > h3:first-child`, `.dc-sidebar-box p + p`, `.dc-toc ol > li > strong`, `.dc-skill-card.dc-two-col .dc-card-inner table`/`ul > li`.
- `.dc-card-pull` (`section.css`): emitted for a blockquote after a `@card` heading; only `snippets/card.md` uses it.
