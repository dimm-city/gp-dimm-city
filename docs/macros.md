

The canonical inventory of macros and classes is `../components.yaml`; `../README.md` lists the macros an author reaches for.

### Plugin class naming convention

All classes emitted by `plugin.js` must use the `dc-` prefix
(e.g. `dc-skill-card`, `dc-outcomes-label`). When adding new plugin output,
always check that the emitted class name has a matching CSS rule before shipping.


**Declared markers.** `@sidebar` (`inset`), `@sidebar-box`, `@definition`, `@specialty-intro`, `@specialty-art`, `@specialty-card`, `@gear`, `@toc`, `@lede`, `@glossary` and `@block` (`panel`, `slate`, `shard`, `codex`) are declared in the `markers` table exported by `plugin.js`, so Gutterpress core parses and closes them.

**Declared section markers.** `@column-panel`, `@tabbed`, `@card-grid`, `@citizen-walkthrough`, `@fiction-excerpt`, `@npc-stat`, `@flaws`, `@ideals` and `@dreams` are the section-styled components, declared with `section: true`. Each is a real core `@section` carrying one class, so `@npc-stat` and `@section .dc-npc-stat` render the same element and classes (the declared form also writes `data-<marker>` only when a variant word is given, and none of these has variants). `@end-npc-stat` acts as `@end-section`; the section closes at the next `@section`/`@page` like any section, and `@continue` keeps its class. Books that write `@section .dc-…` keep working unchanged. Modifiers (`.gp-columns-2`, `.dc-plain`, `.dc-snug`, `.dc-allow-split`, `.dc-cards-two-col`) stay author classes: `@column-panel .gp-columns-2`. See [adding-macros.md](./adding-macros.md#declared-markers-the-default-for-a-plain-wrapper) for how to add one.

**Declared, then transformed.** `@specialty`, `@learning-path` and `@skill` are declared in the same table, so core opens, nests and closes them, and the plugin's core rules rewrite what sits inside each (`dcLearningPaths`, `dcSkillCards`). They nest as specialty > learning path > skill:

- `@specialty augmerc` and `@specialty .augmerc` (or `{.augmerc}`) are the same wrapper. The names are `augmerc`, `proxy`, `streetwarden`, `gutterdruid`, `cybersurgeon`, `wirephreak`, `technosorcerer`, `etherlock`, `dualist` and `generalist`, the specialties `.dc-specialty.<name>` styles.
- Opening a marker that is already open closes it and everything inside it: a second `@skill` closes the first, a second `@learning-path` closes the first path and its skills, a second `@specialty` closes everything. `@end-<name>` closes that marker and what is inside it, so `@end-skill` closes only the skill and `@end-learning-path` closes the path with its skills. `@page`, `@section`, `@chapter` and `@continue` close all three; use `@page-break` to break the page inside a specialty. A closer with nothing open warns (`declared_marker_close_without_open`).
- A skill belongs in a learning path and a path in a specialty. The plugin checks that and reports it in plain words: a skill sitting directly in a specialty ("This skill is outside a learning path…"), a learning path or specialty that starts inside a skill. The usual cause is an `@end-learning-path` above the skills it was meant to close.
- Each `####` heading in a skill is its own card, wearing the classes and attributes of the `@skill` line (`@skill {.dc-allow-split}`). Inside a path a card's tier is `PATHREF.N` unless its heading names one; `data-path-ref` is the enclosing specialty's code (`AUG`, `PRX`, … `PATH` for a specialty without one) and the path's number in it.
- `@continue` inside a skill's card closes the card and opens a `{name} ▸` continuation card. Anywhere else it is core's section continuation.
- `@end-skills` no longer exists, and `@end-skill` no longer closes the learning path around the skill.

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