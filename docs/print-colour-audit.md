# Print colour audit (2026-11-04)

Scope: every colour token in `styles/dc-palette.css` and `styles/dc-identity.css`,
every `color-mix()` tint, every text-on-fill pairing and every statement the
repo makes about CMYK, total ink coverage (TAC) and the press target
(`docs/constitution.md` §V, the token comments, `design-guide/03-palette.md`,
`docs/components-and-palette-reference.md`, `docs/css-architecture.md`).

Method: every token converted sRGB -> CMYK through gutterpress's own
`packages/cli/profiles/CGATS21_CRPC1.icc` with LittleCMS (Pillow, perceptual
intent); OKLab distances for hue separation; WCAG contrast for text pairs.
Ghostscript was not available, so these are the ICC's numbers, not the build's.
They agree with gutterpress #331's real build measurement to within ~10% TAC
(`#000`: build 47/42/40/100, LittleCMS 50/46/44/100). The script is
`scripts/measure-palette-crpc1.py` (needs Python 3 + Pillow); its full output
is in `docs/print-colour-audit-measurements.md`.

## What the vendors require

- DriveThruRPG ("Quick Specifications for Print Books"): CMYK only;
  PDF/X-1a:2001 or PDF/X-3:2002; total ink coverage <= 240%; "Use the
  CGATS21_CRPC1.icc color profile to keep your book in range"; rich black
  C60 M40 Y40 K100; text <= 24pt is 100% K only. Both colour tiers print on
  70# white stock on HP Indigo / Canon inkjet presses.
- IngramSpark / Lightning Source: the same 240% cap and 60/40/40/100 rich black.
- CGATS 21-2 CRPC1 is the coldset-NEWSPRINT reference printing condition
  (ISO/PAS 15339-2), the smallest of the seven gamuts; its 95th-percentile dE
  to CRPC6 (GRACoL coated) is about 15. That is the gamut this palette is
  pushed through.
- CSS: Chromium composes and prints in sRGB; `device-cmyk()` is unsupported.
  The only lever in CSS is which sRGB colour is chosen. `color-mix()` and
  `oklch()` are available (Chromium 111+).

## Finding 1 — the measured TAC figures in this repo are wrong for the pipeline

Every token comment, `docs/constitution.md` §V and the "TAC ceiling 280% /
house target <= 270%" rule rest on figures such as `#000 -> C72 M68 Y67 K88 =
295%` and `--ink -> 278%`. Those are the signature of Ghostscript's
`default_cmyk.icc`, not of CRPC1:

- gutterpress #331 ran `convertToPdfxCmyk`'s exact arguments (gs 10.06) and
  measured `#000 -> 47/42/40/100 = 229%`.
- LittleCMS through the same `.icc`: `#000 -> 50/46/44/100 = 240%`;
  `--ink -> 42/36/33/85 = 196%`; `--ink-dark -> 181%`; `--blood -> 190%`.
- CRPC1's B2A table cannot emit 295%; its own TAC limit is about 240%.

Consequences:
- "TAC ceiling 280% / house target 270%" (constitution §V "Production rules")
  must become "240%: the profile enforces it". Nothing in the palette exceeds
  about 215% after conversion. The six darks "lifted off black" in
  `dc-identity.css` were lifted for a reason that does not exist (harmless, but
  the comments are fiction).
- "POD target: SWOP coated v2 / GRACoL gamut" (constitution §V) is the wrong
  target. DriveThru specifies CRPC1, about two gamut classes smaller. The
  "SWOP-corrected" brand colours were corrected toward the wrong press.
- 78 comments carry stale numbers: 44 in `dc-palette.css`, 23 in
  `dc-identity.css`, 11 in `docs/constitution.md`. Replace them with the
  measured CRPC1 values and say how they were measured.

## Finding 2 — colours to change

### A. Out of the CRPC1 gamut (what prints vs what the screen shows)

| Token | Screen | Prints as | Shift (OKLab x100) |
|---|---|---|---|
| `--brand-magenta` | `#c026d3` neon | `#8e548b` dusty mauve | 16.1 |
| `--signal-indigo` | `#4430e0` electric | `#364882` slate blue | 15.8 |
| `--brand-violet` | `#7030b8` | `#5b447d` | 11.2 |
| `--brand-magenta-deep` | `#8a0a9a` | `#6a3a72` | 11.0 |
| `--proxy-dark` / `--proxy-mid` | `#8a1a90` / `#9a1896` | `#713a71` / `#873876` | 8.8 / 7.9 |
| `--wirephreak-mid` | `#2f2290` | `#28306a` | 7.2 |
| `--fungi-glow` | `#c8e040` | `#c1ca53` | 6.5 |
| `--streetwarden-accent` | `#4db840` | `#69ab4f` | 4.9 |
| `--tint-magenta-rose`, `--crystal-amethyst`, `--crimson` | | | 4.0 / 3.8 / 3.4 |

Worse than the shift is the convergence: in print `--brand-magenta-deep`,
`--brand-violet`, `--crystal-amethyst` and `--proxy-dark` land within dE
1.4-3.8 of each other (`#6a3a72` / `#5b447d` / `#623f77` / `#713a71`). The
constitution's semantic roles ("display punch" magenta vs "the world" violet
vs Proxy's identity) collapse into one plum. Everything in the warm-red, teal
and green families stays within dE 3.5 of itself; leave those alone.

Fix: set the purple-family tokens to in-gamut values (round-trip dE <= ~4) and
re-space them in OKLCh hue so they stay apart AFTER compression (pairwise
OKLab distance >= 8 after conversion): keep magenta genuinely pink (h ~ 340-350,
less blue), violet at h ~ 300, indigo lighter and bluer (h ~ 265-270). The
cheapest first step is to adopt the "prints as" values as the screen colours,
then push each apart in hue. Re-check every contrast comment that names these
tokens.

### B. Tints that went faint when `--paper-cream` became white

With `--paper-cream: #fff` (1.10.2), the `color-mix(..., var(--paper-cream))`
surfaces carry 5-11% total ink with 1-2% minimum channels: vibe callout 5%,
augment entry / lore section 6%, location callout / megacorp 8%, cabal 9%,
reference section / treasure 10%. A 1-2% channel does not hold on Indigo or
inkjet, and these fail the constitution's own "distinguishable in grayscale"
rule. Raise each mix so the surface's dominant ink is >= 8-10%: violet 6-9% ->
about 15%; `--hud-blue-dim` 12-22% -> about 30%; yellow 14% -> about 25%;
crimson 14% -> about 22%; fungi-glow 24% is fine. Mixing `in oklch` keeps hue
stable while doing it; keep `in srgb` only for mixes with `transparent`.

### C. The neutral ladder is inverted and over-populated

- `--paper-form` (`#f5f3ee`, "barely lighter than cream") is now DARKER than
  cream; `--hud-panel`, `--paper-zine` and `--surface-tint-3` sit within dE 1-3
  of each other; `--surface-tint-3` is used by nothing in the package.
  Collapse to three substrates: white paper, one light grey
  (`--concrete-pale`), the wall. Re-point `--paper-form`, `--paper-zine`,
  `--hud-panel` at those (keep the names as aliases if a book reads them).
- `--paper-aged` (`#c8c2b8`) is dE 1.0 from the wall `--bg` (`#c8c5bf`): the
  field chips and `code` sit on a "poster" with no separation from the wall,
  against constitution §II. Lighten it (about `#d6d1c8`) or stop calling it
  paper.

### D. Dark text that prints four-colour

gutterpress's `k-only` pass rewrites only fills with every channel <= 0x1e and
spread <= 0x0a. `--ink` (`#1e1d1c`) just qualifies; `--ink-dark` (`#2f2622`)
does not, and it is the colour of heading slips (`--dc-page-slip-ink`),
flavour lines, entry names, tag text and labels, all 10-13pt, printing as
C36 M36 Y33 K76 across four plates. Likewise `--ink-smoke`, `--ink-mid`,
`--ink-dust` at 10-11pt. Fix in the plugin: point every small-text role at
`--ink`; keep `--ink-dark` for fills and rules. (gutterpress is gaining a
`k-only-neutral` mode; until then the plugin fix stands on its own.)

### E. Contrast failures at the 10pt floor (AA needs 4.5:1)

- `--dc-specialty-intro-title-color: var(--bg)` on `--hud-magenta`: 2.73:1
  (the default; specialties override it, the default itself fails).
- `.dc-classtag` `--orange` text on `--paper-light` (now white): 4.24:1.
  `--orange-deep` passes at 6.85:1.
- Visit callout `--fungi-glow` accent ink on its green: 4.42:1.
- `--ink-dust` on the wall: 3.85:1 (only if a label ever lands on the wall).

### F. Multi-ink hairlines

36 rules at 1px / 1pt / 1.5px, several in 3-4-ink builds: `--border-hairline`
(C13 M13 Y28 K2) as the column rule and table rule, `--ink-dust` dotted rules,
`--paper-aged` and `--hud-blue-dim` 1px borders. A 0.75pt line split across
three plates fringes on misregistration. Rule: hairlines >= 1pt, in `--ink` or
a single-ink tint. Add it to constitution §V (which today says only ">= 0.5pt").

### G. Reversed type on darks

All ten `--*-dark` fills convert to 160-215% four-colour builds with 10pt
reversed type on them. The constitution's "semibold minimum" rule is right; do
not lift the darks further (the ICC already puts K at 45-69%).

## Finding 3 — palette structure

- 70 colour tokens (40 palette + 30 identity). Near duplicates: `--hud-blue` ~
  `--tint-hud-teal` (dE 1.9), `--augmerc-mid` ~ `--dualist-mid` (1.9; two
  specialties share a structural colour), `--fungi-rot` ~ `--streetwarden-dark`
  ~ `--gutterdruid-dark` (2.0), `--brand-magenta-deep` ~ `--proxy-dark` (2.1),
  `--crystal-slate` ~ `--cybersurgeon-mid` (2.9). Alias rather than duplicate.
- Lightness is uneven across the specialty triads: darks span OKLab L
  0.24-0.38, mids 0.35-0.54. Normalise each tier to a band (darks L ~ 0.30,
  mids L ~ 0.47, accents L ~ 0.65-0.75) so "same value, different hue" reads
  as one system and the grayscale-proof rule holds for all ten at once.
- Mixes `in srgb` desaturate through the midpoint; `in oklch` for tints and
  shades, `in srgb` only with `transparent`.

## Work list for the fix PR (target: `release/1.10.2`)

1. Add `scripts/measure-palette-crpc1.py` and regenerate
   `docs/print-colour-audit-measurements.md` after every token change.
2. Finding 1: replace every TAC comment and the constitution §V tables with
   measured CRPC1 values; change the production rules to 240% / CRPC1; remove
   the SWOP/GRACoL target line; say how TAC is measured.
3. Finding 2 D and E: small-text roles -> `--ink`; the three contrast fixes.
4. Finding 2 B: tint percentages (and `in oklch`).
5. Finding 2 C: neutral ladder; `--paper-aged` separation; drop
   `--surface-tint-3` from the palette or mark it design-guide-only.
6. Finding 2 A: in-gamut, hue-separated purple family; re-check contrast
   comments and `specialty-identity.css` band/on-band pairs.
7. Finding 2 F: hairline rule in CSS and constitution.
8. Finding 3: alias the duplicates; document the lightness bands.
9. Update `design-guide/03-palette.md` swatches, `docs/components-and-palette-reference.md`,
   `docs/css-architecture.md`; refresh snapshots; CHANGELOG entry under 1.10.2.

## Resolution (1.10.2)

The fix PR implements the work list. The before/after figures are in the
CHANGELOG and the PR. `docs/print-colour-audit-measurements.md` is regenerated
from the fixed palette. The figures above are the audit as it was found.
Where the PR departs from the audit:

- **2E, classtag.** Not a text failure. The `--orange` in `.dc-classtag` is the
  10px dot (`::before`), and the tag's text is `--ink`. A non-text mark needs
  3:1, and the dot has 4.24:1, so nothing changed.
- **2E, `--ink-dust` on the wall.** Moot. After 2D, `--ink-dust` is no longer a
  text colour anywhere.
- **2C, `--paper-aged`.** It is an alias of `--concrete-pale` rather than
  `#d6d1c8`. The suggested value is dE 2.7 from `--concrete-pale`, so it would
  have been a near-duplicate of it, not a fourth substrate.
- **2C, `--surface-tint-3`.** It stays a token, marked design-guide-only.
- **2B.** Only the tints into paper switched to `in oklch`. The text pre-mixes,
  the ink shades and the band facets and rims stay `in srgb`. They were never
  faint, and changing them would have shifted colours that pass their
  contrast checks.
- **2F.** Light rules (`--hud-blue-dim`, which is nearly cyan alone, and
  `--paper-aged`) keep their colour at 1pt. Light neutrals cannot print in one
  ink: CRPC1 builds greys from C, M and Y.
- **3, lightness bands.** Documented in `dc-identity.css` and constitution §V,
  but not applied: normalising them would repaint all ten specialties.
- **3, near-duplicates.** The five pairs listed above are aliased. So is
  `--tint-magenta-rose`, which printed dE 5.4 from the new magenta.
  `--augmerc-dark` ~ `--dualist-dark` (2.4) remain separate.
