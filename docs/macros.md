

The canonical inventory of macros and classes is `../components.yaml`; `../README.md` lists the macros an author reaches for.

### Plugin class naming convention

All classes emitted by `plugin.js` must use the `dc-` prefix
(e.g. `dc-skill-card`, `dc-outcomes-label`). When adding new plugin output,
always check that the emitted class name has a matching CSS rule before shipping.


**Declared markers.** `@sidebar` (`inset`), `@sidebar-box`, `@definition`, `@specialty-intro`, `@specialty-art`, `@specialty-card`, `@gear`, `@toc`, `@lede`, `@glossary` and `@block` (`panel`, `slate`, `shard`, `codex`) are declared in the `markers` table exported by `plugin.js`, so Gutterpress core parses and closes them.

**Declared section markers.** `@column-panel`, `@tabbed`, `@card-grid`, `@citizen-walkthrough`, `@fiction-excerpt`, `@npc-stat`, `@flaws`, `@ideals` and `@dreams` are the section-styled components, declared with `section: true`. Each is a real core `@section` carrying one class, so `@npc-stat` and `@section .dc-npc-stat` render the same element and classes (the declared form also writes `data-<marker>` only when a variant word is given, and none of these has variants). `@end-npc-stat` acts as `@end-section`; the section closes at the next `@section`/`@page` like any section, and `@continue` keeps its class. Books that write `@section .dc-…` keep working unchanged. Modifiers (`.gp-columns-2`, `.dc-plain`, `.dc-snug`, `.dc-allow-split`, `.dc-cards-two-col`) stay author classes: `@column-panel .gp-columns-2`. See [adding-macros.md](./adding-macros.md#declared-markers-the-default-for-a-plain-wrapper) for how to add one.

**All shipped macros:**
`@chapter`, `@page`, `@section`, `@end-section`, `@spread`, `@page-break`, `@column-break`, `@specialty`, `@end-specialty`,
`@specialty-intro`, `@end-specialty-intro`, `@specialty-art`, `@end-specialty-art`,
`@specialty-card`, `@end-specialty-card`, `@learning-path`, `@end-learning-path`,
`@skill`, `@end-skill`, `@continue`, `@outcome`, `@end-outcome`,
`@block`, `@end-block`, `@card`, `@end-card`,
`@sidebar`, `@end-sidebar`, `@sidebar-box`, `@end-sidebar-box`,
`@definition`, `@end-definition`, `@procedure`, `@end-procedure`,
`@callout`, `@end-callout`, `@dm-note`, `@end-dm-note`,
`@toc`, `@end-toc`,
`@gear`, `@end-gear`, `@tape`, `@lede`, `@end-lede`,
`@glossary`, `@end-glossary`,
`@column-panel`, `@end-column-panel`, `@tabbed`, `@end-tabbed`, `@card-grid`, `@end-card-grid`,
`@citizen-walkthrough`, `@end-citizen-walkthrough`, `@fiction-excerpt`, `@end-fiction-excerpt`,
`@npc-stat`, `@end-npc-stat`, `@flaws`, `@end-flaws`, `@ideals`, `@end-ideals`, `@dreams`, `@end-dreams`

**Deprecated (removed in plugin 17.3.0):** `@roll-table`, `@end-roll-table`, `@options-table`, `@end-options-table`. These markers are stripped as no-ops and emit no HTML or styling. Do not use them in new content.

**Retired — not implemented, do not use:** `@chapter-opener` (the chapter-opener composite is markup-driven now — see the design guide's page-templates chapter) and `@class-entry` / `@end-class-entry` (retired 2026-05-24; its CSS was parked in `css/deprecated.css`). Neither marker is recognised by the plugin, so both pass through as literal text.