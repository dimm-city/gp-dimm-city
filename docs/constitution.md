# DC Design Guide — Constitution

The canonical, self-contained north-star document for the Dimm City Design Guide. Every component, token, override, and review verdict in this codebase answers to the principles here. This file is meant to be read once start-to-finish by anyone joining the project.

If a design decision conflicts with this document, the design decision is wrong unless the conflict is explicitly resolved with a constitution update.

**Version:** 2026-11-04
**Authority:** project-level (this file) > AKM memory > knowledge:print/design/creaturepunk-design-guide
**Related**: [css-architecture.md](./css-architecture.md), [adding-macros.md](./adding-macros.md)

---

## I. North-Star Goals

1. **Reusable** — `gp-dimm-city` installs into any Gutterpress book with zero override files required to render correctly.
2. **Author-friendly** — non-technical writers compose books with simple macros. No HTML in markdown. No per-element class attributes for styling.
3. **TTRPG-quality** — output matches the production bar of D&D 5e PHB, Pathfinder 2e Core, Mothership, Blades in the Dark.
4. **Teachable** — the design guide's own markdown source IS the documentation for the system.

---

## II. The Wall (Core Visual Principle)

> **Components float above / stick to the brick wall background.**
> The page is the wall of an alley in Dimm City. Components are the **posters and digital displays hung on it.**

This is the single most-load-bearing visual principle. Every other component decision flows from it.

### What this means concretely

- **The page background is the WALL** — concrete-ash, gritty, urban, structural. It does not compete for attention.
- **Components are objects HUNG on the wall** — posters glued up, LED panels bolted on, spray-painted sigils, stamped warnings, hand-pasted notices. Each has its own visual register, weight, and edges, but all share the same plane: applied to the wall.
- **Components have separation from the wall** — drop shadows, hard edges, slight rotation or asymmetry, perceptible weight. They sit *on top of* the page, not *inside* it.
- **Depth is two shadows: a hard contact and a soft lift.** The hard offset copy (`--shadow-ink`, the section's hard shadow) says the object is pasted flat; a soft, translucent `box-shadow` under it (`--shadow-lift`, `--dc-section-lift`) says it stands a little off the brick. Recessed things (the fiction cavity, `lore`/`dm`/`choose` panels) take a soft inset (`--shadow-press`) instead of a lift. Both are `box-shadow`, never `filter: drop-shadow()`: a filter on an element that holds text prints that text as a picture (§V production rules).
- **Displays catch the light.** Title bands and skill-card tabs carry a top gloss (`--light-gloss`): a gradient over flat fill, never a sheen on text. The wall itself carries no light or vignette: Chromium paints an `@page` background image in the page area apart from the margins, so a gradient over the wall breaks with a hard edge at the margin line.
- **Components do NOT bleed into the wall** — soft tinted backgrounds that fade into the page colour, low-contrast washes, "subtle web gradients" → all wrong. A poster has a hard edge against brick.
- **The wall has texture; the posters have ink** — the page can carry concrete grain. Components are printed/displayed objects with their own surface.
- **Six stone walls can replace the brick on a page** (`@page wall-1` … `wall-6`: coursed rubble, ashlar, random rubble, running bond, flagstone, square setts), over the whole sheet and in the brick's colours: ash (`--bg`) stone with grey joints, its tones matched to the brick tile's so a stone page weighs the same as a brick one, over a `--bg` fill. Each tile is about 4.5in of wall regrown from its panel with no repeat inside it, so a page shows no grid of the same stones; it prints at 240 DPI (accepted as texture: the production rules below say why) and is generated with its CSS by `scripts/wall-tiles.py` from `source-art/wall-sheet.png`. Flagstone is bedded into flat courses and the setts are half-lapped, so neither reads as paving. Every wall, the brick included, stands on a 0.6in strip of pavement in perspective along the foot of the sheet, under the footer chips (`images/ground.png`; none on a full-bleed plate). The rules below hold on them unchanged: nothing on a wall page sits on the stone.
- **No text is ever printed directly on the wall.** Every glyph sits on a substrate: paper, a panel, a strip, a plate or a chip. That includes what an author writes with no component around it. A free-standing `#` is a banner in the chapter's accent; a `##` is a paper slip bolted to the wall (accent rail, dashed ink foot, hard shadow, a slotted bolt head in each top corner); a `###` is the same slip, plainer, at the full width of its column (a thinner rail and foot); a `####` and below is a label slip that shrinks to its words; one gap (`--dc-page-slip-foot`, 6pt) sits under every one of them, whatever follows; loose paragraphs, lists and quotes share one paper sheet per run; a `@columns` run of nothing but prose is one sheet. The folio, the chapter chip and the Citizen File running head are chips (see §IV). The design guide's explainer pages (`@page .dg-doc`) print plain on white and are the one exception: they are not wall pages.

### Component health check

A component is doing the principle right when:
- It has visible separation from the page (shadow, hard border, contrast, or distinct surface treatment).
- Its edges are decisive — clipped, torn, stamped, framed. Not a CSS rectangle drifting into the page.
- A reader could imagine peeling it off the wall as a single physical object.
- Removing it leaves a clean rectangle of "wall" where it was — not a faded ghost.

A component is doing the principle wrong when:
- It feels embedded in the page (no shadow, no edge, soft tint).
- It looks like a web `<div>` with `background-color`.
- Its boundaries are ambiguous.
- The page texture continues through the component instead of being interrupted by it.

### Two surface families

Components belong to one of two surface registers on the wall:

1. **Paper posters** — flyers, warnings, hand-stamped notices, torn show bills, forms. Light paper substrate: white (`--paper-cream`, and its aliases `--paper-light`, `--paper-form`) under reading text; the one light grey (`--concrete-pale`, and its aliases `--paper-zine`, `--paper-aged`) only for the pull quote, the front-matter lede, the default specialty-intro panel and label and chip grounds; never darker than the wall behind reading text. Hard ink. Stamps, sprays, dotted folds. Every callout, every section body, the lede, the `choose` form, the shard block, the fiction excerpt, NPC stat blocks, gear entries, the procedure plate, the definition page, design-guide chrome.
2. **Digital displays** — LED tickers, status panels, HUD readouts, AP indicators, dark plates. Saturated or ink-dark fills with crisp reverse-out type. Glow at the edges (via top-edge highlight, not literal glow filters). Outcome ladder chips, AP cost chips, skill-card tabs, title bands, the ink bar of the `dm` section and of the `dm` note, label chips and badges, the slate block, the Surreal definition, the at-a-glance readout. These are the select dark elements; nothing else that holds text is dark.

Cards bridge the two: specialty cards and skill cards are cream paper under a bright digital-display band and tab. A single book uses both registers — that's the texture of Dimm City — but a given **component** picks one and stays in it.

### Every variant says what it is — in colour AND in grayscale

A reader flipping pages should know **what kind of content a box holds from its silhouette, edge, label and colour before reading a word.** Magenta must stop meaning everything. The rule for every family of variants (alerts, section kinds, blocks, choice cards, factions, gear kinds, specialties):

- **Each variant is distinguishable at thumbnail size in colour.**
- **Each variant is also distinguishable in grayscale.** A grayscale proof (or a colour-blind reader) must still tell the variants apart, so vary **edge geometry** (cut corners, torn, stepped, stripes, dog-ear, double frame), **edge weight** (a rail's width, a ring, a frame) and **label treatment** (chip, stamp, underline, glyph) — never hue alone, and never a tinted body. A new variant that only recolours an existing one is wrong.
- **Text reads on white.** Every surface that holds reading text is white (`--paper-cream`); a variant's colour is in its rail, frame, title bar and label. Fill value separates display elements only (bars, bands, tabs, chips, badges). A dark body is kept for two named blocks: the slate block ("Binding") and the Surreal definition.
- **Chaos goes on labels, bands, tabs, edges and badges** (the 20% display layer), never on reading surfaces. Body copy stays upright and level.
- **A chapter may re-theme a component's accent but never repaints a variant's identity.** `--dc-section-accent` recolours a panel's bar; it must not turn a warning alert grey-brown or a dm note rust. Per-chapter overrides set the documented accent tokens and leave the variant tokens (`--dc-alert-*` sheets, edges and labels; `--dc-choice-*`; `--dc-faction-*`) alone.

### Semantic colour roles

| Role | Colour | Means | Used by |
|---|---|---|---|
| **Display punch** | Magenta (`--brand-magenta`, `--brand-magenta-deep`) | Style, not content: the loudest thing on the page, never a category | Chapter chevrons, spray titles, pull quotes, `ROLL THE DIE!`, the VAR AP chip, the default `panel` accent (chapters re-theme it), the Augmerc |
| **Player-facing rules and look-ups** | HUD blue / light cyan (`--hud-blue*`) | A rule or a thing to look up | Note alert, reference section, `@panel` block, definitions, megacorp faction, ideals, standard AP |
| **Dream-Master-only** | Cyan on ink (`--brand-cyan` on `--ink-dark`) | Behind the screen; used nowhere else | `dm` alert, `dm` section, the Dream Master chip |
| **Danger, consequence, a choice you must make** | Hazard yellow + ink (`--brand-yellow`, `--ink`) | Stop and read | Warning alert (hazard-stripe rail), enforcer faction, the `choose` "Choose" stamp, the vehicle gear's yellow rail and badge, the SPECS strip |
| **Harm, cost, cult, flaws, binding rulings** | Blood / rust / crimson (`--blood`, `--rust`, `--crimson`) | Something is taken from you, or it is final | Slate block ("Binding"), flaws, cult faction, origin alert's stamp, increased AP, side effects, general gear |
| **The world and the arcane** | Violet / amethyst (`--brand-violet`, `--crystal-amethyst`) | Lore, dreams, treasure | Vibe alert, lore section, dreams, cabal faction, treasure gear |
| **Organic, biological, toxic** | Fungi green (`--fungi-*`) | The living city | Visit alert, drug gear, gutterdruid, streetwarden's toxic green |
| **Value** | Paper / ink | Reading surface or display element | White paper = every surface that holds reading text, whoever it is for; ink-dark fill = a display element (title bars, tabs, badges, label chips, the slate block, the Surreal definition). Who a box is for is said by its rail, frame, title bar and label, never by its fill |

Two registers never share the same hue **and** edge: if two variants must share a hue (the dm note and the example both carry a cyan rail), their silhouette, frame and label differ (a file folder under an ink bar that carries the label in cyan, in an ink ring; a ticket with a cyan ring and a taped-on tag).

---

## III. Creaturepunk Aesthetic

### Tagline

> *"It ain't chrome. It ain't clean."*

Creaturepunk is **hostile, improvised, urban, cold, aggressive, dirty.** Not friendly. Not polished. Not warm. Not luxurious. Not decorative.

The tone is:
- Hostile, not friendly
- Improvised, not polished
- Urban and cold, not warm or fantasy-coded
- Aggressive, not luxurious
- Dirty, not decorative

If the result looks like a friendly handbook, it failed. If it looks like a damaged field guide that still reads cleanly, it worked.

### The four registers

Creaturepunk is **part future tech, part ancient magic, part landfill, part wonderland.** Every component is a deliberate blend of these in specific proportions. The mix is the **identity signal** of who/what made the object and where it sits in Dimm City's stratigraphy.

| Register | Reads as | Visual cues | Token family |
|---|---|---|---|
| **Future tech** | LED indicators, HUD panels, digital displays, brushed metal, circuit traces, neon signal. Lit-from-within, sharp cut edges, saturated crisp fills. | sharp polygon clips, reverse-out crisp type, top-edge highlight (LED-rim), saturated chip fills, mono caps labels | `--brand-magenta/cyan/yellow/violet`, `--hud-blue/blue-dark`, AP-chip / outcome-chip / skill-tab chrome |
| **Ancient magic** | Mineral facets, refractive crystals, faceted geometric chrome, arcane runes, smoky-quartz depth. Cold colour temperature, faceted geometry, multi-stroke depth. | faceted/lozenge clip-paths, mineral aqua/citrine/slate accents (violet is the world's, not a specialty's), geometric ornaments, flat facet planes | `--crystal-aqua/slate/citrine` (`--crystal-amethyst` for the world's gems) |
| **Landfill** | Rust drips, torn paper edges, exposed adhesive, scratched tape, oil stains, smoke-burn. Warm decay, oxidised metal, dried blood. | torn-paper edges, rough/irregular cuts, paper-stain tints, rust drips, smudge/grime overlays, asymmetric rotation | `--rust`, `--blood`, `--orange`, `--amber`, `--crimson`, `--deep-rust`, `--paper-stain`, `--paper-aged` |
| **Wonderland** | Bioluminescent fungi, UV-reactive spore-light, alley moss with a pulse, organic crackle, dream-haze. Yellow-green organic glow, irregular organic boundaries. | fungi-glow accents on dark fills, organic curvature in clip-paths, irregular asymmetric edges, spore-halo treatments | `--fungi-glow`, `--fungi-mid`, `--fungi-rot` |

### Per-specialty register mix (deliberate, not random)

Every specialty leans into a specific register mix that reflects WHO it is in the world. The CSS theme block per specialty (`.dc-specialty.<name>`) should express that mix, not just swap colors.

| Specialty | Future tech | Ancient magic | Landfill | Wonderland | Visual cues (title bands) |
|---|---|---|---|---|---|
| **Augmerc** | ████ HIGH | low | ██ mid | low | Signal-cyan band with an LED rim and a teal-black, cyan-ticked LED rule; hard angular stair-step cuts. Tech-heavy, street-salvaged. |
| **Wirephreak** | ████ HIGH | low | ██ mid | low | Electric-indigo band (a blue-violet of its own, clear of the world's violet), LED rim and a cyan, ink-ticked circuit rule; crisp circuit-jog clips. Decking + interference. |
| **Cybersurgeon** | ████ HIGH | low | █ low | low | Cold chrome band with a bright rim and a ruler-scale rule, medical mono labels, blue-grey steel. Surgical precision. |
| **Proxy** | ████ HIGH | ████ HIGH | low | low | Tech + magic: deep-magenta band with an LED rim **and** a darker facet plane, a cyan rule, centre-notched gate clip. (Cream on the bright magenta is 5.0:1; the band uses `--brand-magenta-deep`, 12.5:1.) |
| **Etherlock** | ██ mid | ████ HIGH | ██ mid | ██ mid | Citrine-yellow band with a pale refractive facet and a mid-gold rule. Secrets-as-currency, manifold magic. |
| **Technosorcerer** | low | ████ HIGH | ████ HIGH | low | Scorch-orange band, darker scorch patch, torn bottom edge, no rule. Ritual worked on burnt scrap. |
| **Streetwarden** | ██ mid | low | ██ mid | low | High-vis toxic-green band over a green-and-ink hazard-tape rule. Civic-warden register. |
| **Gutterdruid** | low | ██ mid | ████ HIGH | ████ HIGH | Fungi-glow band, torn bottom edge, a lichen patch, no rule. Trash heap + spore magic. |
| **Dualist** | ██ mid | ████ HIGH | low | ██ mid | Crystal-aqua band split by a pale facet, dark rule. Two-path walker, lozenge geometry. |
| **Generalist** | ██ mid | ███ HIGH | ██ mid | low | Cool-slate band (steel, not violet) with a darker slab and a pale-stone rule, soft chamfers. Common stone, refracted depth. |

Each band fill is the specialty's own bright signal colour, so ten bands read as ten colours at thumbnail size and differ in grayscale value too (light: yellow, lime, chrome, cyan, green, aqua; mid: orange, indigo; dark: deep magenta, slate) and in edge (rim, facet, torn, hazard). The **specialty cards** keep their own calmer register (cream body, bright band, mid frame); the mix expresses itself on the **title bands**, the display layer.

**Specialty silhouettes (shape carries the register).** Each specialty's frame, band, tab, card body and specialty card are cut from one language, and a cut is never closer to a glyph than 2pt: tech = crisp stair-steps and square bites (augmerc three small steps top right and bottom right; wirephreak two big circuit jogs; cybersurgeon single square bites, no diagonals); magic = facets and lozenges (etherlock a big and a small chamfer on opposite corners; dualist four even chamfers and a bottom point; generalist two big chamfers on opposite corners like a hewn stone; proxy a shallow centre gate plus a stair and a facet); landfill = torn (technosorcerer a burnt corner, a ragged tear across the foot and a chipped tab); organic = wobbly (gutterdruid, no long straight edge); civic hazard = a sign-plate octagon (streetwarden). The band and its frame are cut from the same point list (`--spec-edge-top`) and span the same width, so the band's top edge and both top corners coincide with the frame exactly. Grit is two cues, on edges and bands only: a chipped or torn edge on the landfill and organic specialties, and a misregistered rule (a second ink, 2px off) on the tech bands.

The mix is the SOURCE of design decisions. When polishing a component for a specialty, ask: *which register dominates? what visual cues belong to that register? what does NOT belong?*

**Concrete implications:**
- The LED rim (an inset top highlight on the band) and a ticked LED rule belong on the **title bands** of Augmerc / Wirephreak / Cybersurgeon / Proxy (future-tech high). They do NOT belong on Gutterdruid or Technosorcerer — those bands are torn paper, not a polished tech panel.
- Torn edges belong on the **title bands** of Technosorcerer / Gutterdruid (landfill high: a torn bottom edge, no rule), and on sheets and labels elsewhere (the shard block, the cult faction, the flaw card; the fiction excerpt is broken masonry, not a torn sheet). They do NOT belong on Augmerc / Cybersurgeon — clinical tech doesn't tear — and they are NOT used on the specialty cards themselves.
- A flat faceted plane (a darker or paler shape cut into the band) belongs on Dualist / Proxy / Etherlock / Generalist (ancient-magic high); a hazard-tape rule on Streetwarden.
- Fungi-glow and a lichen patch belong on Gutterdruid (wonderland high). The augmerc's cyan is electric, not organic — those visually differ even though both are "bright accent on dark fill."
- All of it is flat fill and hard-edged stripes: no gradient sheen, no filter, no text-shadow.

---

## IV. Controlled Chaos — the 80/20 Rule

- **80% of the page** is structurally reliable: text frames, margins, table alignment, reading order, page furniture.
- **20% can misbehave**: rotated stamps, broken banners, offset tabs, hard colour hits, asymmetric ornament.

Apply disruption to **display elements**, never to **reading surfaces**.

### Page furniture and wall-level grit

Page furniture is a chip, never bare type, and stays level and legible:

- **Folio** (`P.121`): a paper-cream sticker, 0.225in tall, 10pt type, ink edge, a hard ink shadow drawn as a thicker bottom/right border (margin boxes take no `box-shadow`). Type is centred in the face by the engine (`vertical-align: middle`), not by the font's ascent.
- **Chapter chip** (`C.N` in a book, `E.N` in the design guide's Part 2): a stamped coupon in the chapter's colour (magenta-deep by default; blue, rust, violet, amethyst or amber through a named page, `dc-chip-<hue>`, since a margin box cannot see the chapter's accent), cream type (every face ≥ 4.5:1), the same ink edge and hard shadow. It replaces a dashed magenta outline, which read as a debug box.
- **Placement**: both sit at the top of the footer band (the 0.95in bottom margin, measured from the sheet edge), `--chip-gap` (0.10in) below the text block; the 0.225in chip ends exactly 0.625in from the sheet edge, on DriveThruRPG's 0.5in text minimum, where it always was. The band is deeper than the chips by `--chip-gap` (0.10in), so a sheet or card that fills a page ends at least 0.10in above the chips' tops (its 3pt hard shadow reaches into that gap): the folio and the chapter chip are stickers below the poster with wall showing between them. On recto and verso, for every page word that prints them.
- **Pagination** is a package duty, not the book's, wherever the rule holds for any book's content: text keeps its orphans and widows (three and two in a skill card), a card splits between ability rows, headings, dividers, lead-ins and the first rows of a list or table stay with what follows, a requirement band never splits, and a card that splits across pages is open at the foot and marked by a dashed vector seam in its specialty's colour on both sides of the break (CSS only, no height), while only its real foot carries the cut and shadow; an explicit `@continue` closes the part before it with a straight foot and opens a whole continuation card, with no seam. See the per-spread verdict scheme (§XI): a page under about 40% full with no design reason, or a one- to three-line continuation, is a fault to fix in the package first and the book's forced breaks second. A rule that only holds for one book's content (a row or block count, a size guess) is never the package's: it goes in the book's own sheet.
- **Wall-level grit** is restrained and sits on edges and labels: the bolt heads on a `##` slip, every callout and a skill card (opaque discs in the top corners of a slip or a callout, at a card's top right and bottom left, clear of the text), the dashed foot, the hard-border shadows. Text is never translucent (§V). Nothing clips a glyph: chips and slips are plain bordered boxes; only the title banner's diagonal tail is clipped, and its padding clears it.

| Safe for chaos | Keep stable |
|---|---|
| Chapter openers | Body copy |
| Section banners | Tables |
| AP tags + sticker chains | Rules text |
| Pull quotes + warnings | Lists |
| Image crops + overlays | Page numbers + running heads |

The mistake to avoid: confusing **chaotic** with **hard to use**. Creaturepunk pages should feel **unstable while the information remains easy to scan.**

### Layout rules

- Inner margin: at least 0.5in before any decorative intrusion.
- Outer/bottom margins can feel tighter than inner.
- Bleed art can push outward; rules text never feels trapped in the gutter.
- Body copy is never rotated. Uppercase belongs to display, not long instructions.
- Line length: 45–75 characters.
- Banners may be angled by a few degrees; text baseline inside stays level.

---

## V. Print-First Palette + Tokens

Use a cold-grey page base with narrow, deliberate accent hits. Do not build full-page neon fields. Let grey do most of the work.

### How CMYK and TAC are measured

Every CMYK and TAC figure in this section, in the token comments and on the design guide's swatches is the token converted sRGB → CMYK the way a PDF/X build converts it: a swatch of the colour through Ghostscript's pdfwrite with **CGATS21_CRPC1**, the profile DriveThruRPG specifies and gutterpress embeds in the build, as the output profile, at Ghostscript's default intent (relative colorimetric with black-point compensation), and the `c m y k k` operands read back out of the PDF. `python3 scripts/measure-palette-crpc1.py` does this (Ghostscript 10.03 or newer, Python 3 + Pillow; full output in [print-colour-audit-measurements.md](./print-colour-audit-measurements.md)), so the figures are the build's to the digit. Until 1.10.2-alpha.2 they came from LittleCMS at perceptual intent, which the build never used; those ran 10-30% TAC under the build's on the purples and 15-20% under on the inks (`--ink`: 196% → 211%). They hold for a Ghostscript that honours the output profile: 10.03 and newer do; 10.02.1 (Ubuntu 24.04's package) ignores it and separates everything through its own default CMYK profile (`#000` = C72 M68 Y67 K88 = 295%, the figures this file carried before 1.10.2), and gutterpress (#495) measures which happened on every PDF/X build and warns. Re-run the script when you add or retune a colour, and write its figure in the token's comment, in its row below and on its swatch in the palette chapter; `python3 scripts/measure-palette-crpc1.py --check` is what CI runs, and it fails when any of those figures, or a block of [print-colour-audit-measurements.md](./print-colour-audit-measurements.md), is not the build's (`--write` regenerates that file's blocks).

CRPC1 is the coldset-newsprint reference condition, the smallest of the seven CGATS 21 gamuts, so a saturated screen colour can print as another colour entirely. The script's "printed" column and its dE (OKLab distance × 100 between screen and print) show this; keep a token within dE ~4 of its print.

### Page substrate

Three substrates: white paper, one light grey (`--concrete-pale`) and the wall. Every other paper name is an alias of one of them.

| Token | Hex | CRPC1 CMYK = TAC | Use |
|---|---|---|---|
| `--bg` | `#c8c5bf` | C18 M15 Y18 K2 = 53% | The wall. Ash-concrete page background — gritty, urban, structural. |
| `--concrete-pale` | `#dcdad5` | C12 M9 Y12 K0 = 33% | The one light grey: the front-matter lede, the pullquote and the default specialty-intro panel; the label/chip ground through its aliases below. Not the body of a callout, section, card or entry: those are white. |
| `--paper-cream` | `#ffffff` | C0 M0 Y0 K0 = 0% | White: the unprinted stock, no ink. Every sheet that holds reading text — callouts, section bodies, cards, entries, the fiction page. |
| `--paper-light` | alias of `--paper-cream` | — | White — the lede, specialty intros, alternate panel fills. |
| `--paper-form` | alias of `--paper-cream` | — | White — the `choose` form and the definition sheet. |
| `--paper-zine` | alias of `--concrete-pale` | — | The grey printed page. No package rule reads it (the fiction excerpt and the shard block are white); kept for books. |
| `--hud-panel` | alias of `--concrete-pale` | — | The default specialty-intro panel. |
| `--paper-aged` | alias of `--concrete-pale` | — | Label and chip grounds — field chips, `code`, the outcomes ladder rows, the `reference` section's alternate table rows, the catalog ledger band, three specialty cards. Not a sheet for running text. (Was `#c8c2b8`, dE 1.0 from the wall: no separation.) |
| `--paper-stain` | `#b0a89c` | C23 M20 Y27 K11 = 81% | Dark inset wells and label strips (the shard's label strip). **No body text on it**, and none on any fill darker than the wall. |
| `--ink` | `#1e1d1c` | C44 M38 Y37 K92 = 211% | Body text, **all small text** (labels, slips, tags, h4–h6, flavour lines), key rules, every hairline. The one dark the k-only pass prints in black alone. |
| `--ink-dark` | `#2f2622` | C39 M38 Y38 K87 = 202% | Heavy fills (the dm section's bar and tab, the dm note's label bar, chips, tabs), border anchors and rules ≥ 1.5pt. Not small text: it prints on four plates. |
| `--ink-smoke` | `#4d4339` | C32 M33 Y39 K71 = 175% | Fills and heavy rules: the fiction cavity, the shard's accent rail. |
| `--ink-mid` | `#594f43` | C32 M32 Y40 K62 = 166% | No package rule reads it; kept for books. |
| `--ink-dust` | `#665b4e` | C31 M31 Y41 K53 = 156% | The outcome row's fallback rail. No longer a text colour. |

### Brand signature layer

The dimm.city web-palette analogs, pulled inside the CRPC1 gamut. The purples are spaced so they stay ≥ 11.6 apart (OKLab × 100) once printed through the build's separation, and each prints within dE 4.2 of its screen colour: magenta h355, deep magenta h349, amethyst h316, violet h311, indigo h258.

| Token | Hex | CRPC1 CMYK = TAC | Use |
|---|---|---|---|
| `--brand-magenta` | `#cf217e` | C2 M100 Y1 K12 = 115% | Display punch: section accents, gateway banners, the spray, h1. Pink (h355), inside the press gamut; cream on it 5.0:1. |
| `--brand-magenta-deep` | `#690045` | C24 M94 Y15 K56 = 189% | Press-safe magenta for type and reversed type: chevrons, the crit row, the VAR chip, Proxy's band (12.5:1 with cream either way). |
| `--brand-cyan` | `#00bcd4` | C67 M0 Y11 K0 = 78% | Augmerc accent, wirephreak's LED rule. |
| `--brand-yellow` | `#ffd700` | C0 M5 Y100 K1 = 106% | Brand radiant — etherlock accent, peak triumph. |
| `--brand-violet` | `#662d87` | C62 M100 Y0 K16 = 178% | The world: lore, vibe, cabal, dreams, treasure (h311). No specialty uses it. 9.2:1 with cream. |
| `--signal-indigo` | `#396cb7` | C86 M54 Y0 K0 = 140% | Wirephreak accent: a lighter, bluer indigo (h258) of its own; cream on it 5.3:1. |

### HUD / digital-display layer

| Token | Hex | CRPC1 CMYK = TAC | Use |
|---|---|---|---|
| `--hud-blue` | `#1f6f94` | C78 M29 Y8 K24 = 139% | Mid HUD teal — primary stat lines, secondary chrome. |
| `--hud-blue-dark` | `#14516e` | C74 M34 Y12 K46 = 166% | Deep teal — borders, rules, H2 text. |
| `--hud-blue-dim` | `#7ab8d0` | C46 M9 Y8 K3 = 66% | Light cyan — the `reference` section's title band and column heads, the roll-table heading row, outcome dividers, the blockquote rail, the reduced-cost AP chip. Not a body fill. Nearly one ink (cyan), so it may draw a 1pt rule. |
| `--hud-magenta` | alias of `--brand-magenta` | — | Brand-signature cyber-magenta. |

### Gutter / fire-and-blood layer

| Token | Hex | CRPC1 CMYK = TAC | Use |
|---|---|---|---|
| `--crimson` | `#e1261c` | C0 M100 Y100 K6 = 206% | PMS Red 032 — danger, harm, active states, ROLL THE DIE tags. |
| `--blood` | `#901a12` | C2 M92 Y65 K48 = 207% | Oxidised arterial — DM-chapter table headers (9.0:1 on paper). |
| `--orange` | `#d4500a` | C0 M71 Y100 K13 = 184% | Burnt circuit-board — warnings, AP tags, arrows. |
| `--orange-deep` | `#a03808` | C1 M76 Y88 K39 = 204% | Press-safe orange on paper (6.9:1). |
| `--rust` | `#b23a12` | C0 M80 Y100 K30 = 210% | Burnt rebar — section accents, miss row. |
| `--amber` | `#7a5a20` | C17 M33 Y75 K52 = 177% | Sulphur-scorched brass — gear-chapter section accent. |
| `--deep-rust` | `#70200e` | C11 M73 Y58 K65 = 207% | Shadow rust — deepest warm dark. No package rule reads it; kept for books. |
| `--amber-dark` | `#5c3c10` | C21 M40 Y62 K70 = 193% | Charred amber. |

### Fluorescent fungi layer (wonderland)

| Token | Hex | CRPC1 CMYK = TAC | Use |
|---|---|---|---|
| `--fungi-glow` | `#c8e040` | C19 M0 Y95 K0 = 114% | Bioluminescent yellow-green — gutterdruid accent, outcome-row.hit (with ink text). Prints duller (dE 6.5): proof it. |
| `--fungi-rot` | `#30461e` | C44 M20 Y60 K73 = 197% | Deep moldering green — outcome-row.fail; the streetwarden and gutterdruid darks alias it. |
| `--fungi-mid` | `#6aa030` | not a token; not measured | Luminous lichen mid — reserved for a future fungi-faction signal |

### Ancient crystals layer (magic)

| Token | Hex | CRPC1 CMYK = TAC | Use |
|---|---|---|---|
| `--crystal-amethyst` | `#905aa5` | C45 M80 Y0 K2 = 127% | Mineral violet, lighter and redder than the world's violet (h316) — the amethyst chapter chip (`dc-chip-amethyst`); no specialty accent and no body tint. |
| `--crystal-slate` | `#52626f` | C50 M31 Y22 K42 = 145% | Cool slate stone — generalist accent; cybersurgeon's mid aliases it. |
| `--crystal-aqua` | `#4a98a8` | C62 M13 Y18 K12 = 105% | Crystalline aquamarine — dualist accent. |
| `--crystal-citrine` | `#b89a3a` | not a token; not measured | Burnt mineral gold — reserved for a future crystal-faction signal |

### Specialty palette (per-specialty triad plus band and chip)

Every specialty has three tokens: **accent** (bright signal), **mid** (chrome/structural), **dark** (card-body fill). Two more are wired from them: the **band** (`--spec-band`, the title-band fill and the specialty-card header: the accent, except Proxy's deep magenta) with its **on-band** type (`--spec-on-band`, ink or cream, whichever holds ≥ 4.5:1), and the **tier chip** (`--spec-chip-bg/-fg/-edge`, the pill on a skill-card tab: the accent with ink or cream type, or a cream chip with dark type where the accent fails 4.5:1 for 10pt type: Technosorcerer and Proxy). The old bronze/gold/silver tier badges are gone: a tier pill belongs to its specialty, not to a position. A dark or mid within dE ~3 of another token is an alias of it, not a second colour. The last column is the dark's CRPC1 TAC; every dark is ≤ 209%.

| Specialty | accent | mid | dark | band / on-band | Register lean | dark TAC |
|---|---|---|---|---|---|---|
| augmerc | brand-cyan | `#006878` | `#003a40` | accent / ink | future-tech HIGH + landfill mid | 191% |
| technosorcerer | orange | `#7a3008` | `#4c290f` | orange / ink | magic HIGH + landfill HIGH | 200% |
| streetwarden | `#4db840` toxic-civic | `#347828` | `--fungi-rot` | accent / ink | tech mid + landfill mid | 197% |
| gutterdruid | fungi-glow | `#4d6020` | `--fungi-rot` | accent / ink | landfill HIGH + wonderland HIGH | 197% |
| cybersurgeon | `#a8b4b8` chrome | `--crystal-slate` | `#303840` | accent / ink | future-tech HIGH | 184% |
| wirephreak | signal-indigo | `#093c81` | `#181b45` | accent / cream | future-tech HIGH + landfill mid | 209% |
| proxy | brand-magenta | `#9c0f63` | `--brand-magenta-deep` | magenta-deep / cream | tech HIGH + magic HIGH | 189% |
| etherlock | brand-yellow | `#8a6a00` | `#46360c` | accent / ink | magic HIGH + landfill mid + wonderland mid | 197% |
| dualist | crystal-aqua | `--augmerc-mid` | `--augmerc-dark` | accent / ink | magic HIGH + tech mid + wonderland mid | 191% |
| generalist | crystal-slate | `#3a4854` | `#212a32` | accent / cream | magic HIGH | 200% |

**Lightness bands.** A tier reads as one system when every specialty's value is about the same and only the hue changes, and that is what keeps the ten apart in a grayscale proof. Targets in OKLab L: darks ~0.30, mids ~0.47, accents 0.65–0.75. Today the darks span 0.25–0.37, the mids 0.37–0.54 and the accents 0.49–0.89 (the outliers are listed in `dc-identity.css`); move a colour toward its band whenever you add or retune one.

### Production rules (CMYK + press-safe)

- **Press profile: CGATS21_CRPC1** (DriveThruRPG; IngramSpark's limits are the same). Both colour tiers print on 70# white stock.
- **TAC: 240%, enforced by the CGATS21_CRPC1 profile.** The profile cannot emit more; no token exceeds 211% after conversion. There is no reason to lift a dark off black for coverage.
- **Gamut:** keep every token within dE ~4 of its CRPC1 print (the script's "printed" column), and keep tokens that must read as different colours ≥ 8 apart *after* conversion.
- **Tints** are for small grounds that hold no reading text (tape, a chip, a mark, a rule). A body surface is white: no callout, section, card or entry is tinted. A tint of a colour into paper mixes `in oklch` and keeps its strongest ink at ≥ 8–10%: a 1–2% dot does not hold on HP Indigo or inkjet. Mix `in srgb` only with `transparent`.
- **Colour space: author in sRGB hex.** Chromium writes every colour into the PDF as sRGB `DeviceRGB`, clipped to the sRGB gamut: `oklch(62% 0.30 340)` comes out `.927 0 .739`, `color(display-p3 1 0 0)` comes out `1 0 0`, and `color(srgb …)` and `lab()` come out as their sRGB value. No CSS colour space reaches the press; the chain is CSS → sRGB (clipped) → Ghostscript → CGATS21_CRPC1 at relative colorimetric with black-point compensation. So: write tokens as sRGB hex, which is what the PDF carries; choose a value by its press round trip (the Gamut rule, measured with `scripts/measure-palette-crpc1.py`, which runs the build's own separation); use `oklch` only as the interpolation space of a `color-mix()` (the Tints rule); keep neutrals exactly neutral, because the K-only rewrite takes text to the black plate only when its channels are within `0x0a` (0.04) of each other and at or under `0x1e` (0.12), which is why `--ink` qualifies and the warm `--ink-dark` prints on four plates; and stay off the saturated sRGB corners (pure magenta, pure blue), which clip hard and shift hue under relative colorimetric. Do not author a colour with `color()` or `oklch()`: in print they add nothing and hide the clipping.
- **Hairlines: ≥ 1pt, in `--ink` or a one-ink tint** (such as `--hud-blue-dim`, nearly cyan alone). A thinner rule, or one split over three or four plates, fringes when the plates are misregistered. Heavy rules (≥ 1.5pt) may use any colour.
- **Small text in `--ink`.** Gutterpress's k-only pass prints only near-black (every channel ≤ `0x1e`, spread ≤ `0x0a`) in black alone; `--ink` qualifies, `--ink-dark` and the lighter inks do not and print on four plates. Every label, slip, tag, h4–h6, flavour line and secondary line is `--ink`; keep `--ink-dark` for fills and rules.
- Body-text contrast: ≥ 4.5:1 (WCAG AA).
- Large-text contrast: ≥ 3:1.
- Reversed type: semibold minimum, only on solid fills, and never below the 10pt floor. The darks convert to 156–214% four-colour builds; do not lift them further.
- Body text reads on white: never on noisy or tinted backgrounds, and never on `--paper-stain` or any fill darker than the wall (`--bg`). The two dark blocks (the slate block and the Surreal definition) are the exceptions: a decisive dark fill with light type.
- **The type floor is 10pt for every glyph, no exceptions** (§VI): body, tables, captions, chips, tabs, tier pills, AP chips, badges, labels, stamps, folios, stat keys. The token is `--fs-floor` (`dc-palette.css`).
- Every variant must also pass the colour-and-grayscale test (§II).
- Magenta, crimson and fungi-glow shift most on press — proof these first.
- **Images print at 300 DPI.** Gutterpress checks every `<img>` against that bar at its printed size, but no check sees a CSS background. The six stone-wall tiles are the known exception: they print at about 240 DPI with about 110 DPI of real detail (`source-art/wall-sheet.png` is 1024×1536, about 512px a panel, which `scripts/wall-tiles.py` already grows about 2×) and are accepted as texture; upsampling would add no detail. A sharper wall needs a source sheet of at least 2048×3072. The brick (600 DPI) and the ground (300 DPI) meet the bar.
- **Translucent artwork is allowed; translucent text is not.** Shadows, lifts, bevels and tints may be translucent: that depth is the wall's look (§II), and its cost is accepted. A PDF/X page that carries any of it prints its artwork, rules and fills included, as one 300 DPI picture, and the file grows with it; Gutterpress's `pdfx.transparency: preserve-text` (the guide's manifest sets it) keeps that page's text live, so fonts, search and the K-only black rewrite are unaffected. No rule asks a page to stay vector. Text colours stay opaque: a translucent glyph cannot be kept live and flattens its page whole (the *keep text opaque* convention test enforces it).
- **No `filter` on an element that holds text.** Chromium prints the text of a filtered element as a picture, in the plain PDF as well. A filter may sit only on a text-free `::before`/`::after` layer (a convention test enforces it).

---

## VI. Typography

| Role | Preferred | Fallback | Size |
|---|---|---|---|
| Display | `lixdu` | Titillium Web Bold | H1 26pt, H2 20pt, H3 16pt, H4 13pt, H5 11pt; leading 1.35 (`--lh-display`) |
| Body | Titillium Web | Tomorrow | Reading floor 10pt; the package sets 12pt (`--fs-body`) on 18pt leading (`--lh-normal`, 1.5), 11pt compact (`--fs-body-sm`) |
| Labels / Mono | Tomorrow | monospace | All-caps labels 10pt (the floor), tracked 0.08em or wider. H6 is one of them |

### Type floor: 10pt, for ALL text

**No glyph the package prints is smaller than 10pt.** There is one floor and no second, smaller floor for "chrome". It is the token `--fs-floor` in `dc-palette.css`; components reference it rather than writing the number. It is a floor, not a target: running body stays 12pt, compact prose 11pt. Short all-caps labels sit exactly on it, with their tracking brought down (0.08–0.12em) so they do not balloon.

| Text | Size |
|---|---|
| Running body, rules and ability text, table cells, stat lines, captions, card pitches, callout and definition bodies, lede/flavor/fiction, list items, intro text | **≥ 10pt** (body 12pt, compact 11pt) |
| Chip, badge, tab and tag labels, tier pills, AP chips, stickers, mono section labels, table header cells, field labels, stat keys, band names, running-head and folio chips, stamps | **10pt**, tracking ≥ 0.08em |
| Reversed type (light on a solid fill) | **10pt, semibold or bold**, solid fills only |

The page baseline (`dc-core.css`) keeps to it: body 12pt, table cells and header cells 10pt, inline code never under 10pt, lists, definition lists and figure captions inherit the 12pt body. The credits colophon is 10pt. The footer chips (folio, chapter coupon) and the citizen-file running head are 10pt in a 17pt box. The design guide's own running foot, kickers, code fences and swatch labels are held to the same floor.

**Lists, one ink, display punctuation.** A list is a tight column: the bold `»` (or a right-aligned numeral) in the component's own ink (`--dc-accent-ink`) hangs in the list's left padding (1.1em; 1.6em for a numbered list; each nesting level adds one hang), so a wrapped line aligns under the first word and the hang scales with a 10pt intro, callout or card. Items sit `--space-xs` apart, loose or tight (an item's `<p>` has no margin); a list adds no space above itself and `--space-sm` below. Running text has one ink: `body` sets `--ink`, so list items and table cells print what paragraphs print, never the browser's pure black. A heading breaks only between words: a single word wider than its column is not split (`overflow-wrap: normal`, `hyphens: manual`; a soft hyphen in the source still works) and overflows on the trailing side, so give it a wider column. Lixdu covers only U+0020-007E; its curly quotes, en and em dashes and ellipsis come from a second `lixdu` `@font-face` cut from the Tomorrow Bold file (`unicode-range`), so they print in a matching weight.

Display-face (lixdu) names inside a component must not wrap a short name onto two lines in a two-column run: size and track them so typical names fit (an NPC name at 11pt and 0.03em; a catalog entry name at 11pt with balanced wrapping; a specialty-card name on one line).

### Type hierarchy

**One scale, no literal sizes.** Every `font-size` in the package is a `--fs-*` token (or a multiple of one, for the two decorative display steps: the pull quote's mark and the design guide's Part title). The steps are 10, 11, 12, 13, 16, 20 and 26pt. Headings step down by about a quarter (26, 20, 16, 13); below 13pt the sizes are a point apart, too close to tell levels apart by size alone, so each level there differs in kind (face, caps, weight), never in size only. Headings are set on `--lh-display` (1.35). That is tight for this face, not loose: lixdu's capitals fill the whole em, so at 1.2 the two lines of a wrapped heading sit 2pt apart. `small`, `sub` and `sup` are held at the floor too.

| Element | Spec | Notes |
|---|---|---|
| H1 | lixdu, 26pt (`--fs-h1`), uppercase | Chapter punch, minimal copy |
| H2 | lixdu, 20pt (`--fs-h2`) | Can sit on angled magenta banner |
| H3 | lixdu, 16pt (`--fs-h3`), deep teal | Sub-sections |
| H4 | lixdu, 13pt (`--fs-h4`), ink | Component sub-headings (skill names, stat-block name) |
| H5 | lixdu, 11pt (`--fs-h5`), 0.1em tracking | Sub-labels. Smaller than body: caps in the display face carry it |
| H6 | Tomorrow bold caps, 10pt (`--fs-h6`, the floor), 0.1em tracking | Metadata labels. A label, not a smaller H5: the two are a point apart, so they differ in face |
| Body | 12pt (reading floor 10pt) on 18pt leading | Default reading size |
| Component rules text | 10–11pt | Never below 10pt |
| Captions, table cells, stat lines | 10pt | Never below 10pt |
| Reversed | 10pt minimum, semibold | Only on solid fills |

### Type rules

- Do not rotate body copy.
- Uppercase belongs to display, not long instructions.
- Keep line length 45–75 characters.
- Street voice in short bursts; rules text stays clear.
- Display sizes need negative tracking (lixdu defaults are body-tuned). Apply via component-level `letter-spacing` only when justified by surface — banners on dark fills, not body copy.
- H5 mono caps are tracked (about 0.1em) to read as chrome labels; no all-caps mono label is tracked under 0.08em.

---

## VII. Component Visual Patterns

Each component lives in ONE surface register (paper poster or digital display) and inherits visual cues from its specialty's register mix. Every family of variants obeys §II: each variant differs in silhouette, edge and label, not hue alone, and its reading text sits on white.

### Section banners (chapter chevron + spray)

- **Surface**: paper poster register (cream-stamped + clip-cut)
- **One aggressive banner per section** is enough — don't double up.
- Keep banner copy short.
- If angled, text baseline inside stays level.
- Clipped edges define the banner — never use a default rectangle.
- Background fill is solid (not gradient) — the brick-wall-poster ideal means flat-ink on substrate, not a sheen.
- Per-chapter `--dc-section-accent` token drives the chevron + spray colour.
- **Chevron** = a deep-magenta (`--brand-magenta-deep`) full-width banner with one clean diagonal. **Spray** = a stencilled tag: a bright-magenta slab that shrink-wraps its words, a stepped overspray right edge and a dashed ink stencil line along the foot. Two magenta titles, two silhouettes. The `spec-tweak` heading carries its own paper strip, so it never sits on the wall; the chevron and spray are slabs and so are their own substrate.

### Section kinds (what kind of text is this?)

A section kind is read from its bar, its edge and its silhouette before its words; every sheet is white. Each cuts its own corners, and the cut carries the meaning (see "Shape language" below): precise symmetric chamfers for player rules, a file-folder tab for the classified, long asymmetric slashes for the world, ticket notches for a form, a sign plate for danger, a torn edge for fiction and landfill. Padding on every clipped edge is the cut's depth plus 2pt; no glyph, rule or marker is ever cut.

| Kind | Bar | Sheet | Silhouette | Colour |
|---|---|---|---|---|
| `panel` | solid accent bar | cream | one larger chamfer (top right), a chipped bottom-left corner | the chapter accent (magenta by default; the only kind chapters re-theme) |
| `reference` | pale HUD band ruled in ink above and below (a machined spec-sheet header) | white, alternate table rows in `--paper-aged`, tight 10pt rows | four small even machined chamfers | HUD blue: a look-up |
| `lore` | deep violet bar, torn along the top | white, recessed | long ASYMMETRIC slashes: shallow top-left, steep bottom-right | violet: the world |
| `dm` | ink bar with a cyan rule, a cyan rail | white, recessed | a file-folder tab in the box's own top band (it carries *Dream Master*, cyan on ink; its own layer, so a page break cannot strand it) and one opposite corner cut, bottom right | cyan on ink: Dream Master only. The tab is drawn with or without a heading |
| `choose` | none: a form | a white paper sheet (`--paper-form`) | a ticket: a V punched in the middle of each side, a perforated foot, an ink edge, recessed (sunk into the wall: a cast shadow along the top, a light lip on the bottom and right), no drop shadow | ink title over a double rule in the chapter accent; heavy ink tick boxes (2.25pt); a hazard-yellow *Choose* stamp; dotted write-in rules. A printed, stamped form, not a web control |

**Hung or sunk.** `panel` and `reference` hang on the wall like posters (a hard drop shadow). `lore`, `dm` and `choose` are recessed, sunk into the wall: no drop shadow, the wall's top edge casting a hard shadow down over the sheet's top and its title bar (the rail stays clear), and a light lip along the bottom and right (`--dc-section-recess`, `-recess-depth`, `-shade`, `-lip`). All vector, opaque inset shadows.

**Edges carry the kind by shape and colour.** Clip-path silhouettes and border colour are the primary way a kind is told apart; dashed and dotted borders are kept for the few places where the dash is the object itself: the warning's hazard-stripe rail and the enforcer's hazard band, stencil lines (the `##` slip foot, `.dc-spray`), write-in rules on a form, the origin stamp's worn ring, the side-effect field frame, link and ROLL THE DIE! underlines, and the tech specialties' LED tick rules. Everything else is a solid edge.

**Labels are raised.** Every label (an alert label, a section tab or stamp, a block tag, a choice chip, a faction or entry badge, a field label, a tier pill, a price tag, a die chip) stands off the element it sits on with a hard 2px ink shadow (`--dc-label-shadow`), or, where a clip-path would cut an outer shadow, the same ink as an inset bottom-and-right edge (`--dc-label-edge`). The dm note's label is the exception: it is the note's ink bar, not a chip.

Magenta is the `panel` default only. `flat` (a rail, no bar, no clip, no shadow) is distinct from all of these. A bare `@section` (no variant word) is a plain sheet of paper under the text: no text is ever set straight on the brick wall. Every section kind sets `--dc-accent-ink`, the text-safe ink of its accent (the accent mixed 72% toward ink, so a chapter that re-themes the accent re-themes it; dm sets HUD blue, slate a light tint of crimson on its dark body), which `ROLL THE DIE!` and other accent text read.

### Block registers (`@block`: panel, slate, shard)

- `.dc-panel`: HUD-blue band, symmetric hex chamfers. Player-facing rules summaries, structured data.
- `.dc-slate`: a sign plate: octagonal corners in a heavy crimson frame, an ink body, a **blood** band with a crimson rule and a stamped (double-edged) *Binding* tag. Binding rulings, Dream Master directives that settle an argument. Not magenta and not cyan, so it cannot be mistaken for `dm`.
- `.dc-shard`: a white sheet, a torn (zig-zag) foot and a dog-eared corner, a taupe label strip with an ink title and a solid rule, no accent hue. Fiction, atmosphere, setting asides.

### Choice cards (`@flaws`, `@ideals`, `@dreams`)

- A choice card says which choice it is. The enclosing kind sets `--dc-choice-accent/-kind`, the edge weights (`--dc-choice-edge/-band/-rail`) and the card's shape; the card reads them.
- **Flaw** = blood, a heavy solid edge, a deep crack (a 40x26px nick and a foot jagged up to 13px) and a blood-ruled quote. **Ideal** = HUD blue, a clean solid edge, a steady ticket stub (14px V notches in each side), a rule under the name. **Dream** = violet, a double edge, a top edge rising 30px to the right and a perforated foot (two V tears). All three are white sheets; they differ in edge weight and in how deep the silhouette bites, so they differ in grayscale. Siblings differ in silhouette; the two ticket shapes mean "a choice", the torn one "a cost".
- The choice chrome is scoped to a card inside `@flaws`/`@ideals`/`@dreams`; any other `.dc-card` (a gear entry, a faction) keeps the plain card. Each choice carries a 6px rail and 5px top band in the kind colour, a 1.5pt ink edge, a one-word mono chip (10pt semibold, reversed) (FLAW / IDEAL / DREAM) over the name, and the closing quote in ink on the card's white, ruled down its left in the kind colour (its ground is `--dc-choice-tint`, white by default; never grey `--paper-stain`).
- The card name is the first `####` (core converts only that heading to `.dc-card-heading`). Write `####`; a `###` is dressed the same but is not the card heading.

### Skill cards (the most-repeated component)

- **Surface**: paper poster register (cream body + clipped tab + ink border)
- Skill card body uses `--paper-cream` substrate with a colored tab on the top edge.
- Tab background uses `--dc-card-tab-bg` (specialty's mid colour) with a clipped polygon shape.
- Per-specialty clip-path geometry distinguishes specialties at-a-glance, and the silhouette follows the register (see "Specialty silhouettes" under the register table): tech = crisp stair-steps and square bites (augmerc, wirephreak, cybersurgeon), magic = facets and lozenges (etherlock, dualist, generalist, proxy's gate), landfill = torn (technosorcerer), organic = wobbly (gutterdruid), civic hazard = a sign-plate octagon (streetwarden). The tab, the card body, the path banner and the intro share a specialty's language.
- The **tier pill** on the tab (AUG1.3) is the specialty's own chip (`--spec-chip-*`), not a position colour. There is no bronze/gold/silver and no featured-card variant: every card is the same card.
- The flavor line's rail is the specialty's mid colour.
- AP chips and inline ROLL THE DIE markers ride INSIDE the card body — they're digital-display elements pinned to the paper poster.
- A `ROLL THE DIE!` in a specialty card, path or intro takes that specialty's own text-safe ink (`--spec-ink` → `--dc-accent-ink`: deep teal for augmerc, deep magenta for proxy, a dark ink of the family where the accent is bright yellow, green or chrome), at 4.5:1 or better on the cream, light or aged paper it sits on.
- Body and ability text ≥ 10pt; chip and tab labels at the 10pt floor too.

### Specialty cards (the 10-card grid + profile shells)

- **Surface**: the specialty's own learning-path banner, as a sheet. A specialty card reads as the same family as that specialty's skill cards and path banner: the same colour and the same cut.
- Card body: `--paper-cream` (aged or light paper where the specialty's skill cards use it). Body text: `--ink`. An ink outline cut in the banner's silhouette (`--dc-path-shell-clip`), with a soft lift off the wall.
- **Title band**: the name on the specialty's band colour (`--spec-band`, type `--spec-on-band`), cut in the path banner's title shape (`--dc-path-title-shape`), with the band's top gloss and rule. This is the specialty's primary visual signature at grid scale. The name is set on one line (a name such as TECHNOSORCERER is tracked tighter, never wrapped).
- Every cut stays clear of the type (padding on a clipped edge is the cut depth plus 2pt or more).
- **The catalog is a spread.** On `@page specialty-catalog` the cards are one designed two-page spread: it opens on a left page, the title, four cards and Dualist fill the left page, and a short `@lede` (placed after Dualist), four cards and Generalist the right; every one-column card is one size and both full-width cards another; in aligned rows (a two-column grid; beyond it the package keeps `grid-template-columns` for single components), and nothing else shares the two pages. Dualist and Generalist, the two specialties built from the others, span both columns as the last row of each page (Dualist on the left, Generalist on the right); the book lists Dualist fifth and Generalist last, as dense cards with the portrait beside the text. The right page's portraits are taller, since it has no title above them. Both pages, Dualist and Generalist included, must fit their sheet in the preview and in print; the rows size to their cards rather than to a fixed height. Each card is a poster: the portrait on top in a single ink-matted frame cut in the specialty's own silhouette (a picture that has not loaded reads as a paper-aged field with its alt text), then the name (display, on one line), the tagline (mono caps over a rule) and the pitch (10pt). No number chip on the portrait. The dense card (a floated thumbnail) is the card anywhere else.
- **NO** corner accent triangles, NO portrait double-edge framing, NO noise overlays, NO LED-rim inset highlights, NO tonal-lift gradient on the body, NO hazard-tape borders, NO torn-paper irregular clip-paths — all Pass 6/7/8 experiments were rejected by user-eye review as over-styling. Restraint wins.
- The rule: **specialty color belongs in the band, the cut, and at most a tint of the substrate** — not as a saturated fill across the entire card.

### Title bands (learning-path banner, specialty-intro title)

- **Surface**: digital display register. The band fill is the specialty's own bright signal colour with ink or cream type at ≥ 4.5:1, so ten specialties read as ten colours (and ten values) at a glance.
- The register rides on three flat layers: the **rim** (an inset top highlight, tech only), a **facet** plane at the right (magic: pale or dark; landfill: a burnt or lichen patch) and a **rule** under the band (tech: a rule of ink or accent LED dots (a dotted border); Streetwarden: hazard tape, a slanted dashed border; landfill: none, the bottom edge is torn instead).
- All flat fills, borders and clipped polygons, no gradient at all: a gradient is dropped or rasterised in a PDF/X build, so the dots, tape and facets are drawn as borders and clip-paths.
- A path with no subtitle and no stickers is the band alone (the shell hugs it). The subtitle sits on the shell's own paper in `--ink-dark`, with a 3px rail in the specialty's mid colour.

### Outcome ladder chips (digital display)

- **Surface**: digital display register (saturated chip + LED-rim highlight)
- 5-row creaturepunk gradient: crit (brand-magenta-deep) → hit (fungi-glow + ink text) → mixed (orange-deep) → miss (rust) → fail (fungi-rot).
- Each chip has tonal gradient + inset top-highlight + inset bottom-shadow ("pressed/stamped" LED-display register).
- Each row's text-cell has `border-left: 2px solid var(--row-color)` tethering the result text to the band colour.
- The chip column is 26% of the ladder (min 130px, `--dc-outcome-key-col`) so a long band name wraps on two or three lines, not a cramped one. Band names are 10pt semibold (the floor), centred, balanced; result text 10pt. The frame is a machined HUD plate (four even 6px chamfers, one chip out of the foot); a roll table is a die-faced plate (two opposite 14px cuts, a die chip stuck a little off square). Both set `--dc-accent-ink`.

### AP cost chips (digital display, the LED-indicator pattern)

- **Surface**: digital display register (LED chrome stuck on tech)
- Tonal gradient on the chip fill + inset top-highlight + layered shadow (close + soft far) + text-shadow.
- 1pt `--ink-dark` border for press registration grip.
- Slight rotation (`transform: rotate(-1deg)`) keeps the chip from feeling pixel-aligned.
- Type is 10pt semibold (the floor). The triangles and the lamp are drawn as CSS shapes (borders and a radius), not glyphs: independent of any font, and vector wherever the page prints vector.
- Variants by AP cost, told apart in colour **and** by a glyph or fill value: **free** = an unlit LED (the grey lens of a dead indicator, ink type, ink edge and a hollow lamp: the quietest chip, so "0 AP" is not a red flag), **standard** = HUD blue dark, **reduced** = pale blue with a down-triangle, **increased** = blood with an up-triangle, **VAR** = deep magenta (cream on the bright magenta is 5.0:1, on the deep one 12.5:1), **special** = amber with cream type. Free and increased are never the same red.

### Callouts (.dc-alert variants)

- **Surface**: paper poster register: every register is a white sheet (`--dc-alert-bg`, `--paper-cream`). One shell, eight registers, told apart by silhouette, edge and label — in colour and in grayscale. A callout's colour is in its rail, its frame and its label chip, never in its fill.

| Register | Silhouette | Edge | Label |
|---|---|---|---|
| `note` | machined 6px chamfers on all four corners, one chipped notch (player rules) | 8px blue rail, a 2pt blue ring; a bolt head in each top corner | blue chip with paper type |
| `warning` | sign plate: octagon, 12px cuts (danger) | 14px yellow/ink hazard-stripe rail, 3px ink frame with a 2px crimson second pass out of register; a bolt head in each top corner | yellow caution-tape chip with ink type, rotated -1.5deg |
| `dm` | file folder: a tab rising 9px over the left 42% and one cut corner, bottom right (classified) | an ink bar across the top over a cyan rule, its left end the folder tab; under it a 6px cyan rail and a 2pt ink ring; a bolt head in each top corner of the white body | the bar itself: cyan type on ink (Dream Master only) |
| `vibe` | long shallow diagonals at two opposite corners (the world) | a 3pt violet frame all round, along the diagonals too, its left side a 4px rail; a bolt head in each top corner | violet chip with paper type; italic voice |
| `origin` | torn bottom edge, square corners (backstory) | a 3pt rust frame along the torn foot, its left side a 6px rail; a bolt head in each top corner | crimson double-bordered rubber stamp with a worn (dashed) outer ring, rotated -2deg; italic second-person voice |
| `location` | torn bottom edge, square corners, as origin (a place written up) | a 3pt teal frame along the torn foot, its left side a 6px rail; a bolt head in each top corner | deep-teal double-bordered rubber stamp with a worn (dashed) outer ring, rotated -2deg |
| `visit` | wobbly organic polygon ending in a signpost point (a place) | a 3pt fungi-green frame along the wobbling edge and the signpost point, its left side an 8px rail; a bolt head in each top corner | fungi-green chip with paper type and a map-pin glyph |
| `example` | ticket: a V notch in the right edge (a sample) | 6px cyan rail, a 2pt cyan ring; a bolt head in each top corner | taped-on tag |

- A flat white sheet — no tint, no tonal gradient, no inset cream stroke (the Pass 6 attempt stays reverted). A frame is one hard line, not a double stroke on a fill. On the square-edged registers it is an inset ring (`--dc-alert-frame`: 2pt in the accent by default, ink on the warning and the dm note). Vibe, origin, location and visit have an outline a ring cannot follow, so their frame runs along every cut (`--dc-alert-frame-width`, 3pt): the box is filled with the accent and a white copy of its silhouette sits inside it, with the text on the white copy; the left side of the frame is the rail. All edge art (the hazard rail, the dog-ear fold) is drawn in vector, never a gradient: a skewed dashed-border rail and a clip-path triangle.
- Every clipped edge is padded by at least its cut depth + 2pt, so no glyph is ever cut. Every variant sets `--dc-accent-ink`, the text-safe ink of its own accent on its own surface (note, dm, location and example `--hud-blue-dark`, warning and origin `--blood`, vibe `--brand-violet`, visit `--fungi-rot`; on white, cyan is a rail colour, never a text one); the lede sets it from `--dc-intro-ink`.
- Body copy is level, ≥ 10pt, ink on white in every register (none is reversed); labels 10pt mono caps tracked 0.1–0.14em. Chaos is on the labels and edges only.
- A chapter must NOT re-theme a callout's variant tokens: identity survives re-theming.

### NPC stat blocks

- **Surface**: paper poster register (cream-stamped + 2pt top-rule on name + chrome labels)
- Name (H4) gets a 2pt top-rule in `--rust` (chapter accent) — `border-top: 2pt solid var(--rust)`. In a two-column run the name is 11pt tracked 0.03em so "GREASE MONKEY" stays on one line.
- TRAITS / EQUIPMENT / CYBERNETICS (H5) at 10pt mono caps with 0.1em tracking — read as chrome labels, not competing headings.
- The flavor line (`>`) is a ruled line, not a well: a 4px rail in the block's rule colour, ink text on the paper.
- Primary stat line (HP/damage) is a **chip**: its first line set 12pt bold, cream on the block's primary colour (`--hud-blue-dark`; blood in a rust chapter) via `::first-line`, so it is the first thing scanned. A second line in the same paragraph (Fodder/size) falls under it as a small-caps mono tag, 10pt (stat lines are reading text), `--ink-smoke`; written as its own paragraph it is the same tag at 10pt semibold. The stat lines are chosen by position (the first two paragraphs after the `>`), so a description belongs inside the quote, not between the quote and the stat lines. The compact variant draws both as 10pt semibold chips.

### Factions (`@faction megacorp | cabal | cult | enforcer`)

Each kind has its own silhouette, top band, name colour and badge:
- **megacorp**: machined: a rectangle with an L-shaped step out of the top right and bottom left, a white sheet, an ink-blue band with a cyan edge, blue name, square badge. Bands are drawn as solid inset shadows (vector), never gradients.
- **cabal**: violet, long asymmetric slashes (shallow top-right, steep bottom-left: lore's cuts mirrored), a white sheet, deep-violet band, an inset violet shadow.
- **cult**: blood, torn top and foot, a blood rail, blood band, a white sheet, blood name.
- **enforcer**: a sign plate: an octagon in a heavy ink frame, an ink-and-yellow hazard-stripe band (a yellow strip under a skewed thick dashed ink border: vector), the name set as a yellow label in ink, an ink badge with yellow type.

### Fiction excerpt

- A hole smashed in the wall, with the story on the page behind it (the opposite of a hung poster): the edge breaks along the brick courses in brick-sized steps, with fractured brick ends and a few hairline cracks into the wall. The broken wall's thickness shows as one dark face all round (`--dc-fiction-cavity`, `--ink-smoke`, 5px), every step's sides joined, over the page (`--dc-fiction-bg`, white). Its `#` title is set at `--dc-fiction-title-size` (the `##` size): a story's name, a step under a chapter's. Depth comes from the masonry, not the light: no glow, no lit faces. Vector and opaque, no blur, no image. No rail, no title bar, narrative leading; text sits only on the page, 10pt+. Differs from the lede (a light panel with a rail), flavor (a rail and no box) and the panel (a bar and a rail).
- Two clipped layers on a box 16px larger than the excerpt: the face (`--dc-fiction-hole`) and the page (`--dc-fiction-shape`, the hole shrunk by the face). Both polygons are generated by `scripts/fiction-break.py`; each edge holds whole 172px runs of steps (CSS `round()`), so the bricks keep their size at any box size and nothing tiles or seams. The 16px reach is the excerpt's margin, so all of it stays inside the column (the page clips anything past it, and so does print). The wall never reaches past the box edge.

### Entry cards by kind (`@gear` and its kinds)

Each kind is a silhouette, a frame, a mark, a badge and a name colour on a white sheet, not a rail colour alone:
- **gear**: a hang tag — a paper card in a heavy ink frame, top-left and bottom-right clipped, a rust rail and badge, a ring eyelet, the bold price line stamped as a raised, rust-edged price tag. No tan: cool paper, hard against the wall.
- **augment**: a spec chip — a white plate, a stepped PCB notch top-right, a cyan top rule, a teal name.
- **treasure**: a gem — an octagon cut, a violet rail, a hexagon badge, a violet name.
- **vehicle**: an industrial plate — octagonal 12px cut corners, a heavy 3px ink inset frame, an inner seam, a yellow rail and badge. No hazard stripes: those are the danger register's.
- **drug**: a prescription label — an irregular, wobbling organic outline, one frame (a fungi-green head band and rail), an "Rx · Drug" pill badge, a green name.

An entry never splits across pages.

### Catalog (`@section catalog`)

A price board: the entries are ruled in their kind's colour, not boxed, and each is kept whole (it never splits across a column or a page; the catalog itself splits between entries). The title bar is a ledger header, a pale aged-paper band under heavy ink rules with an ink rail and an INVENTORY chip: not a magenta bar, and not a dark one (a dark bar is the Dream Master's).

### Fields

One chip family (the same slanted-edge label chip) for all six. What each means shows in its frame: **effects** = a solid teal frame, a "+" on the chip (the benefit); **side effects** = a dashed blood frame, a "–" on the chip (the cost); both on white. SPECS is the dark strip with a yellow rail; traits and equipment are a plain line under a chip; requires is a bar.

### Procedure (`@procedure`)

An instruction plate, not a tinted list: a cream surface, a 2px ink frame, a hard shadow, a solid HUD-blue number strip down the left (reversed 12pt mono numerals), step text in ink at 10pt, ruled dividers, bold leads in `--ink` (not red). Nothing sits above its top edge: the staple that once held it read as a stray mark. Text never sits on the wall. The list may split between steps; each step stays whole.

### At-a-glance tile

A readout: a reversed 10pt mono-caps label band (HUD blue, its top-right corner cut) over a 24px display value, an ink frame and a hard shadow.

### Definition (`@definition`)

A dictionary page: cream, a 3pt HUD-blue-dark rule above and a hairline below, a hard shadow, no rail and no cut corners. The term is a blue headword set first (display caps for a `####` term); the body is italic ink. It must not read as a tinted note.

Two variant words, `@definition lucid` and `@definition surreal`, are the two roll states drawn as opposites (in colour and in greyscale). **Lucid**: the lightest sheet, four even 45-degree machined chamfers, a blue frame with a cyan hairline inside it, upright type, a headword ruled off in blue. **Surreal**: an inverted violet-black sheet with light type, a skewed outline torn along the foot, magenta and violet inks off-register on opposite inner edges, a leaning headword (the body is never rotated). Reading text in both is 11pt.

### Tables

- Header row in `--ink-dark` by default (a structural bar with no chroma of its own); `reference` sections use the pale HUD band, and a chapter may set its own header colour through a declared token.
- Header text: mono caps, 10pt, cream on a solid fill (reversed type: 10pt, semibold minimum).
- Body rows: 10pt body font on alternating cream tints (the floor).
- Inner cell padding generous (0.04in vertical, 0.08in horizontal).

### Lede (.dc-intro / @lede)

- **Surface**: paper poster register — a `--paper-light` substrate (lighter than the wall), a 6px accent-colour rail and a 3px ink foot rule, a hard poster shadow. Flat solid fill — no tonal lift, no noise overlay.
- Upright, 600-weight ink type at 13pt (`--fs-h4`), larger than the 12pt body: the chapter's opening statement.
- Per-chapter `--dc-section-accent` / `--dc-intro-accent` colours the rail. A lede stacked flush on a box (front matter, contents, credits) drops the foot rule and, on contents and credits, sets body size and regular weight.
- The lede sets `--dc-accent-ink` from `--dc-intro-ink` (orange-deep by default; the front-matter and intro pages set it to their deep-magenta accent), so a `ROLL THE DIE!` in a lede takes the lede's colour.
- **Flavor** (`.dc-flavor`) is the opposite register: in-world voice, italic, a rail and a paper strip behind it (`--dc-flavor-bg`; no text is ever set on the brick), ink-dark.

### Inline chrome: tag, tape, human callout

- **Tag** (`.dc-tag`): an inline chip — mono 10pt bold, 0.08em tracking, ink on cream with a 1px ink border and a 1px hard shadow; the same family as the AP chip and the class tag.
- **Tape** (`.dc-tape`): a strip of masking tape — tan (`--brand-yellow` 30% in `--paper-aged`), torn ends, ink edges top and bottom, an ink label at 10pt, 0.2em tracking, crimson dashes either side.
- **Human callout** (`.dc-human-callout`): a contact card — a blue ID header band, a 2px ink border, a poster shadow, a solid ink strip foot. Floatable.

### Outcome row text-cell tether (Pass 5b finding)

The right-cell of each outcome row gets `border-left: 2px solid var(--row-color)` so result text is visually tethered to its row band. Without it the right cell floats untethered.

---

## VIII. Hard Architectural Constraints

These are non-negotiable. Violations rate the work AWKWARD or BROKEN regardless of visual appearance.

### Selector ownership

- `.page` / `.chapter` selectors are reserved for **counters, page-templates, TOC IDs, and per-instance positioning**.
- Component visuals live exclusively in `components/*.css` under the `.dc-*` namespace (kebab-case).
- The package owns no column layout: columns are core's `@columns N`. The package sets only `--gp-column-gap` and `--gp-column-rule`, once, at `:root` (column-ownership rule).
- `@page` and `@chapter` take the **declared words** (`@page chapter-start`, `@chapter rules`); a book never invents a page class of its own.

### Naming

- `.dc-component-name` lowercase-kebab.
- Tokens: `--<scope>-<role>` (e.g., `--dc-card-tab-bg`, `--brand-magenta`, `--augmerc-accent`).
- Macros: `@section <word>` for reusable visual components (`@section panel`; the `.dc-X` class spelling is equivalent). `@page <word>` and `@chapter <word>` for where content sits.

### Counter strategy

`@chapter` emits the wrapper element and increments the counter. Pages inherit chapter numbering from that wrapper. **Never hand-apply `.chapter-NN`** — that bypasses the counter.

### Cascade discipline

- Component styles in `components/*.css` expose `--dc-X-*` token surfaces defaulted in `dc-component-defaults.css`.
- Per-book overrides in the book's own sheet (unlayered — it beats this package at any specificity) set those tokens via **natural selector chains** (chapter id → page template → section component).
- Override files NEVER carry bare `.dc-*` rules — only context-scoped selectors (`#ch-X .dc-Y`, `.page.dc-page-Z .dc-Y`, `.dc-chapter-Z .dc-Y`, `.section.dc-X`).
- Section variants ride on the section's own variant word (`@section panel`, `@section flat`, `@section reference`, `lore`, `dm`, `choose`, or a component word such as `@section npc`) or its `.dc-X` class. No utility variant classes (`.dc-accent-X`, `.variant-Y` are forbidden); declared section, page and chapter variants (`@section panel`, `@page chapter-start`, `@chapter rules`) are not utility classes, because each is one word the plugin declares, resolves to one `dc-` class, and sets tokens rather than drawing a one-off look.
- Authors NEVER write per-element class attributes for styling (`{.dc-warning}` on a paragraph is forbidden).

### File ownership

| File | Owns |
|---|---|
| `dc-palette.css`, `dc-identity.css`, `dc-component-defaults.css` | `:root` tokens |
| `dc-fonts.css` | `@font-face` |
| `dc-core.css` | `html`/`body` baseline, element resets, heading defaults, `* { print-color-adjust }` |
| `components/*.css` | Every `.dc-*` component (base + thin variants + token contracts) |
| `components/section.css` | The section variants (`.dc-section-panel`, `-flat`, `-reference`, `-lore`, `-dm`, `-choose`) and the section components |
| `page-templates.css` | `.page.*` layouts, paged wrapper scaffolding, and the location rules for the page and chapter words (tokens only; no column layout: that is core's `@columns`) |
| `page-rules.css` | `@page` declarations, named pages, folio + chapter footers |
| the design guide's own sheet (unlayered) | `div.chapter` scaffolding, design-guide specimen chrome |
| a book's own sheet (unlayered) | Context-scoped layout rules only: chapter / page-template / section context selectors setting `--dc-*` tokens |

---

## IX. Anti-Patterns (explicit)

Do not drift into:

- **Clean corporate manual** layouts
- **Warm parchment fantasy** styling
- **Smooth chrome cyberpunk glamour** (Blade Runner luxury, not creaturepunk)
- **Full-page black neon web aesthetics** that don't reproduce in print
- **Randomized chaos** that hurts scan speed
- **Web-2.0 sheen** — large gradients, gloss, drop-shadow bevels, polished glass surfaces
- **Polished frosted-glass** translucency
- Every page using the same tilt-and-banner trick
- Undefined token names across templates
- Accent colors competing instead of supporting hierarchy
- Too many textures making the page muddy
- Decorative aggression with no focal point
- Component drift into the wall — soft tinted backgrounds, ambiguous edges, no separation from page

- **One colour meaning everything.** Magenta is display punch only; a variant that is only a recolour of another, or that cannot be told apart in grayscale, fails §II.
- **Low-contrast, soft-tint text on a stain.** No body text on `--paper-stain` or any fill darker than the wall; no italic-on-grey reading surfaces.
- **Type under the floors, or inflated past them.** The §VI floors are minimums; do not under-run them and do not pad text beyond them to fake hierarchy.

### Component-level failures (Pass 6/7 specifically)

These polish moves were tried and REJECTED:

- `text-shadow` on display type (reads as web-2.0 sheen)
- Tonal gradient on banner fills (banners want flat ink, not gradient)
- Paper-grain noise overlay on solid fills (didn't visibly land; processing cost without benefit)
- Corner accent triangle via `::after` on specialty cards (broke clipping on lozenge / chamfered shapes)
- Portrait double-edge frame chrome (made empty placeholders MORE prominent)
- Inset cream double-stroke on callouts (looks deluxe-web, not creaturepunk)

When in doubt: keep components FLAT, give them HARD SHADOWS, hard edges, decisive separation from the wall. **Subtle ≠ better. Decisive ≠ overdone.**

---

## X. Image and Texture Use

### Texture rules

- Use grain at very low opacity (2–3% visual strength) on the WALL (page background), never on components.
- Prefer one subtle global texture over many competing overlays.
- Never place noise behind small body text.
- Torn edges + spray effects belong on banners, tabs, dividers — not everywhere.

### Image rules

- Favor high-contrast art with urban decay, hard lighting, threat.
- Let art interrupt layout instead of sitting politely in frames.
- Magenta or orange light accents as supporting note, not whole image strategy.
- Avoid cute expressions, fantasy scrollwork, sleek luxury tech imagery.

---

## XI. Review Requirement — The Four Judges

Before any commit to `components/*.css`, `dc-palette.css`, `dc-identity.css`, `dc-component-defaults.css`, `page-templates.css`, or any markdown file under `dc-design-guide/`, **four designated reviewers must all return GO**. A FIX or NO-GO from any single judge blocks the commit.

The judges are dispatched as parallel agents (Sonnet model, background) with the prompts framed below. Each judge has a specific charter and reads the screenshots + this constitution as their rubric.

### Judge 1 — CSS Architecture

**Charter**: cascade discipline, token contract integrity, naming, file ownership boundaries, no architectural violations.

**Key questions**:
- Are component styles in `components/*.css` with `--dc-X-*` token surfaces?
- Are per-book overrides in the book's own sheet setting tokens via context selectors only?
- Any bare `.dc-*` rules in override files? Any raw property assignments where tokens should mediate?
- Are token contract comments present and accurate on the major components?
- Could a new author add a 9th specialty by following an existing pattern?

**Verdict**: GO / FIX / NO-GO + file-by-file cascade compliance score (1–5).

### Judge 2 — Print Production

**Charter**: POD-safe rendering through the CGATS21_CRPC1 profile (§V). TAC 240%, enforced by the profile. Body contrast ≥ 4.5:1. Hairlines ≥ 1pt in `--ink` or a one-ink tint; small text in `--ink`. Type at or above the §VI floor: every glyph ≥ 10pt; reversed type semibold.

**Key questions**:
- Measure every new or changed token with `scripts/measure-palette-crpc1.py`. Does it print within dE ~4 of the screen, and ≥ 8 from the colours it must differ from?
- WCAG contrast on every text-on-fill pair, including reversed-out.
- Registration risk on hard ink-to-substrate edges (specialty card band/body boundary, etc.).
- Hairline rules thinner than 1pt, or split over three or four plates?
- Any saturated-small-text legibility risks under press dot gain?

**Verdict**: GO / FIX / NO-GO + numeric CMYK + contrast table.

### Judge 3 — Creaturepunk Brand

**Charter**: aesthetic fidelity to **hostile, improvised, urban, cold, aggressive, dirty** Dimm City. NOT fantasy-coded, NOT corporate-clean, NOT smooth-cyberpunk-glamour. The 4-register system (future-tech + ancient-magic + landfill + wonderland) and per-specialty register mix.

**Key questions**:
- Does the page feel like a wall in Dimm City, not a clean book page?
- Do components feel like posters/displays hung on the wall, not embedded?
- Are the 4 registers all visibly present (not just 2)?
- Is the page register cold-urban, not warm-vintage?
- Does color usage feel deliberate and earned, not decorative?
- Does each specialty's register mix read at-a-glance?

**Verdict**: GO / FIX / NO-GO + per-register check + brand-fidelity-blockers.

### Judge 4 — TTRPG Visual Design Contest

**Charter**: would this *legitimately beat* Pathfinder 2e Core Rulebook, D&D 5e PHB, Mothership Player's Survival Guide, and Mörk Borg in a visual design contest (ENnie-tier judging)? The bar is **contest-winner**, not "good for indie."

**Key questions**:
- Per reference book (PHB / PF2e Core / Mothership PSG / Mörk Borg): WORSE / EQUAL / BETTER, with justification?
- Component-by-component score against contest bar (BELOW / AT / ABOVE BAR).
- Top 3 contest-blockers — what specifically prevents the work from being declared CONTEST-WINNER right now?

**Verdict**: CONTEST-WINNER / CONTENDER / NOT YET + comparative table.

This judge typically also acts as the editorial / book-design reviewer (page density, typography rhythm, spread cohesion) and uses the canonical `agent:print/print-layout-reviewer` prompt (or the contest-judge framing above).

### Dispatch pattern

All four judges run in parallel as background sonnet agents. Each is dispatched with:
- A short summary of what changed in the current pass.
- Pointers to the relevant CSS files and screenshots.
- An ask for verdict + top-3 fixes (if FIX) in under 400 words.

Iterate on the union of all four judges' findings. Re-dispatch after fixes land. Loop until **all four return GO simultaneously** (or CONTENDER → CONTEST-WINNER for Judge 4 + GO on the other three).

### Anti-patterns in expert dispatch

- **Don't dispatch judges in isolation.** A single judge approving is not a green light. All four must agree.
- **Don't grade-inflate**. Judges should be honest. "Pretty good" is not GO.
- **Don't trust the chorus over the user's eye.** If the user-eye verdict says over-styled and all four judges said GO, the JUDGES were wrong — they evaluated against a lower bar. Recalibrate prompts to lift the bar.
- **Don't iterate on cosmetic moves while ignoring structural ones.** If three judges flag a fundamental issue (e.g., "the substrate collapsed into the wall"), fix that BEFORE pursuing micro-polish.
- **Don't lose the user's accepted moves.** Track what the user has explicitly liked (outcome ladder depth, AP chip LED treatment, grey paper substrate) and protect those through iteration.

### Per-spread verdict scheme (designer-eye review)

| Verdict | Definition |
|---|---|
| **OK** | Could appear in a professionally published book without editorial comment. Visible type hierarchy. Brand identity coherent. Reviewer can name a positive reason it's ship-ready. |
| **MINOR** | Single flaw a professional art director would mark on first pass. Ragged-bottom > 20%, drifting heading, one card clipping. Shippable with polish. |
| **AWKWARD** | Reader would notice quality problems unprompted. Ragged-bottom > 40%, lopsided spread, under-filled pages with no design justification. When in doubt between MINOR/AWKWARD, choose AWKWARD. |
| **BROKEN** | Reader-facing failure. Content < 40% of spread, blank page that should have content, component clipped mid-word, body text 2-3 words per line. Always blocks GO. |

### Review pre-flight checklist

- Does the page feel hostile without hiding information?
- Is the reading order obvious in under 5 seconds?
- Is disruption focused on display elements rather than body copy?
- Are accent colors limited to a few deliberate hits?
- Are margins and gutter safety respected?
- Is body text comfortably printable at size?
- Does the spread avoid both corporate cleanliness and unusable chaos?
- Does each component register correctly (paper poster vs digital display)?
- Does each specialty component reflect its per-specialty register mix?
- Would this still work if printed slightly darker than the screen proof?

---

## XII. Documentation Layer

- **This file** (`constitution.md`) is the project-level north star.
- [css-architecture.md](./css-architecture.md) — file ownership + load order.
- [adding-macros.md](./adding-macros.md) — plugin authoring guide.
- [knowledge:print/design/creaturepunk-design-guide] — extended aesthetic reference (AKM stash).
- [memory:dimm-city-design-guide-constitution-2026-05-23] — AKM hot-recall of these principles.
- [agent:print/print-layout-reviewer] — canonical review prompt for the quality gate.
- The design guide's own markdown source (`0*.md`, `30*.md`) IS the user-facing documentation.

If those documents disagree, this file takes precedence. Update the AKM memory to match.

---

## XIII. Quick Reference

| Area | Default decision |
|---|---|
| Page background ("the wall") | `--bg` cold ash-concrete |
| Primary text | `--ink` near-black |
| Main accents | brand-magenta / brand-cyan / rust / fungi-glow / crystal-amethyst |
| Body copy | Stable, upright, readable |
| Chaos placement | Labels, banners, image edges, stickers — never body |
| Card feel | Industrial, clipped, slightly darker than page |
| Texture | Barely visible grime on wall only |
| Overall test | Forbidden street intel, not polished UI |
| Component register check | Paper poster OR digital display — not both |
| Type floor | Every glyph ≥ 10pt (`--fs-floor`) |
| Specialty register check | Does the design read its per-specialty mix correctly? |

If it looks like a friendly handbook, it failed. If it looks like a damaged field guide that still reads cleanly, it worked.
