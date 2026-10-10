# Plan: per-specialty variants for section components

Status: planned, not started. For a later session.

## Goal

An author writes `@npc-stat wirephreak` (or `@column-panel augmerc`) and the
section takes on that specialty's colours and corner shapes, the same way a
skill card does inside `@specialty .wirephreak`. Autocomplete then offers
`@npc-stat wirephreak`, `@npc-stat augmerc`, … with no extra work, because
Gutterpress lists every declared variant.

## Where things stand (1.2.0)

- The nine section components (`@column-panel`, `@tabbed`, `@card-grid`,
  `@citizen-walkthrough`, `@fiction-excerpt`, `@npc-stat`, `@flaws`,
  `@ideals`, `@dreams`) are `section: true` markers with **no variants**,
  because no section style changes per specialty today.
- Specialty theming lives only on `.dc-specialty.<name>`
  (`styles/components/specialty-identity.css`). Each block sets the identity
  tokens `--spec-accent`, `--spec-mid` and `--spec-dark` plus its shape
  polygons. Four shared wiring rules then read `--spec-*` into the skill
  card, path shell, specialty intro and specialty card.
- A variant is one extra class (Gutterpress rule: a variant only adds a class).

## Proposed design

1. **Variant class = the specialty's own class name.** Declare one shared
   table, used by every section component that should be themable:

   ```js
   const specialtyVariants = {
     augmerc: 'augmerc', proxy: 'proxy', streetwarden: 'streetwarden',
     gutterdruid: 'gutterdruid', cybersurgeon: 'cybersurgeon',
     wirephreak: 'wirephreak', technosorcerer: 'technosorcerer',
     etherlock: 'etherlock', dualist: 'dualist', generalist: 'generalist',
   };
   'npc-stat': { section: true, class: 'dc-npc-stat', variants: specialtyVariants },
   ```

   `@npc-stat wirephreak` then renders
   `<div class="section dc-npc-stat wirephreak">`, exactly what
   `@section .dc-npc-stat .wirephreak` gives. Books can use either spelling.

2. **Reuse the identity blocks; don't copy them.** Widen each identity
   selector from `.dc-specialty.<name>` to `:is(.dc-specialty, .section).<name>`,
   so a themed section gets the same `--spec-*` tokens and polygons. Nothing
   else in those blocks changes.

3. **Add the per-section wiring once.** For each themable section style, add
   one rule in `styles/components/section.css` that reads `--spec-*` into
   that section's own custom properties (border, header background, title
   colour, corner shape). It falls back to today's look when no specialty
   class is present. That gives one rule per section, not one per specialty
   per section.

4. **Decide which sections are themable.** This is a design call, to be
   made with the visual review rather than up front. The likely candidates
   are `@npc-stat`, `@column-panel` and `@fiction-excerpt`. `@flaws`,
   `@ideals` and `@dreams` already carry their own accent, so leave them out
   unless the review says otherwise.

## Work list

1. Design pass: mock the candidate sections in two or three specialties in
   the design guide and pick the token mapping (header, border, shape).
   Resize screenshots before any judge review (repo rule 0b).
2. CSS: widen the identity selectors and add the wiring rules.
3. Plugin: the `specialtyVariants` table on the chosen markers. Update the
   snippets only if the structure changes; it shouldn't.
4. Docs: `docs/macros.md`, `components.yaml` and a design-guide page
   showing each themed section in every specialty.
5. Tests: one test for the declared versus `@section` spelling, for one
   variant. Accept snapshot changes for the new design-guide page only.

## Checks before release

- `bun run book-diff` against both books must show no change. They don't use
  the variants yet, and widening the selector must not leak onto sections
  that sit inside a `@specialty`.
  - Watch for this leak: a `.section.augmerc` inside `.dc-specialty.proxy`
    would now set its own tokens, which is intended. But an existing
    `@section .augmerc` in a book would start picking up the theme. Grep
    both books for `@section` lines carrying a specialty class before
    widening.
- The plugin's `integrity.test.js` must stay green, including no component
  sheet selecting `.page` or `.chapter`.
- Gutterpress's `unknown_variant` warning (planned for 0.11.16-alpha.3)
  will flag misspelled specialty words once these variants exist.
