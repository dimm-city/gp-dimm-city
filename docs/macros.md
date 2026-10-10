

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
- A skill belongs in a learning path and a path in a specialty. The plugin checks that and reports it in plain words: skills sitting directly in a specialty (one problem per run of them: "This skill (and any right after it) is outside a learning path…"), a learning path or specialty that starts inside a skill. The usual cause is an `@end-learning-path` above the skills it was meant to close.
- Each `####` heading in a skill is its own card, wearing the classes and attributes of the `@skill` line (`@skill {.dc-allow-split}`). Inside a path a card's tier is `PATHREF.N` unless its heading names one; `data-path-ref` is the enclosing specialty's code (`AUG`, `PRX`, … `PATH` for a specialty without one) and the path's number in it.
- `@continue` inside a skill's card closes the card and opens a `{name} ▸` continuation card. Anywhere else it is core's section continuation.
- `@end-skills` no longer exists, and `@end-skill` no longer closes the learning path around the skill.

**Content components.** `@card`, `@outcome` and `@procedure` are declared the same way, and rules (`dcCards`, `dcOutcomes`, `dcProcedures`) rewrite what sits inside each:

- `@card` is `div.dc-card`. Inside it the first `####` is `.dc-card-heading`, a quote straight after the heading is `.dc-card-pull`, everything else is `.dc-card-body`, and the last quote in the body is tagged `.dc-card-footer`. A card with only a heading has no body. It takes classes, `#id` and `key=value` attributes (`@card .dc-flaws`, `@card {.dc-flaws}`, `@card class=dc-flaws`).
- `@outcome` is `div.dc-outcomes`, one row per `roll | name | text` line, coloured by position (crit, hit, mixed, miss, fail; a sixth row is a plain hit). `@outcome flush` (or `.dc-flush`) adds `.dc-flush`. The lines can be in one paragraph or several, with or without blank lines around the markers.
- `@procedure` turns each numbered list inside it into the zero-padded step list (`ol.dc-steps`). It has no element of its own, so it adds no wrapper to the HTML.
- They nest like every declared marker. A `@card`, `@outcome` or `@procedure` written in a skill (even after its card, with no `@end-skill`) is part of that skill's card, so an outcome ladder under a skill's abilities is where it should be. A new one closes the one before it, `@end-<name>` closes it, and `@page`, `@section`, `@chapter` and `@continue` close them all. A closer directly under a list item or a quote is a closer: `@end-card` no longer needs a blank line before it.
- `@callout` and `@dm-note` (below) are declared too, and nest the same way: `@callout`, `@procedure`, `@end-procedure`, `@end-callout` is a callout with a procedure in it. One in a skill stays in the skill's card.
- A `@card` left open at the end of the document closes silently. A `@procedure` or `@outcome` left open gets core's `declared_marker_eof_close` warning, because whatever follows it is read as its steps or its rows. A closer with nothing open warns (`declared_marker_close_without_open`).
- The plugin reports, in plain words with the fix: an `@outcome` line that is not `roll | name | text`, a table, list or heading inside an `@outcome` (they are left out), an `@outcome` with no rows, and a `@procedure` with no numbered list (a bullet list does not count).

**Callouts.** `@callout` is a declared wrapper, `div.dc-alert` with the variant's class, and `@dm-note` is its alias with the `dm` variant preset (`@dm-note` is `@callout dm`; `@end-dm-note` closes it). The variant is a bare word: `note`, `warning`, `dm`, `vibe`, `origin`, `visit` or `gear`, as in `@callout vibe` or `@callout .float-right origin label="Image Is Everything"`. A core rule (`dcCallouts`) adds the variant's name as the label (`Dream Master Note` for `dm`) unless `label="…"` is given. No variant is a note.

- `variant=` is no longer accepted: `@callout variant=note` is read as a plain attribute, so the callout would be a note. The plugin reports each one in plain words, on its line: `@callout: no longer takes variant=note; write "@callout note" instead.`
- A bare word that is not a variant (`@callout vibes`) is a note, and core warns (`unknown_variant`).
- `> [!TYPE]` is the one-paragraph form of the same callouts (plus `FLAVOR` and `PULLQUOTE`).

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
`@gear`, `@end-gear`, `@lede`, `@end-lede`,
`@glossary`, `@end-glossary`,
`@column-panel`, `@end-column-panel`, `@tabbed`, `@end-tabbed`, `@card-grid`, `@end-card-grid`,
`@citizen-walkthrough`, `@end-citizen-walkthrough`, `@fiction-excerpt`, `@end-fiction-excerpt`,
`@npc-stat`, `@end-npc-stat`, `@flaws`, `@end-flaws`, `@ideals`, `@end-ideals`, `@dreams`, `@end-dreams`

**Retired — not implemented, do not use:** `@tape` (removed in 1.2.0: write the raw `<div class="dc-tape">Label</div>`; it can return as a declared marker once core has a self-closing marker, gutterpress#344), `@roll-table` / `@options-table` (use `@outcome` or a pipe table), `@chapter-opener` (the chapter-opener composite is markup-driven now — see the design guide's page-templates chapter) and `@class-entry` / `@end-class-entry` (retired 2026-05-24; its CSS was parked in `css/deprecated.css`). Neither marker is recognised by the plugin, so both pass through as literal text.