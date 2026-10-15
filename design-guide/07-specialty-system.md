@chapter #ch-specialty .dg-guide ch="7"

@page .dg-doc

Chapter 7 {.dg-kicker}

# The Specialty System

The richest family in the book. A specialty wrapper sets the shape and color; inside it, an intro panel, an art plate, a catalog card, learning paths, and skill cards all inherit that identity. Authors never set a variant on a card — the parent decides. {.dg-lede}


## Specialty

`@specialty .<name>` is the parent scope. It emits nothing visible itself; every component inside it reads its clip-path silhouettes and accent color. Ten families ship:

`augmerc` · `proxy` · `streetwarden` · `gutterdruid` · `cybersurgeon` · `wirephreak` · `technosorcerer` · `etherlock` · `dualist` · `generalist`

The silhouette says what kind of specialty it is, on the card, its tab, the path banner and the intro alike: tech ones are crisp stair-steps and square bites (Augmerc, Wirephreak, Cybersurgeon), magic ones are facets and lozenges (Etherlock, Dualist, Generalist, and the Proxy's gate), the Technosorcerer is torn, the Gutterdruid wobbly, the Streetwarden a sign-plate octagon. The title band spans its frame exactly and every cut stays clear of the type.

```markdown
@specialty .augmerc

… intro, art, learning paths, skills …

@end-specialty
```

Opening a new `@specialty` closes the previous one, along with every path and skill inside it. `@end-specialty` does the same, and so does the next `@chapter`, `@page` or `@section`: a specialty cannot straddle a page, so put a page break inside one with `@page-break`. A specialty is written one of two ways, `@specialty augmerc` or `@specialty .augmerc`, and both give the same wrapper. A skill belongs inside a learning path inside a specialty; the Problems panel flags a skill sitting directly in the specialty. Tokens the wrapper sets for its children: `--spec-accent`, `--spec-mid`, `--spec-dark`, `--spec-band` and `--spec-on-band` (the title-band fill and its type), `--spec-chip-bg`, `--spec-chip-fg` and `--spec-chip-edge` (the tier pill), `--dc-skill-tab-shape`, `--dc-skill-body-shape`, `--dc-path-title-shape`, `--dc-path-shell-clip`, `--dc-specialty-intro-title-shape`, `--dc-specialty-intro-clip`.

## Specialty intro

The title-banded panel on a specialty's first page: the `##` name, the pitch, and a `###` spec tweak. The band is the specialty's own signal colour, so ten specialties read as ten colours and ten values at a glance, and each carries its own register: the tech specialties an LED rim and a rule of LED dots, the magic ones a faceted plane, Streetwarden a hazard-tape rule, and Technosorcerer and Gutterdruid a torn bottom edge with no rule.

```markdown
@specialty .augmerc

@specialty-intro

## Augmerc

An Augmerc is muscle for hire. Street thugs, corporate bodyguards, deniable enforcers — the difference is gear, grafts, and how much of them is still original.

### Spec Tweak: **Wired to Kill**

Augmerc learning paths assume combat-grade augmentations. Without the implants, the Augmerc spends 1 extra AP to activate a path's abilities.

@end-specialty-intro

@end-specialty
```

Result {.dg-result}

<div class="dg-stage">

@specialty .augmerc

@specialty-intro

## Augmerc

An Augmerc is muscle for hire. Street thugs, corporate bodyguards, deniable enforcers — the difference is gear, grafts, and how much of them is still original.

### Spec Tweak: **Wired to Kill**

Augmerc learning paths assume combat-grade augmentations. Without the implants, the Augmerc spends 1 extra AP to activate a path's abilities.

@end-specialty-intro

@end-specialty

</div>

Tokens: `--dc-specialty-intro-bg`, `--dc-specialty-intro-title-bg`, `--dc-specialty-intro-title-color`, and for the band's register `--dc-band-rule`, `--dc-band-rule-h`, `--dc-band-tick`, `--dc-band-tick-style`, `--dc-band-tick-w`, `--dc-band-rule-skew`, `--dc-band-rule-bleed`, `--dc-band-facet`, `--dc-band-facet-width`, `--dc-band-facet-clip`, `--dc-band-rim`, `--dc-band-reg` (a second ink printed 2px off, tech bands).

## Specialty art

A full-page art plate. It takes its own page and bleeds to the edge; in a book this follows the intro. The rendered plate is the next page. The placeholders here are local PNGs in `design-guide/img/`, one per specialty.

```markdown
@specialty .augmerc

@specialty-art

![Augmerc](img/specialty-augmerc-wide.png)

@end-specialty-art

@end-specialty
```

@specialty .augmerc

@specialty-art

![Augmerc](img/specialty-augmerc-wide.png)

@end-specialty-art

@end-specialty


## Specialty card

The catalog card for a "choose your specialty" page: portrait, a `>` tagline, and a short pitch, inside a `@card-grid`, with `@columns 2` laying the cards out two across. Each card sits in its own `@specialty` so it carries its own color, its silhouette and its own portrait cut. On a [`@page specialty-catalog`](#ch-templates) the ten cards become a two-page spread of tall poster cards (portrait on top, then name, tagline and pitch, an index chip on the portrait); anywhere else they are the dense card, a small thumbnail beside the text. The card's layout is tokens: `--dc-specialty-card-display`, `-media-order`, `-media-float`, `-media-margin`, `-media-shape`, `-media-mat`, `-name-size` and `-index`, and the grid's `--dc-card-grid-display`, `-item-display`, `-row` and `-gap`.

```markdown {.dg-split}
@card-grid

@columns 2

@specialty .augmerc

@specialty-card #card-augmerc

### Augmerc

![Augmerc](img/specialty-augmerc-card.png)

> Cybernetic Commando

Heavily armed and wired for war, Augmercs are the blunt force of any squad.

@end-specialty-card

@end-specialty

@specialty .gutterdruid

@specialty-card #card-gutterdruid

### Gutterdruid

![Gutterdruid](img/specialty-gutterdruid-card.png)

> Feral Shapeshifter

Gutterdruids rewrite their own flesh to match the wasteland around them.

@end-specialty-card

@end-specialty

@end-columns

@end-card-grid
```

Result {.dg-result}

<div class="dg-stage">

@card-grid

@columns 2

@specialty .augmerc

@specialty-card #card-augmerc

### Augmerc

![Augmerc](img/specialty-augmerc-card.png)

> Cybernetic Commando

Heavily armed and wired for war, Augmercs are the blunt force of any squad.

@end-specialty-card

@end-specialty

@specialty .gutterdruid

@specialty-card #card-gutterdruid

### Gutterdruid

![Gutterdruid](img/specialty-gutterdruid-card.png)

> Feral Shapeshifter

Gutterdruids rewrite their own flesh to match the wasteland around them.

@end-specialty-card

@end-specialty

@end-columns

@end-card-grid

</div>

The full ten-card grid is in [Specialty Overview](#ch-example-specialty-overview). Tokens: `--dc-specialty-card-bg`, `--dc-specialty-card-accent`, `--dc-specialty-card-band-bg`, `--dc-specialty-card-band-fg`, `--dc-specialty-card-media-height`, `--dc-specialty-card-title-color`.


## Learning path

A named path: a `###` title (rendered as a title band in the specialty's signal colour, with the path's code), a `>` subtitle, and a bullet list of its skills, which becomes the sticker chain. A bold paragraph after the list is the path's signature augment. Skill cards follow inside the path. The code (`AUG1`) and each card's tier (`AUG1.1`, `AUG1.2`, …) are computed from position.

```markdown {.dg-split}
@specialty .augmerc

@learning-path

### Biting Distance

> If you can touch it, you can maul it. When things get close, they bleed.

- Punishing Counter
- Rage Hit

**Backbiter Spines:** Reactive spine rigs in the forearms and shins. Spend an action defending and the rig braces, resisting 2 damage from melee and dealing 1 to everything in reach.

@skill

#### Punishing Counter

> See an opening, ya take it.

1. **0 AP** *Steel Says No:* When an enemy in reach rolls a hard choice or worse on a basic attack, knock it off line. On a Failure or worse, ROLL THE DIE! and make a basic attack.
2. **2 AP** *Bullet to Blood:* Slip a ranged shot as it screams past, surge forward, and ROLL THE DIE! to make a basic attack.

##### Openings are invitations to take a chunk outta 'em.

@skill

#### Rage Hit

> Risk it, swing wild, an hit hard!

1. **0 AP** *Full Send:* Throw everything into a reckless attack. Describe the chaos and ROLL THE DIE!
2. **2 AP** *All Gas, No Brakes:* Two basic attacks against one target. If either roll is a 1, both fail.

##### Full send or full regret.

@end-skill

@end-learning-path

@end-specialty
```

Result {.dg-result}

<div class="dg-stage dg-tall">

@specialty .augmerc

@learning-path

### Biting Distance

> If you can touch it, you can maul it. When things get close, they bleed.

- Punishing Counter
- Rage Hit

**Backbiter Spines:** Reactive spine rigs in the forearms and shins. Spend an action defending and the rig braces, resisting 2 damage from melee and dealing 1 to everything in reach.

@skill

#### Punishing Counter

> See an opening, ya take it.

1. **0 AP** *Steel Says No:* When an enemy in reach rolls a hard choice or worse on a basic attack, knock it off line. On a Failure or worse, ROLL THE DIE! and make a basic attack.
2. **2 AP** *Bullet to Blood:* Slip a ranged shot as it screams past, surge forward, and ROLL THE DIE! to make a basic attack.

##### Openings are invitations to take a chunk outta 'em.

@skill

#### Rage Hit

> Risk it, swing wild, an hit hard!

1. **0 AP** *Full Send:* Throw everything into a reckless attack. Describe the chaos and ROLL THE DIE!
2. **2 AP** *All Gas, No Brakes:* Two basic attacks against one target. If either roll is a 1, both fail.

##### Full send or full regret.

@end-skill

@end-learning-path

@end-specialty

</div>

A path with no subtitle and no sticker chain is the band alone. Tokens: `--dc-path-title-bg`, `--dc-path-title-color`, `--dc-path-code-bg`, `--dc-path-code-fg`, `--dc-path-chip-bg`, `--dc-path-chip-fg`, `--dc-path-chip-edge`, `--dc-path-note-rail`, `--dc-path-accent`, `--dc-arrow-color`, and the band tokens above.


## Skill card

The anatomy of one card: a `####` name, optionally `| Tier` to override the computed tier; a `>` flavor line; an ordered list where each item starts with `**N AP**` — rendered as a cost chip — and an italic ability name; and a closing `#####` line that becomes the card's sub-header sticker. A skill sits in a learning path. `@skill` opens a skill, and opening the next one closes it; `@end-skill` closes just that skill, never the path around it. A `####` heading starts a card, so one `@skill` with two `####` headings makes two cards.

```markdown
@specialty .augmerc

@learning-path

### Example Path

@skill

#### Dirty Work | AUG1.3

> Fair fights are for nice mercs who lose.

Once per round, outside your turn, you exploit a target in reach:

1. **0 AP** *Off-Hand Insurance:* Slip in a hidden strike that deals 1 damage.
2. **1 AP** *Street Tricks:* Snag their balance. Gain Lucidity on your next roll against the target.
3. **VAR AP** *Break the Read:* ROLL THE DIE! On a hit the target is Dazed; extend it for 1 AP per round.

##### You don't need an opening. You make one.

@end-skill

@end-learning-path

@end-specialty
```

Result {.dg-result}

<div class="dg-stage">

@specialty .augmerc

@learning-path

### Example Path

@skill

#### Dirty Work | AUG1.3

> Fair fights are for nice mercs who lose.

Once per round, outside your turn, you exploit a target in reach:

1. **0 AP** *Off-Hand Insurance:* Slip in a hidden strike that deals 1 damage.
2. **1 AP** *Street Tricks:* Snag their balance. Gain Lucidity on your next roll against the target.
3. **VAR AP** *Break the Read:* ROLL THE DIE! On a hit the target is Dazed; extend it for 1 AP per round.

##### You don't need an opening. You make one.

@end-skill

@end-learning-path

@end-specialty

</div>

| Option | You write | Effect |
|---|---|---|
| Tier | `#### Name \| AUG1.3` | Override the computed tier on the tab |
| Anchor | `@skill id="dirty-work"` | A link target for the card |
| Two columns | `@columns 2` … `@end-columns` around part of the body | Pack a long ability list into two columns; the flavor line and sub-header stay full width |
| Avoid split | `@skill {.dc-avoid-split}` | Keep a card whole instead of letting it break across pages |

The AP chip reads the number: `0 AP` is free (an unlit LED: a grey lens with a hollow lamp and an ink edge, the quietest chip on the card), a number is standard (HUD blue), `VAR` or a range is variable (deep magenta). Two more come from a raw span: `.reduced` is pale blue with a down-triangle and `.increased` is blood with an up-triangle, so they differ in grayscale too. A raw `<span class="dc-ap">2 AP</span>` makes a chip in prose.

### Two columns

<div class="dg-stage">

@specialty .augmerc

@learning-path

### Example Path

@skill

#### Boost Morale | AUG3.4

> When we get outta dis, Imma take whoever has the most kills to the EntD!

When an ally in range ROLLS THE DIE!, bark encouragement that hits just right. Once per round.

@columns 2

1. **2 AP** *Push the Fail:* A Failure becomes a Hard Choice.
2. **1 AP** *Salvage the Choice:* A Hard Choice becomes a Success.
3. **3 AP** *Make It Legend:* A Success becomes a Triumph.
4. **4 AP** *Drag It Up:* A Catastrophe becomes a Hard Choice.

@end-columns

##### Courage spreads. So does panic.

@end-skill

@end-learning-path

@end-specialty

</div>


## Continuing a long card

When one ability runs past a page, `@continue` inside the card closes it and opens a continuation card with a small triangle after the name on its tab, keeping the same specialty shape. Cards split across pages by default; `@continue` is for a break at a boundary you chose.

```markdown {.dg-split}
@specialty .augmerc

@learning-path

### Example Path

@skill

#### Pain Compliance | AUG1.4

> Enough pain'll make a punk outta anyone!

1. **1 AP** *Take Control:* Overpower one target in reach and place them in a painful hold. A controlled target cannot react out of turn and rolls Surreal.

@continue

2. **4 AP** *Applied Leverage:* Each round you sustain control, choose *Break Them* (disable one limb) or *Strip Them* (pry one item free).
3. **3 AP** *Lights Out:* The target goes unconscious at the end of your turn.

##### Predators don't negotiate.

@end-skill

@end-learning-path

@end-specialty
```

Result {.dg-result}

<div class="dg-stage">

@specialty .augmerc

@learning-path

### Example Path

@skill

#### Pain Compliance | AUG1.4

> Enough pain'll make a punk outta anyone!

1. **1 AP** *Take Control:* Overpower one target in reach and place them in a painful hold. A controlled target cannot react out of turn and rolls Surreal.

@continue

2. **4 AP** *Applied Leverage:* Each round you sustain control, choose *Break Them* (disable one limb) or *Strip Them* (pry one item free).
3. **3 AP** *Lights Out:* The target goes unconscious at the end of your turn.

##### Predators don't negotiate.

@end-skill

@end-learning-path

@end-specialty

</div>

## Outcomes inside a card

A `| Roll | Outcome |` table inside a skill card renders as that card's outcome ladder.

```markdown {.dg-split}
@specialty .augmerc

@learning-path

### Example Path

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

@end-learning-path

@end-specialty
```

Result {.dg-result}

<div class="dg-stage">

@specialty .augmerc

@learning-path

### Example Path

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

@end-learning-path

@end-specialty

</div>


## One source, eight shapes {.gp-page-break}

The same path and card markdown, dropped into a different `@specialty`, takes that family's silhouette and color with no change to the source. Here it is under Gutterdruid. (The Dualist and Generalist borrow other specialties' skills, so they have no trees of their own.)

<div class="dg-stage">

@specialty .gutterdruid

@learning-path

### Beastmode

> Some adapt and overcome. You mutate and dominate.

- Feralmorph
- Environmental Assimilation

@skill

#### Feralmorph

> You drop into a shape that hides in cracks or hunts the street.

1. **2 AP** *Take the Shape:* Your body rewrites into a natural form, from a mouse to a horse. The form has 6 HP; you gain its movement and senses but cannot use abilities, items, or language.

##### Some problems need teeth, paws, and claws.

@end-skill

@end-learning-path

@end-specialty

</div>

Skill-card tokens: `--dc-card-accent`, `--dc-card-surface`, `--dc-card-tab-bg`, `--dc-card-tab-title-color`, `--dc-card-gap`, `--dc-card-tab-shadow`; tier pill: `--dc-tier-bg`, `--dc-tier-fg`, `--dc-tier-edge` (the specialty's own chip: its signal colour, or cream where that colour fails contrast for the type); AP chip: `--dc-ap-bg`, `--dc-ap-fg`, `--dc-ap-border`.
