# DC Design Guide — Constitution

The canonical, self-contained north-star document for the Dimm City Design Guide. Every component, token, override, and review verdict in this codebase answers to the principles here. This file is meant to be read once start-to-finish by anyone joining the project.

If a design decision conflicts with this document, the design decision is wrong unless the conflict is explicitly resolved with a constitution update.

**Version:** 2026-10-14
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
- **Components do NOT bleed into the wall** — soft tinted backgrounds that fade into the page colour, low-contrast washes, "subtle web gradients" → all wrong. A poster has a hard edge against brick.
- **The wall has texture; the posters have ink** — the page can carry concrete grain. Components are printed/displayed objects with their own surface.
- **No text is ever printed directly on the wall.** Every glyph sits on a substrate: paper, a panel, a strip, a plate or a chip. That includes what an author writes with no component around it. A free-standing `#` is a banner in the chapter's accent; a `##` is a paper slip pasted to the wall (accent rail, dashed ink foot, hard shadow, masking tape over the foot); a `###` is a plainer tag that shrinks to its words and hangs in from the left (every second one hangs further, so a wall page reads as posters put up by hand); a `####` and below is a label slip that shrinks to its words; loose paragraphs, lists and quotes share one paper sheet per run; a `@columns` run of nothing but prose is one sheet. The folio, the chapter chip and the Citizen File running head are chips (see §IV). The design guide's explainer pages (`@page .dg-doc`) print plain on white and are the one exception: they are not wall pages.

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

1. **Paper posters** — flyers, warnings, hand-stamped notices, torn show bills, forms. Light paper substrate (`--paper-cream`, `--paper-form`, `--paper-zine`, `--paper-light`; never darker than the wall behind reading text). Hard ink. Stamps, sprays, dotted folds. Most callouts (note, warning, vibe, origin, example), the lede, the `choose` form, the shard block, the fiction excerpt, NPC stat blocks, gear entries, the procedure plate, the definition page, design-guide chrome.
2. **Digital displays** — LED tickers, status panels, HUD readouts, AP indicators, dark placards. Saturated or ink-dark fills with crisp reverse-out type. Glow at the edges (via top-edge highlight, not literal glow filters). Outcome ladder chips, AP cost chips, skill-card tabs, title bands, the `dm` alert and section, the visit placard, the at-a-glance readout.

Cards bridge the two: specialty cards and skill cards are cream paper under a bright digital-display band and tab. A single book uses both registers — that's the texture of Dimm City — but a given **component** picks one and stays in it.

### Every variant says what it is — in colour AND in grayscale

A reader flipping pages should know **what kind of content a box holds from its silhouette, fill value and colour before reading a word.** Magenta must stop meaning everything. The rule for every family of variants (alerts, section kinds, blocks, choice cards, factions, gear kinds, specialties):

- **Each variant is distinguishable at thumbnail size in colour.**
- **Each variant is also distinguishable in grayscale.** A grayscale proof (or a colour-blind reader) must still tell the variants apart, so vary **fill value** (light paper / mid fill / ink-dark), **edge geometry** (cut corners, torn, stepped, stripes, dog-ear, double frame) and **label treatment** (chip, stamp, underline, glyph) — never hue alone. A new variant that only recolours an existing one is wrong.
- **Chaos goes on labels, bands, tabs, edges and badges** (the 20% display layer), never on reading surfaces. Body copy stays upright and level.
- **A chapter may re-theme a component's accent but never repaints a variant's identity.** `--dc-section-accent` recolours a panel's bar; it must not turn a warning alert grey-brown or a dm slab rust. Per-chapter overrides set the documented accent tokens and leave the variant tokens (`--dc-alert-*` fills, edges and labels; `--dc-choice-*`; `--dc-faction-*`) alone.

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
| **Value** | Paper / ink | Who it is for | Light paper = player-facing; ink-dark fill = Dream Master or insider; aged or zine paper = fiction and world |

Two registers never share the same hue **and** value: if two variants must share a hue (the dm slab and the vibe sign are both cool), their fill value and edge differ (ink slab with a cyan rail; a light, barely violet sheet in a dashed violet edge).

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
| **Proxy** | ████ HIGH | ████ HIGH | low | low | Tech + magic: deep-magenta band with an LED rim **and** a darker facet plane, a cyan rule, centre-notched gate clip. (Cream on the bright magenta fails 4.5:1, so the band uses `--brand-magenta-deep`.) |
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
- Torn edges belong on the **title bands** of Technosorcerer / Gutterdruid (landfill high: a torn bottom edge, no rule), and on sheets and labels elsewhere (the fiction excerpt, the shard block, the cult faction, the flaw card). They do NOT belong on Augmerc / Cybersurgeon — clinical tech doesn't tear — and they are NOT used on the specialty cards themselves.
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
- **Placement**: both sit at the top of the footer band (the 0.875in bottom margin, measured from the sheet edge), 0.025in below the text block; the 0.225in chip ends exactly 0.625in from the sheet edge, on DriveThruRPG's 0.5in text minimum. On recto and verso, for every page word that prints them.
- **Pagination** is a package duty, not the book's, wherever the rule holds for any book's content: text keeps three orphans and three widows, a card splits between ability rows, headings and dividers stay with what follows. See the per-spread verdict scheme (§XI): a page under about 40% full with no design reason, or a one- to three-line continuation, is a fault to fix in the package first and the book's forced breaks second. A rule that only holds for one book's content (a row or block count, a size guess) is never the package's: it goes in the book's own sheet.
- **Citizen File running head**: an amber tab, cream type, same edge and shadow, hung 0.625in below the sheet top in a 0.875in top margin, ending at the top of the text block.
- **Wall-level grit** is restrained and sits on edges and labels: the tape on a `##` slip, the dashed foot, the hard-border shadows. Vector and opaque only. Nothing clips a glyph: chips and slips are plain bordered boxes; only the title banner's diagonal tail is clipped, and its padding clears it.

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

### Page substrate

Every TAC figure in this section is **measured**, not estimated: a swatch PDF converted with the build's own Ghostscript arguments and its CGATS21_CRPC1 profile (gutterpress `convertToPdfxCmyk`), the CMYK fill operator read back. That conversion builds dark RGB as a heavy four-colour black (raw `#000` = C72 M68 Y67 K88 = 295%), so a token that looks "just black" can sit over the ceiling. House target: **every token ≤ 270%**; hard ceiling 280%.

| Token | Hex | Measured CMYK = TAC | Use |
|---|---|---|---|
| `--bg` | `#c8c5bf` | C21 M18 Y22 K0 = 61% | The wall. Ash-concrete page background — gritty, urban, structural. |
| `--paper-form` | `#f5f3ee` | C2 M2 Y5 K0 = 10% | The `choose` form's sheet: barely lighter than cream, printed stock not a screen. |
| `--paper-cream` | `#f0eee9` | C4 M4 Y7 K0 = 14% | Paper-poster substrate — flyers, callouts, cards on the cream register. Brighter than the wall. |
| `--paper-zine` | `#e9e6e0` | C7 M7 Y10 K0 = 24% | Printed-page neutral between cream and light — the fiction excerpt and the shard block. A neutral, not parchment. |
| `--paper-light` | `#e2ded7` | C10 M9 Y13 K0 = 32% | Lighter-than-the-wall grey paper — the lede, specialty intros, alternate panel fills. |
| `--paper-aged` | `#c8c2b8` | C21 M20 Y26 K0 = 66% | Weathered grey, about the wall's own value — the outcomes ladder rows, field chips, catalog ledger band. Label and rule grounds, not a reading surface. |
| `--paper-stain` | `#b0a89c` | C32 M30 Y37 K0 = 99% | Dark inset wells and label strips (the shard's label strip). **No body text on it**, and none on any fill darker than the wall. |
| `--ink` | `#1e1d1c` | C69 M66 Y67 K76 = 278% | Body text, key rules, heavy borders. |
| `--ink-dark` | `#2f2622` | C61 M66 Y69 K69 = 266% | Heavy callout fills (DM notes), border anchors. |
| `--ink-smoke` | `#4d4339` | C57 M60 Y68 K47 = 231% | Secondary labels, the NPC flavor line (7.4:1 on paper). |
| `--ink-mid` | `#594f43` | C55 M56 Y67 K38 = 217% | Secondary card text. |
| `--ink-dust` | `#665b4e` | C53 M54 Y64 K29 = 200% | Form-label micro-headings, dashed dividers (4.58:1 on cream). |

### Brand signature layer

The dimm.city web-palette analogs, SWOP-corrected for POD:

| Token | Hex | Measured CMYK = TAC | Use |
|---|---|---|---|
| `--brand-magenta` | `#c026d3` | C41 M85 Y0 K0 = 126% | Bright neon signal — section accents, gateway banners |
| `--brand-magenta-deep` | `#8a0a9a` | C56 M100 Y0 K0 = 156% | Press-safe magenta on cream (crit row text-on-fill 6.21:1) |
| `--brand-cyan` | `#00bcd4` | C70 M1 Y16 K0 = 87% | Augmerc accent, wirephreak's LED rule |
| `--brand-yellow` | `#ffd700` | C1 M13 Y100 K0 = 114% | Brand radiant — etherlock accent, peak triumph |
| `--brand-violet` | `#7030b8` | C69 M87 Y0 K0 = 156% | The world: lore, vibe, cabal, treasure. No specialty uses it |
| `--signal-indigo` | `#4430e0` | C81 M78 Y0 K0 = 159% | Wirephreak accent: an electric blue-violet of its own |

### HUD / digital-display layer

| Token | Hex | Measured CMYK = TAC | Use |
|---|---|---|---|
| `--hud-blue` | `#1f6f94` | C87 M50 Y26 K4 = 167% | Mid HUD teal — primary stat lines, secondary chrome |
| `--hud-blue-dark` | `#14516e` | C93 M64 Y38 K20 = 214% | Deep teal — borders, rules, H2 text |
| `--hud-blue-dim` | `#7ab8d0` | C50 M13 Y12 K0 = 76% | Light cyan panel tint — note alert fill, table headers default, reduced-cost AP chip |
| `--hud-magenta` | (alias --brand-magenta) | — | Brand-signature cyber-magenta |
| `--hud-panel` | `#eeece8` | C5 M5 Y7 K0 = 16% | Neutral light cream — note/callout default fill |

### Gutter / fire-and-blood layer

| Token | Hex | Measured CMYK = TAC | Use |
|---|---|---|---|
| `--crimson` | `#e1261c` | C5 M98 Y100 K0 = 203% | PMS Red 032 — danger, harm, active states, ROLL THE DIE tags |
| `--blood` | `#901a12` | C27 M99 Y100 K28 = 254% | Oxidised arterial — DM-chapter table headers (6.3:1 on cream) |
| `--orange` | `#d4500a` | C11 M82 Y100 K2 = 195% | Burnt circuit-board — warnings, AP tags, arrows |
| `--orange-deep` | `#a03808` | C25 M88 Y100 K20 = 233% | Press-safe orange on cream (mixed row 5.25:1) |
| `--rust` | `#b23a12` | C21 M89 Y100 K12 = 222% | Burnt rebar — section accents, miss row |
| `--amber` | `#7a5a20` | C41 M57 Y100 K29 = 227% | Sulphur-scorched brass — gear-chapter section accent |
| `--deep-rust` | `#70200e` | C32 M91 Y100 K45 = 268% | Shadow rust — deepest warm dark (was `#6a1a08`, 273%) |
| `--amber-dark` | `#5c3c10` | C44 M66 Y100 K49 = 258% | Charred amber |

### Fluorescent fungi layer (wonderland)

| Token | Hex | Measured CMYK = TAC | Use |
|---|---|---|---|
| `--fungi-glow` | `#c8e040` | C26 M0 Y91 K0 = 116% | Bioluminescent yellow-green — gutterdruid accent, outcome-row.hit (with ink text) |
| `--fungi-mid` | `#6aa030` | C64 M17 Y100 K2 = 183% | Luminous lichen mid — reserved for a future fungi-faction signal (not yet a token) |
| `--fungi-rot` | `#30461e` | C72 M47 Y97 K51 = 268% | Deep moldering green — outcome-row.fail (large-fill only; was `#2a4015`, 274%) |

### Ancient crystals layer (magic)

| Token | Hex | Measured CMYK = TAC | Use |
|---|---|---|---|
| `--crystal-amethyst` | `#6a3a8a` | C71 M92 Y9 K1 = 173% | Mineral violet — the world's gem tint (treasure); no longer a specialty accent |
| `--crystal-slate` | `#52626f` | C70 M54 Y43 K18 = 185% | Cool slate stone — generalist accent |
| `--crystal-aqua` | `#4a98a8` | C71 M26 Y30 K0 = 127% | Crystalline aquamarine — dualist accent |
| `--crystal-citrine` | `#b89a3a` | C28 M35 Y96 K3 = 162% | Burnt mineral gold — reserved for a future crystal-faction signal (not yet a token) |

### Specialty palette (per-specialty triad plus band and chip)

Every specialty has three tokens: **accent** (bright signal), **mid** (chrome/structural), **dark** (card-body fill). Two more are wired from them: the **band** (`--spec-band`, the title-band fill and the specialty-card header: the accent, except Proxy's deep magenta) with its **on-band** type (`--spec-on-band`, ink or cream, whichever holds ≥ 4.5:1), and the **tier chip** (`--spec-chip-bg/-fg/-edge`, the pill on a skill-card tab: the accent with ink or cream type, or a cream chip with dark type where the accent fails 4.5:1 for 10pt type: Technosorcerer and Proxy). The old bronze/gold/silver tier badges are gone: a tier pill belongs to its specialty, not to a position. Measured TAC of the dark in the last column: every dark is ≤ 268%.

| Specialty | accent | mid | dark | band / on-band | Register lean | dark TAC |
|---|---|---|---|---|---|---|
| augmerc | brand-cyan | `#006878` | `#003a40` | accent / ink | future-tech HIGH + landfill mid | 260% |
| technosorcerer | orange | `#7a3008` | `#4c290f` | orange / ink | magic HIGH + landfill HIGH | 268% |
| streetwarden | `#4db840` toxic-civic | `#347828` | `#294c1f` | accent / ink | tech mid + landfill mid | 268% |
| gutterdruid | fungi-glow | `#4d6020` | `#394017` | accent / ink | landfill HIGH + wonderland HIGH | 268% |
| cybersurgeon | `#a8b4b8` chrome | `#606870` | `#303840` | accent / ink | future-tech HIGH | 246% |
| wirephreak | signal-indigo | `#2f2290` | `#1e0f50` | accent / cream | future-tech HIGH + landfill mid | 268% |
| proxy | brand-magenta | `#9a1896` | `#8a1a90` | magenta-deep / cream | tech HIGH + magic HIGH | 156% |
| etherlock | brand-yellow | `#8a6a00` | `#46360c` | accent / ink | magic HIGH + landfill mid + wonderland mid | 267% |
| dualist | crystal-aqua | `#2a6878` | `#143a4a` | accent / ink | magic HIGH + tech mid + wonderland mid | 252% |
| generalist | crystal-slate | `#3a4854` | `#212a32` | accent / cream | magic HIGH | 265% |

### Production rules (CMYK + press-safe)

- POD target: SWOP coated v2 / GRACoL gamut.
- **TAC ceiling: 280%; house target ≤ 270% for every token.** Any token over 280% is print-unsafe. TAC is measured through the build's own conversion (see the substrate note above), never estimated from a hex: a dark that looks fine can read 284%. Re-measure when you add or retune a dark, and write the figure in the token's comment in `dc-palette.css`.
- Hairlines: ≥ 0.5pt. Any rule thinner vanishes in CMYK.
- Body-text contrast: ≥ 4.5:1 (WCAG AA).
- Large-text contrast: ≥ 3:1.
- Reversed type: semibold minimum, only on solid fills, and never below the 10pt floor.
- Body text never on noisy or tinted backgrounds, and never on `--paper-stain` or any fill darker than the wall (`--bg`) unless it is a decisive dark fill with light type.
- **The type floor is 10pt for every glyph, no exceptions** (§VI): body, tables, captions, chips, tabs, tier pills, AP chips, badges, labels, stamps, folios, stat keys. The token is `--fs-floor` (`dc-palette.css`).
- Every variant must also pass the colour-and-grayscale test (§II).
- Magenta + crimson drift muddy in early proofs — proof these first.
- Avoid rich black for small text.

---

## VI. Typography

| Role | Preferred | Fallback | Size |
|---|---|---|---|
| Display | `lixdu` | Titillium Web Bold | H1 26–32pt, H2 18–24pt |
| Body | Titillium Web | Tomorrow | Reading floor 10pt; the package sets 12pt (`--fs-body`), 11pt compact (`--fs-body-sm`), with 13–15pt leading |
| Labels / Mono | Tomorrow | monospace | All-caps labels 10pt (the floor), tracked 0.08em or wider |

### Type floor: 10pt, for ALL text

**No glyph the package prints is smaller than 10pt.** There is one floor and no second, smaller floor for "chrome". It is the token `--fs-floor` in `dc-palette.css`; components reference it rather than writing the number. It is a floor, not a target: running body stays 12pt, compact prose 11pt. Short all-caps labels sit exactly on it, with their tracking brought down (0.08–0.12em) so they do not balloon.

| Text | Size |
|---|---|
| Running body, rules and ability text, table cells, stat lines, captions, card pitches, callout and definition bodies, lede/flavor/fiction, list items, intro text | **≥ 10pt** (body 12pt, compact 11pt) |
| Chip, badge, tab and tag labels, tier pills, AP chips, stickers, mono section labels, table header cells, field labels, stat keys, band names, running-head and folio chips, stamps | **10pt**, tracking ≥ 0.08em |
| Reversed type (light on a solid fill) | **10pt, semibold or bold**, solid fills only |

The page baseline (`dc-core.css`) keeps to it: body 12pt, table cells and header cells 10pt, inline code never under 10pt, lists, definition lists and figure captions inherit the 12pt body. The credits colophon is 10pt. The footer chips (folio, chapter coupon) and the citizen-file running head are 10pt in a 17pt box. The design guide's own running foot, kickers, code fences and swatch labels are held to the same floor.

Display-face (lixdu) names inside a component must not wrap a short name onto two lines in a two-column run: size and track them so typical names fit (an NPC name at 11pt and 0.03em; a catalog entry name at 11pt with balanced wrapping; a specialty-card name on one line).

### Type hierarchy

| Element | Spec | Notes |
|---|---|---|
| H1 | lixdu, 26–32pt, uppercase | Chapter punch, minimal copy |
| H2 | lixdu, 18–24pt | Can sit on angled magenta banner |
| H3 | bold display or body-bold, 13–16pt | Use accent color sparingly |
| H4 | body-bold or mono-bold, ~13pt | Component sub-headings (skill names, stat-block name) |
| H5 | mono-caps, 10–11pt with 0.1em tracking | Chrome labels (TRAITS, EQUIPMENT, OUTCOMES) |
| Body | 12pt (reading floor 10pt) with 13–15pt leading | Default reading size |
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

Each component lives in ONE surface register (paper poster or digital display) and inherits visual cues from its specialty's register mix. Every family of variants obeys §II: each variant differs in fill value, edge and label, not hue alone.

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

A section kind is read from its bar, its sheet and its silhouette before its words. Each cuts its own corners, and the cut carries the meaning (see "Shape language" below): precise symmetric chamfers for player rules, a file-folder tab for the classified, long asymmetric slashes for the world, ticket notches for a form, a sign plate for danger, a torn edge for fiction and landfill. Padding on every clipped edge is the cut's depth plus 2pt; no glyph, rule or marker is ever cut.

| Kind | Bar | Sheet | Silhouette | Colour |
|---|---|---|---|---|
| `panel` | solid accent bar | cream | one larger chamfer (top right), a chipped bottom-left corner | the chapter accent (magenta by default; the only kind chapters re-theme) |
| `reference` | pale HUD band ruled in ink above and below (a machined spec-sheet header) | pale blue wash, tight 10pt rows | four small even machined chamfers | HUD blue: a look-up |
| `lore` | deep violet bar, torn along the top | lilac, recessed | long ASYMMETRIC slashes: shallow top-left, steep bottom-right | violet: the world |
| `dm` | ink bar with a cyan rule, a cyan rail | cold concrete, recessed | a file-folder tab in the box's own top band (it carries *Dream Master*, cyan on ink; its own layer, so a page break cannot strand it) and one opposite corner cut, bottom right | cyan on ink: Dream Master only. The tab is drawn with or without a heading |
| `choose` | none: a form | a paper sheet barely lighter than cream (`--paper-form`) | a ticket: a V punched in the middle of each side, a perforated foot, an ink edge, recessed (sunk into the wall: a cast shadow along the top, a light lip on the bottom and right), no drop shadow | ink title over a double rule in the chapter accent; heavy ink tick boxes (2.25pt); a hazard-yellow *Choose* stamp; dotted write-in rules. A printed, stamped form, not a web control |

**Hung or sunk.** `panel` and `reference` hang on the wall like posters (a hard drop shadow). `lore`, `dm` and `choose` are recessed, sunk into the wall: no drop shadow, the wall's top edge casting a hard shadow down over the sheet's top and its title bar (the rail stays clear), and a light lip along the bottom and right (`--dc-section-recess`, `-recess-depth`, `-shade`, `-lip`). All vector, opaque inset shadows.

**Edges carry the kind by shape and colour.** Clip-path silhouettes and border colour are the primary way a kind is told apart; dashed and dotted borders are kept for the few places where the dash is the object itself: the warning's hazard-stripe rail and the enforcer's hazard band, stencil lines (the `##` slip foot, `.dc-spray`), write-in rules on a form, the origin stamp's worn ring, the side-effect field frame, link and ROLL THE DIE! underlines, and the tech specialties' LED tick rules. Everything else is a solid edge.

**Labels are raised.** Every label (an alert label, a section tab or stamp, a block tag, a choice chip, a faction or entry badge, a field label, a tier pill, a price tag, a die chip) stands off the element it sits on with a hard 2px ink shadow (`--dc-label-shadow`), or, where a clip-path would cut an outer shadow, the same ink as an inset bottom-and-right edge (`--dc-label-edge`).

Magenta is the `panel` default only. `flat` (a rail, no bar, no clip, no shadow) is distinct from all of these. A bare `@section` (no variant word) is a plain sheet of paper under the text: no text is ever set straight on the brick wall. Every section kind sets `--dc-accent-ink`, the text-safe ink of its accent (the accent mixed 72% toward ink, so a chapter that re-themes the accent re-themes it; dm sets HUD blue, slate a light tint of crimson on its dark body), which `ROLL THE DIE!` and other accent text read.

### Block registers (`@block`: panel, slate, shard)

- `.dc-panel`: HUD-blue band, symmetric hex chamfers. Player-facing rules summaries, structured data.
- `.dc-slate`: a sign plate: octagonal corners in a heavy crimson frame, an ink body, a **blood** band with a crimson rule and a stamped (double-edged) *Binding* tag. Binding rulings, Dream Master directives that settle an argument. Not magenta and not cyan, so it cannot be mistaken for `dm`.
- `.dc-shard`: light zine paper (`--paper-zine`), a torn (zig-zag) foot and a dog-eared corner, a taupe label strip with an ink title and a solid rule, no accent hue. Fiction, atmosphere, setting asides.

### Choice cards (`@flaws`, `@ideals`, `@dreams`)

- A choice card says which choice it is. The enclosing kind sets `--dc-choice-accent/-tint/-kind` and the card's shape; the card reads them.
- **Flaw** = blood, the darkest sheet with a heavy solid edge, a deep crack (a 40x26px nick and a foot jagged up to 13px) and a blood-tinted quote. **Ideal** = HUD blue, the mid sheet with a clean solid edge, a steady ticket stub (14px V notches in each side), a rule under the name. **Dream** = violet, the lightest sheet with a double edge, a top edge rising 30px to the right and a perforated foot (two V tears). The three differ in fill value and edge weight, so they differ in grayscale. Siblings differ in silhouette; the two ticket shapes mean "a choice", the torn one "a cost".
- The choice chrome is scoped to a card inside `@flaws`/`@ideals`/`@dreams`; any other `.dc-card` (a gear entry, a faction) keeps the plain card. Each choice carries a 6px rail and 5px top band in the kind colour, a 1.5pt ink edge, a one-word mono chip (10pt semibold, reversed) (FLAW / IDEAL / DREAM) over the name, and the closing quote in a kind-tinted well (ink on it, never grey `--paper-stain`).
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

- **Surface**: paper poster register — paper-cream substrate with a printed colored header. The full-dark-fill pattern was over-styled; specialty color lives in the **header band + title + thick left border**, NOT the card body.
- Card body: `--paper-cream` (default). Body text: `--ink`. Reads as a printed flyer pasted on the brick wall.
- **Colored header band**: thick top border (~16pt) in the specialty's bright band colour (`--spec-band`). This is the specialty's primary visual signature at grid scale.
- **Colored title**: the h3 title is the specialty's dark, set on one line (a name such as TECHNOSORCERER is tracked tighter, never wrapped).
- **Thick colored left border** (3pt) in the band colour — secondary signature, vertical anchor.
- **Outer 1.5pt border** in the specialty's mid color — frame.
- Per-specialty clip-path geometry — secondary identity cue, in the same language as the skill cards (see "Specialty silhouettes"); every cut stays clear of the type (padding on a clipped edge is the cut depth plus 2pt or more).
- **The catalog is a spread.** On `@page specialty-catalog` the ten cards are one designed two-page spread: it opens on a left page, the title, the lede and four cards fill the left page and six the right, in aligned rows of equal height (wrapped flex rows, two across; the package keeps `grid-template-columns` for single components), and nothing else shares the two pages. Each card is a poster: the portrait on top in a single ink-matted frame cut in the specialty's own silhouette (a picture that has not loaded reads as a paper-aged field with its alt text), then the name (display, on one line), the tagline (mono caps over a rule) and the pitch (10pt), with an index chip (01 to 10) on the portrait. The dense card (a floated thumbnail) is the card anywhere else.
- **NO** corner accent triangles, NO portrait double-edge framing, NO noise overlays, NO LED-rim inset highlights, NO tonal-lift gradient on the body, NO hazard-tape borders, NO torn-paper irregular clip-paths — all Pass 6/7/8 experiments were rejected by user-eye review as over-styling. Restraint wins.
- The rule: **specialty color belongs in border, title, and at most a tint of the substrate** — not as a saturated fill across the entire card.

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
- Type is 10pt semibold (the floor). The triangles and the lamp are drawn as CSS shapes (borders and a radius), not glyphs: vector in PDF/X and independent of any font.
- Variants by AP cost, told apart in colour **and** by a glyph or fill value: **free** = an unlit LED (the grey lens of a dead indicator, ink type, ink edge and a hollow lamp: the quietest chip, so "0 AP" is not a red flag), **standard** = HUD blue dark, **reduced** = pale blue with a down-triangle, **increased** = blood with an up-triangle, **VAR** = deep magenta (cream on the bright magenta is 4.06:1), **special** = amber with cream type. Free and increased are never the same red.

### Callouts (.dc-alert variants)

- **Surface**: mostly paper poster register; `dm` and `visit` are dark placards (display register). One shell, eight registers, told apart by silhouette, fill value, edge and label — in colour and in grayscale.

| Register | Fill (value) | Silhouette | Edge | Label |
|---|---|---|---|---|
| `note` | HUD-blue dim (mid) | machined 6px chamfers on all four corners, one chipped notch (player rules) | blue rail | plain mono caps |
| `warning` | light warm cream | sign plate: octagon, 12px cuts (danger) | 14px yellow/ink hazard-stripe rail, 3px ink frame with a 2px crimson second pass out of register | yellow caution-tape chip with ink type, rotated -1.5deg |
| `dm` | ink-dark (darkest) | file folder: a 12px tab over the left 42% and one cut corner (classified) | 3px cyan rail | cyan chip with ink type, top right (Dream Master only) |
| `vibe` | barely violet (light, flat) | long shallow diagonals at two opposite corners (the world) | one violet edge all round, no rail, a tan tape strip on top | violet-edged chip; italic voice |
| `origin` | warm paper (light) | torn bottom edge and a 16px dog-ear (backstory) | rust rail | crimson double-bordered rubber stamp with a worn (dashed) outer ring, rotated -2deg; italic second-person voice |
| `location` | cool map paper (light) | torn bottom edge and a 16px dog-ear, as origin (a place written up) | teal rail | deep-teal double-bordered rubber stamp with a worn (dashed) outer ring, rotated -2deg |
| `visit` | fungi green (dark) | wobbly organic polygon ending in a signpost point (a place) | none | map-pin glyph + underlined caps |
| `example` | cream (light) | ticket: a V notch in the right edge (a sample) | cyan rail | taped-on tag |

- Flat solid fill — no tonal gradient, no inset cream stroke on the paper registers (the Pass 6 attempt stays reverted). The warning's ink frame is a hard ring and the vibe's edge a single line, not a double stroke on a fill. All edge art (the hazard rail, the dog-ear fold) is drawn in vector, never a gradient: a skewed dashed-border rail and a clip-path triangle.
- Every clipped edge is padded by at least its cut depth + 2pt, so no glyph is ever cut. Every variant sets `--dc-accent-ink`, the text-safe ink of its own accent on its own surface (note a 50% HUD-blue/ink mix, warning and origin `--blood`, dm `--hud-blue-bright`, vibe `--brand-violet`, visit `--fungi-glow`, example `--hud-blue-dark`); the lede sets it from `--dc-intro-ink`.
- Body copy is level, ≥ 10pt (the reversed DM and visit bodies are semibold); labels 10pt mono caps tracked 0.1–0.14em. Chaos is on the labels and edges only.
- A chapter must NOT re-theme a callout's variant tokens: identity survives re-theming.

### NPC stat blocks

- **Surface**: paper poster register (cream-stamped + 2pt top-rule on name + chrome labels)
- Name (H4) gets a 2pt top-rule in `--rust` (chapter accent) — `border-top: 2pt solid var(--rust)`. In a two-column run the name is 11pt tracked 0.03em so "GREASE MONKEY" stays on one line.
- TRAITS / EQUIPMENT / CYBERNETICS (H5) at 10pt mono caps with 0.1em tracking — read as chrome labels, not competing headings.
- The flavor line (`>`) is a ruled line, not a well: a 4px rail in the block's rule colour, ink-smoke text on the paper.
- Primary stat line (HP/damage) is a **chip**: its first line set 12pt bold, cream on the block's primary colour (`--hud-blue-dark`; blood in a rust chapter) via `::first-line`, so it is the first thing scanned. A second line in the same paragraph (Fodder/size) falls under it as a small-caps mono tag, 10pt (stat lines are reading text), `--ink-smoke`; written as its own paragraph it is the same tag at 10pt semibold. The stat lines are chosen by position (the first two paragraphs after the `>`), so a description belongs inside the quote, not between the quote and the stat lines. The compact variant draws both as 10pt semibold chips.

### Factions (`@faction megacorp | cabal | cult | enforcer`)

Each kind has its own silhouette, top band, name colour and badge:
- **megacorp**: machined: a blue rectangle with an L-shaped step out of the top right and bottom left, cool wash, an ink-blue band with a cyan edge, blue name, square badge. Bands are drawn as solid inset shadows (vector), never gradients.
- **cabal**: violet, long asymmetric slashes (shallow top-right, steep bottom-left: lore's cuts mirrored), lilac sheet, deep-violet band, an inset violet shadow.
- **cult**: blood, torn top and foot, a blood rail, blood band, pale blood wash, blood name.
- **enforcer**: a sign plate: an octagon in a heavy ink frame, an ink-and-yellow hazard-stripe band (a yellow strip under a skewed thick dashed ink border: vector), the name set as a yellow label in ink, an ink badge with yellow type.

### Fiction excerpt

- A page sunk into the wall, or revealed from behind it (the opposite of a hung poster): a dark ragged cavity (`--dc-fiction-cavity`, a torn polygon `--dc-fiction-hole`) with the aged page (`--paper-zine`, a dog-eared shape) sitting back inside it. The hole casts a hard shadow down the page's top and left (`--dc-fiction-depth`, 6px; 10px on a chapter-start page) and a light lip (`--dc-fiction-lip`) catches on its bottom and right. Vector and opaque, no blur. No rail, no title bar, narrative leading; text sits only on the page, 10pt+. Differs from the lede (a light panel with a rail), flavor (a rail and no box) and the panel (a bar and a rail). Painted by clipped sibling layers, so the box itself is not clipped and its margin is the rim.

### Entry cards by kind (`@gear` and its kinds)

Each kind is a silhouette, a surface value, a mark, a badge and a name colour, not a rail colour alone:
- **gear**: a hang tag — a paper card in a heavy ink frame, top-left and bottom-right clipped, a rust rail and badge, a ring eyelet, the bold price line stamped as a raised, rust-edged price tag. No tan: cool paper, hard against the wall.
- **augment**: a spec chip — the lightest cool plate, a stepped PCB notch top-right, a cyan top rule, a teal name.
- **treasure**: a gem — pale amethyst, an octagon cut, one hard two-tone facet, a violet rail, a hexagon badge.
- **vehicle**: an industrial plate — concrete, octagonal 12px cut corners, a heavy 3px ink inset frame, an inner seam, a yellow rail and badge. No hazard stripes: those are the danger register's.
- **drug**: a prescription label — an irregular, wobbling organic outline, lime tint, one frame (a fungi-green head band and rail), an "Rx · Drug" pill badge, a green name.

An entry never splits across pages.

### Catalog (`@section catalog`)

A price board: the entries are ruled in their kind's colour, not boxed, and each is kept whole (it never splits across a column or a page; the catalog itself splits between entries). The title bar is a ledger header, a pale aged-paper band under heavy ink rules with an ink rail and an INVENTORY chip: not a magenta bar, and not a dark one (a dark bar is the Dream Master's).

### Fields

One chip family (the same slanted-edge label chip) for all six. What each means shows in its frame: **effects** = a solid teal frame on a pale teal ground, a "+" on the chip (the benefit); **side effects** = a dashed blood frame on a pale blood ground, a "–" on the chip (the cost). SPECS is the dark strip with a yellow rail; traits and equipment are a plain line under a chip; requires is a bar.

### Procedure (`@procedure`)

An instruction plate, not a tinted list: a cream surface, a 2px ink frame, a hard shadow, a solid HUD-blue number strip down the left (reversed 12pt mono numerals), step text in ink at 10pt, ruled dividers, bold leads in `--ink` (not red), and a staple holding the plate to the wall (the grit cue). Text never sits on the wall. The list may split between steps; each step stays whole.

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

**Charter**: POD-safe rendering (SWOP coated v2 / GRACoL gamut). TAC ceiling 280%. Body contrast ≥ 4.5:1. Hairlines ≥ 0.5pt. Type at or above the §VI floor: every glyph ≥ 10pt; reversed type semibold.

**Key questions**:
- CMYK estimate every new or changed token. Any over 280%?
- WCAG contrast on every text-on-fill pair, including reversed-out.
- Registration risk on hard ink-to-substrate edges (specialty card band/body boundary, etc.).
- Hairline rules thinner than 0.5pt that will vanish on press?
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
