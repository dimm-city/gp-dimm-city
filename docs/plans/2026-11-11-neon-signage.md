# Plan: neon signage (draft constitution amendment)

Status: **draft for the owner's review.** Nothing here is in the package yet.
No physical proof is available for months, so the work is gated on a **soft
proof** instead (`proofs/neon/softproof.py`, results below) and on conservative
widths. A physical proof is still worth ordering with the next book proof; it
confirms the values here, it does not block them.

## Where this comes from

The owner asked for the neon of dimm.city in the printed book, without the
site's dark theme. Three design reviews (print production, art direction,
design system, 2026-11-11) agreed:

- Ink cannot emit light. On paper neon reads only as a saturated tube with a
  pale core on a small **dark plate**, with stepped hard-edged rings. A glow
  on white reads as an outline or a smudge.
- It must be flat, opaque vector: no blur, filter, text-shadow, gradient or
  translucency (each rasterises, bands or muddies on CRPC1 newsprint).
- The site's colours do not print: `#d946ef` prints as a dusty orchid
  (dE 13.4) and `#00ffff` as a pale wash (dE 11.2). The book's neon is cyan,
  yellow, fungi green, civic green, orange and a hotter pink.
- Neon is a new kind of object, a sign mounted on the wall, not a glow added
  to existing components.

One review proposed lighting the "ROLL THE DIE!" bill and the die call as
the cheapest first win. The art-direction review ruled against it, and so does
this plan: those are paper, the pack's voice, and lighting them would make
neon common and blur what it means.

## Proposed amendment (to constitution §IV, after "The paste-up register")

### Neon signage

Neon is the city's own signage: fixtures Dimm City has installed, bolted to
the wall and wired, lit by somebody who is not the pack. Paper is what the pack
pastes up: the rules, the stickers, its voice. A sign is neon; a sheet, a tag,
a sticker or a bill is paper. Neon is never a call to action (the sticker and
the bill already are) and never a way to make an element louder.

- **Where it goes.** A chapter opener (a sign above the banner, spelling the
  chapter's word), a specialty opener (one sign in the specialty's colour), the
  Dream Master chapter's opener (a sign that is mostly dark: the DM decides what
  is lit), and, later, location entries (blade signs and lightboxes). Art may
  glow freely; it costs no budget.
- **Where it never goes.** Section title tags, stickers and street lines, the
  ROLL THE DIE! bill and the die call, outcome ladders, specialty title bands,
  stat blocks, tables, body text, footer chips, the wall, and the street (except
  the light pool under an opener's sign).
- **How it is drawn.** A small `--ink` plate on standoffs (a deeper hard shadow
  than a sheet's), bolted to the wall; on it, the tube as four opaque layers,
  back to front: an outer ring (the hue's dark), an inner ring (its mid), the
  tube (the hue) and a pale core (the hue mixed about 25% into white). Rings
  step at least 1.5pt; the core is at least 1.5pt. A cable
  runs down the wall to a transformer box. Every sign has one dead letter: a
  grey tube with no rings, a different letter in each chapter.
- **The lettering stays live text** (the chapter title itself is still the real
  heading; the sign is decoration).
- **Budget.** At most one sign per spread, and none on about 85% of spreads:
  roughly 25 to 30 in the Field Guide. A sign covers no more than about 8% of a
  page, never covers text or a title tag, and may carry stickers on its plate
  but never across its tubes.
- **Tube colours** (each a soft-proofed ladder, tube → mid → dark): Rules
  orange, Dream Master cyan, Gear yellow, Citizen File and lore hot pink, each
  specialty its own accent where it survives print. Every tube hex is one the
  press can make (its printed value), so the screen PDF shows what will print.
  Indigo, violet and the deep magentas go dull as tubes: those specialties take
  the nearest tube that holds.

This amendment also narrows the rejected-experiments list in §VII ("NO LED-rim
inset highlights"): that list stays for components; neon signs are not
components and follow the rules above.

## Soft proof (2026-11-11)

Each tube went sRGB → CGATS21_CRPC1 → sRGB (relative colorimetric with
black-point compensation, as the build converts). "Prints" is the colour the
press makes; dE76 is how far that is from the screen; contrast is on the printed
`--ink` plate. The third panel of the soft proof adds ink spread and a one-pixel
(0.085mm) cyan/magenta misregistration.

| Tube | Hex | Prints | dE | On plate | Verdict |
|---|---|---|---|---|---|
| Cyan | `#00bcd4` | `#12bbd4` | 1 | 7.3:1 | holds |
| Yellow | `#ffd700` | `#fcdc2a` | 7 | 12.3:1 | holds |
| Orange (today) | `#d4500a` | `#d75a34` | 14 | 4.3:1 | dull, reads as rust |
| Orange, brighter | `#f06a1e` | `#ef713d` | 12 | 5.7:1 | holds; use for Rules |
| Hot pink | `#f0288c` | `#f14693` | 9 | 4.8:1 | holds |
| Brand magenta | `#cf217e` | `#d53e86` | 7 | 3.9:1 | too dim to read as lit |
| Fungi green | `#c8e040` | `#ced741` | 8 | 10.7:1 | holds |
| Civic green | `#4db840` | `#60b54e` | 9 | 6.6:1 | holds |
| Chrome | `#a8b4b8` | `#a8b4b9` | 0 | 7.9:1 | holds (a white tube) |
| Indigo (today) | `#396cb7` | `#3e6fb1` | 5 | 3.3:1 | dull |
| Indigo, brighter | `#4f8cf0` | `#6187c1` | 23 | 4.6:1 | rejected: out of gamut, prints dusty |
| Azure | `#0090d8` | `#288fc9` | 8 | 4.7:1 | best blue the press makes; near cyan |

No blue on this press gets past about 41 chroma, so there is no bright indigo
tube. Wirephreak takes azure (the owner's choice, 2026-11-11; close to
Augmerc's cyan, but the two never share a spread).

Under ink spread and misregistration a 1pt core goes muddy and a 1.5pt core
stays clean; ring steps of 1.5pt stay apart. Hence the 1.5pt minimums above.

## New colour tokens (pending the colour audit)

Tokens take the printed value, not the screen value, so the PDF matches the
press.

- A hot pink tube, `#f14693` (from `#f0288c`): `--brand-magenta` prints at only
  3.9:1 on ink, because its K12 dims it.
- A brighter Rules orange tube, `#ef713d` (from `#f06a1e`).
- Wirephreak's tube: azure, `#288fc9` (from `#0090d8`).
- The ladders are `--neon-<hue>`, `-core`, `-ring-1`, `-ring-2` in
  dc-palette.css; a sign reads `--dc-neon`, `-core`, `-ring-1`, `-ring-2`, set
  per chapter word next to `--dc-section-accent` and per specialty in
  components/neon.css. The plate is `--ink`.

Each new hex goes through `scripts/measure-palette-crpc1.py` on Ghostscript
10.03 or newer before it is committed.

## Steps

1. **Soft proof** (`proofs/neon/`): done, results above. Re-run
   `softproof.py` on every sign before it ships.
2. **Amend the constitution** with the text above, once the owner approves it.
3. **Prototype** (done, before the amendment, at the owner's request): signs
   on the Rules, Dream Master and Gear openers and on every specialty's art
   page, automatic from the chapter word or specialty (no new markup). An
   opener's sign takes no flow height: every other pixel of those chapters is
   unchanged. An opener that starts with a sheet (the Citizen File's fiction
   excerpt) has no headroom and gets none.
4. **Roll out** further (the specialty gateway, lore) once the prototype is
   approved.
5. **Later:** location blade signs and lightboxes.
6. **Whenever a physical proof is ordered:** include `proofs/neon/` and check it
   against the soft proof; adjust the tokens if the press disagrees.
