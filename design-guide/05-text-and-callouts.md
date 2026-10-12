@chapter #ch-text .dg-guide ch="5"

@page .dg-doc

Chapter 5 {.dg-kicker}

# Text & Callouts

The components that live inside running prose: the lede that opens a chapter, flavor and pull quotes for in-world voice, the alert family for notes a reader must not miss, and the tape, tags, and roll chip that punctuate a page. {.dg-lede}


## Lede

The opening paragraph of a chapter or major section, set larger on its own panel.

```markdown
@lede

The city didn't go quiet — it got loud. You came to Dimm City to disappear, and instead the whole block learned your name.

@end-lede
```

Result {.dg-result}

<div class="dg-stage">

@lede

The city didn't go quiet — it got loud. You came to Dimm City to disappear, and instead the whole block learned your name.

@end-lede

</div>

Tokens: `--dc-intro-bg`, `--dc-intro-accent`.

## Flavor

In-world voice: italic, accent-railed, spoken from inside the fiction. Inside a `@skill` card the first `>` line is flavor automatically; anywhere else, tag the quote.

```markdown
> [!FLAVOR]
> Down here we don't ask what you were before the grafts. We ask what's left.
```

Result {.dg-result}

<div class="dg-stage">

> [!FLAVOR]
> Down here we don't ask what you were before the grafts. We ask what's left.

</div>

Tokens: `--dc-flavor-accent`, `--dc-flavor-accent-width`, `--dc-flavor-color`.

## Pull quote

A large-format excerpt with rules above and below. One per chapter, to let a single line breathe. The attribution goes after a blank `>` line.

```markdown
> [!PULLQUOTE]
> The rig braces and answers every swing.
>
> Field manual, second draft
```

Result {.dg-result}

<div class="dg-stage">

> [!PULLQUOTE]
> The rig braces and answers every swing.
>
> Field manual, second draft

</div>

Tokens: `--dc-pullquote-accent`, `--dc-pullquote-accent-soft`, `--dc-pullquote-bg`.


## Alerts

One shell, seven registers. Write a GFM alert — a blockquote whose first line is `[!TYPE]` — and the label, color, and rail come with the type. Use the blockquote form for a single paragraph; for several paragraphs, a list, or a custom label, use the `@callout` block below.

```markdown {.dg-split}
> [!NOTE]
> A character may hold no more than one Signature Augment at a time.

> [!WARNING]
> Trauma Patches stabilize a dying character but do not restore HP.

> [!DM]
> If a player hasn't chosen starting gear by the end of session zero, hand them a Scavenger Pack and move on.

> [!VIBE]
> The rain in Dimm City never quite stops — it just changes color under the signage.

> [!ORIGIN]
> You didn't choose the street — the street chose you.

> [!VISIT]
> The Neon Bazaar doesn't close. If you can name it, someone here is selling a knockoff of it two stalls down.

> [!GEAR]
> **Ripper Blades (Mk II)**
>
> Melee. Damage 1d8+STR. *Serrated:* on a critical hit, the target bleeds for 1d4.
```

Result {.dg-result}

<div class="dg-stage dg-tall">

> [!NOTE]
> A character may hold no more than one Signature Augment at a time.

> [!WARNING]
> Trauma Patches stabilize a dying character but do not restore HP.

> [!DM]
> If a player hasn't chosen starting gear by the end of session zero, hand them a Scavenger Pack and move on.

> [!VIBE]
> The rain in Dimm City never quite stops — it just changes color under the signage.

> [!ORIGIN]
> You didn't choose the street — the street chose you.

> [!VISIT]
> The Neon Bazaar doesn't close. If you can name it, someone here is selling a knockoff of it two stalls down.

> [!GEAR]
> **Ripper Blades (Mk II)**
>
> Melee. Damage 1d8+STR. *Serrated:* on a critical hit, the target bleeds for 1d4.

</div>

### Which alert

| Type | Who it is for | Register |
|---|---|---|
| `NOTE` | Players | A rules clarification |
| `WARNING` | Players | A rule with consequences, in amber |
| `DM` | The Dream Master only | Guidance, hooks, adjudication |
| `VIBE` | Players | Atmosphere and narrative voice, full width |
| `ORIGIN` | Players, in second person | Backstory addressed to the character |
| `VISIT` | Players | A location, present tense, before an encounter |
| `GEAR` | Players | A named item: weapon, armor, notable equipment |

Tokens shared by the family: `--dc-alert-bg`, `--dc-alert-border`, `--dc-alert-fg`, `--dc-alert-label-color`, `--dc-alert-border-width`.


## Callout block

The multi-paragraph form of an alert. A variant word after `@callout` picks the register; `label` replaces the default label.

```markdown
@callout warning label="Heat is shared"

**Heat is shared, not personal.** When any member of the crew draws Corporate attention, the whole crew's Heat track ticks up.

At Heat 3, expect a response. At Heat 5, the crew is actively hunted, and every public roll carries a complication.

@end-callout
```

Result {.dg-result}

<div class="dg-stage">

@callout warning label="Heat is shared"

**Heat is shared, not personal.** When any member of the crew draws Corporate attention, the whole crew's Heat track ticks up.

At Heat 3, expect a response. At Heat 5, the crew is actively hunted, and every public roll carries a complication.

@end-callout

</div>

| Option | Values | Default |
|---|---|---|
| a variant word (`@callout vibe`) | `note` `warning` `dm` `vibe` `origin` `visit` `gear` `example` | `note` |
| `label` | any text | the variant's label |

## Worked example

`@callout example` is the one spelling for a worked example: a play example, a sample exchange, a step-by-step. It is never a rule, and it reads that way: a dashed cyan edge, a taped-on label that says *Example*, upright body text. Speech lines stay as `>` lines inside it. (A bare `>` blockquote is reserved for a flavor line.) A longer example can be a `@section`; this is for the short ones that sit inside a section.

```markdown
@callout example

The Dream Master: "The guard turns toward you. What do you do?"

You: "I flip the noodle cart into the doorway." That is risky, so you **ROLL THE DIE!** and get a 14: a Success. The cart blocks the door.

@end-callout
```

Result {.dg-result}

<div class="dg-stage">

@callout example

The Dream Master: "The guard turns toward you. What do you do?"

You: "I flip the noodle cart into the doorway." That is risky, so you **ROLL THE DIE!** and get a 14: a Success. The cart blocks the door.

@end-callout

</div>

A callout can also float beside the text: add `.dc-sidebar` (see [Layout](#ch-layout)).

## Dream Master note

`@dm-note` is shorthand for `@callout dm`, for the longer GM asides — scene setups, adjudication, design notes.

```markdown
@dm-note label="Running the Setup"

The fixer offering this job doesn't know it's bait — they're a cut-out, paid to pass the contract along and ask no questions.

If the players investigate before accepting, they can smell the trap with a Streetwise roll, DC 14.

@end-dm-note
```

Result {.dg-result}

<div class="dg-stage">

@dm-note label="Running the Setup"

The fixer offering this job doesn't know it's bait — they're a cut-out, paid to pass the contract along and ask no questions.

If the players investigate before accepting, they can smell the trap with a Streetwise roll, DC 14.

@end-dm-note

</div>


## Tape

A torn-tape strip for a section break or a label between groups — tiers of NPCs, parts of a list.

```markdown
<div class="dc-tape">Operators</div>
```

Result {.dg-result}

<div class="dg-stage">

<div class="dc-tape">Operators</div>

</div>

Tokens: `--dc-tape-bg`, `--dc-tape-border`, `--dc-tape-color`. Add `dc-flush` (`<div class="dc-tape dc-flush">Label</div>`) to run it edge to edge.

## Dashed rule

A plain `---` between entries is a red dashed rule — the separator for gear lists and NPC entries.

```markdown
Trauma Kit × 2

---

Signal Jammer (single-use)
```

Result {.dg-result}

<div class="dg-stage dg-on-paper">

Trauma Kit × 2

---

Signal Jammer (single-use)

</div>

## Tags and class tags

Inline pills. `.dc-tag` is a keyword or cost label; `.dc-classtag.<specialty>` is a specialty identity with that specialty's dot. These are raw HTML spans — the one place the system asks for it inline.

```markdown
<span class="dc-tag">Melee</span> <span class="dc-tag">Reach 2</span> <span class="dc-tag">Loud</span>

<span class="dc-classtag augmerc">Augmerc</span> <span class="dc-classtag wirephreak">Wirephreak</span>
```

Result {.dg-result}

<div class="dg-stage dg-on-paper">

<span class="dc-tag">Melee</span> <span class="dc-tag">Reach 2</span> <span class="dc-tag">Loud</span>

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

</div>

## Roll the die

The text `ROLL THE DIE!` in prose becomes the die chip automatically, and so do `ROLL A DIE!`, `ROLLS A DIE!` and `ROLLING THE DIE!`: uppercase, with the exclamation mark, as written. Inside a code span, raw HTML or a heading it is left alone. The chip is set inside the line and never splits across two, so it never makes a line taller.

```markdown
When an ability says ROLL THE DIE!, roll a d20 and read the outcome ladder. A trap may say ROLL A DIE! or ROLLING THE DIE! instead.
```

Result {.dg-result}

<div class="dg-stage dg-on-paper">

When an ability says ROLL THE DIE!, roll a d20 and read the outcome ladder. A trap may say ROLL A DIE! or ROLLING THE DIE! instead.

</div>

Tokens: `--dc-roll-the-die-color`, `--dc-roll-the-die-border`.
