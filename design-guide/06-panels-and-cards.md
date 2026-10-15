@chapter #ch-panels .dg-guide ch="6"

@page .dg-doc

Chapter 6 {.dg-kicker}

# Panels, Cards & Data

The enclosures: the section variants and the kinds of text they hold, three block registers, definition and glossary forms, the numbered procedure, the outcome ladder and roll tables, choice cards, item entries (gear, augments, treasure, vehicles, drugs), fields, catalogs, factions, tables, and the stat blocks a Dream Master runs from. {.dg-lede}


## Section

A `@section` groups what is inside it. Bare, it is core's plain box: no look of its own beyond a sheet of paper under the text (no text is ever set straight on the wall); a word after it picks the look. Two are general and work anywhere, and four more say what kind of text they hold ([below](#kinds-of-text)). Sections split across pages by default; `.dc-avoid-split` keeps one whole. One accent knob, `--dc-section-accent`, colours a panel's rail and title bar. For the named components (`@npc-stat`, `@gear`, `@outcome` and the rest), [Pick a section](#ch-start) maps what you are writing to the marker.

```markdown {.dg-split}
@section panel

## Rules Panel

The card: a cream substrate, an accent rail, a clipped corner, a shadow, and the first `##` or `###` as a title bar.

@end-section

@section flat

The rail on a plain host, for text that should read as a continuation of the page.

@end-section

@section

A bare section: no look of its own. The text sits on a plain sheet of paper.

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

</div>

<div class="dg-stage dg-on-paper">

@section

A bare section: no look of its own. The text sits on a plain sheet of paper.

@end-section

</div>

`panel` is the look for rules text with a heading; `.dc-avoid-split` on it keeps a short panel on one page. For a short note set off from the text, use [`@callout`](#ch-text). Tokens: `--dc-section-bg`, `--dc-section-accent`, `--dc-section-pad-top`, `-right`, `-bottom`, `-left`, and for `panel` also `--dc-section-surface` and `--dc-section-shadow` (`none` removes the layer).

The components below that are sections have a marker of their own and a word on `@section`: `@npc-stat` (`npc`), `@fiction-excerpt` (`fiction`), `@citizen-walkthrough` (`walkthrough`), `@card-grid` (`cards`), `@flaws`, `@ideals` and `@dreams`.

## Kinds of text {#kinds-of-text}

`reference`, `lore`, `dm` and `choose` are panels that say what kind of text they hold, so a reader can tell a look-up from a rule from the world from advice for the Dream Master at a glance, in any chapter, in colour and in grayscale. Each cuts its own corners, as the skill cards do per specialty (a panel one larger chamfer, a reference four small even ones, lore long asymmetric slashes, dm a file-folder tab, choose ticket notches), and each has its own bar and sheet: a panel's bar is solid accent on cream, a reference's is a pale band, lore is deep violet, dm is ink with a cyan rule, and choose has no bar at all. The shape, the bar and the sheet say which kind it is before the colour does. Each has a word on `@section` and nothing else to learn: write the heading and the content as you would in a panel.

| You are writing | Write | Looks like |
|---|---|---|
| A table or list to look up: prices, conditions, a menu of options | `@section reference` | HUD blue, a pale title band ruled in ink above (a heavy inset rule) and below (a double rule) like a machined spec-sheet header, 10pt tight rows, four small even chamfers |
| The world, not the rules: places, factions' history, setting | `@section lore` | A deep violet bar with a slashed top-left corner and a torn top edge over a pale lilac sheet, long asymmetric slashes (shallow at the top left, steep at the bottom right), italic sub-heads |
| Advice for the Dream Master, behind the screen | `@section dm` | A classified file folder: an ink tab in the box's top band that carries the words *Dream Master* in cyan (it never splits from the box at a page break), an ink title bar with a cyan rule and a cyan rail over a cold concrete body, and one opposite corner cut (bottom right). The tab is drawn with or without a heading |
| A choice the player writes on the Citizen File | `@section choose` | A printed form, not a panel: a paper sheet a hair lighter than cream, sunk into the wall in an ink edge cut like a ticket (a V punched in the middle of each side, a perforated foot), no bar, an ink title over a double rule in the chapter's accent, dotted write-in rules, heavy ink tick boxes and a yellow *Your choice* stamp |

```markdown {.dg-split}
@section reference

## Street Prices

| Item | Cost |
| --- | --- |
| Noodle voucher | 2 DC |
| Signal flare | 15 DC |

- Prices are for a Tuesday. Ask the fixer on a Friday.

@end-section

@section lore

## The Lower Monoverse

Where the city keeps what it would rather forget: dripping pipework, dead billboards, and neighbours who still wave.

@end-section

@section dm

## Running a Chase

Keep the pressure on. Let the dice say who gets away, and let the city complicate it.

@end-section

@section choose

## Pick a Quirk

- Hums when nervous.
- Never sits with their back to a door.
- Collects bus tickets.

@end-section
```

Result {.dg-result}

<div class="dg-stage dg-tall">

@section reference

## Street Prices

| Item | Cost |
| --- | --- |
| Noodle voucher | 2 DC |
| Signal flare | 15 DC |

- Prices are for a Tuesday. Ask the fixer on a Friday.

@end-section

@section lore

## The Lower Monoverse

Where the city keeps what it would rather forget: dripping pipework, dead billboards, and neighbours who still wave.

@end-section

@section dm

## Running a Chase

Keep the pressure on. Let the dice say who gets away, and let the city complicate it.

@end-section

@section choose

## Pick a Quirk

- Hums when nervous.
- Never sits with their back to a door.
- Collects bus tickets.

@end-section

</div>

`@flaws`, `@ideals` and `@dreams` are `choose` sections that hold a run of `@card` (below); with no heading they draw nothing around the cards, which carry the look. The kind wins over the chapter: a `reference` panel stays HUD blue in a rust chapter, and `choose` takes the chapter's accent only for its title rule and tick boxes. Tokens are the section's own (`--dc-section-accent`, `--dc-section-bg`, and for the panel kinds `--dc-section-clip`, `--dc-section-rail`; a `choose` form has no cut corners or rail) plus the chip: `--dc-section-tab` (its text, `none` for no chip), `--dc-section-tab-bg` (yellow on `choose`) and `--dc-section-tab-fg`.

## Fiction excerpt

Fiction, lore, a chapter-opening story. An aged page sunk into the wall, or revealed from behind it: a dark ragged hole torn in the wall with the page sitting back inside it, the hole casting a hard shadow down the page's top and left and a light lip catching on its bottom and right, no rail, no title bar, narrative leading, and the first image floats left. On a chapter-start page the hole is deeper (a 10px shadow instead of 6px).

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

Tokens: `--dc-fiction-bg` (the page), `--dc-fiction-line-height`, `--dc-fiction-depth` (the cast shadow's depth, 6px) and `--dc-fiction-depth-bg` (its colour), `--dc-fiction-cavity` (the hole's rim), `--dc-fiction-lip`, `--dc-fiction-rim` (how far the hole reaches past the page), `--dc-fiction-shape` (the page) and `--dc-fiction-hole` (the torn cavity), `--dc-fiction-rule` (an ink edge weight on the page, 0), `--dc-fiction-shadow` (an extra box-shadow on the page), `--dc-fiction-art-float`, `--dc-fiction-art-width`.

## Block

One macro, three registers. The class on the opener picks the silhouette and surface; `label` fills the title band and can be omitted.

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
| `.dc-panel` | HUD blue band, symmetric hex chamfers | Player-facing rules summaries, structured data |
| `.dc-slate` | A sign plate: octagonal corners in a heavy crimson frame, ink body, a blood band with a crimson rule and a stamped (double-edged) *Binding* tag | Binding rulings, Dream Master directives |
| `.dc-shard` | Light zine paper, a torn foot and a dog-eared corner, a taupe label strip, no accent hue | Fiction, atmosphere, setting asides |

The fourth register, `.dc-codex` (look-ups and glossaries), is retired: write a look-up as [`@section reference`](#kinds-of-text), a small box inside a section as `@block panel`, and a glossary as an `@definition` run.

<div class="dg-stage">

@block .dc-slate label="The Core Loop"

1. The **Dream Master** presents a situation.
2. The **Dreamers** declare intent.
3. The **fiction resolves** — sometimes on a die, sometimes on a word.

@end-block

@block .dc-shard label="The Neon Bazaar"

Hologram haze cuts the gloom you're stumbling through. Flickering ads claw the air above blades of neon, and the scent of burnt oil rides over hot garbage.

@end-block

</div>

Tokens: `--dc-block-bg`, `--dc-block-fg`, `--dc-block-accent`, `--dc-block-title-bg`, `--dc-block-title-fg`, `--dc-block-title-rule` (a whole `border-bottom` under the band), `--dc-block-tag` (a quoted word stamped on the band) and `--dc-block-tag-edge` (its border).


## Definition

A short dictionary-style entry for a term: in-world vocabulary, an NPC type, an item category. It is a cream page with a heavy rule over it and a hairline under it, the term set first as a blue headword, and the body in italic. Stack several in an `@columns 2` run for a glossary of entries, or put a run of `#### Term` entries in one `@definition` and it reads as a glossary: each term is a display-caps headword in blue, with a rule between entries. A `---` inside is the same rule, and a bold lead (`**Term** — gloss`) needs nothing.

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

### A glossary

```markdown
@definition

#### Heat

The running tally of attention you've drawn.

#### Hard Choice

A roll of 6–10. The fiction advances, but it costs you.

#### Twitch

An ability you use outside your turn when its trigger happens.

@end-definition
```

Result {.dg-result}

<div class="dg-stage">

@definition

#### Heat

The running tally of attention you've drawn.

#### Hard Choice

A roll of 6–10. The fiction advances, but it costs you.

#### Twitch

An ability you use outside your turn when its trigger happens.

@end-definition

</div>

A box with its own heading and a divider is the same thing:

```markdown
@definition

#### Dice Etiquette

---

Roll your dice in the open. If a die lands off the table, it doesn't count: reroll it.

@end-definition
```

### Lucid and Surreal

The two states of a roll get a definition each, one word on the marker, and they are drawn as opposites so a reader can tell them apart across the table. `@definition lucid` is sharp, aligned and in control: the lightest sheet, four even machined chamfers, a blue frame with a cyan hairline inside it, upright type and a headword ruled off in blue. `@definition surreal` is reality pushing back: an inverted, violet-black sheet with light type, a skewed outline torn along the foot, two inks (magenta and violet) off-register on opposite inner edges and a leaning headword. They differ in value, edge and type, so they stay opposites in greyscale. The body text is never rotated: only the headword leans.

```markdown
@definition lucid

#### Lucid

Roll 2d20, take the higher. You're sharp, aligned, in control.

@end-definition

@definition surreal

#### Surreal

Roll 2d20, take the lower. Reality pushes back.

@end-definition
```

Result {.dg-result}

<div class="dg-stage">

@columns 2

@definition lucid

#### Lucid

Roll 2d20, take the higher. You're sharp, aligned, in control.

@end-definition

@column-break

@definition surreal

#### Surreal

Roll 2d20, take the lower. Reality pushes back.

@end-definition

@end-columns

</div>

Tokens: `--dc-definition-block-surface`, `--dc-definition-block-accent` (the rules), `--dc-definition-block-term` (the headword), `--dc-definition-block-accent-width` and `--dc-definition-block-rule-bottom` (the rules' weights; 0 for lucid and surreal), `--dc-definition-block-shape` (the silhouette; none by default), `--dc-definition-block-fg`, `--dc-definition-block-style`, `--dc-definition-block-frame` (the hard shadow, or an inset frame) and `--dc-definition-block-pad`. For a plain term list, a markdown definition list (`Term` / `: meaning`) needs no macro — see [Writing a Page](#ch-writing).

## Procedure

A numbered instruction plate for anything the table runs in order: a cream plate with an ink frame and a hard shadow, a solid HUD-blue number strip down the left, 10pt ink step text with bold leads, ruled dividers, and a staple holding the plate to the wall. It sits on its own paper, never on the wall. The list may break between steps; a step is never cut.

Tokens: `--dc-steps-accent` (the number strip), `--dc-steps-surface` (the plate).

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

The chip column is a quarter of the ladder wide (never under 130px), so a long band name wraps on two or three lines instead of cramping; band names are 10pt semibold, centred.

Tokens: `--dc-outcomes-surface`, `--dc-outcomes-border`, `--dc-outcomes-label-bg`, `--dc-outcomes-label-color`, `--dc-outcome-key-color`, `--dc-outcome-name-color`, `--dc-outcome-key-col` (the chip column's width).

### A table of the five bands is the ladder

Write the result table you would write anyway. A two-column pipe table whose first column holds exactly the five standard bands (`20`, `11-19`, `6-10`, `2-5`, `1`, in either order) is drawn as the same ladder, in a skill card or anywhere else. The headers do not decide it (`Roll | Result`, `Result | Effect`, or empty); the ladder shows them in its label bar, over the two columns, and an empty header reads "Outcomes". A band is read however it is typed: `11-19`, `11 – 19`, `**20**`. Any other set of bands (six bands, a split at 10) is not a ladder, and stays a plain table: for those, use `@roll-table` below.

```markdown
| Roll | Result |
| --- | --- |
| 20 | The jammed door gives. Something comes with it. |
| 11–19 | The door opens. |
| 6–10 | It opens, loudly. |
| 2–5 | It holds. |
| 1 | The handle comes off in your hand. |
```

Result {.dg-result}

<div class="dg-stage">

| Roll | Result |
| --- | --- |
| 20 | The jammed door gives. Something comes with it. |
| 11–19 | The door opens. |
| 6–10 | It opens, loudly. |
| 2–5 | It holds. |
| 1 | The handle comes off in your hand. |

</div>

## Roll table

A random table that is not the ladder: one die, equal-weight rows, no tier colours. Wrap a pipe table in `@roll-table`; `label` names it and `die` picks the die on the chip (`d20` when you write none). Put the range in the first column (`1-4`, `5-8`, ...) and the result in the second.

```markdown
@roll-table label="Pocket Lint" die=d20

| Roll | Result |
| --- | --- |
| 1-4 | A bent key that opens nothing nearby. |
| 5-8 | Half a noodle voucher, still valid. |
| 9-12 | A dead earbud with a name scratched in. |
| 13-16 | A folded map of a different district. |
| 17-20 | A battered signal flare. |

@end-roll-table
```

Result {.dg-result}

<div class="dg-stage">

@roll-table label="Pocket Lint" die=d20

| Roll | Result |
| --- | --- |
| 1-4 | A bent key that opens nothing nearby. |
| 5-8 | Half a noodle voucher, still valid. |
| 9-12 | A dead earbud with a name scratched in. |
| 13-16 | A folded map of a different district. |
| 17-20 | A battered signal flare. |

@end-roll-table

</div>

Tokens: `--dc-roll-table-accent` (frame, caption and range rule), `--dc-roll-table-surface`, `--dc-roll-table-head-bg`.



## Card

A choice card: heading, body, and a closing quote that becomes the card's footer. Wrap a run of cards in `@flaws`, `@ideals` or `@dreams` for that step of character creation: each kind has its own colour, silhouette and a one-word chip. A Flaw is blood with a cracked edge, an Ideal is HUD blue with a steady ticket-stub shape (a V punched out of each side), a Dream is violet with a rising edge and a perforated foot. The heading is the first `####`: core turns only a `####` into the card's heading, so write `####`.

```markdown
@flaws

@card

#### Addictive Personality

You chase instant gratification without weighing the consequences. The city always has one more hit on offer.

> "Just one more, and then I'll quit."

@end-card

@end-flaws
```

Result {.dg-result}

<div class="dg-stage">

@flaws

@card

#### Addictive Personality

You chase instant gratification without weighing the consequences. The city always has one more hit on offer.

> "Just one more, and then I'll quit."

@end-card

@end-flaws

</div>

The same card under `@ideals` is an ideal: HUD blue, a steady tablet:

<div class="dg-stage">

@ideals

@card

#### Honor

You believe in a code, and upholding it is your duty no matter the cost.

> "I made a promise to help those in need, and I'll keep it at all costs."

@end-card

@end-ideals

</div>

## Gear and its kinds

An item entry is a card with a name and the item's prose. It is one marker, `@gear`, and a bare word on the marker line picks the kind, so a book's catalog can tell them apart at a glance: `@gear` alone for general gear, `@gear augment` for cybernetics and mods, `@gear treasure` for magic items and relics, `@gear vehicle`, and `@gear drug` for drugs, elixirs and other consumables. Each kind has its own silhouette, surface, badge and name colour, so a reader knows what an entry is before reading it, and in grayscale: gear is a hang tag (a paper card in a heavy ink frame, a rust rail, an eyelet), an augment is a spec chip (a pale plate, a stepped notch, a cyan rule, a teal name), treasure is a gem (violet, an eight-sided cut, a facet), a vehicle is an industrial plate (octagonal cut corners, a heavy ink frame, a dotted seam of rivets, a yellow badge) and a drug is a prescription label (a wobbling organic outline, lime, an *Rx · Drug* pill). The kind badge is added for you; then your markdown. The name is the first `####` heading (`###` works too). A blockquote straight under it is the tagline.

```markdown {.dg-split}
@gear augment

#### Kestrel Optics

> Sees what you would rather not.

Two lenses in the orbit, a thermal layer, and a tiny voice that names what it sees. The chrome is rated for rain, not for sentiment.

**SPECS:** See in the dark to Far range. +1 to spot rolls. Needs a Neurolink to run the overlay.

@end-gear

@gear treasure

#### Lantern of Second Thoughts

> A brass lantern with a very honest flame.

Whoever carries it hears the doubts of anyone standing in its light.

- **Rewind:** Once per cycle, take back one thing you just said.
- **Fast Forward:** Skip a conversation that was going nowhere.

@end-gear

@gear vehicle

#### Skyskiff Courier

> Two seats, one fuel cell, no questions.

A ducted-fan runabout built for rooftops and bad ideas.

**SPECS:** IL: 3. Durability: 10. Mod Slots: 2.

@end-gear

@gear drug

#### Slowglass

A pale syrup sold in thimbles. The world gets quiet and a little too clear.

**Effects:** Reroll one failed roll this scene.

**Side Effects:** The next cycle begins with a Tough Choice you did not ask for.

@end-gear
```

Result {.dg-result}

<div class="dg-stage">

@gear augment

#### Kestrel Optics

> Sees what you would rather not.

Two lenses in the orbit, a thermal layer, and a tiny voice that names what it sees. The chrome is rated for rain, not for sentiment.

**SPECS:** See in the dark to Far range. +1 to spot rolls. Needs a Neurolink to run the overlay.

@end-gear

@gear treasure

#### Lantern of Second Thoughts

> A brass lantern with a very honest flame.

Whoever carries it hears the doubts of anyone standing in its light.

- **Rewind:** Once per cycle, take back one thing you just said.
- **Fast Forward:** Skip a conversation that was going nowhere.

@end-gear

@gear vehicle

#### Skyskiff Courier

> Two seats, one fuel cell, no questions.

A ducted-fan runabout built for rooftops and bad ideas.

**SPECS:** IL: 3. Durability: 10. Mod Slots: 2.

@end-gear

@gear drug

#### Slowglass

A pale syrup sold in thimbles. The world gets quiet and a little too clear.

**Effects:** Reroll one failed roll this scene.

**Side Effects:** The next cycle begins with a Tough Choice you did not ask for.

@end-gear

</div>

A `@gear` after another `@gear` closes the first, so a run needs an `@end-gear` only after the last entry. An entry with no name, or with two, is reported as a problem, and a word that is not one of the four kinds is reported and read as general gear. General gear keeps its own shape: an italic tagline paragraph and a bold price line, picked out by their shape (the price line is stamped as a dashed price tag).

```markdown {.dg-split}
@gear

### Throwaway Blaster

*Ranged. Pistol. CQC Locked, Pack Fed.*

**Range** Reach to Near only. **Damage** 2 on a Hit, 4 on a Triumph. Disposable after the run; serial-clean and untraceable.

@end-gear
```

Result {.dg-result}

<div class="dg-stage">

@gear

### Throwaway Blaster

*Ranged. Pistol. CQC Locked, Pack Fed.*

**Range** Reach to Near only. **Damage** 2 on a Hit, 4 on a Triumph. Disposable after the run; serial-clean and untraceable.

@end-gear

</div>

Tokens: `--dc-entry-accent` (rail), `--dc-entry-ink` (name), `--dc-entry-surface`, `--dc-entry-rail`, `--dc-entry-rule`, `--dc-entry-kind` (the badge word, a quoted string or `none`), `--dc-entry-shape` (the silhouette), `--dc-entry-radius`, `--dc-entry-ornament` with `--dc-entry-orn-inset`, `-orn-bg`, `-orn-border`, `-orn-clip` and `-orn-z` (the kind's solid-fill ornament layer: a treasure's facet, a vehicle's rivets), `--dc-entry-frame`, `--dc-entry-badge-bg`, `--dc-entry-badge-fg`, `--dc-entry-badge-shape`, `--dc-entry-badge-radius`.

### Fields

A field is a labelled line of an entry: its rules, its traits, what a drug does and costs, what a power needs. Write `@field` with a variant word, and the variant's name is the label; `label="…"` replaces it, as with `@callout`.

| Variant | Default label | Look |
|---|---|---|
| `specs` | SPECS | the boxed rules strip: dark, with a yellow rail |
| `traits` | Traits | a plain line under a chip |
| `equipment` | Equipment | the same, in grey |
| `effects` | Effects | a solid teal frame on a pale teal ground, a + on the chip: the benefit; sits over side effects |
| `side-effects` | Side Effects | a dashed blood frame on a pale blood ground, a – on the chip: the cost |
| `requires` | Requires | a grey requirement bar |

```markdown {.dg-split}
@field specs

Rolls of 19-20 are a Triumph while the lenses are tuned.

@end-field

@field requires label="Instrument"

A disposable injector kit.

@end-field
```

Result {.dg-result}

<div class="dg-stage">

@field specs

Rolls of 19-20 are a Triumph while the lenses are tuned.

@end-field

@field requires label="Instrument"

A disposable injector kit.

@end-field

</div>

You rarely need to type it. Inside an entry card, an `@npc-stat` and a `@skill`, a paragraph that opens with one of the labels the books already use is the same field: `**SPECS:**`, `**Traits:**`, `**Equipment:**`, `**Effects:**`, `**Side Effects:**`, `**Requires:**`, `**Wirephreak Gear:**`, `**Cybersurgeon Instrument:**` (also `Instruments` and `Instrument(s)`) and `**TECHNOENHANCEMENT:**`, in any case, with the colon inside the bold. The label stays in your own words. Anywhere else the paragraph is a paragraph. A label on its own line is a bare chip over the paragraph that follows. The list of labels is one table in `plugin.js`.

### Catalog

A run of entries goes in a `@section catalog`: a panel with a title bar and an intro, whose entries are ruled instead of boxed. The title bar is a pale ledger band with an *Inventory* chip, not an accent bar, and an entry never splits across a column or a page. Each entry takes a rule in its own accent colour over it, so there is no `---` between entries (one left in draws nothing). Put the entries in `@columns 2` under the intro, as for any column run.

```markdown {.dg-split}
@section catalog

## Optics and Ears

A short intro for the run.

@columns 2

@gear augment

#### Kestrel Optics

Two lenses, a thermal layer and a quiet voice.

**SPECS:** See in the dark to Far range.

@gear augment

#### Pinhole Ears

Hears a coin drop two rooms away.

**SPECS:** +1 to listen rolls.

@gear augment

#### Sable Voicebox

A voice that is never quite yours.

**SPECS:** Change your voice at will.

@end-columns

@end-section
```

Result {.dg-result}

<div class="dg-stage">

@section catalog

## Optics and Ears

A short intro for the run.

@columns 2

@gear augment

#### Kestrel Optics

Two lenses, a thermal layer and a quiet voice.

**SPECS:** See in the dark to Far range.

@gear augment

#### Pinhole Ears

Hears a coin drop two rooms away.

**SPECS:** +1 to listen rolls.

@gear augment

#### Sable Voicebox

A voice that is never quite yours.

**SPECS:** Change your voice at will.

@end-columns

@end-section

</div>

## Faction

An organization's profile: a card with a kind badge. The kind is the bare word: `megacorp`, `cabal`, `cult` or `enforcer`, and each has its own silhouette, top band, name colour and badge: megacorp a machined blue rectangle (an L-shaped step out of two corners) with a cyan edge, cabal violet with long asymmetric slashes, cult blood and torn along the top and foot with a broken rail, enforcer a sign plate (an octagon in a heavy frame) with a hazard-tape band and a yellow name label. `label="…"` names a badge of your own; with no word there is no badge. Write the name as a `####` heading, then the fields and prose as you would anyway.

```markdown {.dg-split}
@faction megacorp

#### Halcyon Reach Holdings

**HQ:** Tech District. **Led by:** Orla Vantine.

They own the lights and the water and would like to own the rest.

@end-faction

@faction cult

#### The Church of Static

Sing the signal and the signal sings back.

@end-faction
```

Result {.dg-result}

<div class="dg-stage">

@faction megacorp

#### Halcyon Reach Holdings

**HQ:** Tech District. **Led by:** Orla Vantine.

They own the lights and the water and would like to own the rest.

@end-faction

@faction cabal

#### The Quiet Table

A back booth, a rotating guest list, and a very long memory.

@end-faction

@faction cult

#### The Church of Static

Sing the signal and the signal sings back.

@end-faction

@faction enforcer

#### Blue Line Wardens

They keep the peace, for a fee.

@end-faction

</div>

Tokens: `--dc-faction-accent` (the rail and the badge fill), `--dc-faction-badge-fg`, `--dc-faction-shape`, `--dc-faction-surface`, `--dc-faction-band` (a box-shadow list: solid inset bands, so it prints as vector ink), `--dc-faction-band-height`, `--dc-faction-pad-bottom`, `--dc-faction-badge-shape`, `--dc-faction-title` (the name colour) and `--dc-faction-title-bg` / `-title-pad` (a label behind the name); a kind class sets them.

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

The narrative form a Dream Master reads aloud: `@npc-stat` with a `####` name, a `>` flavor line, the stat lines, and `#####` sub-headings for traits and equipment. The flavor line is a ruled line (a rail in the block's rule colour), not a box. The stat lines are picked by position: the first paragraph after the `>` is the primary line, set as a chip (its first line 12pt bold, cream on the block's colour), and a second line in it (or the next paragraph) is the secondary, a small-caps tag (10pt); no markup is needed, `2 HP — 1 Damage` over `Fodder — Medium` is the whole convention. A description belongs inside the quote, not between the quote and the stat lines.

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

A block with several `####` entries breaks between creatures and never inside one; the title bar stays with the first entry. A block with no `####`, or one, is one creature, and it stays on one page by itself; `--dc-npc-stat-break-inside: auto` lets one split.

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

### Compact: a small creature, a companion, a drone

`@npc-stat compact` is the same entry, packed: no panel, a framed box, a small name, and the two stat lines drawn as chips side by side. Use it for the small ones, in a run or in `@columns 2`.

```markdown
@npc-stat compact

#### Beacon Bug

> A thumb-sized surveillance drone made of living glass.

1 HP — 1 Damage

Fodder — Tiny

##### Traits

**Climb, Jump, Invisible.** Unless it moves, your eyes slide right past it.

@end-npc-stat
```

Result {.dg-result}

<div class="dg-stage">

@npc-stat compact

#### Beacon Bug

> A thumb-sized surveillance drone made of living glass.

1 HP — 1 Damage

Fodder — Tiny

##### Traits

**Climb, Jump, Invisible.** Unless it moves, your eyes slide right past it.

@end-npc-stat

</div>

### The stat strip

A table with an **HP** column and a **Damage** column is a creature's stat line, and it is set as a strip wherever it sits: no marker, no change to the table. A cell that holds only a number (`1`, `20`) is set large and centred. This is what to write for a creature inside a skill's ability text, where a section marker such as `@npc-stat compact` would end the skill.

```markdown
| Name | HP | Damage | Traits |
|------|:--:|:------:|--------|
| Beacon Bug | 1 | 1 | Climb, Jump, Invisible |
```

Result {.dg-result}

<div class="dg-stage">

| Name | HP | Damage | Traits |
|------|:--:|:------:|--------|
| Beacon Bug | 1 | 1 | Climb, Jump, Invisible |

| Type | Size | HP | Damage |
|---|---|:---:|:---:|
| Operator | Small/Medium | 4 | 2 |

</div>

Tokens: `--dc-stat-strip-accent` (frame and label band), `--dc-stat-strip-value` (the big numbers).

## Stat grid and at-a-glance cards

Two raw-HTML forms for numbers at a glance. The four-cell stat grid takes combat stats (HP / DEF / AP / DMG) for a creature or social stats (REP / HEAT / FEE / TURN) for a contact; the at-a-glance row is one reversed label band over one big value per tile, with an ink frame and a hard shadow. Tokens for the tile: `--dc-at-a-glance-accent` (frame and label band), `--dc-at-a-glance-value`.

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

A contact card floated beside prose: a `.dc-human-callout` inside a raw `.dc-sidebar`. It has a blue ID header band reading *Contact*, an ink border, a hard shadow and a solid ink strip foot.

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
