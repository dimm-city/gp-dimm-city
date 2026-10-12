@chapter #ch-panels .dg-guide ch="6"

@page .dg-doc

Chapter 6 {.dg-kicker}

# Panels, Cards & Data

The enclosures: the section variants, four block registers, the sidebar box, definition and glossary forms, the numbered procedure, the outcome ladder, choice cards, gear entries, tables, and the stat blocks a Dream Master runs from. {.dg-lede}


## Section

A `@section` groups what is inside it. Bare, it is core's plain box and adds no look; a word after it picks the look. Three are general and work anywhere. Sections split across pages by default; `.dc-avoid-split` keeps one whole. One accent knob, `--dc-section-accent`, colours the rail and the title bar of all three. For the named components (`@npc-stat`, `@gear`, `@outcome` and the rest), [Pick a section](#ch-start) maps what you are writing to the marker.

```markdown {.dg-split}
@section panel

## Rules Panel

The card: a cream substrate, an accent rail, a clipped corner, a shadow, and the first `##` or `###` as a title bar.

@end-section

@section flat

The rail on a plain host, for text that should read as a continuation of the page.

@end-section

@section aside

### Worth Knowing

A short note set off from the text: a hairline frame, an accent rail, an italic heading.

@end-section

@section

A bare section: no look at all. The text sits on the page.

@end-section
```

Result {.dg-result}

<div class="dg-stage dg-tall">

@section panel

## Rules Panel

The card: a cream substrate, an accent rail, a clipped corner, a shadow, and the first `##` or `###` as a title bar.

@end-section

@section flat

The rail on a plain host, for text that should read as a continuation of the page.

@end-section

@section aside

### Worth Knowing

A short note set off from the text: a hairline frame, an accent rail, an italic heading.

@end-section

</div>

<div class="dg-stage dg-on-paper">

@section

A bare section: no look at all. The text sits on the page.

@end-section

</div>

`panel` is the look for rules and reference text with a heading; `.dc-avoid-split` on it keeps a short panel on one page. `aside` is the sidebar-box treatment on a section; reach for `@sidebar-box` itself when the note needs its own divider. Tokens: `--dc-section-bg`, `--dc-section-accent`, `--dc-section-pad-top`, `-right`, `-bottom`, `-left`, and for `panel` also `--dc-section-surface` and `--dc-section-shadow` (`none` removes the layer).

The components below that are sections have a marker of their own and a word on `@section`: `@npc-stat` (`npc`), `@fiction-excerpt` (`fiction`), `@citizen-walkthrough` (`walkthrough`), `@card-grid` (`cards`), `@flaws`, `@ideals` and `@dreams`.

## Fiction excerpt

Fiction, lore, a chapter-opening story. Aged paper instead of a card: no rail, no title bar, narrative leading, and the first image floats left. On a chapter-start page it takes a heavier edge, two ink rules and an offset shadow.

```markdown {.dg-split}
@fiction-excerpt

"It's hard being me, but I guess it's the same for anyting sentient in the monoverse, ay?!"

I wuz tearin down an alley, lungs burnin, heart jackhammering like it wanted out.

@end-fiction-excerpt
```

Result {.dg-result}

<div class="dg-stage">

@fiction-excerpt

"It's hard being me, but I guess it's the same for anyting sentient in the monoverse, ay?!"

I wuz tearin down an alley, lungs burnin, heart jackhammering like it wanted out.

@end-fiction-excerpt

</div>

Tokens: `--dc-fiction-bg`, `--dc-fiction-line-height`, `--dc-fiction-rule` (top and bottom edge weight), `--dc-fiction-shadow`, `--dc-fiction-art-float`, `--dc-fiction-art-width`.

## Block

One macro, four registers. The class on the opener picks the silhouette and surface; `label` fills the title band and can be omitted.

```markdown
@block .dc-panel label="Action Economy"

On your turn you get **one Move and one Action**. Spend Augment Points to push past it.

- **Move:** shift one Distance band. Free.
- **Action:** attack, hack, or trigger an ability.

@end-block
```

Result {.dg-result}

<div class="dg-stage">

@block .dc-panel label="Action Economy"

On your turn you get **one Move and one Action**. Spend Augment Points to push past it.

- **Move:** shift one Distance band. Free.
- **Action:** attack, hack, or trigger an ability.

@end-block

</div>

| Variant | Register | Use for |
|---|---|---|
| `.dc-panel` | HUD blue, hex corners | Player-facing rules summaries, structured data |
| `.dc-slate` | Dark surface, magenta band | Binding rulings, Dream Master directives |
| `.dc-shard` | Aged paper, rust band, zine cut | Fiction, atmosphere, setting asides |
| `.dc-codex` | Pale cyan, octagon corners | Glossaries, lookups, compendium entries |

<div class="dg-stage">

@block .dc-slate label="The Core Loop"

1. The **Dream Master** presents a situation.
2. The **Dreamers** declare intent.
3. The **fiction resolves** — sometimes on a die, sometimes on a word.

@end-block

@block .dc-shard label="The Neon Bazaar"

Hologram haze cuts the gloom you're stumbling through. Flickering ads claw the air above blades of neon, and the scent of burnt oil rides over hot garbage.

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

</div>

Tokens: `--dc-block-bg`, `--dc-block-fg`, `--dc-block-accent`, `--dc-block-title-bg`, `--dc-block-title-fg`.


## Sidebar box

A standalone reference box with its own heading and an internal dashed divider — rules etiquette, a standalone ruling, anything that needs its own boundary.

```markdown
@sidebar-box

#### Dice Etiquette

---

Roll your dice in the open. If a die lands off the table, it doesn't count: reroll it.

@end-sidebar-box
```

Result {.dg-result}

<div class="dg-stage">

@sidebar-box

#### Dice Etiquette

---

Roll your dice in the open. If a die lands off the table, it doesn't count: reroll it.

@end-sidebar-box

</div>

Tokens: `--dc-sidebar-box-surface`, `--dc-sidebar-box-border`, `--dc-sidebar-box-accent`, `--dc-sidebar-box-rail`.

## Definition

A short italic callout for one term — in-world vocabulary, an NPC type, an item category. Stack several in an `@columns 2` run for a glossary of callouts.

```markdown
@definition

**Tick / Tic:** A heartbeat. The space between deciding and doing. Used in ability text to mean *immediate*.

@end-definition
```

Result {.dg-result}

<div class="dg-stage">

@columns 2

@definition

**Tick / Tic:** A heartbeat. The space between deciding and doing. Used in ability text to mean *immediate*.

@end-definition

@definition

**Shortly / Shorty:** Roughly a scene. Long enough to cross a district, tend a wound, or shake a tail.

@end-definition

@column-break

@definition

**Fixer:** The person who slides into the booth with a dirty envelope and a job you'll regret.

@end-definition

@definition

**Sporo:** A native of Dimm City wearing an animal form.

@end-definition

@end-columns

</div>

Tokens: `--dc-definition-block-surface`, `--dc-definition-block-accent`, `--dc-definition-block-accent-width`. For a plain term list, a markdown definition list (`Term` / `: meaning`) needs no macro — see [Writing a Page](#ch-writing).

## Glossary

A run of **term** — gloss paragraphs as one connected register, the form of an appendix glossary.

```markdown
@glossary

**Heat** — The running tally of attention you've drawn.

**Hard Choice** — A roll of 6–10. The fiction advances, but it costs you.

@end-glossary
```

Result {.dg-result}

<div class="dg-stage">

@glossary

**Heat** — The running tally of attention you've drawn.

**Hard Choice** — A roll of 6–10. The fiction advances, but it costs you.

@end-glossary

</div>


## Procedure

A zero-padded step list for anything the table runs in order.

```markdown
@procedure

1. **The Dream Master describes the situation.** Where you are, what's wrong.
2. **A Dreamer declares an action.** Say what your character does.
3. **If the outcome is uncertain, ROLL THE DIE!**
4. **The result determines what happens next.**

@end-procedure
```

Result {.dg-result}

<div class="dg-stage">

@procedure

1. **The Dream Master describes the situation.** Where you are, what's wrong.
2. **A Dreamer declares an action.** Say what your character does.
3. **If the outcome is uncertain, ROLL THE DIE!**
4. **The result determines what happens next.**

@end-procedure

</div>

## Outcome ladder

The d20 result table every roll resolves against. One row per line: `roll | name | text`. Rows are colored by position, top to bottom: crit, hit, mixed, miss, fail. `@outcome flush` runs it edge to edge.

```markdown
@outcome

20 | Triumph | Best-case outcome. You do it, and the moment breaks your way.
11–19 | Success | You do it. Clean.
6–10 | Hard Choice | You succeed, but it costs you.
2–5 | Failure | You don't get what you wanted.
1 | Catastrophe | It goes bad, and then worse.

@end-outcome
```

Result {.dg-result}

<div class="dg-stage">

@outcome

20 | Triumph | Best-case outcome. You do it, and the moment breaks your way.
11–19 | Success | You do it. Clean.
6–10 | Hard Choice | You succeed, but it costs you.
2–5 | Failure | You don't get what you wanted.
1 | Catastrophe | It goes bad, and then worse.

@end-outcome

</div>

Tokens: `--dc-outcomes-surface`, `--dc-outcomes-border`, `--dc-outcomes-label-bg`, `--dc-outcomes-label-color`, `--dc-outcome-key-color`, `--dc-outcome-name-color`.


## Card

A choice card: heading, body, and a closing quote that becomes the card's footer. Wrap a run of cards in `@flaws`, `@ideals`, or `@dreams` to color the accent for that step of character creation.

```markdown
@flaws

@card

### Addictive Personality

You chase instant gratification without weighing the consequences. The city always has one more hit on offer.

> "Just one more, and then I'll quit."

@end-card

@end-flaws
```

Result {.dg-result}

<div class="dg-stage">

@flaws

@card

### Addictive Personality

You chase instant gratification without weighing the consequences. The city always has one more hit on offer.

> "Just one more, and then I'll quit."

@end-card

@end-flaws

</div>

The same card under `.dc-ideals` takes the ideal accent:

<div class="dg-stage">

@ideals

@card

### Honor

You believe in a code, and upholding it is your duty no matter the cost.

> "I made a promise to help those in need, and I'll keep it at all costs."

@end-card

@end-ideals

</div>

## Gear

An item entry: a display-face name, an italic tagline of tags, then the mechanics. Separate entries with `---`.

```markdown {.dg-split}
@gear

### Throwaway Blaster

*Ranged. Pistol. CQC Locked, Pack Fed.*

**Range** Reach to Near only. **Damage** 2 on a Hit, 4 on a Triumph. Disposable after the run; serial-clean and untraceable.

@end-gear

---

@gear

### Snake Cable

*Utility. Mechanized. Reach 50 ft.*

A 50-foot length of mechanized links that coils itself, climbs, anchors, or cinches around an object.

@end-gear
```

Result {.dg-result}

<div class="dg-stage">

@gear

### Throwaway Blaster

*Ranged. Pistol. CQC Locked, Pack Fed.*

**Range** Reach to Near only. **Damage** 2 on a Hit, 4 on a Triumph. Disposable after the run; serial-clean and untraceable.

@end-gear

---

@gear

### Snake Cable

*Utility. Mechanized. Reach 50 ft.*

A 50-foot length of mechanized links that coils itself, climbs, anchors, or cinches around an object.

@end-gear

</div>


Gear is a card with an orange rail. The name, the italic tagline and the bold price line are picked out by their shape, and a `@callout gear label="SPECS"` at the foot sits a gap below the body. A long run packs tighter two-up: put the entries in `@columns 2` inside a `@section`. Entries fill the first column, then the second, and a section splits by default, so a run longer than a page breaks between entries. [Gear & Tech](#ch-example-gear-tech) shows gear in columns.


## Tables

Pipe tables carry every lookup: augment slots, weapon lists, roll tables, option tables, NPC statlines. No class, no macro.

```markdown
| Augment | Slot | Cost | Effect |
|---|---|---|---|
| Reflex Booster | Legs | 1,200 | +2 to initiative rolls |
| Subdermal Plating | Torso | 1,800 | Reduce bludgeoning damage by 1 |
| Optic Splice | Head | 900 | Ignore darkness penalties |
```

Result {.dg-result}

<div class="dg-stage">

| Augment | Slot | Cost | Effect |
|---|---|---|---|
| Reflex Booster | Legs | 1,200 | +2 to initiative rolls |
| Subdermal Plating | Torso | 1,800 | Reduce bludgeoning damage by 1 |
| Optic Splice | Head | 900 | Ignore darkness penalties |

</div>

A roll table is the same thing with a `Roll` column:

<div class="dg-stage">

| Roll | Encounter |
|---|---|
| 1–4 | A patchhead swarm picks a fight over nothing |
| 5–8 | A fixer slides into the booth with a dirty envelope |
| 9–12 | A SercDog patrol sweeps the block; lie low or run |
| 13–20 | You find a sealed crate the corps forgot to log |

</div>

## NPC stat block

The narrative form a Dream Master reads aloud: `@npc-stat` with a `####` name, a `>` flavor line, the stat lines, and `#####` sub-headings for traits and equipment.

```markdown
@npc-stat

#### Patchhead

> See a Patchhead comin' at you, you best move. Ain't no reasoning with 'em.

2 HP — 1 Damage
Fodder — Usually Small to Medium

##### Traits

**Bloodlust:** Patchheads add 1 to their Damage whenever they hit a creature that is missing Hit Points.

##### Equipment

Weighted chains, shivs, knuckle dusters; junk shields or crash helmets.

@end-npc-stat
```

Result {.dg-result}

<div class="dg-stage">

@npc-stat

#### Patchhead

> See a Patchhead comin' at you, you best move. Ain't no reasoning with 'em.

2 HP — 1 Damage
Fodder — Usually Small to Medium

##### Traits

**Bloodlust:** Patchheads add 1 to their Damage whenever they hit a creature that is missing Hit Points.

##### Equipment

Weighted chains, shivs, knuckle dusters; junk shields or crash helmets.

@end-npc-stat

</div>

A block with several `####` entries breaks between creatures and never inside one; the title bar stays with the first entry. A block with no `####` is one creature; add `.dc-avoid-split` (`@npc-stat .dc-avoid-split`) to keep it on one page.

To set the entries in columns, put them in `@columns 2` inside the block: the bar and an optional intro stay above, full width.

```markdown
@npc-stat

### Street Crews

Two crews that work the same block.

@columns 2

#### Patchhead

> See a Patchhead comin' at you, you best move.

2 HP — 1 Damage
Fodder — Small to Medium

##### Traits

**Bloodlust:** Patchheads add 1 to their Damage whenever they hit a creature that is missing Hit Points.

#### Grease Monkey

> Hold still, this'll only sting a lot.

3 HP — 1 Damage
Fodder — Medium

##### Traits

**Quick Fix:** A Grease Monkey patches an ally for 1 HP once per scene.

@end-columns

@end-npc-stat
```

Result {.dg-result}

<div class="dg-stage">

@npc-stat

### Street Crews

Two crews that work the same block.

@columns 2

#### Patchhead

> See a Patchhead comin' at you, you best move.

2 HP — 1 Damage
Fodder — Small to Medium

##### Traits

**Bloodlust:** Patchheads add 1 to their Damage whenever they hit a creature that is missing Hit Points.

#### Grease Monkey

> Hold still, this'll only sting a lot.

3 HP — 1 Damage
Fodder — Medium

##### Traits

**Quick Fix:** A Grease Monkey patches an ally for 1 HP once per scene.

@end-columns

@end-npc-stat

</div>

Tokens: `--dc-npc-stat-label-color`, `--dc-npc-stat-primary`, `--dc-npc-stat-secondary`, `--dc-npc-stat-rule`, `--dc-npc-stat-rule-width`.

## Stat grid and at-a-glance cards

Two raw-HTML forms for numbers at a glance. The four-cell stat grid takes combat stats (HP / DEF / AP / DMG) for a creature or social stats (REP / HEAT / FEE / TURN) for a contact; the at-a-glance row is one label and one value per card.

```markdown
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
  <div class="dc-stat-line"><strong>Patch Job:</strong> treats wounds between scenes for FEE × severity.</div>
</div>

@columns 3

<div class="dc-at-a-glance-card"><h4>HP</h4><p>14</p></div>
<div class="dc-at-a-glance-card"><h4>Speed</h4><p>Near</p></div>
<div class="dc-at-a-glance-card"><h4>Heat</h4><p>3</p></div>

@end-columns
```

Result {.dg-result}

<div class="dg-stage">

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
  <div class="dc-stat-line"><strong>Patch Job:</strong> treats wounds between scenes for FEE × severity.</div>
</div>

@columns 3

<div class="dc-at-a-glance-card"><h4>HP</h4><p>14</p></div>
<div class="dc-at-a-glance-card"><h4>Speed</h4><p>Near</p></div>
<div class="dc-at-a-glance-card"><h4>Heat</h4><p>3</p></div>

@end-columns

</div>

## NPC sidebar

A contact capsule floated beside prose: a `.dc-human-callout` inside a raw `.dc-sidebar`.

```markdown
<div class="dc-sidebar"><div class="dc-human-callout">
<p><strong>Vance "Static" Oyelaran</strong> — Fixer</p>
<p>Two cybernetic eyes, owes everyone. <strong>Hook:</strong> the chip is real; the access tunnel on it is bait.</p>
</div></div>
```

Result {.dg-result}

<div class="dg-stage dg-on-paper">

The Dreamers are low on credits and lower on luck when the noodle-stall door swings open. A figure slides into the booth across from them, drops a battered data chip on the table, and waits.

<div class="dc-sidebar"><div class="dc-human-callout">
<p><strong>Vance "Static" Oyelaran</strong> — Fixer</p>
<p>Two cybernetic eyes, owes everyone. <strong>Hook:</strong> the chip is real; the access tunnel on it is bait.</p>
</div></div>

Read the room before you read the chip. A fixer who makes it back out the door clean is a fixer who knew the drone was coming. Either way, the job's already in motion the moment Static sat down.

</div>
