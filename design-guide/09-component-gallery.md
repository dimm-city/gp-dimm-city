@chapter C.09 #ch-gallery .dg-guide

@page .page-chapter-start .dc-chapter-start

# Component Gallery

@page

@lede

Live specimens for every component in the Dimm City design system, each rendered
with real, representative game content and full variant coverage. The gallery is
organized by role — prose and typography, alerts and callouts, block registers,
sidebars and panels, tables, the specialty system, gear and stat blocks, and the
divider and reference furniture. This chapter is the canonical render: the
design-system mirror sources its component cards directly from these specimens,
so every wired variant — skill-card highlight, the AP chip set
(standard / reduced / increased / special), two-column skill bodies,
dualist and generalist shells, and continuation markers — appears here exactly
as it ships.

@end-lede

---

# 01. Prose & Typography

The base type layer every Dimm City page inherits — narrative paragraphs, the framing lede, in-world voice, and the spray-paint heading chrome. These components need no specialty or learning-path wrapper; they carry the DC type scale, leading, and accent color on their own.

---

## Body Prose

Standard markdown paragraphs inherit the DC type scale, leading, and color automatically — no class or wrapper required. **Strong text** lands in burnt orange and *emphasis* shifts to warm smoke, so a paragraph can carry rules emphasis and tone without ever reaching for HTML.

When an enemy falters, you may trigger one of the following counters. **Backbiters** are simply part of what makes an Augmerc dangerous — they don't wait for permission, and they don't telegraph. A trained merc reads the opening half a beat before it appears, which is the difference between a *clean* hit and a wasted action.

Most of what you'll read in this book lives at this register: plain prose doing the work, with the occasional bold term or italic aside to mark a keyword or a voice that isn't yours.

---

## Intro Lede

@lede

The city didn't go quiet — it got loud. That feline snarl tore through the alley speakers, chased hard by the thundercrack of gunfire. You came to Dimm City to disappear, and instead the whole block learned your name.

@end-lede

---

## Flavor Text

In-world voice for atmospheric lines and card flavor — italic, accent-railed, and always *spoken from inside the fiction* rather than about it. Standalone flavor uses the `[!FLAVOR]` alert; stacking a few here shows how the register reads across different voices.

> [!FLAVOR]
> "How bright's it ay?! Anotha cycle, anotha scar — an the city still don't know yer name."

> [!FLAVOR]
> "See an opening, ya take it. Best time to hit 'em is when they think it's over."

> [!FLAVOR]
> "Down here we don't ask what you were before the grafts. We ask what's left."

---

## Pull Quote

Large-format excerpt with accent rules above and below. Use sparingly — one per chapter — to let a single line breathe. The attribution sits on its own line after a blank `>`.

> [!PULLQUOTE]
> The rig braces and answers every swing.
>
> Field manual, second draft

---

## Blockquote

Epigraphs and attributed in-world text, rendered with the accent-alt left rail and italic body. Plain markdown `>` — no alert tag — carries quotes, asides, and signed fragments.

> Every city has a language. Dimm City's is neon, static, and the sound of someone's implants glitching at 3am. Learn to read it or learn to bleed.
>
> — Hollis Vance, *Street Anthropology Vol. 4*

---

## Code Block

Fenced code blocks render with an orange left border, cream substrate, and Tomorrow monospace. They carry authoring syntax, macro examples, and any literal text that must not be reflowed.

```markdown
@skill
#### Devoted Strike | PRX1.1
> You don't swing — you transmit.
1. **0 AP** *Channel:* Make a melee attack. On a Hit, add Devotion to damage.
@end-skill
```

---

## Banners & Headers

The three heading treatments that give a Dimm City page its structure: the chevron banner opens a chapter, the spray banner breaks a major topic, and the spec-tweak rule flags an optional mechanic. Stacking all three shows the hierarchy at a glance. The demos below are wrapped in a `@section` so their heading levels render as live banners without being read as section breaks.

@section .dc-banner-demo

# Augmerc {.dc-chevron}

## Biting Distance {.dc-spray}

### Spec Tweak: Wired to Kill {.dc-spec-tweak .dc-no-top}

@end-section

A spec-tweak rule sits beneath its spray banner and reads as an optional mechanic — here, the `.dc-no-top` modifier pulls it tight against the heading above so the rule and its trigger stay visually bound.

---

# 02. Alerts & Callouts

The alert family layers thin variant classes on the shared `.dc-alert` shell. The inline GFM form (`> [!NOTE]`, `> [!WARNING]`, and so on) covers single-paragraph callouts; the `@callout` and `@dm-note` block macros handle multi-paragraph content, lists, and nested prose. This specimen stacks every variant together so the full register range is visible at a glance.

## Alert & Callout Family

Note, Warning, Vibe, Origin, Visit, Gear, and Dream Master callouts shown back-to-back, followed by the multi-paragraph `@callout` and `@dm-note` block forms.

> [!NOTE]
> A character may hold no more than one Signature Augment at a time. Installing a second requires a Cybersurgeon and an open augment slot — the old graft has to come out first, and that's its own scene.

> [!WARNING]
> Trauma Patches stabilize a dying character but do not restore HP. A character at 0 HP with a Patch applied is still incapacitated and cannot act until they receive proper treatment between scenes.

> [!VIBE]
> The rain in Dimm City never quite stops — it just changes color under the signage. Somewhere below the overpass a busted holo loops the same ad for noodles that closed down two years ago, and nobody's bothered to kill the feed.

> [!ORIGIN]
> You didn't choose the street — the street chose you. Before the grafts, before the crew, there was just hunger and the particular talent for surviving what should have killed you. The city remembers that. So should you.

> [!VISIT]
> The Neon Bazaar doesn't close. Day-shift workers and third-shift scavengers brush shoulders between stalls selling augment cartridges, black-market permits, and fried synthetic crab. If you can name it, someone here is selling a knockoff of it two stalls down for half the price.

> [!GEAR]
> **Ripper Blades (Mk II)**
>
> Melee. Damage 1d8+STR. *Serrated:* on a critical hit, the target bleeds for 1d4 damage at the start of their next turn. Retractable — no visible profile when sheathed.

> [!DM]
> If a player hasn't chosen their starting gear by the end of session zero, hand them a Scavenger Pack and move on. You can always backfill the details once the table finds its rhythm — don't stall the first session over an equipment list.

@callout variant="warning"

**Heat is shared, not personal.** When any member of the crew draws Corporate attention, the whole crew's Heat track ticks up — not just the one who pulled the trigger.

At Heat 3, expect a response: a tail, a frozen account, a contact who suddenly stops returning calls. At Heat 5, the crew is actively hunted, and every public roll carries a complication. Heat only clears between jobs, and only if the crew lies low or spends a favor to bury the paper trail.

@end-callout

@dm-note label="Running the Setup"

The fixer offering this job doesn't know it's bait — they're a cut-out, paid to pass the contract along and ask no questions. The real client wants the crew burned, not the cargo moved.

If the players investigate before accepting, they can smell the trap with a Streetwise roll, DC 14. On a Hard Choice, they learn it's a setup but not who's behind it; on a clean Hit, they get a name. Either way, let them choose to walk in with eyes open — a knowing crew makes for a better heist than an ambushed one.

@end-dm-note

---

# 03. Block Variants

The four `@block` registers each carry a different kind of content. The variant class is set on the opener — `@block .dc-panel`, `.dc-slate`, `.dc-shard`, or `.dc-codex` — and the optional `label="…"` fills the title band. Each specimen below renders the register with the kind of content it is built to hold.

---

## Panel — Tactical / Stats Summary

The HUD-blue `.dc-panel` carries player-facing rules summaries and structured combat data: the action economy, range bands, and at-a-glance numbers a Dreamer reads mid-fight.

@block .dc-panel label="Action Economy"

On your turn you get **one Move and one Action** — that's your pulse for the round. Spend Augment Points (AP) to push past it.

- **Move:** Shift one Distance band closer or farther, or reposition within your current band. Free.
- **Action:** Attack, Hack, Interface, or trigger an ability. Free unless the ability lists an AP cost.
- **Out-of-Turn:** One free reaction per round. Each extra reaction costs **+1 AP**, and most don't replace your Move or Action.

You start every dream with **10 AP**. Run dry and you recover **1 AP** per full rest, stacking up to a **5 AP** rest cap in a single session.

@end-block

@block .dc-panel label="Distance Bands"

| Band | Range | What you can do |
|---|---|---|
| **Reach** | Adjacent | Melee, grab, hand off gear |
| **Near** | Same room / alley | Move in one action, short throws |
| **In Range** | Across the gap | Ranged shots only — close the distance to melee |
| **Far** | Two moves out | Two full turns of bad ground to cross |

@end-block

---

## At-a-Glance Cards — Stat Grid

A compact label/value grid for character sheets, specialty summaries, and creature previews → `.dc-at-a-glance-cards` / `.dc-at-a-glance-card`. Each card holds one `<h4>` label and one `<p>` value. Shown here as a Citizen's combat snapshot, the row a Dreamer scans before the dice come out.

<div class="dc-at-a-glance-cards">
  <div class="dc-at-a-glance-card"><h4>HP</h4><p>14</p></div>
  <div class="dc-at-a-glance-card"><h4>Speed</h4><p>Near</p></div>
  <div class="dc-at-a-glance-card"><h4>Edge</h4><p>+2</p></div>
  <div class="dc-at-a-glance-card"><h4>Heat</h4><p>3</p></div>
  <div class="dc-at-a-glance-card"><h4>Augments</h4><p>2 / 4</p></div>
</div>

---

## Slate — Rules Contract / Authority Text

The dark, magenta-banded `.dc-slate` is for binding rulings and Dream Master directives — the lines that override table chatter. High contrast signals "this is the rule."

@block .dc-slate label="The Core Loop"

Every moment in Dimm City runs on a three-beat rhythm:

1. The **Dream Master** presents a situation.
2. The **Dreamers** declare intent.
3. The **fiction resolves** — sometimes on a die, sometimes on a word.

When intent meets resistance, roll a d20 and read the Outcome Ladder. The fiction always moves; the only question is *who pays*.

@end-block

@block .dc-slate label="Spec Tweak: Mistrunner"

You move through the city like fog through a gap in the wall.

Once per scene, you may cross through one barrier — a locked door, a guarded threshold, a checkpoint — without triggering an obstacle roll. The city lets you through. It doesn't know why, and neither do you.

@end-block

---

## Shard — Lore / Atmosphere Fragment

The aged-paper, rust-banded `.dc-shard` holds fiction, world detail, and the asides that make Dimm City feel lived-in. Zine-cut geometry; in-world voice.

@block .dc-shard label="The Neon Bazaar"

Hologram haze cuts the gloom you're stumbling through. Flickering ads claw the air above blades of neon, and the scent of burnt oil rides over hot garbage.

The Bazaar doesn't close. Day-shift workers and third-shift scavengers brush shoulders between stalls hawking augment cartridges, black-market permits, and fried synthetic crab. Somewhere a C-grade influencer is raising hell; somewhere else a fixer is selling the same secret twice.

@end-block

@block .dc-shard label="Streets Don't Care"

> "Streets don't care how clever you are. Dey only care what you live through."
>
> — Lil Thump, rabbit out of the EntD

The city scans you before you speak — name, scars, size, and stance read in a heartbeat. Rule one is staying frosty. Rule zero is having enough augs, or enough crew, to keep breathing.

@end-block

---

## Codex — Quick-Reference Glossary

The pale-cyan `.dc-codex` is the clean data register: glossary terms, table lookups, and compendium entries a player or DM flips to mid-session.

@block .dc-codex label="Dreamer's Glossary"

- **Tick / Tic** — A heartbeat of time. A reaction window. Used in abilities to mean *immediately*.
- **Shortly / Shorty** — Roughly a scene. Long enough to cross a district, tend a wound, or shake a tail.
- **Reach** — Close enough to touch. Adjacent. Extend a limb and make contact.
- **AP** — Augment Points. Fuel for your heaviest moves. Spend it and it's gone until you rest.
- **The Dream** — The shared fiction. A session is one dream; the city is the place you dream inside.
- **Master** — A major threat or boss. Take one down and your whole pack earns bonus AP.

@end-block

@block .dc-codex label="Outcome Ladder (d20)"

| Roll | Result | What happens |
|---|---|---|
| **20** | Triumph | Best case, with extra impact |
| **11–19** | Success | You do the thing |
| **6–10** | Hard Choice | You succeed, but it costs you |
| **2–5** | Failure | You don't get what you wanted |
| **1** | Catastrophe | It goes bad — and then worse |

@end-block

---

# 04. Sidebars & Panels

Floated reference panels, definition callouts, sidebar boxes, and NPC sidebars — the compact prose-furniture that lives alongside body text without interrupting it. The `@sidebar` float in particular only reads correctly with running prose beside it, so each specimen below is shown in a realistic host context.

---

## Sidebar — GM Aside (floated reference)

A floated reference panel that runs alongside body prose. The host paragraphs wrap around it, so it never reads as a box stranded in white space.

When the Dreamers push past **Too Far** and try to reach a mark on the other side of the district, the table starts asking how movement actually works — and that is exactly when a floated aside earns its place on the page.

@sidebar

### Distance, Fast

Three bands, no grid, no tape measure. **In Reach** is one swing away — close enough to smell blood pumping under skin. **Nearby** is a burned Move across a few meters of busted pavement. **Too Far** might as well be the other side of the ether: spend your Move *and* your Action just to scrape into range, and expect a smart mark to bolt again before you arrive.

@end-sidebar

Keep the bands fictional, not metric. If a player asks "how many feet," answer with the city instead: a thrown bottle, a sprint across a rooftop, a comms call you can't close in time. The Dream Master sets the band; the dice decide whether you close it. A Dreamer who wants to cross two bands in one turn is telling you they're willing to spend everything to get there — let them, and let it cost.

---

@page .page-sidebar

## Sidebar — Inset Variant

The `.inset` modifier turns the panel into a full-height rail pinned to the page's right edge. It needs the `@page .page-sidebar` template, which reserves the column the rail stands in — this page is that template, and the body text you are reading stops at the rail's edge because of it.

Initiative in Dimm City is fast and loose: roll Lucidity, act in order, and remember that out-of-turn abilities still cost AP even when the first use each round is free.

@sidebar .inset

### Free, Not Costless

One out-of-turn ability per round is *free to trigger* — but it still spends its listed AP. Each additional out-of-turn use that round costs **+1 AP** on top. They don't replace your Move or Action.

@end-sidebar

That distinction trips up new tables constantly, so it belongs in the margin right where the rule first bites — not buried three pages later in a reference appendix.

@page

---

## Definition Blocks — Glossary Terms (multi-instance)

Short italic callouts with a warm-cream fill and red left border — used for in-world vocabulary, NPC-type summaries, and item-category definitions. Stacked in a two-column section so the terms read as a connected glossary rather than three boxes floating apart.

@section .gp-columns-2 .dc-column-panel

@definition

**Tick / Tic:** A heartbeat. A breath. The space between deciding and doing. Not a formal unit — used in ability text to mean *immediate*, before anyone can react.

@end-definition

@definition

**Longtick:** A minute or so. Long enough for shrouded wildlife or environmental sensors to register an intruder and warn you before they arrive.

@end-definition

@definition

**Quickwhile:** Five to ten minutes of focused, hands-on work. Time enough to scavenge a district block, jam a node into place, or patch a wound between fights.

@end-definition

@definition

**Shortly / Shorty:** Roughly a scene. Long enough to cross a district, tend a wound, or shake a tail you didn't know you'd picked up.

@end-definition

@column-break

@definition

**Fixer:** The person who slides into the booth with a dirty envelope and a job you'll regret. Brokers work, gear, and silence — for a fee, a favor, or a piece of you.

@end-definition

@definition

**Sporo:** A native of Dimm City wearing an animal form. Cats run the Market arcades as guides, dealers, and — when the deal sours — predators.

@end-definition

@end-section

---

## Glossary / Term List

A run of **term** — gloss paragraphs wrapped by `@glossary … @end-glossary` renders as one connected reference register → `.dc-terms`. Unlike the floated `@definition` callouts above, this is the form an appendix glossary or a specialty's keyword box uses.

@glossary

**Augmerc** — A specialist who fuses cybernetic augmentation with close-range combat training — the body itself is the weapon platform.

**Hard Choice** — A roll of 6–10. The fiction advances, but it costs you — position, gear, Heat, or a piece of the plan.

**Signature Augment** — The defining graft an Augmerc takes free at character creation. A character may hold only one at a time.

**Heat** — The running tally of attention you've drawn. Let it climb and the city stops ignoring you.

@end-glossary

---

## Sidebar Box — Standalone Reference

An H4-headed callout with an internal dashed divider and cream background — for rules etiquette and standalone reference blocks that need their own visual boundary. The heading sits above the rule; the body sits below it.

@sidebar-box

#### Dice Etiquette

---

Roll your dice in the open. Both players should see every result clearly — hidden dice undermine the shared fiction. If a die lands off the table, it doesn't count: reroll it. Yeah, it stings to roll a "1." It stings worse to cheat the Dream. Call your intent before you roll, then live with what the dice say.

@end-sidebar-box

@sidebar-box

#### Pressure & Breathing Room

---

When the scene tightens — alarms tripped, a pack closing, the wirephreak still jamming the last node — the table is under **Pressure**: outcomes bite harder and Hard Choices cost more. When the heat drops and there's a beat to patch wounds or split loot, that's **Breathing Room**. Name which one you're in out loud; it tells the Dreamers how much rope they have.

@end-sidebar-box

---

## NPC Sidebar — Human Callout (floated)

A compact NPC capsule inside a floated `.dc-sidebar`, with the named contact's hook in a single tight block. Shown beside host prose so it floats against running text the way it will on a real encounter page.

The Dreamers are low on credits and lower on luck when the noodle-stall door swings open. Burnt oil clings to everything. A figure slides into the booth across from them, drops a battered data chip on the table, and waits — and whether this job is salvation or a setup depends entirely on who's offering it.

<div class="dc-sidebar"><div class="dc-human-callout">
<p><strong>Vance "Static" Oyelaran</strong> — Fixer</p>
<p>Two cybernetic eyes, owes everyone, and always knows where the bodies are charging. Deals straight only when straight is cheaper than the alternative. <strong>Hook:</strong> the chip is real; the access tunnel on it is bait.</p>
</div></div>

Read the room before you read the chip. A fixer who makes it back out the door clean is a fixer who knew the drone was coming — and a fixer who eats the drone on the threshold was never the one who set the trap. Either way, the job's already in motion the moment Static sat down.

---

## NPC Sidebar — Social Stat Capsule (floated)

The same `.dc-human-callout` float carrying a contact's social stats inline (REP / HEAT / FEE / TURN) for quick reference during play, beside the prose that introduces them.

Patch jobs between scenes are how a crew stays in the fight, and everyone south of the rail line knows exactly one name worth calling when the trauma kit runs dry. She doesn't ask what you did. She asks whether your credits are clean.

<div class="dc-sidebar"><div class="dc-human-callout">
<p><strong>Doc Solenn</strong> — Contact · Ripperdoc</p>
<p>REP 4 · HEAT 2 · FEE ×1.5 · TURN −1</p>
<p><strong>Patch Job:</strong> treats wounds between scenes for FEE × severity. Won't install hot chrome, won't ask why you're bleeding.</p>
</div></div>

Her fee scales with how badly you're hurt and how badly you need it kept quiet — a clean graze is cheap, a gut wound with a corp tail on you is not. Burn her trust once and the next TURN she's not in when you knock.

---

# 05. Tables

Standard markdown pipe tables receive DC styling automatically — colored header row, alternating row fills, and the small data-register type scale. No wrapper or class is required. Roll tables and option tables also use plain GFM pipe tables: the `@roll-table` and `@options-table` macros are deprecated (removed in plugin 17.3.0), so author every lookup as a standard pipe table.

---

## Augment Slot Table

A cybernetics reference table — the canonical data-table use case. Each augment lists the body slot it occupies and the mechanical effect it grants.

| Augment           | Slot   | Cost (cr) | Effect                                        |
|-------------------|--------|-----------|-----------------------------------------------|
| Reflex Booster    | Legs   | 1,200     | +2 to initiative rolls                        |
| Subdermal Plating | Torso  | 1,800     | Reduce incoming bludgeoning damage by 1       |
| Optic Splice      | Head   | 900       | Ignore darkness penalties; see the UV spectrum |
| Neural Tap        | Head   | 2,400     | +1 die on Hack and Interface checks           |
| Pulse Gauntlets   | Arms   | 2,000     | Melee hits knock targets back to Near range   |
| Spinal Jack       | Torso  | 3,000     | Slot one extra ability into your loadout      |

---

## Weapon & Gear Table

Equipment loadout reference — weapons and field gear with range bands, damage, and tags. Useful as a quick shopping list during downtime.

| Item              | Range  | Damage | Tags                       |
|-------------------|--------|--------|----------------------------|
| Throwaway Blaster | Near   | 1      | Disposable, Loud           |
| Pulse Pistol      | Near   | 2      | Force, Reliable            |
| Monowire Whip     | Reach  | 2      | Concealed, Slashing        |
| Scrap Rifle       | Far    | 3      | Loud, Two-Handed           |
| Patchwork Armor   | —      | —      | Reduce shock damage by 1   |
| Biogrip Adhesive  | —      | —      | Single syringe, Consumable |

---

## Roll Table (Street Encounters)

A d20 roll table, authored as a plain GFM pipe table (not the deprecated `@roll-table` macro). Roll a die and read across to the encounter the city throws at you.

| Roll  | Encounter                                                              |
|-------|-----------------------------------------------------------------------|
| 1–4   | A patchhead swarm picks a fight over nothing — three of them, Berserk |
| 5–8   | A fixer slides into the booth with a dirty envelope and a bad job     |
| 9–12  | A H.O.U.N.D. SercDog patrol sweeps the block; lie low or run          |
| 13–16 | A data-runner offers a hot chip — half truth, half trap               |
| 17–19 | A back-alley cybersurgeon will trade work for a favor owed later      |
| 20    | You find a sealed crate the corps forgot to log. It's still warm.     |

---

## Options Table (Downtime Actions)

An options-table lookup, also authored as a plain pipe table. Pick one downtime action per cycle; the result column tells you what it costs and what you get.

| Option         | Cost            | Result                                              |
|----------------|-----------------|-----------------------------------------------------|
| Lay Low        | One cycle       | Clear all Heat; gain nothing else                   |
| Tend Wounds    | One scene       | Recover up to 4 Hit Points                          |
| Work the Wire  | 200 cr          | Roll a die — on 11+, learn one rumor that matters   |
| Calibrate Gear | One scene       | Re-slot one augment without a SysCheck              |
| Call a Favor   | Burn a contact  | An NPC ally shows up once, then the debt is gone    |

---

## NPC Stat Reference

A compact statline table for running a scene — Fodder, Operators, and Masters side by side so the DM can stat an encounter at a glance.

| NPC          | Tier     | HP | Damage | Notable Trait                          |
|--------------|----------|----|--------|----------------------------------------|
| Patchhead    | Fodder   | 2  | 1      | Bloodlust: +1 Damage vs wounded foes   |
| Tech Scav    | Fodder   | 4  | 2      | Carries a Pulse Pistol (force damage)  |
| Street Shaman| Operator | 4  | 2      | Phase Shifter: moves through walls      |
| Undertow     | Master   | 10 | 4      | Stranglehold: grapple on a hit          |
| Chromejaw    | Master   | 20 | 5      | Scrapcoat: resistant to bludgeon/slash  |

---

# 06. Specialty System

The richest component family in the book. Every specialty specimen below is wrapped in an `@specialty .<name>` parent container — the **Contextual Cascade**: the card silhouette, learning-path shell shape, sticker chain, and accent color all flow down from that wrapper. Authors never set a `variant=` attribute on a card. The first group themes as **Augmerc** (`@specialty .augmerc`); the closing two specimens re-theme as **Gutterdruid** (`@specialty .gutterdruid`) and a **Dualist / Generalist** pair so the family-specific clip-path shells can be compared side by side.

---

## Specialty Intro Panel — Augmerc

Title-banded opening panel for a specialty's first page → `.dc-specialty-intro`. The accent band and rule color are inherited from the `@specialty .augmerc` parent.

@specialty .augmerc

@specialty-intro

## Augmerc

An Augmerc is muscle for hire. Street thugs, corporate bodyguards, deniable enforcers — the difference is gear, grafts, and how much of them is still original. Some run with packs, some lone-wolf it. Either way, most don't get paid until the job is done.

This heavy fights with skill, weapons, and tuned augmentation. The best are trained-up, tooled-up, and rebuilt with chrome, grafts, and salvaged tech. How much meat, metal, or monster your Augmerc carries is up to you.

If you want to start quickly, choose these abilities: Punishing Counter, Rage Hit, Spit Flame, Bodycover, Rub Some Dirt on It!, and Apex Physiology.

### Spec Tweak: **Wired to Kill**

Augmerc techniques are partly natural. Their learning paths assume the presence of combat-grade augmentations installed in the body: reinforced bones, reflex accelerators, adrenal regulators, neural predictors, and battlefield processors. These implants are rugged, brutal, and often salvaged from military or industrial hardware.

Each Augmerc learning path lists a Signature Augment — a common piece of cyberware that enables the techniques within that path. Without the implants, the Augmerc spends 1 extra AP to activate the path's abilities. They are simply part of what makes an Augmerc dangerous.

@end-specialty-intro

@end-specialty

---

## Specialty Art Panel — Augmerc

Full-bleed art panel for a specialty opener → `.dc-specialty-art`. Placeholder image shown; in the book this is full character art bleeding to the page edge.

@specialty .augmerc

@specialty-art

![Augmerc](https://placehold.co/640x360/1a1d2b/e8503a/png?text=Augmerc)

@end-specialty-art

@end-specialty

---

## Specialty Overview Card — Augmerc

Individual specialty entry card with portrait + accent band → `.dc-specialty-card`, laid out inside a `@section .dc-card-grid` multi-column grid. This is the chapter-01 "choose your specialty" pattern. Two cards are shown so the two-column grid lays out at full card width rather than collapsing a lone card into a narrow column.

@section .dc-card-grid

@specialty .augmerc

@specialty-card #specimen-card-augmerc

### Augmerc

![Augmerc](https://placehold.co/300x340/1a1d2b/e8503a/png?text=Augmerc)

> Cybernetic Commando

Heavily armed and wired for war, Augmercs are the blunt force of any squad. They charge the front, soak the pain, and unload hell using brute strength and brutal tech.

@end-specialty-card

@end-specialty

@specialty .gutterdruid

@specialty-card #specimen-card-gutterdruid

### Gutterdruid

![Gutterdruid](https://placehold.co/300x340/1a1d2b/4a9d6e/png?text=Gutterdruid)

> Feral Shapeshifter

Gutterdruids rewrite their own flesh to match the wasteland around them. They mutate, adapt, and out-survive anything the city throws at the pack.

@end-specialty-card

@end-specialty

@end-section

---

## Learning Path — Biting Distance (Augmerc)

A named spray-banner path with an auto-generated sticker chain and flavor line → `.dc-path-shell` + `.dc-learning-path`. The path index and tier codes (`AUG1.1`, `AUG1.2`, …) are auto-computed from position; the sticker chain is generated from the bullet list, with the first sticker marked `.active`. The shell silhouette is the **augmerc** clip-path, assigned by the parent container.

@specialty .augmerc

@learning-path

### Biting Distance

> If you can touch it, you can maul it. When things get close, they bleed.

- Punishing Counter
- Rage Hit
- Dirty Work
- Pain Compliance
- It's Personal

**Backbiter Spines:** Anyone who walks the Biting Distance path installs reactive spine rigs in the forearms, shins, or wherever their street doc could wedge the hardware. When creatures crowd into reach, you can trigger the system to bloom outward — blades, spikes, studs, or writhing polyalloy pseudopods. Spend an action defending and the rig braces and answers every swing, letting you resist 2 damage from all melee attacks and dealing 1 damage to all creatures in reach at the start of your turn.

@skill

#### Punishing Counter

> See an opening, ya take it. Best time to hit 'em is when they think it's over.

When an enemy falters, you may trigger one of the following counters:

1. **0 AP** *Steel Says No:* When an enemy in reach makes a basic attack and rolls a hard choice or worse, your Backbiters knock the strike off line. No damage. On a Failure or worse, drive steel into their liver — **ROLL THE DIE!** and make a basic attack. Free counter once per round.
2. **2 AP** *Bullet to Blood:* When an enemy you can see makes a ranged basic attack and rolls a hard choice or worse, you slip the shot as it screams past. No damage. On a failure or worse, surge forward through the smoke, close to reach if a clear path exists, and **ROLL THE DIE!** to make a basic attack. Free counter once per round.

##### Openings are invitations to take a chunk outta 'em.

@skill

#### Rage Hit

> In some situations, it's best to risk it, swing wild, an hit hard!

1. **0 AP** *Full Send:* You throw everything into a reckless attack. Make it your signature. Describe the chaos and **ROLL THE DIE!**
2. **2 AP** *All Gas, No Brakes:* Make two basic attacks against one target. If either roll is a 1, both attacks catastrophically fail as your movement snags on gear, armor, or the environment at the worst possible moment. DM's call on how bad it gets.

##### Full send or full regret.

@end-skill

@end-learning-path

@end-specialty

---

## Skill Card — Standard (Augmerc, with AP chip variants)

A single `@skill` card carries an H4 title, a `>` flavor line (auto-styled `.dc-flavor`), and an ordered ability list. The leading `**N AP**` on each list item is rendered as a `.dc-ap` chip. This specimen exercises the inline AP chip variants directly: **free** (crimson), **standard** (HUD green), **variable** (magenta), **reduced**, **increased**, and **special**.

@specialty .augmerc

@skill

#### Dirty Work | AUG1.3

> Fair fights are for nice mercs who lose. Never fight clean. Fight to finish.

Once per round, outside your turn, you exploit a target in reach. Choose one technique. The cost chip tells you what kind of action you're spending:

1. <span class="dc-ap free">0 AP</span> *Off-Hand Insurance:* Slip in a hidden strike. Make an attack that deals 1 damage.
2. <span class="dc-ap standard">1 AP</span> *Street Tricks:* Snag their balance with a sweep or throw something grody at 'em. Gain Lucidity on your next roll against the target and deal +1 damage on hit.
3. <span class="dc-ap var">VAR</span> *Break the Read:* Fake 'em out. **ROLL THE DIE!** If you hit, the target is Dazed until the end of their next turn — extend the daze for 1 AP per additional round.
4. <span class="dc-ap reduced">−1 AP</span> *Crew Assist:* When a pack-mate already has the target in a hold, this technique costs 1 less AP (minimum 0).
5. <span class="dc-ap increased">+2 AP</span> *Against a Master:* Cheap Shot on a Master costs 2 extra AP — they see it coming.
6. <span class="dc-ap special">FREE COUNTER</span> *Hook and Control:* Stick to them like glue. The target's next roll against you is Surreal, and your next roll against them is Lucid.

##### You don't need an opening. You make one.

@end-skill

@end-specialty

---

## Skill Card — Highlight Variant (Augmerc)

The **highlight** variant flags a featured / signature ability → `.dc-skill-card.dc-highlight` (crimson tab halo) + `.dc-card-body.dc-highlight-body` (warm crimson wash). Authored via the `| highlight` tier flag together with a `{.dc-highlight}` card class so both the tab-halo rule and the body-wash rule fire.

@specialty .augmerc

@skill {.dc-highlight}

#### Apex Physiology | AUG4.1 | highlight

> Brutality is your default setting!

Killwire fibers coil beneath the skin while bio-tuned bones brace for the impact, primed to snap harder and faster than natural muscle ever could.

1. **0 AP** *Built for Violence:* Your basic unarmed attacks — punches, kicks, knees, elbows, headbutts, tail-whips, whatever you're built with — deal 2 HP instead of 1.
2. **0 AP** *Hammerfist Synergy:* Combining this with cybernetic or biomod enhancements does not increase damage. Instead, your Triumph range expands to 19–20.

##### Violence begins in the bones.

@end-skill

@end-specialty

---

## Skill Card — Two-Column Body Layout (Augmerc)

The **two-col** variant packs a long ability list into two columns → `.dc-skill-card.dc-two-col`. Authored via the `{.dc-two-col}` card class. Use it for catalog-style abilities with many short rows, like the Lead from the Front warcant set.

@specialty .augmerc

@skill {.dc-two-col}

#### Boost Morale | AUG3.4

> When we get outta dis, Imma take whoever has the most kills to the EntD!

When an ally in range and able to hear you **ROLLS THE DIE!**, you bark encouragement, threats, promises, or pure nonsense that hits just right. This doesn't count as an action on your turn, but you can only use it once per round.

1. **2 AP** *Push the Fail:* When an ally rolls a Failure (2–5), cuss 'em into a Hard Choice.
2. **1 AP** *Salvage the Choice:* When an ally rolls a Hard Choice (6–10), push it to a Success. You must do this before the DM details the hard choice.
3. **3 AP** *Make It Legend:* When an ally rolls a Success (11–19)… nah. **IT'S A TRIUMPH! (20)**
4. **4 AP** *Drag It Up:* When an ally rolls a Catastrophe (1), drag it up to a Hard Choice.

##### Courage spreads. So does panic. Make your choice!

@end-skill

@end-specialty

---

## Skill Card — Continuation (Augmerc)

When an ability is too long for one card, `@continue` closes the current card and opens a continuation card with a `▸` suffix on the tab title → `.dc-skill-card.dc-skill-card-cont`.

There is no separate "continued" / "continued on next card" marker element. `.dc-card-cont-marker` and `.dc-card-fwd-marker` were injected at render time by `plugins/dimm-city-runtime.js`, which nothing ever loaded — Gutterpress's plugin contract has no script-injection hook. Both the script and their CSS were removed 2026-07-25. The `▸` on the continuation tab is the only continuation affordance.

@specialty .augmerc

@skill {.dc-allow-split}

#### Pain Compliance | AUG1.4

> Enough pain'll make a punk outta anyone!

1. **1 AP** *Take Control:* You overpower one target in reach (fodder or operators only; no masters) and place them in a painful hold. A controlled target must remain in reach, is immobilized in your augs, cannot react out of turn, rolls Surreal, and attacks made by others against it roll Lucid and deal double damage.

When you Take Control, you may also **ROLL A DIE!** and apply one of the following, and may deal up to 2 damage: *Shift* (knock them prone or haul them upright), *Toss* (throw them prone into a nearby area, releasing them), or *Drag* (move them with you to another space in reach).

@continue

2. **4 AP** *Applied Leverage:* All the effects of Take Control plus dirty tricks as your Backbiters sink in deeper, locking joints and digging into muscle like a living vice. Each round you spend an action to sustain control, choose *Break Them* (disable one limb until the target gets medical attention) or *Strip Them* (both **ROLL A DIE!** Surreal; on a Success, pry one non-implanted item free).
3. **3 AP** *Lights Out:* All effects of Take Control, plus lethal escalation. The target goes unconscious at the end of your turn, helpless as the implants press tight against the neck or spine. If you spend your next action to maintain control on the same unconscious target, they die at the end of your turn. No roll.

##### Predators don't negotiate.

@end-skill

@end-specialty

---

## Learning Path & Skill — Gutterdruid (re-themed cascade)

The same `@learning-path` and `@skill` markers, dropped into `@specialty .gutterdruid`, inherit the **gutterdruid** shell silhouette (soft angular, shallow-corner banner) and the gutterdruid accent — no syntax change. This demonstrates the Contextual Cascade by contrast with the augmerc specimens above.

@specialty .gutterdruid

@learning-path

### Beastmode

> Some adapt and overcome. You mutate and dominate.

- Feralmorph
- Environmental Assimilation
- Adaptive Mutation
- Flesh Perfected
- Horizon Stalker

@skill {.dc-allow-split}

#### Feralmorph

> You drop into a shape that hides in cracks or hunts the street.

1. **2 AP** *Take the Shape:* Your body rewrites into a natural form — flesh, bone, and instinct taking over. Choose any natural creature no smaller than a mouse and no larger than a horse, including humanoids. You become a generic expression of that species, not a specific individual. Everything you carry folds into the form.

While in **animal form** this form has 6 HP; tiny/small forms deal 1 damage, medium/big forms deal 2. You gain the creature's movement, senses, and natural behaviors but cannot use abilities, items, or language. You may return to your normal form at any time, restoring your original HP.

##### Some problems require hands and feet. Others need teeth, paws, and claws.

@skill

#### Environmental Assimilation

> The environment stops being survivable. You stop being ordinary.

1. **1 AP** *Adapt:* Your body makes small, immediate changes to keep you functional. Choose one: Air (smoke, gas, low oxygen), Temperature (industrial heat, deep freeze), Corrosion (acid, chemicals), Difficult Terrain (sludge, mud, debris), or Particulates (ash, sand, snow). For the scene, you ignore ordinary harm and penalties from that hazard.
2. **2 AP** *Restructure:* Your form fully restructures into something that belongs where normal bodies fail. Choose one: Vacuum, Radiation, or Extreme Pressure.

##### Decay is just another cycle of life.

@end-skill

@end-learning-path

@end-specialty

---

## Learning Path Shells — Dualist vs Generalist Silhouettes

The path-shell and card clip-path are read from the parent `@specialty .<name>`. The **dualist** and **generalist** families have their own silhouettes distinct from the eight core specialties. Each specimen ships a full five-entry path plus a contained `@skill` card so both the path-shell banner and the card clip-path silhouette render and can be compared directly.

@specialty .dualist

@learning-path

### Split Discipline

> Two crafts, one body. You never fully belong to either — and that's the edge.

- Crossover Stance
- Borrowed Reflex
- Hybrid Tempo
- Seam Walker
- Whole Cloth

**Split Rig:** A dualist runs two partial loadouts wired to a shared controller, so neither craft ever fully powers down. While you hold gear or an implant tied to each of your two disciplines, you may keep one technique from each "primed" between scenes. Switching which technique is primed costs no action the first time each round.

@skill

#### Crossover Stance

> The moment they read you as one thing, you become the other.

1. **1 AP** *Read the Frame:* Declare which of your two disciplines an enemy in reach expects you to use this round. Until your next turn, the first technique you spend from the *other* discipline rolls Lucid against that enemy.
2. **2 AP** *Seam Strike:* Make a basic attack that draws on both disciplines at once. On a hit, deal 1 damage and choose one rider from either discipline you have access to; the target cannot react out of turn until the end of their next turn.

##### Belonging to neither means owning the gap between them.

@end-skill

@end-learning-path

@end-specialty

@specialty .generalist

@learning-path

### Jack of the Sprawl

> Master of none, ready for anything. When the specialist's tool breaks, you're the one still standing.

- Field Improvisation
- Adaptive Loadout
- Good Enough
- Patch and Carry
- Last One Standing

**Salvage Kit:** A generalist carries the unglamorous gear nobody else bothers with — spare cells, tape, a cracked multitool, half a med-kit. Once per scene you may declare you "happen to have" one ordinary, non-augment item the situation plausibly calls for, no roll required. The DM sets a fair limit on anything exotic.

@skill

#### Field Improvisation

> No right tool? Fine. Every wrong tool works if you swing it hard enough.

1. **1 AP** *Make It Work:* Attempt a task that normally requires gear or training you don't have. **ROLL THE DIE!** On a Success you pull it off; on a Hard Choice it works but costs you the makeshift tool or a turn of cleanup.
2. **2 AP** *Good Enough for Now:* Apply a temporary patch to a broken device, wound, or structure. It functions until the end of the scene or until it takes another hit, whichever comes first.
3. **0 AP** *Borrowed Confidence:* When an ally in reach attempts something outside their specialty, lend a hand and let them roll Lucid on that one attempt. Once per round.

##### The specialist quits when the manual ends. You're just getting started.

@end-skill

@end-learning-path

@end-specialty

---

## Classtag Identity Dots — all specialties

Inline class-identity pill with a specialty-colored dot → `.dc-classtag.<name>`. One per specialty family, shown together so the ten accent colors can be checked at a glance.

<span class="dc-classtag augmerc">Augmerc</span>
<span class="dc-classtag proxy">Proxy</span>
<span class="dc-classtag streetwarden">Streetwarden</span>
<span class="dc-classtag gutterdruid">Gutterdruid</span>
<span class="dc-classtag cybersurgeon">Cybersurgeon</span>
<span class="dc-classtag wirephreak">Wirephreak</span>
<span class="dc-classtag technosorcerer">Technosorcerer</span>
<span class="dc-classtag etherlock">Etherlock</span>
<span class="dc-classtag dualist">Dualist</span>
<span class="dc-classtag generalist">Generalist</span>

---

# 07. Gear, Stat Blocks & NPCs

@lede

Equipment entries, creature and contact stat blocks, and the flaws / ideals / dreams card grid — the chrome that fills the Dream Master's reference pages. Each specimen below renders live so you can verify the dashed-rule separators, the four-cell stat grids, and the per-section card accents.

@end-lede

---

## Gear Entries

The `@gear` macro renders an item as a crimson display heading, an italic mechanical tagline (range / damage / tags), and the prose that follows. Entries are separated by `---`, which becomes a red dashed rule. Stack several so the gear-chapter rhythm is visible.

@gear

### Throwaway Blaster

*Ranged. Pistol. CQC Locked, Pack Fed.*

When you have a dirty job to do and want the result to be anonymous, throwaway blasters are the standard choice for contract killers and street soldiers alike. **Range** Reach to Near only — you have to be up close and personal — but the frame is small and easily concealed by even the crudest sleight of hand. **Damage** 2 on a Hit, 4 on a Triumph. Disposable after the run; serial-clean and untraceable.

@end-gear

---

@gear

### Gutter Snap Grenade

*Thrown. Burst. Force, Piercing.*

A wrist-loaded breaching charge that vents a cone of shaped concussion. **Range** Nearby burst. **Damage** 4 to everything caught in the blast; barriers and unpowered cover shred on a hit of 10+. **BONUS BOOM:** creatures in Reach of the detonation take 1 extra damage from pure concussive fury. One-use — the casing crumples after firing.

@end-gear

---

@gear

### Snake Cable

*Utility. Mechanized. Reach 50 ft.*

A 50-foot length of mechanized links that coils itself, climbs and anchors to higher or lower ground, projects across a horizontal gap to form a tightrope, or cinches around an inanimate (or animate) object. **Range** anywhere within its length. The cable locks rigid in a variety of shapes and is controlled by linked remote, onboard cybernetics, or any paired external device. Not a weapon — but it has ended fights.

@end-gear

---

## NPC & Creature Stat Blocks

Both block types share the `.dc-stat` shell and the four-cell `.dc-stat-grid`. **Creature blocks** use the numeric combat variant — HP / DEF / AP / DMG — for things you fight. **Contact blocks** use the social variant — REP / HEAT / FEE / TURN — for fixers, dealers, and patrons you negotiate with. Both close with a `.dc-stat-line` trait. `.dc-flush` drops the side margins so the block runs full-column.

<div class="dc-stat dc-flush">
  <div class="dc-stat-head">
    <div class="dc-stat-name">Wirewolf, Pack-Beta</div>
    <div class="dc-stat-class">— Threat · Apex Hunter —</div>
  </div>
  <div class="dc-stat-grid">
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">HP</div>
      <div class="dc-stat-cell-val">22</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">DEF</div>
      <div class="dc-stat-cell-val">14</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">AP</div>
      <div class="dc-stat-cell-val">3</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">DMG</div>
      <div class="dc-stat-cell-val">d20</div>
    </div>
  </div>
  <div class="dc-stat-line">
    <strong>Pack Tactic:</strong> While two or more wirewolves are in Reach of the same target, every wolf in the pack attacks with advantage. Drop the pack below two and they break and circle.
  </div>
</div>

---

<div class="dc-stat dc-flush">
  <div class="dc-stat-head">
    <div class="dc-stat-name">Doc Solenn</div>
    <div class="dc-stat-class">— Contact · Back-Alley Cybersurgeon —</div>
  </div>
  <div class="dc-stat-grid">
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">REP</div>
      <div class="dc-stat-cell-val">4</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">HEAT</div>
      <div class="dc-stat-cell-val">2</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">FEE</div>
      <div class="dc-stat-cell-val">×1.5</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">TURN</div>
      <div class="dc-stat-cell-val">−1</div>
    </div>
  </div>
  <div class="dc-stat-line">
    <strong>Patch Job:</strong> Solenn treats wounds and installs grey-market grafts between scenes. Cost is FEE × severity, and every visit raises your HEAT with whoever is hunting her this week.
  </div>
</div>

---

## Card Entries — Flaws, Ideals & Dreams

The `@card` macro inside a `@section .dc-flaws`, `.dc-ideals`, or `.dc-dreams` wrapper renders a character-creation card. Each section's accent color signals its register: flaws bite, ideals anchor, dreams drive. The H3 names the trait, prose explains it, and the closing blockquote is the line the character lives by.

@section .dc-flaws

@card

### Addictive Personality

You have a tendency to become addicted to substances or activities, often chasing instant gratification without weighing the consequences. The city always has one more hit on offer, and it knows your name.

> "Just one more, and then I'll quit."

@end-card

@card

### Cold-Hearted

You lack empathy and reliably put your own goals ahead of anyone else's well-being. When the crew hesitates over a hard call, you don't — and that scares them as much as it saves them.

> "I don't care about their suffering. It's survival of the fittest."

@end-card

@end-section

@section .dc-ideals

@card

### Information Freedom

You value the free flow of information and stand for digital privacy, strong encryption, and the right to unrestricted knowledge. A locked archive is, to you, an admission of guilt.

> "If knowledge is locked away, it's already being abused."

@end-card

@card

### Honor

You believe in a code, and upholding it is your duty no matter the cost. Promises are load-bearing — break one and the whole self comes down.

> "I made a promise to help those in need, and I'll keep it at all costs."

@end-card

@end-section

@section .dc-dreams

@card

### Hack Daemon & Expose the Truth

Daemon isn't just a leader — they're a cult burning through the city's operating system. Every feed, every riot, every "random" patrol routes back to them. You don't want to kill Daemon; you want to unmask them in front of every DimmCit who'll watch.

> "Crack the shell, drag the secrets out, and let the city see who's been steering it."

@end-card

@card

### Discover the Secrets of My Own Origins

Names rot fast. Records glitch. Homes vanish. You don't know if you were grown, printed, stitched, summoned, or stolen — and the gaps in your past itch when the lights flicker just right. Someone out there knows why you were made the way you are.

> "The truth might give me clarity, or prove I was never meant to be free."

@end-card

@end-section

---

# 08. Dividers & Reference

Section breaks, inline labels, and the two structural reference blocks — numbered procedures and the d20 outcome ladder. These components carry the rules-and-reference furniture of the book: the seams between gear entries, the labels on a specialty, the step-by-step of character creation, and the single table every roll resolves against.

---

## Tape & Dashed Dividers

Two section-break treatments shown together. The torn-tape strip (`.dc-tape.dc-flush`) carries a real section label and spans edge to edge; the dashed rule (`.dc-dashed-rule`, applied to every `---`) separates entries inside a list. Below, three tape labels frame a short gear list whose entries are split by dashed rules.

<div class="dc-tape dc-flush">Operators</div>

The Augmerc walks point. Heavy chassis, heavier ordnance, and just enough flesh left to feel the recoil.

<div class="dc-tape dc-flush">Field Loadout</div>

Trauma Kit × 2

---

Signal Jammer (single-use)

---

Spare Power Cell, Ripper Blades (Mk II)

<div class="dc-tape dc-flush">Aftermath</div>

When the smoke clears, tally Heat, patch what's bleeding, and decide whether the contract was worth the scars.

---

## Class Tags

Inline identity pills, one per specialty family. Each `.dc-classtag.<name>` carries that specialty's accent dot, so a roster line reads at a glance. Shown here as a full eight-class roster the way a party sheet or specialty index lists them.

<span class="dc-classtag augmerc">Augmerc</span>
<span class="dc-classtag proxy">Proxy</span>
<span class="dc-classtag streetwarden">Streetwarden</span>
<span class="dc-classtag gutterdruid">Gutterdruid</span>
<span class="dc-classtag cybersurgeon">Cybersurgeon</span>
<span class="dc-classtag wirephreak">Wirephreak</span>
<span class="dc-classtag technosorcerer">Technosorcerer</span>
<span class="dc-classtag etherlock">Etherlock</span>

For inline cost and keyword labels that aren't class identities, use the plain pill (`.dc-tag`) instead:

<span class="dc-tag">Melee</span>
<span class="dc-tag">Reach 2</span>
<span class="dc-tag">Disposable</span>
<span class="dc-tag">Loud</span>

---

## Numbered Procedure

Zero-padded ordered list for any sequence the table runs in order (`.dc-steps`). Two real procedures stacked: the core play loop that every scene runs on, and the character-creation walkthrough.

@procedure

1. **The Dream Master describes the situation.** Where you are, what's wrong, and what the moment is asking of you.
2. **A Dreamer declares an action.** Say what your character does, plainly and out loud.
3. **If the outcome is uncertain, ROLL THE DIE.** Activate an ability or roll a d20 against the table below.
4. **The result determines what happens next.** Triumph, success, a hard choice, failure, or catastrophe.
5. **The scene evolves and the Dream continues.** The Monoverse answers, and you go again.

@end-procedure

@procedure

1. **Build a body and a vibe.** Picture your Citizen before you touch a number — the look, the scars, the reason you're still breathing.
2. **Pick a Spec.** Augmerc, Proxy, Streetwarden — one of eight specialty families.
3. **Spend 6 Spec Points.** Distribute them across the paths in your chosen specialty.
4. **Take a Signature Augment.** Free at character creation — the graft that makes you *you*.
5. **Set your Flaw, Ideal, and Dream.** One thing that breaks you, one you stand for, one you're chasing.

@end-procedure

---

## Outcome Ladder

The single d20 result table every roll resolves against (`.dc-outcomes`). Five rungs, color-coded by severity from Triumph down to Catastrophe — the canonical ladder used at every table in Dimm City.

@outcome

20 | Triumph | Best-case outcome. You do it, and the moment breaks your way — extra impact, leverage, or reach.
11–19 | Success | You do it. What you set out to accomplish happens, clean.
6–10 | Hard Choice | You succeed, but it costs you — position, gear, Heat, or a piece of the plan.
2–5 | Failure | You don't get what you wanted. The situation turns, and the spotlight shifts.
1 | Catastrophe | It goes bad, and then worse. Automatic fail with a setback that lingers.

@end-outcome

---

# 09. Page-Level Components

The page-scale layouts that frame whole spreads rather than sit inside body prose: the citizen-walkthrough that guides a reader through filling out a Citizen File, the fiction excerpt that opens a chapter with in-world narrative, and the NPC stat block in both its narrative (combat) and at-a-glance (social) forms. Each is authored as a `@section .<name>` chassis, so the specimens below render live exactly as they ship in the Field Guide.

---

## Citizen Walkthrough

A field-by-field guide for filling out the Citizen File → `@section .dc-citizen-walkthrough`. Each `####` heading names a Citizen File field and the prose beneath it walks the reader through the choice. The `.gp-columns-2 .dc-column-panel` modifier pair puts two short fields side by side in a column-panel card; without them the section runs full column. These are the real character-creation fields a Dreamer fills in before they touch a single number.

@section .dc-citizen-walkthrough .gp-columns-2 .dc-column-panel

#### What's Yr Handle?

Choose a name.

It can come from any culture, any language, or straight out of your imagination. Pull it from a book, a show, a half-remembered dream, or invent something that sounds right for the city.

#### Designation

Let others know how to refer to you.

She/her, he/him, they/them, or something else entirely. Names and pronouns matter when life itself is constantly trying to strip both away.

@end-section

@section .dc-citizen-walkthrough

#### Species

In Dimm City, you're not human — you never were. Every Dreamer is an anthropomorphic creature: a splice of animal instinct, street survival, and whatever the corps, gods, or bad luck bolted on afterward.

Choose a species that fits your vibe. Species carries no mechanical weight — it shapes your look, your voice, and how Dimm City reads you. The city has seen it all: cats and rabbits, rats and ravens, wolves and worse things with no clean name left.

@end-section

@section .dc-citizen-walkthrough

#### Origins

Where did you start, and how far is that from where you are now?

Origins tell the Dream Master how your character fits the city's grid. A corporate-born Dreamer walks the alleys differently than someone who grew up in the Flats. They know different people, owe different debts, and have different reasons to still be breathing.

Choose one: **EntD rat**, **Corp exile**, **District-born**, **Offworld arrival**, **Street-raised**, or **Something the city made and hasn't claimed yet**.

@end-section

---

## Fiction Excerpt

In-world narrative for a chapter opener or vignette → `@section .dc-fiction-excerpt`. Provides the wider narrative leading, break control, and automatic art positioning: the first image floats left and the prose wraps around it — authors place the image in the flow with no per-image class. A placeholder stands in for the full character art; the text is Lil Thump's opening tale exactly as it runs in the Field Guide.

@section .dc-fiction-excerpt

"It's hard being me, but I guess it's the same for anyting sentient in the monoverse, ay?! Tag's Thump, an I'm a rabbit outta dee EntD here in Dimm City. Lemme post ya a tale about life here in da middle 'o dee ether.

![Lil Thump](https://placehold.co/600x400/1a1d2b/e8503a/png?text=Lil+Thump)

I wuz tearin down an alley, lungs burnin, heart jackhammering like it wanted out. Da cauldron wuz right on mai heels now, wings chopping da air, close enough I could smell da oil an blood on 'em.

I turned hard an hit a dead end. Balcony. High rise. Peak chaos screaming thirty meters in da cut below. No exits.

I spun to face dem, back to da rail, fists up an shakin. Bats fanned out, claws flexing, chromed teeth catchin the light. Red eyes. Hungry eyes. I knew dat look — da look right before somethin eats you and vlurps your name outta existence.

Then I looked down. I laughed... an den jumped.

A BANANACOM™ ADdrone caught me in a hard dip, jolting mai spine, but I stayed alive. I slapped dee access panel, jacked in wit a hard line, an blasted a warning yelp at max pitch. Sound ripped through da air like a prison shank. Da bats froze mid-flight, shrieking an tumbling outta da sky.

@end-section

---

## NPC Stat Block — Narrative & At-a-Glance Variants

The two NPC stat-block forms shown together so the register split is visible at a glance. The **narrative variant** (`@section .dc-npc-stat`) carries a `####` name with a rust top-rule, a `>` flavor quote, the primary / secondary mono stat lines, and `#####` TRAITS / EQUIPMENT subsection anchors — the form a Dream Master reads aloud while running a combat NPC. The **at-a-glance variant** (raw HTML `.dc-stat` / `.dc-stat-grid`) packs a contact's social numbers into the four-cell grid — the form a Dreamer scans before negotiating. Both carry real Field Guide NPCs.

@section .dc-npc-stat

#### Patchhead

> See a Patchhead comin' at you, you best move. Ain't no reasoning with 'em — minds melted and muscles twitchin' like they're about to burst. You can smell the burnt plastic and sweat long before they get close.

2 HP — 1 Damage
Fodder — Usually Small to Medium

##### Traits

**Bloodlust:** Patchheads add 1 to their Damage value whenever they hit a creature that is currently missing Hit Points.

##### Equipment

Makeshift weapons — weighted chains, shivs, knuckle dusters — paired with junk shields or crash helmets for basic protection. May carry a Shadowbit token holding 50–100 Dream Creds of crypto and other sketchy paraphernalia.

##### Cybernetics

UniArm 100 / Redi-Mobile Cyberleg / RedEye Optical Prosthetic — could be just one, or all three.

@end-section

The same scene's social contact, statted in the at-a-glance grid: the same `.dc-stat-grid` shell as the creature block, switched to the social register (REP / HEAT / FEE / TURN) for the fixer you bargain with before the dice come out.

<div class="dc-stat dc-flush">
  <div class="dc-stat-head">
    <div class="dc-stat-name">Vance "Static" Oyelaran</div>
    <div class="dc-stat-class">— Contact · Fixer —</div>
  </div>
  <div class="dc-stat-grid">
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">REP</div>
      <div class="dc-stat-cell-val">5</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">HEAT</div>
      <div class="dc-stat-cell-val">3</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">FEE</div>
      <div class="dc-stat-cell-val">×2</div>
    </div>
    <div class="dc-stat-cell">
      <div class="dc-stat-cell-key">TURN</div>
      <div class="dc-stat-cell-val">0</div>
    </div>
  </div>
  <div class="dc-stat-line">
    <strong>Brokered Work:</strong> Static slides a job and a name across the table for FEE × the risk. Two cybernetic eyes, owes everyone, and always knows where the bodies are charging — the chip he hands you is real; the access tunnel on it is bait.
  </div>
</div>
