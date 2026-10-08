@chapter #ch-variants .dg-guide ch="11"

@page .dg-doc

Chapter 11 {.dg-kicker}

# Variant Gallery

Every element that ships more than one variant, with all of its variants on one stage so they can be compared directly. Each section names the switch that picks the variant; the chapter that documents the element has the full syntax and tokens. Specialty content is the Field Guide's own, excerpted to one ability per card (an ellipsis marks a cut). {.dg-lede}

## Skill trees — one per specialty

A learning path is a skill tree: the spray title, the subtitle, the skill stickers, and the skill cards. The `@specialty` wrapper sets every color and shape, so each tree below is the same markdown under a different class — and its skill card is that specialty's card. The Dualist and Generalist have no trees of their own: they take their skills from the other eight.

### Augmerc — `.augmerc`

<div class="dg-stage">

@specialty .augmerc

@learning-path

### Biting Distance

> If you can touch it, you can maul it. When things get close, they bleed.

- Punishing Counter
- Rage Hit
- Dirty Work

@skill

#### Punishing Counter

> See an opening, ya take it. Best time to hit 'em is when they think it's over.

1. **0 AP** *Steel Says No:* When an enemy in reach makes a basic attack and rolls a **Hard Choice** or worse, your Backbiters knock the strike off line. They miss. …

@end-skill

@end-learning-path

@end-specialty

</div>

### Proxy — `.proxy`

<div class="dg-stage">

@specialty .proxy

@learning-path

### Refuse Finality

> Nothing ends while you are still standing.

- Zeal Stitch
- Borrowed Mercy
- Redline Rhythm

@skill

#### Zeal Stitch

> Your zeal is not fury, but light refusing the shadows.

1. **0 AP** You grasp a willing creature in reach or clamp a hand over your own wound, pouring the light of your conviction into the injury as bioluminescent threads stitch flesh together. ROLL THE DIE!

@end-skill

@end-learning-path

@end-specialty

</div>

### Streetwarden — `.streetwarden`

<div class="dg-stage">

@specialty .streetwarden

@learning-path

### Streetwise

> The more you know the less you carry.

- Gut Sense
- Quick Fix
- Stealth Camp Shroud

@skill

#### Gut Sense

> The alley stinks wrong. The silence is too wide. Something's gonna drop.

1. **0 AP** When you enter a new location—building, block, train car, street—you may ask the Dream Master one question. … The DM gives you one true insight about the area.

@end-skill

@end-learning-path

@end-specialty

</div>

### Gutterdruid — `.gutterdruid`

<div class="dg-stage">

@specialty .gutterdruid

@learning-path

### Beastmode

> Some adapt and overcome.

- Feralmorph
- Environmental Assimilation
- Adaptive Mutation

@skill

#### Feralmorph

> You drop into a shape that hides in cracks or hunts the street.

1. **2 AP** Your body rewrites into a natural form, flesh, bone, and instinct taking over. …

@end-skill

@end-learning-path

@end-specialty

</div>

### Cybersurgeon — `.cybersurgeon`

<div class="dg-stage">

@specialty .cybersurgeon

@learning-path

### Trauma Economy

> Doctors are sworn to heal the sick but I require a 2000 cred downpayment to uphold my oath.

- Peep and Patch
- Medicated Calm
- Triage Rig

@skill

#### Peep and Patch

> Time is money and your injuries are wasting both!

1. **0 AP** You quickly examine a creature in reach of you and foam wounds shut, staple torn flesh, and flood the pain with emergency chems. Your efforts immediately restore 3 HP but do not remove impairments, heal permanent wounds, or cure diseases.

@end-skill

@end-learning-path

@end-specialty

</div>

### Wirephreak — `.wirephreak`

<div class="dg-stage">

@specialty .wirephreak

@learning-path

### Professional Courtesy

> Every contract should end clean.

- Dead or Alive
- Killer Instinct
- Hemorrhage

@skill

#### Dead or Alive

> Every alley talks. Every fixer owes somebody. Every bounty leaves a trail. You just know where to start looking.

1. **0 AP** You check darksites, contact fixers, browse bounty boards, and quietly ask around the city's underworld. After a byte or two, you know which bounties are worth chasing, who's offering them, and roughly how dangerous the marks are. …

@end-skill

@end-learning-path

@end-specialty

</div>

### Technosorcerer — `.technosorcerer`

<div class="dg-stage">

@specialty .technosorcerer

@learning-path

### Prestidigitalization

> Reality doesn't have to change. You just have to sell the alternative.

- Practical Power
- Digital Chameleon
- Override

@skill

#### Practical Power

> Surprise, amuse, or baffle those around you with a touch of digital magic.

1. **0 AP** You conjure harmless sensory or environmental effects by manipulating cybernetics, technology, or reality itself. Using an Action, you can maintain up to **6 ongoing effects** at once. …

@end-skill

@end-learning-path

@end-specialty

</div>

### Etherlock — `.etherlock`

<div class="dg-stage">

@specialty .etherlock

@learning-path

### Mutanthurgy

> Matter, momentum, gravity, flesh. None of them are laws. They're habits. Break them all.

- Rubber Soul
- Skyhook
- Stolen Momentum

@skill

#### Rubber Soul

> Everything bends. Everything bounces. You just gotta convince it.

1. **2 AP** As your Action, you radically increase the elasticity of yourself, one willing packmate, or one surface or object **In Range** until the end of the encounter. …

@end-skill

@end-learning-path

@end-specialty

</div>

## Skill card variants

Every switch on one card, each under the same Augmerc wrapper. `@continue`, which splits a long card across pages, is shown in [The Specialty System](#ch-specialty).

### Default — `@skill`

A card outside a learning path has no tier on its tab; inside one, the tier is computed from its position (the skill trees above).

<div class="dg-stage">

@specialty .augmerc

@skill

#### Dirty Work

> Fair fights are for nice mercs who lose.

1. **1 AP** *Street Tricks:* Snag their balance. Gain Lucidity on your next roll against the target.

@end-skill

@end-specialty

</div>

### Tier override — `#### Name | AUG1.3`

The tier is written on the heading and printed on the tab.

<div class="dg-stage">

@specialty .augmerc

@skill

#### Dirty Work | AUG1.3

> Fair fights are for nice mercs who lose.

1. **1 AP** *Street Tricks:* Snag their balance. Gain Lucidity on your next roll against the target.

@end-skill

@end-specialty

</div>

### Highlight on the heading — `#### Name | AUG4.1 | highlight`

The featured tab and body.

<div class="dg-stage">

@specialty .augmerc

@skill

#### Apex Physiology | AUG4.1 | highlight

> Brutality is your default setting!

1. **0 AP** *Built for Violence:* Your basic unarmed attacks deal 2 HP instead of 1.
2. **0 AP** *Hammerfist Synergy:* Your Triumph range expands to 19–20.

@end-skill

@end-specialty

</div>

### Highlight on the card — `@skill {.dc-highlight}`

The same register with the class on the card root.

<div class="dg-stage">

@specialty .augmerc

@skill {.dc-highlight}

#### Apex Physiology | AUG4.1

> Brutality is your default setting!

1. **0 AP** *Built for Violence:* Your basic unarmed attacks deal 2 HP instead of 1.
2. **0 AP** *Hammerfist Synergy:* Your Triumph range expands to 19–20.

@end-skill

@end-specialty

</div>

### Two columns — `@skill {.dc-two-col}`

A long ability list packed into two columns.

<div class="dg-stage">

@specialty .augmerc

@skill {.dc-two-col}

#### Boost Morale | AUG3.4

> When we get outta dis, Imma take whoever has the most kills to the EntD!

When an ally in range ROLLS THE DIE!, bark encouragement that hits just right. Once per round.

1. **2 AP** *Push the Fail:* A Failure becomes a Hard Choice.
2. **1 AP** *Salvage the Choice:* A Hard Choice becomes a Success.
3. **3 AP** *Make It Legend:* A Success becomes a Triumph.
4. **4 AP** *Drag It Up:* A Catastrophe becomes a Hard Choice.

@end-skill

@end-specialty

</div>

### Two columns for every card — `.dc-cards-two-col`

`@skill {.dc-two-col}` sets one card. To make every skill card under a wrapper two-column, put `.dc-cards-two-col` on any ancestor: the `@specialty` marker, a `@chapter`, a `@page`, a `@section`. Only running text flows in the columns, and a paragraph may break between them so the columns balance; a list item stays whole. The flavor line, ability rows, tables, outcome ladders, sub-heads and rules span the card. A card marked `{.dc-allow-split}` stays single-column. A card that also has its own `{.dc-two-col}` keeps that stricter per-card form (paragraphs whole) and ignores the ancestor's.

```markdown
@specialty .augmerc .dc-cards-two-col

@skill
#### Boost Morale | AUG3.4
…
```

### Outcome table — a `| Roll | Outcome |` table inside the card

The table becomes the card's outcome ladder.

<div class="dg-stage">

@specialty .augmerc

@skill

#### Spit Flame | AUG2.1

> Breathe deep. Let it out.

1. **1 AP** *Torch:* Vent a cone of ignited bio-fuel at everything in Reach. ROLL THE DIE!

| Roll | Outcome |
|---|---|
| 20 | Quadruple damage. |
| 11–19 | Double damage. |
| 6–10 | Double damage, but the target counters. |
| 2–5 | You miss. The target counters Lucid. |
| 1 | You fall prone and lose your next turn. |

@end-skill

@end-specialty

</div>

## AP chips

The plugin picks the chip from the cost written in bold at the start of an ability. The cards are the Augmerc's Dirty Work and the Proxy's Borrowed Mercy (its range line excerpted). The last four registers have no markdown form; they are raw spans.

<div class="dg-stage dg-on-paper">

@specialty .augmerc

@skill

#### Dirty Work | AUG1.3

> Fair fights are for nice mercs who lose.

Once per round, outside your turn, you exploit a target in reach:

1. **0 AP** *Off-Hand Insurance:* Slip in a hidden strike that deals 1 damage.
2. **1 AP** *Street Tricks:* Snag their balance. Gain Lucidity on your next roll against the target.
3. **VAR AP** *Break the Read:* ROLL THE DIE! On a hit the target is Dazed; extend it for 1 AP per round.

@end-skill

@end-specialty

@specialty .proxy

@skill

#### Borrowed Mercy

> For a moment, suffering looks elsewhere.

1. **2 AP** You invoke your devotion: whether to a deity, an ideal, or a personal creed. Project sustaining force into the fray. You and all nearby allies immediately heal 2 HP.
2. **3-X AP** You may commit more of yourself to the cause when invoking this ability. For each AP spent, increase the healing by +1 HP.

@end-skill

@end-specialty

<span class="dc-ap standard">2 AP</span> <span class="dc-ap reduced">1 AP</span> <span class="dc-ap increased">3 AP</span> <span class="dc-ap special">SPC</span>

</div>

| Chip, in order | You write | Class |
|---|---|---|
| Free | `**0 AP**` | `.dc-ap.free` |
| Standard | `**1 AP**`, `**2 AP**` | `.dc-ap` |
| Variable | `**VAR AP**` | `.dc-ap.variable` |
| Variable | `**3-X AP**`, any range or `X` | `.dc-ap.variable` |
| Standard, explicit | `<span class="dc-ap standard">` | `.dc-ap.standard` |
| Reduced | `<span class="dc-ap reduced">` | `.dc-ap.reduced` |
| Increased | `<span class="dc-ap increased">` | `.dc-ap.increased` |
| Special | `<span class="dc-ap special">` | `.dc-ap.special` |

## Specialty intros

`@specialty-intro` inside each `@specialty`: the same panel, ten title bands. Intro text is the opening of each Field Guide profile.

<div class="dg-stage">

@specialty .augmerc

@specialty-intro

## Augmerc

An Augmerc is muscle for hire. Street thugs, corporate bodyguards, deniable enforcers — the difference is gear, grafts, and how much of them is still original.

@end-specialty-intro

@end-specialty

</div>

<div class="dg-stage">

@specialty .proxy

@specialty-intro

## Proxy

Belief burns bright in Dimm City, and Proxies carry the sparks others cannot hold. A word that stops a heart, a prayer that drags a soul back to its feet.

@end-specialty-intro

@end-specialty

</div>

<div class="dg-stage">

@specialty .streetwarden

@specialty-intro

## Streetwarden

Dimm City may look like a concrete jungle, but its sentient population is far outnumbered by the insects, animals, fungi, protista, and monera that thrive throughout its shadowed sprawl. …

@end-specialty-intro

@end-specialty

</div>

<div class="dg-stage">

@specialty .gutterdruid

@specialty-intro

## Gutterdruid

Nature thrives in Dimm City, but it grows meaner here. It roots in drains, nests in vents, blooms on corpses, cracks through concrete, and feeds on carrion, heat, rust, blood, and whatever the city throws on the curb. …

@end-specialty-intro

@end-specialty

</div>

<div class="dg-stage">

@specialty .cybersurgeon

@specialty-intro

## Cybersurgeon

Need a new arm? Sit down. Need a neuroimplant wired so the Datasphere crawls behind your eyes? That's extra.

@end-specialty-intro

@end-specialty

</div>

<div class="dg-stage">

@specialty .wirephreak

@specialty-intro

## Wirephreak

The invisible professionals of Dimm City. Corporations, syndicates, governments, and private clients alike rely on Wirephreaks when information must be acquired, facilities infiltrated, witnesses eliminated, or valuable assets extracted without leaving a trace.

@end-specialty-intro

@end-specialty

</div>

<div class="dg-stage">

@specialty .technosorcerer

@specialty-intro

## Technosorcerer

Technosorcerers see the world as one enormous operating system. Magic, cybernetics, matter, even the laws of existence are simply different layers of the same source code waiting to be understood—and rewritten.

@end-specialty-intro

@end-specialty

</div>

<div class="dg-stage">

@specialty .etherlock

@specialty-intro

## Etherlock

Dimm City leaks magic. Raw ether and elements seep through fractures between substantialities, saturating matter and space, feeding the strange ecology of Dimm City itself.

@end-specialty-intro

@end-specialty

</div>

<div class="dg-stage">

@specialty .dualist

@specialty-intro

## Dualist

Dualists refuse to choose. They walk two specialty paths at once, drawing skills from both at the cost of mastery in either.

@end-specialty-intro

@end-specialty

</div>

<div class="dg-stage">

@specialty .generalist

@specialty-intro

## Generalist

Generalists don't specialize — they scavenge. Picking up scraps of every art the city offers, they're the operative no one expects.

@end-specialty-intro

@end-specialty

</div>

## Specialty cards

`@specialty-card` inside each `@specialty`, in a `@section .dc-card-grid`. Cards alternate `data-position="odd|even"` down the grid.

<div class="dg-stage dg-tall">

@section .dc-card-grid

@specialty .augmerc

@specialty-card

### Augmerc

![Augmerc](https://placehold.co/300x340/png?text=Augmerc)

> Cybernetic Commando

Heavily armed and wired for war, Augmercs are the blunt force of any squad. They charge the front, soak the pain, and unload hell using brute strength and brutal tech. Combat-born, augged to kill, and never outgunned.

@end-specialty-card

@end-specialty

@specialty .proxy

@specialty-card

### Proxy

![Proxy](https://placehold.co/300x340/png?text=Proxy)

> Militant Monolith

Marked by something higher—god, ghost, code, or conviction—Proxies walk the line between zealot and judge. They wield divine force like a weapon, bending battles and conversations alike with power that burns louder than faith.

@end-specialty-card

@end-specialty

@specialty .streetwarden

@specialty-card

### Streetwarden

![Streetwarden](https://placehold.co/300x340/png?text=Streetwarden)

> Sprawl Sentinel

They don't wear badges—they are the law when no one else shows. Streetwardens guard the city's broken places with fists, grit, and a code all their own. They know the alleys like arteries and protect the forgotten.

@end-specialty-card

@end-specialty

@specialty .gutterdruid

@specialty-card

### Gutterdruid

![Gutterdruid](https://placehold.co/300x340/png?text=Gutterdruid)

> Wold Witch

They walk the alleys like sacred ground—feeding the hungry, tending weeds, raising the forgotten. Gutterdruids draw power from the pulse beneath the pavement, shaping the raw, primal force that keeps the city alive even as it rots.

@end-specialty-card

@end-specialty

@specialty .cybersurgeon

@specialty-card

### Cybersurgeon

![Cybersurgeon](https://placehold.co/300x340/png?text=Cybersurgeon)

> Mech Medic

Life is flexible. Cybersurgeons prove it daily—cutting, splicing, upgrading flesh into something more. Whether they're back-alley butchers or elite biomech specialists, these med-techs push the edge of evolution, one implant at a time.

@end-specialty-card

@end-specialty

@specialty .wirephreak

@specialty-card

### Wirephreak

![Wirephreak](https://placehold.co/300x340/png?text=Wirephreak)

> Ping Predator

Killers, thieves, forgers—Wirephreaks specialize in slipping past locks, firewalls, and people. Some work clean, some loud, all lethal. Whether the job calls for stealth, sabotage, or sleight-of-hand, a Wirephreak on the crew means the job gets done.

@end-specialty-card

@end-specialty

@specialty .technosorcerer

@specialty-card

### Technosorcerer

![Technosorcerer](https://placehold.co/300x340/png?text=Technosorcerer)

> Modular Magician

Technosorcerers walk on the razor's edge between magic and technology. They believe one to be no different than the other and use the strengths of each to help nullify the other's weaknesses.

@end-specialty-card

@end-specialty

@specialty .etherlock

@specialty-card

### Etherlock

![Etherlock](https://placehold.co/300x340/png?text=Etherlock)

> Manifold Magus

Secrets are currency—and Etherlocks are rich in them. Tapping into elemental forces, spirit echoes, and the buried laws of the monoverse, they wield magic that slips through cracks in reality.

@end-specialty-card

@end-specialty

@specialty .dualist

@specialty-card

### Dualist

![Dualist](https://placehold.co/300x340/png?text=Dualist)

> Two-Path Walker

Dualists refuse to choose. They walk two specialty paths at once, drawing skills from both at the cost of mastery in either. Where others sharpen one edge, the Dualist carries two — equally at home picking locks and pulling triggers, casting circuits and reading rooms.

@end-specialty-card

@end-specialty

@specialty .generalist

@specialty-card

### Generalist

![Generalist](https://placehold.co/300x340/png?text=Generalist)

> Sprawl Survivor

Generalists don't specialize — they scavenge. Picking up scraps of every art the city offers, they're the operative no one expects: a passable hacker who can shoot, a mediocre fighter who can sneak, a half-druid who knows a guy. Master of none. Useful to everyone.

@end-specialty-card

@end-specialty

@end-section

</div>

## Class tags

`<span class="dc-classtag <specialty>">`, one per specialty.

<div class="dg-stage dg-on-paper">

<span class="dc-classtag augmerc">Augmerc</span> <span class="dc-classtag proxy">Proxy</span> <span class="dc-classtag streetwarden">Streetwarden</span> <span class="dc-classtag gutterdruid">Gutterdruid</span> <span class="dc-classtag cybersurgeon">Cybersurgeon</span> <span class="dc-classtag wirephreak">Wirephreak</span> <span class="dc-classtag technosorcerer">Technosorcerer</span> <span class="dc-classtag etherlock">Etherlock</span> <span class="dc-classtag dualist">Dualist</span> <span class="dc-classtag generalist">Generalist</span>

</div>

## Alerts and callouts

`> [!TYPE]` for one paragraph, `@callout variant=…` for more — both emit the same seven registers.

<div class="dg-stage dg-tall">

> [!NOTE]
> A character may hold no more than one Signature Augment at a time.

> [!WARNING]
> Trauma Patches stabilize a dying character but do not restore HP.

> [!DM]
> If a player hasn't chosen starting gear by the end of session zero, hand them a Scavenger Pack.

> [!VIBE]
> The rain in Dimm City never quite stops — it just changes color under the signage.

> [!ORIGIN]
> You didn't choose the street — the street chose you.

> [!VISIT]
> The Neon Bazaar doesn't close.

> [!GEAR]
> **Ripper Blades (Mk II)** — Melee. Damage 1d8+STR.

</div>

## Blocks

`@block .dc-panel | .dc-slate | .dc-shard | .dc-codex`.

<div class="dg-stage">

@block .dc-panel label="Panel"

Player-facing rules summaries and structured data.

@end-block

@block .dc-slate label="Slate"

Binding rulings and Dream Master directives.

@end-block

@block .dc-shard label="Shard"

Fiction, atmosphere, and setting asides.

@end-block

@block .dc-codex label="Codex"

Glossaries, lookups, and compendium entries.

@end-block

</div>

## Choice cards

`@card` inside `@section .dc-flaws`, `.dc-ideals` or `.dc-dreams`.

<div class="dg-stage">

@section .dc-flaws

@card

### Addictive Personality

You chase instant gratification without weighing the consequences.

> "Just one more, and then I'll quit."

@end-card

@end-section

@section .dc-ideals

@card

### Honor

You believe in a code, and upholding it is your duty no matter the cost.

> "I made a promise to help those in need, and I'll keep it at all costs."

@end-card

@end-section

@section .dc-dreams

@card

### Settle a Score

Settle a score from my past. Your Drive should pull you toward trouble, hard choices, and things worth risking your hide for.

> If chasing it can't change you, it ain't big enough.

@end-card

@end-section

</div>

## Outcome ladder

`@outcome`, then `@outcome flush`. `flush` removes the ladder's outer margin, so the difference is the spacing around it, not the ladder itself.

<div class="dg-stage">

@outcome

20 | Triumph | Best-case outcome.
11–19 | Success | You do it. Clean.
6–10 | Hard Choice | You succeed, but it costs you.
2–5 | Failure | You don't get what you wanted.
1 | Catastrophe | It goes bad, and then worse.

@end-outcome

@outcome flush

20 | Triumph | Best-case outcome.
11–19 | Success | You do it. Clean.
6–10 | Hard Choice | You succeed, but it costs you.
2–5 | Failure | You don't get what you wanted.
1 | Catastrophe | It goes bad, and then worse.

@end-outcome

</div>

## Tape

`@tape label="…"`, then the raw form with `.dc-flush`, which removes the tape's outer margin.

<div class="dg-stage">

@tape label="Operators"

<div class="dc-tape dc-flush">Operators</div>

</div>

## Stat grid

`<div class="dc-stat">`, then `<div class="dc-stat dc-flush">`, which removes the block's outer margin.

<div class="dg-stage">

<div class="dc-stat">
  <div class="dc-stat-head">
    <div class="dc-stat-name">Doc Solenn</div>
    <div class="dc-stat-class">— Contact · Ripperdoc —</div>
  </div>
  <div class="dc-stat-grid">
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">REP</div><div class="dc-stat-cell-val">4</div></div>
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">HEAT</div><div class="dc-stat-cell-val">2</div></div>
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">FEE</div><div class="dc-stat-cell-val">×1.5</div></div>
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">TURN</div><div class="dc-stat-cell-val">−1</div></div>
  </div>
</div>

<div class="dc-stat dc-flush">
  <div class="dc-stat-head">
    <div class="dc-stat-name">Doc Solenn</div>
    <div class="dc-stat-class">— Contact · Ripperdoc —</div>
  </div>
  <div class="dc-stat-grid">
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">REP</div><div class="dc-stat-cell-val">4</div></div>
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">HEAT</div><div class="dc-stat-cell-val">2</div></div>
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">FEE</div><div class="dc-stat-cell-val">×1.5</div></div>
    <div class="dc-stat-cell"><div class="dc-stat-cell-key">TURN</div><div class="dc-stat-cell-val">−1</div></div>
  </div>
</div>

</div>

## Heading chrome

`{.dc-chevron}`, `{.dc-spray}`, `{.dc-spec-tweak}` and `{.dc-spec-tweak .dc-no-top}`.

<div class="dg-stage">

@section .dc-banner-demo

# Augmerc {.dc-chevron}

## Biting Distance {.dc-spray}

### Spec Tweak: Wired to Kill {.dc-spec-tweak}

Augmerc learning paths assume combat-grade augmentations.

### Spec Tweak: Wired to Kill {.dc-spec-tweak .dc-no-top}

@end-section

</div>

## Section chassis

A bare `@section`, `@section .dc-plain`, `@section .dc-tabbed` with an `##` and a `###` tab, and `@section .gp-columns-2 .dc-column-panel`.

<div class="dg-stage dg-tall">

@section

### Bare section

The panel chrome: substrate, accent rule, and the first heading as a bar.

@end-section

@section .dc-plain

### Plain section

No substrate, rail or shadow: the text sits on whatever is behind it. A first heading still prints as a bar.

@end-section

@section .dc-tabbed

## Tabbed, H2

The heading hangs off the panel edge as the primary tab.

@end-section

@section .dc-tabbed

### Tabbed, H3

The subordinate tab: smaller type, tighter padding.

@end-section

@section .gp-columns-2 .dc-column-panel

### Column panel

Dimm City twitches like a clamped nerve at the edge of existence.

@column-break

Nothing here is safe. Nothing here is free.

@end-section

</div>

## Sidebars

`@sidebar` floats beside the text; `@sidebar .inset` is a full-height rail and needs its own `@page .page-sidebar` — see [Layout](#ch-layout).

<div class="dg-stage dg-on-paper">

When the Dreamers push past Too Far, the table starts asking how movement works.

@sidebar

### Distance, Fast

Three bands, no grid. **In Reach** is one swing away. **Nearby** is a burned Move.

@end-sidebar

Keep the bands fictional, not metric. The Dream Master sets the band; the dice decide whether you close it. A Dreamer who wants to cross two bands in one turn is telling you they're willing to spend everything to get there.

</div>

## Image floats

`{.dc-img-float-left}` and `{.dc-img-float-right}`.

<div class="dg-stage dg-on-paper">

![Scavenger](img/scavenger.png){.dc-img-float-left}

Blasts lit the dusk like glitchfire. Bolts and teeth and claws tangled mid-air. Neon signs cracked. Alleyways bled smoke. Debris rained in bursts.

DimmCitz scattered, vanished into bolted dens and reinforced rooftops.

![Scavenger](img/scavenger.png){.dc-img-float-right}

This wasn't about glory — it was turf. It was pride. It was blood memory, raw and ugly, of family torn away by their rival.

The air stank of scorched fur, ozone, and cordite.

</div>
