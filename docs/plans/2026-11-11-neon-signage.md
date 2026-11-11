# Plan: neon signage (draft constitution amendment)

Status: **draft for the owner's review.** Nothing here is in the package yet.
Step 1 of the plan is a physical print proof (`proofs/neon/`); the amendment
below goes into the constitution only once the proof is approved, with any
changes the proof calls for.

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
  step at least 1.5pt; the core is at least 1.2pt (the proof decides). A cable
  runs down the wall to a transformer box. Every sign has one dead letter: a
  grey tube with no rings, a different letter in each chapter.
- **The lettering stays live text** (the chapter title itself is still the real
  heading; the sign is decoration).
- **Budget.** At most one sign per spread, and none on about 85% of spreads:
  roughly 25 to 30 in the Field Guide. A sign covers no more than about 8% of a
  page, never covers text or a title tag, and may carry stickers on its plate
  but never across its tubes.
- **Tube colours** (each a proofed ladder, tube → mid → dark): Rules orange,
  Dream Master cyan, Gear yellow, Citizen File and lore hot pink, each specialty
  its own accent where it survives print. Indigo, violet and the deep magentas
  go dull as tubes: those specialties take a brighter tube variant.

This amendment also narrows the rejected-experiments list in §VII ("NO LED-rim
inset highlights"): that list stays for components; neon signs are not
components and follow the rules above.

## New colour tokens (pending the proof and the colour audit)

- A hot pink tube, `#f0288c` (C0 M100 Y4 K2 = 106%, 4.3:1 on `--ink`): the
  existing `--brand-magenta` reaches only 3.3:1 on ink, because its K12 dims it.
- A brighter indigo tube for Wirephreak, `#4f8cf0` candidate (5.1:1 on ink;
  `--signal-indigo` is 3.2:1).
- The neon tokens (`--dc-neon`, `-core`, `-ring-1`, `-ring-2`, `-plate`), set
  per chapter word next to `--dc-section-accent`.

Each new hex goes through `scripts/measure-palette-crpc1.py` on Ghostscript
10.03 or newer before it is committed.

## Steps

1. **Proof** (`proofs/neon/`): build the page as PDF/X (Ghostscript 10.03+ and
   qpdf, as CI has) and order a DriveThruRPG print proof. Check that each ladder
   reads as lit, the core does not fringe, the rings stay apart, and the pinks
   and the indigo candidate hold.
2. **Amend the constitution** with the text above, adjusted to the proof.
3. **Prototype the opener sign on the Rules chapter**, automatic from the
   chapter word (no new markup), with a page-count diff of the Field Guide.
4. **Roll out** to every chapter and specialty opener, and the Dream Master's
   dark sign.
5. **Later:** location blade signs and lightboxes, once the opener sign has been
   proofed.
