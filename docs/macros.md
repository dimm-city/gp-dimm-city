

The canonical inventory of macros and classes is `../components.yaml`; `../README.md` lists the macros an author reaches for.

### Plugin class naming convention

All classes emitted by `plugin.js` must use the `dc-` prefix
(e.g. `dc-note-callout`, `dc-outcomes-label`). When adding new plugin output,
always check that the emitted class name has a matching CSS rule before shipping.


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
`@glossary`, `@end-glossary`

**Deprecated (removed in plugin 17.3.0):** `@roll-table`, `@end-roll-table`, `@options-table`, `@end-options-table`. These markers are stripped as no-ops and emit no HTML or styling. Do not use them in new content.

**Retired — not implemented, do not use:** `@chapter-opener` (the chapter-opener composite is markup-driven now — see the design guide's page-templates chapter) and `@class-entry` / `@end-class-entry` (retired 2026-05-24; its CSS was parked in `css/deprecated.css`). Neither marker is recognised by the plugin, so both pass through as literal text.