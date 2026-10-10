# Adding A DC Macro

This is the shortest safe path for adding a new Dimm City plugin macro.

Use the existing `@skill` implementation in `plugin.js` as the main reference (the `skill` entry in `markers` and the `dcSkillCards` rule). It follows the right model:

- one real root class: `.dc-skill-card`
- **no per-card variant** — shapes come from the `.dc-specialty.<name>` parent container (CSS parent-selector model, not card-level attributes)
- internal styling through descendant selectors: `.dc-skill-card .dc-card-tab`, `.dc-skill-card .dc-card-body`, `.dc-skill-card .dc-ability`

For new macros, prefer the simplest version that works. In many cases you do not need extra child classes at all. A root shell plus descendant element selectors is often enough, which keeps both the plugin and the markdown simpler.

## Variant system note

Card variants (skill cards, path shells, specialty cards, specialty intros) are controlled entirely by the `.specialty.<name>` parent container, not by `variant=` attributes. The `@specialty augmerc` (or `@specialty .augmerc`) wrapper applies the augmerc clip-path and accent color to every card inside automatically. Do NOT add `variant=` attributes to `@skill`, `@continue`, or `@learning-path`.

## Declared markers (the default for a plain wrapper)

A wrapper that only needs an element and classes does not belong in the `dimm_city_transform` state machine. It is one line in the `markers` table exported at the bottom of `plugin.js`, and Gutterpress core does the rest: parsing, author classes, `#id`, `data-source-range`, nesting, closing at the next `@page`/`@section`/`@chapter`, and the `unknown_marker` typo check.

```js
export const markers = {
  sidebar: wrapper('dc-sidebar', { variants: { inset: 'inset' } }),
  block: wrapper('dc-block', {
    variants: { panel: 'dc-panel', slate: 'dc-slate' },
    label: { tag: 'div', class: 'dc-block-title', from: 'attr:label' },
  }),
};
```

`wrapper(cls, extra)` is a two-line helper in `plugin.js` that adds `autoCloseAt: ['eof']`, so a wrapper left open at the end of a file closes silently, as these always have. To add one:

1. Add its line to `markers` (kebab-case name; `end-` names are reserved for the auto-derived closer).
2. Add `snippets/<name>.md`, whose first line is the marker. The editor inserts it when the author types `@`.
3. Add the CSS, the `components.yaml` entry and the design-guide specimen as usual.

Things to know:

- A **variant** is a bare word on the marker line (`@sidebar inset`). It adds the mapped class and a `data-<marker>="<variant>"` attribute; nothing else changes. The `.inset` class shorthand keeps working beside it.
- A **label** (`label="…"`) becomes a child element with the declared class, plus `data-label` on the wrapper.
- Declared containers nest as a stack. Opening a second one of the same kind closes the first and everything opened after it; `@end-<name>` closes that container and everything inside it; `@page`, `@section`, `@chapter` and `@continue` close them all. Hand-written markers do not close them.
- Attributes follow core's rules: `key=value` becomes `data-key`, `#id` becomes `id`.
- Declared markers are a Gutterpress feature. Under a bare `new MarkdownIt().use(plugin)` they are not recognised, so tests that cover them render through `createMarkdownRenderer([{ name, plugin, options, markers }])`.
- A **hand-written** marker whose name is within a couple of edits of a declared one gets a false `unknown_marker` warning from core. `@specialty-card` triggered it next to `@specialty-art`, so it is declared too; its odd/even `data-position` comes from a small core rule (`dcSpecialtyCardPositions`) that numbers the open tokens.

### A section-styled component

A component whose CSS lives on `.section.dc-x` is a core section with a class, not a wrapper element. Declare it with `section: true` instead of `wrapper(…)`:

```js
'npc-stat': { section: true, class: 'dc-npc-stat' },
```

Core rewrites `@npc-stat` into `@section .dc-npc-stat` (plus any author classes), so the HTML is exactly what the hand-written `@section` spelling gives and existing books are untouched. `@end-npc-stat` acts as `@end-section`, `@continue` keeps the class, and the section closes at the next `@section`/`@page` like any other. `section: true` cannot be combined with `tag`, `label` or `autoCloseAt`.

Add `variants` only when the CSS styles the component differently per variant word (`@block panel`); a variant only adds a class and a `data-<marker>` attribute. None of the section components has one: per-specialty styling lives on `.dc-specialty.<name>`, from `@specialty`. Modifiers such as `.gp-columns-2`, `.dc-plain` and `.dc-snug` stay author classes.

Declared today (wrappers): `@sidebar`, `@sidebar-box`, `@definition`, `@specialty-intro`, `@specialty-art`, `@specialty-card`, `@gear`, `@toc`, `@lede`, `@glossary`, `@block`. Declared today (sections): `@column-panel`, `@tabbed`, `@card-grid`, `@citizen-walkthrough`, `@fiction-excerpt`, `@npc-stat`, `@flaws`, `@ideals`, `@dreams`. Declared and transformed: `@specialty` (variants `augmerc` … `generalist`), `@learning-path`, `@skill`. Everything else below is still hand-written in `plugin.js`.

### Declare, then transform (a macro that rebuilds its content)

A macro that turns its markdown into its own structure (a `####` into a card tab, a list into sticker chips) is still declared in `markers`. Core then parses, nests, closes and source-maps it, and gives the plugin a token pair to work on: a `layout_component_open` / `layout_component_close` whose open token carries `meta = { line, component, kind, variant, attrs, labelled }`. `kind` is the marker name. The plugin writes an ordinary markdown-it core rule that finds those pairs and rewrites the tokens between them. No flags, no state machine, no closing logic: core already did the nesting.

```js
// declare it: core owns the parsing and the closing
'learning-path': wrapper('dc-learning-path dc-path-block'),

// transform it: a core rule over the tokens between each open/close pair
function dcLearningPaths(state) {
  forEachComponent(state.tokens, 'learning-path', (run, enclosing) => {
    const [open, close] = [run[0], run[run.length - 1]];
    open.attrSet('data-path-ref', refFor(enclosing));   // enclosing: the open tokens of its parents
    return [open, ...rewrite(run.slice(1, -1)), close]; // or return nothing to leave the run alone
  });
}
md.core.ruler.push('dc_learning_paths', dcLearningPaths); // in the plugin function
```

`forEachComponent(tokens, kind, rewrite)` is a small helper in `plugin.js` (about 20 lines, inlined because plugin code cannot import anything). It calls `rewrite(run, enclosing)` for each component whose `meta.kind` matches, in document order.

Rules of thumb:

- Register the rule with `md.core.ruler.push` after `dimm_city_transform`, so a `@card` or `@procedure` inside the component is already rewritten when your rule looks at it.
- The declared token renders as `<div class="…">` with the author's classes and `data-*` attributes. Keep it as the element when that is what you want (`@learning-path`), or set `open.hidden = close.hidden = true` and render its attributes yourself when one marker makes several elements (`@skill`: one card per `####`).
- Read the enclosing components from `enclosing`, not from a global: `@learning-path` takes its `data-path-ref` from the enclosing `@specialty`, whichever way the specialty was spelled.
- Structure rules (what may sit inside what) go in the declaration's `validate(component)`, not in the transform. It receives `{ name, variant, attrs, line, text, blocks }`, where a nested marker is `{ type: 'component', name, line }`, and returns problem messages (or `{ message, line }`) in plain language, with the fix. Core reports them as layout warnings, so they reach `gutterpress validate`, the Problems panel and the build log.
- Test through `createMarkdownRenderer([{ name, plugin, options, markers }])`: a bare `new MarkdownIt().use(plugin)` never sees `markers`.

## Currently registered macros

`@chapter`, `@page`, `@section`, `@end-section`, `@spread`, `@page-break`, `@column-break`, `@specialty`, `@end-specialty`,
`@specialty-intro`, `@end-specialty-intro`, `@specialty-art`, `@end-specialty-art`,
`@specialty-card`, `@end-specialty-card`,
`@learning-path`, `@end-learning-path`, `@skill`, `@end-skill`, `@continue`,
`@outcome`, `@end-outcome`,
`@block`, `@end-block`, `@card`, `@end-card`,
`@sidebar`, `@end-sidebar`, `@sidebar-box`, `@end-sidebar-box`,
`@definition`, `@end-definition`, `@procedure`, `@end-procedure`,
`@callout`, `@end-callout`, `@dm-note`, `@end-dm-note`,
`@toc`, `@end-toc`,
`@gear`, `@end-gear`, `@tape`, `@lede`, `@end-lede`,
`@glossary`, `@end-glossary`

> **Deprecated (removed in plugin 17.3.0):** `@roll-table`, `@end-roll-table`, `@options-table`, `@end-options-table` are stripped as no-ops and emit no HTML or styling. Do not use them in new content.
>
> **Deprecated (2026-05-24):** `@class-entry` / `@end-class-entry` and the
> `.section.dc-class-entry` CSS were retired after zero production usage. The
> CSS was parked in `css/deprecated.css`, which has since been deleted —
> the dc-op-manual repo's history (`dc-design-guide/css/deprecated.css`) has the rules. Do not use
> them in new content — author the same layout with `@section .dc-class-entry`
> plus structural child elements (see the design guide's page-templates chapter).
>
> **Retired — `@chapter-opener`:** never re-add it. The chapter-opener composite
> is markup-driven: `markers.js` injects
> `<div class="chapter-opener" data-chapter-label="C.NN">` as the first child of
> a labeled chapter's first page, and `styles/components/*.css` style it plus the
> `.chapter[data-chapter-label] > .page[data-page="intro"] > .section` chain.
> The plugin registers no `@chapter-opener` marker.

## Blank-line requirement for markers

Macro open and close markers **must** be separated from surrounding content by blank lines. Without the blank lines, markdown-it merges the marker line into the preceding or following paragraph and the macro is silently ignored.

Correct:

```markdown
@callout
This is the callout body.

More content here.

@end-callout
```

Wrong (markers merged into paragraph — macro never fires):

```markdown
@callout
This is the callout body.
@end-callout
```

The rule applies to every open marker (`@macro-name`) and every close marker (`@end-macro-name`):

- Open marker: must have a blank line **after** it before the first content line.
- Close marker: must have a blank line **before** it after the last content line.

When two macros appear back-to-back (e.g. multiple `@skill` cards inside a `@learning-path`), each open/close pair must still follow this rule — no two markers should share the same paragraph block.

This is a markdown-it parsing constraint, not a plugin limitation. If a macro appears to render nothing, missing blank lines around its markers are the first thing to check.

## 1. Design the emitted HTML first

Before touching the parser, decide the exact root class and inner hooks.
(`dc-intel-card` below is a made-up example; the package ships no such
component.)

Good shape:

```html
<section class="dc-intel-card variant-2">
  <div class="dc-intel-card-head">Black Site</div>
  <div class="dc-intel-card-body">
    <p>Body copy.</p>
  </div>
</section>
```

Even simpler shape:

```html
<section class="dc-intel-card variant-2">
  <h3>Black Site</h3>
  <p>The vault is below street level.</p>
  <ul>
    <li>Two drone nests</li>
    <li>One blind service tunnel</li>
  </ul>
</section>
```

Rules:

- Emit one top-level `dc-` class for the component shell.
- Put variant classes on that same root element.
- Style internals with descendant selectors, not separate top-level sibling classes.
- Prefer descendant element selectors like `.dc-intel-card h3` and `.dc-intel-card p + p` when the content structure is simple and stable.
- Add child classes only when you need repeated roles that plain elements cannot identify clearly.
- Only expose a small variant API: surface, accent, foreground, title treatment.
- Do not turn padding, margins, widths, or break behavior into a large custom-property API.

## 2. Add the marker to `plugin.js`

For a simple wrapper macro, use the `markers` table above instead of the hand-written pattern below. A macro that rebuilds its content, like `@skill`, is declared too and transformed by a core rule (see "Declare, then transform" above). The hand-written `dimm_city_transform` handlers that remain (`@card`, `@outcome`, `@procedure`, `@callout`, `@dm-note`, `@tape`) follow this pattern, and are not the one to copy for a new macro:

```js
const intelMarker = parseMarker(tok, tokens, i, '@intel-card');
if (intelMarker.matched) {
  const userAttrs = { ...intelMarker.attrs };
  const variant = userAttrs['variant'] ? ' variant-' + esc(userAttrs['variant']) : '';
  delete userAttrs['variant'];

  newTokens.push(
    makeToken(
      'html_block',
      '<section' + buildAttrs(userAttrs, 'dc-intel-card' + variant) + '>\n'
    )
  );
  i += 2;
  continue;
}

if (isMarker(tok, tokens, i, '@end-intel-card')) {
  newTokens.push(makeToken('html_block', '</section>\n'));
  i += 2;
  continue;
}
```

If the macro has structure, parse markdown tokens into named child elements the same way `@skill` turns:

- `####` into the card title
- `>` into flavor text
- ordered lists into ability rows

That is usually better than asking authors to write raw HTML.

If the macro is just a shell around normal markdown content, do less: open the wrapper, let standard markdown render `h3`, `p`, `ul`, and `li`, then close the wrapper. That keeps the parser logic small and avoids creating extra internal hook classes you do not really need.

## 3. Add CSS in `styles/components/cards.css`

The root class owns the shell. Inner parts are descendants.

```css
.dc-intel-card {
  --dc-intel-bg: var(--paper-light);
  --dc-intel-accent: var(--hud-blue);
  --dc-intel-fg: var(--ink);

  background: var(--dc-intel-bg);
  border-left: 4px solid var(--dc-intel-accent);
  color: var(--dc-intel-fg);
  padding: var(--space-lg) var(--space-xl);
  break-inside: avoid;
  page-break-inside: avoid;
}

.dc-intel-card .dc-intel-card-head {
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: var(--ls-display);
  margin: 0 0 8pt;
}

.dc-intel-card p {
  margin: 0;
}

.dc-intel-card p + p,
.dc-intel-card ul,
.dc-intel-card ol {
  margin-top: 6pt;
}
```

Simpler still, with no child classes beyond the shell:

```css
.dc-intel-card {
  --dc-intel-bg: var(--paper-light);
  --dc-intel-accent: var(--hud-blue);
  --dc-intel-fg: var(--ink);

  background: var(--dc-intel-bg);
  border-left: 4px solid var(--dc-intel-accent);
  color: var(--dc-intel-fg);
  padding: var(--space-lg) var(--space-xl);
  break-inside: avoid;
  page-break-inside: avoid;
}

.dc-intel-card h3 {
  margin: 0 0 8pt;
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: var(--ls-display);
}

.dc-intel-card p,
.dc-intel-card ul,
.dc-intel-card ol {
  margin: 0;
}

.dc-intel-card p + p,
.dc-intel-card p + ul,
.dc-intel-card p + ol,
.dc-intel-card ul + p,
.dc-intel-card ol + p,
.dc-intel-card ul + ul,
.dc-intel-card ol + ol {
  margin-top: 6pt;
}
```

That pattern is usually the right default for a new wrapper macro:

- plugin emits one shell class
- markdown stays normal
- CSS targets descendant elements inside the shell
- variants only change the shell-level public API

## 4. Add thin root-level variants

Variants should override only the small public API or a truly exceptional property.

```css
.dc-intel-card.variant-2 {
  --dc-intel-bg: var(--paper-aged);
  --dc-intel-accent: var(--crimson);
}

.dc-intel-card.variant-3 {
  --dc-intel-bg: var(--ink-dark);
  --dc-intel-fg: var(--paper-cream);
  --dc-intel-accent: var(--amber);
}
```

Use semantic variant names when they represent meaning. Numeric `variant="N"` is a valid pattern for new macros when the variants are just preset visual shells.

> **DC-specific rule:** Do NOT use `variant=` on `@skill`, `@continue`, or `@learning-path`. Those macros derive their visual shape entirely from the `.specialty.<name>` parent container — a `@specialty .augmerc` wrapper applies the correct clip-path and accent to every card inside automatically. `variant=` on a skill or path card is a no-op and must be removed.

## 5. Add markdown examples

Simple wrapper example:

```markdown
@intel-card variant="2" #black-site
### Black Site
The vault is below street level.

- Two drone nests
- One blind service tunnel
@end-intel-card
```

Simplest authoring form:

```markdown
@intel-card variant="2" #black-site
### Black Site
The vault is below street level.

- Two drone nests
- One blind service tunnel
@end-intel-card
```

The plugin does not need to convert `###`, paragraphs, or lists into custom internal HTML for that version. It can just emit the opening and closing shell and let markdown render the contents normally.

If you want the macro to behave more like `@skill`, document the intended structure explicitly:

```markdown
@intel-card variant="3"
#### Black Site
> Quiet on the outside. Surgical on the inside.
1. **Entry:** Service lift behind the noodle stand.
2. **Heat:** Corporate response in 2 rounds.
@end-intel-card
```

## 6. Validate it in the guide

- Add a specimen in the appropriate guide chapter.
- Confirm the emitted class has a matching rule in `components/cards.css`.
- Add or update the component's entry in `../components.yaml`.
- Keep the component root-owned: one `.dc-*` shell, thin root variants, descendant selectors underneath.

## Skill Card Checklist

When in doubt, copy these decisions from `@skill`:

- root class owns variant state
- child structure is fixed and predictable
- descendant selectors style internals
- variants are thin and live on the root
- markdown authors write content structure, not HTML chrome

For simpler macros, reduce that even further:

- one shell class on the wrapper
- one optional root variant class
- descendant element selectors for headings, paragraphs, and lists
- no extra child classes unless they solve a real structural problem
