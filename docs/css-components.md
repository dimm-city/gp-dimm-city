
**What Good Component CSS Looks Like**
1. One real base class owns structure and defaults.
2. Variant classes only override a small documented public API (custom properties).
3. Direct property overrides on variants only for truly distinct structural exceptions.
4. Keep selectors flat and predictable.
5. Use semantic variants, not implementation variants.

**Good Pattern — `.dc-alert` base + thin variants**
```css
/* Base: owns structure, spacing, typography, break behavior, and the public API */
.dc-alert {
  --dc-alert-bg:          var(--paper-cream);   /* every callout reads on white */
  --dc-alert-border:      var(--hud-blue-dark);  /* the accent: rail, frame, label chip */
  --dc-alert-fg:          var(--ink);
  --dc-alert-label-color: var(--paper-cream);

  background:   var(--dc-alert-bg);
  border-left:  var(--dc-alert-border-width) solid var(--dc-alert-border);
  color:        var(--dc-alert-fg);
  font-size:    var(--dc-alert-body-size);
  line-height:  var(--lh-normal);
  padding:      var(--space-lg) var(--space-xl);
  break-inside: avoid;
  page-break-inside: avoid;
}

.dc-alert p             { margin: 0; }
.dc-alert p + p         { margin-top: 6pt; }
```

```css
/* Thin variants: override only the public API */
.dc-vibe-callout {
  --dc-alert-border: var(--brand-violet);
}

.dc-origin-callout {
  --dc-alert-border:       var(--rust);
  --dc-alert-label-color:  var(--blood);
  --dc-alert-border-width: 6px;
}
```

The public API for `.dc-alert` variants is: `--dc-alert-bg`, `--dc-alert-border`,
`--dc-alert-fg`, `--dc-alert-label-color`, plus the edge and label chrome
(`--dc-alert-frame`, `--dc-alert-frame-width`, `--dc-alert-label-bg`, …). Each of the
eight registers (note, warning, dm, vibe, origin, location, visit, example) differs from
the others in silhouette, edge and label, so it reads in grayscale
as well as in colour; every one is a white sheet, its colour in the rail, the frame and the label; a book's chapter never sets these variant tokens. Direct property overrides (e.g. `margin`,
`border-left-width`, `width`) are acceptable on individual variants when the value is
truly exceptional and not shared.

**Bad Pattern — direct structural overrides on variants**
```css
/* Don't do this — variants copy structural rules from the base */
.dc-alert--vibe {
  --dc-alert-border: var(--hud-magenta);
  padding: var(--space-sm) var(--space-md);   /* ← structural, not API */
  font-size: 10pt;                             /* ← structural, not API */
}

.dc-alert--origin {
  --dc-alert-bg: var(--surface-orange-tint);  /* ← a tinted body: a callout reads on white */
  --dc-alert-border: var(--blood);
  border-left-width: 3px;
  padding: 6pt 9pt;                            /* ← duplicates base padding logic */
  font-size: 11pt;                             /* ← duplicates base font-size */
}
```

Padding and font-size are structural. When variants start overriding them directly,
you end up with parallel copies of the component shell that diverge silently over time.

**Bad Pattern — over-engineered internal variable API**
```css
/* Don't do this — exposes every internal dimension as a configurable knob */
.dc-alert {
  --alert-margin-top: …;
  --alert-margin-right: …;
  --alert-margin-bottom: …;
  --alert-margin-left: …;
  --alert-padding-x: …;
  --alert-padding-y: …;
  --alert-label-size: …;
  --alert-label-weight: …;
  --alert-label-spacing: …;
  --alert-label-display: …;
  --alert-border-width: …;
  --alert-border-color: …;
  …
}
```

This turns the component into a configuration engine. Variants no longer look like
thin overrides — they look like full re-declarations. Use direct properties for
one-off exceptions; use custom properties only for the small shared API.

**How This Applies to Alert Variants**

Keep `.dc-alert` as the only shell. Let variant classes `.dc-note`, `.dc-vibe-callout`,
`.dc-origin-callout`, `.dc-visit-callout`, `.dc-dm-note`, `.dc-example-callout` override:
- accent/border color (`--dc-alert-border`) and rail width (`--dc-alert-border-width`)
- label color and chip (`--dc-alert-label-color`, `--dc-alert-label-bg`)
- frame (`--dc-alert-frame`, an inset ring; `--dc-alert-frame-width` where the frame follows the outline) and the silhouette (`--dc-alert-shape`)
- not the surface: `--dc-alert-bg` stays white in every register
- exceptional spacing only when truly needed (direct property, not a new variable)

**Reference Methodologies**
- BEM: base block + modifier classes
- CUBE CSS: composition/layout separate from component block
- Design-token layering: global tokens → component aliases → variant overrides
