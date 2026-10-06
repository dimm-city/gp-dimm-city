@chapter #ch-specialty .dg-guide ch="7"

@page

# The Specialty System

@lede

The richest family in the book. A specialty wrapper sets the shape and color; inside it, an intro panel, an art plate, a catalog card, learning paths, and skill cards all inherit that identity. Authors never set a variant on a card — the parent decides.

@end-lede


## Specialty

`@specialty .<name>` is the parent scope. It emits nothing visible itself; every component inside it reads its clip-path silhouettes and accent color. Ten families ship:

`augmerc` · `proxy` · `streetwarden` · `gutterdruid` · `cybersurgeon` · `wirephreak` · `technosorcerer` · `etherlock` · `dualist` · `generalist`

```markdown
@specialty .augmerc

… intro, art, learning paths, skills …

@end-specialty
```

Opening a new `@specialty` closes the previous one, along with any open path or skill. Tokens the wrapper sets for its children: `--spec-accent`, `--spec-mid`, `--spec-dark`, `--dc-skill-tab-shape`, `--dc-skill-body-shape`, `--dc-path-title-shape`, `--dc-path-shell-clip`, `--dc-specialty-card-shell-shape`, `--dc-specialty-intro-title-shape`, `--dc-specialty-intro-clip`.

## Specialty intro

The title-banded panel on a specialty's first page: the `##` name, the pitch, and a `###` spec tweak.

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

@specialty .augmerc

@specialty-intro

## Augmerc

An Augmerc is muscle for hire. Street thugs, corporate bodyguards, deniable enforcers — the difference is gear, grafts, and how much of them is still original.

### Spec Tweak: **Wired to Kill**

Augmerc learning paths assume combat-grade augmentations. Without the implants, the Augmerc spends 1 extra AP to activate a path's abilities.

@end-specialty-intro

@end-specialty

Tokens: `--dc-specialty-intro-bg`, `--dc-specialty-intro-title-bg`, `--dc-specialty-intro-title-color`.

## Specialty art

A full-page art plate. It takes its own page and bleeds to the edge; in a book this follows the intro.

```markdown
@specialty .augmerc

@specialty-art

![Augmerc](https://placehold.co/640x360/1a1d2b/e8503a/png?text=Augmerc)

@end-specialty-art

@end-specialty
```

Result {.dg-result}

@specialty .augmerc

@specialty-art

![Augmerc](https://placehold.co/640x360/1a1d2b/e8503a/png?text=Augmerc)

@end-specialty-art

@end-specialty


## Specialty card

The catalog card for a "choose your specialty" page: portrait, a `>` tagline, and a short pitch, inside a `@section .dc-card-grid` that lays the cards out two across. Each card sits in its own `@specialty` so it carries its own color.

```markdown
@section .dc-card-grid

@specialty .augmerc

@specialty-card #card-augmerc

### Augmerc

![Augmerc](https://placehold.co/300x340/1a1d2b/e8503a/png?text=Augmerc)

> Cybernetic Commando

Heavily armed and wired for war, Augmercs are the blunt force of any squad.

@end-specialty-card

@end-specialty

@specialty .gutterdruid

@specialty-card #card-gutterdruid

### Gutterdruid

![Gutterdruid](https://placehold.co/300x340/1a1d2b/4a9d6e/png?text=Gutterdruid)

> Feral Shapeshifter

Gutterdruids rewrite their own flesh to match the wasteland around them.

@end-specialty-card

@end-specialty

@end-section
```

Result {.dg-result}

@section .dc-card-grid

@specialty .augmerc

@specialty-card #card-augmerc

### Augmerc

![Augmerc](https://placehold.co/300x340/1a1d2b/e8503a/png?text=Augmerc)

> Cybernetic Commando

Heavily armed and wired for war, Augmercs are the blunt force of any squad.

@end-specialty-card

@end-specialty

@specialty .gutterdruid

@specialty-card #card-gutterdruid

### Gutterdruid

![Gutterdruid](https://placehold.co/300x340/1a1d2b/4a9d6e/png?text=Gutterdruid)

> Feral Shapeshifter

Gutterdruids rewrite their own flesh to match the wasteland around them.

@end-specialty-card

@end-specialty

@end-section

The full ten-card grid is in [Specialty Overview](#ch-example-specialty-overview). Tokens: `--dc-specialty-card-bg`, `--dc-specialty-card-border`, `--dc-specialty-card-accent`, `--dc-specialty-card-media-height`, `--dc-specialty-card-title-color`, `--dc-specialty-card-shadow`.


## Learning path

A named path: a `###` title (rendered as a spray banner with the path's code), a `>` subtitle, and a bullet list of its skills, which becomes the sticker chain. A bold paragraph after the list is the path's signature augment. Skill cards follow inside the path. The code (`AUG1`) and each card's tier (`AUG1.1`, `AUG1.2`, …) are computed from position.

```markdown
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

Tokens: `--dc-path-title-bg`, `--dc-path-title-color`, `--dc-path-accent`, `--dc-arrow-color`.


## Skill card

The anatomy of one card: a `####` name, optionally `| Tier` to override the computed tier; a `>` flavor line; an ordered list where each item starts with `**N AP**` — rendered as a cost chip — and an italic ability name; and a closing `#####` line that becomes the card's sub-header sticker. `@skill` opens the next card and closes the previous; `@end-skill` closes the last.

```markdown
@specialty .augmerc

@skill

#### Dirty Work | AUG1.3

> Fair fights are for nice mercs who lose.

Once per round, outside your turn, you exploit a target in reach:

1. **0 AP** *Off-Hand Insurance:* Slip in a hidden strike that deals 1 damage.
2. **1 AP** *Street Tricks:* Snag their balance. Gain Lucidity on your next roll against the target.
3. **VAR AP** *Break the Read:* ROLL THE DIE! On a hit the target is Dazed; extend it for 1 AP per round.

##### You don't need an opening. You make one.

@end-skill

@end-specialty
```

Result {.dg-result}

@specialty .augmerc

@skill

#### Dirty Work | AUG1.3

> Fair fights are for nice mercs who lose.

Once per round, outside your turn, you exploit a target in reach:

1. **0 AP** *Off-Hand Insurance:* Slip in a hidden strike that deals 1 damage.
2. **1 AP** *Street Tricks:* Snag their balance. Gain Lucidity on your next roll against the target.
3. **VAR AP** *Break the Read:* ROLL THE DIE! On a hit the target is Dazed; extend it for 1 AP per round.

##### You don't need an opening. You make one.

@end-skill

@end-specialty

| Option | You write | Effect |
|---|---|---|
| Tier | `#### Name \| AUG1.3` | Override the computed tier on the tab |
| Anchor | `@skill id="dirty-work"` | A link target for the card |
| Highlight | `#### Name \| AUG4.1 \| highlight` with `@skill {.dc-highlight}` | A featured ability: crimson tab halo and body wash |
| Two columns | `@skill {.dc-two-col}` | Pack a long ability list into two columns |
| Allow split | `@skill {.dc-allow-split}` | Let a tall card break across pages |

The AP chip reads the number: `0 AP` is free (crimson), a number is standard, `VAR` or a range is variable (magenta). A raw `<span class="dc-ap">2 AP</span>` makes a chip in prose.

### Highlight and two-column variants

@specialty .augmerc

@skill {.dc-highlight}

#### Apex Physiology | AUG4.1 | highlight

> Brutality is your default setting!

1. **0 AP** *Built for Violence:* Your basic unarmed attacks deal 2 HP instead of 1.
2. **0 AP** *Hammerfist Synergy:* Your Triumph range expands to 19–20.

##### Violence begins in the bones.

@skill {.dc-two-col}

#### Boost Morale | AUG3.4

> When we get outta dis, Imma take whoever has the most kills to the EntD!

When an ally in range ROLLS THE DIE!, bark encouragement that hits just right. Once per round.

1. **2 AP** *Push the Fail:* A Failure becomes a Hard Choice.
2. **1 AP** *Salvage the Choice:* A Hard Choice becomes a Success.
3. **3 AP** *Make It Legend:* A Success becomes a Triumph.
4. **4 AP** *Drag It Up:* A Catastrophe becomes a Hard Choice.

##### Courage spreads. So does panic.

@end-skill

@end-specialty


## Continuing a long card

When one ability runs past a page, `@continue` inside the card closes it and opens a continuation card with a `▸` on its tab, keeping the same specialty shape. Prefer this to `.dc-allow-split`: the break lands at a boundary you chose.

```markdown
@specialty .augmerc

@skill

#### Pain Compliance | AUG1.4

> Enough pain'll make a punk outta anyone!

1. **1 AP** *Take Control:* Overpower one target in reach and place them in a painful hold. A controlled target cannot react out of turn and rolls Surreal.

@continue

2. **4 AP** *Applied Leverage:* Each round you sustain control, choose *Break Them* (disable one limb) or *Strip Them* (pry one item free).
3. **3 AP** *Lights Out:* The target goes unconscious at the end of your turn.

##### Predators don't negotiate.

@end-skill

@end-specialty
```

Result {.dg-result}

@specialty .augmerc

@skill

#### Pain Compliance | AUG1.4

> Enough pain'll make a punk outta anyone!

1. **1 AP** *Take Control:* Overpower one target in reach and place them in a painful hold. A controlled target cannot react out of turn and rolls Surreal.

@continue

2. **4 AP** *Applied Leverage:* Each round you sustain control, choose *Break Them* (disable one limb) or *Strip Them* (pry one item free).
3. **3 AP** *Lights Out:* The target goes unconscious at the end of your turn.

##### Predators don't negotiate.

@end-skill

@end-specialty

## Outcomes inside a card

A `| Roll | Outcome |` table inside a skill card renders as that card's outcome ladder.

```markdown
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
```

Result {.dg-result}

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


## One source, ten shapes

The same path and card markdown, dropped into a different `@specialty`, takes that family's silhouette and color with no change to the source. Gutterdruid, then the two multi-discipline shells:

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

@specialty .dualist

@learning-path

### Split Discipline

> Two crafts, one body. You never fully belong to either — and that's the edge.

- Crossover Stance
- Borrowed Reflex

@skill

#### Crossover Stance

> The moment they read you as one thing, you become the other.

1. **1 AP** *Read the Frame:* Declare which discipline an enemy expects. The first technique from the *other* discipline rolls Lucid against them.

##### Belonging to neither means owning the gap between them.

@end-skill

@end-learning-path

@end-specialty

@specialty .generalist

@learning-path

### Jack of the Sprawl

> Master of none, ready for anything.

- Field Improvisation
- Adaptive Loadout

@skill

#### Field Improvisation

> No right tool? Every wrong tool works if you swing it hard enough.

1. **1 AP** *Make It Work:* Attempt a task that needs gear or training you don't have. ROLL THE DIE!

##### The specialist quits when the manual ends. You're just getting started.

@end-skill

@end-learning-path

@end-specialty

Skill-card tokens: `--dc-card-accent`, `--dc-card-surface`, `--dc-card-tab-bg`, `--dc-card-tab-title-color`, `--dc-card-gap`, `--dc-card-tab-shadow`; AP chip: `--dc-ap-bg`, `--dc-ap-fg`, `--dc-ap-border`.
