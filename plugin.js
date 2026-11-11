/**
 * Dimm City — the gp-dimm-city Gutterpress plugin (server-side markdown-it)
 *
 * IMPORTANT: This plugin only transforms content marked with special markers.
 * Regular markdown content passes through unchanged.
 *
 * DECLARED MARKERS (the `markers` export at the bottom of this file — core
 * Gutterpress parses, nests, closes and source-maps these; this file only
 * names the element, classes and variants). Each also has an `@end-<name>`:
 *   @definition [lucid|surreal] → div.dc-prose-panel.dc-definition-block (a term, or a run of `####` terms); the word is the roll's state, drawn as opposites
 *   @faction [megacorp|cabal|cult|enforcer]
 *                        → div.dc-card.dc-faction[.dc-faction-<kind>] + span.dc-faction-kind
 *   @roll-table [die=d20] [label="…"]
 *                        → div.dc-roll-table + div.dc-roll-table-caption, over the author's table
 *   @specialty-intro     → div.dc-specialty-intro
 *   @specialty-art       → div.dc-specialty-art (full-bleed art panel)
 *   @specialty-card      → div.dc-specialty-card[data-position=odd|even]
 *   @gear [augment|treasure|vehicle|drug|program]
 *                        → div.dc-card.dc-entry.dc-gear (general gear), or
 *                          div.dc-card.dc-entry.dc-<kind>: augment (cybernetics, mods),
 *                          treasure (magic items, relics), vehicle, drug (drugs,
 *                          elixirs, consumables), program (deck software: a data cartridge)
 *   @toc                 → div.dc-toc
 *   @lede                → div.dc-intro
 *   @block [panel|slate|shard] label="Title"
 *                        → div.dc-block.dc-<variant> + div.dc-block-title
 *                          (`@block .dc-panel` class form works too)
 *
 * DECLARED, THEN TRANSFORMED (declared in `markers`, so core opens, nests and
 * closes them; core rules below rewrite what sits between the open and close
 * token — see forEachComponent):
 *   @specialty [name]    → div.dc-specialty.<name>  (`@specialty augmerc` and
 *                          `@specialty .augmerc` are the same; names in
 *                          SPECIALTIES, styled by `.dc-specialty.<name>`)
 *   @learning-path       → div.dc-learning-path.dc-path-block[data-path-ref]
 *                          > div.dc-path-shell (title, subtitle, stickers) + skills
 *   @skill               → one div.dc-skill-card per `####` heading
 *   @card                → div.dc-card > .dc-card-heading (first ####),
 *                          .dc-card-pull (a quote right after it), .dc-card-body
 *                          (the rest; its last blockquote is .dc-card-footer)
 *   @ladder              → div.dc-ladder: a run of `###` rungs whose headings end in an
 *                          outcome band, `### Triumphs (20)`; each is div.dc-rung.<tier>
 *                          > h3.dc-rung-title (the tier's chip) + div.dc-rung-body
 *   @outcome [flush]     → div.dc-outcomes[.dc-flush]: the d20 ladder, one row
 *                          per `roll | name | text` line (crit, hit, mixed, miss, fail)
 *   @procedure           → ol.dc-steps: each numbered list inside becomes the
 *                          zero-padded step list (the wrapper renders nothing)
 *   @callout [variant]   → div.dc-alert.<variant class> > span.dc-alert-label.
 *                          Variants (bare word): note, warning, dm, vibe, origin,
 *                          location, visit, example; none is a note. The label is `label="…"`,
 *                          or the variant's name. `@dm-note` is `@callout dm`
 *                          (an alias). `variant=` is gone: validate reports it.
 *   Core's nesting rule is the only one: a declared marker that is already
 *   open is closed (with everything inside it) when it opens again;
 *   `@end-<name>` closes that marker and what is inside it; `@page`,
 *   `@section`, `@chapter` and `@continue` close them all. The structure
 *   rules (a skill belongs in a path, a path in a specialty, an outcome is
 *   made of rows, a procedure of a numbered list) are the plugin's:
 *   the `validate` of each declaration.
 *
 * THE REST OF WHAT THIS FILE DOES (plain markdown-it rules, no markers):
 *   @continue           → Continuation marker — inside a skill's card it emits a
 *                          card with a "{name} ▸" tab so an oversized skill card
 *                          can be split across pages while keeping a visible link
 *                          to its origin card (dcContinueClassifier claims it
 *                          before core's layout transform; anywhere else it is
 *                          core's section continuation)
 *   `ROLL THE DIE!` (also ROLL A DIE!, ROLLS A DIE!, ROLLING THE DIE!, ROLL THE DIE TWICE!, ROLL TWO DICE!)
 *                        → span.dc-roll-the-die
 *   an image-only paragraph gets p.dc-img-wrapper
 *   the h1 under `@page intro | credits | contents` gets .dc-chevron
 *   a table of the five standard bands is the outcome ladder (it keeps the
 *                          table's `{#id .class}`); `@procedure` keeps the
 *                          attributes written on its line, on its list
 *
 * GFM ALERT SYNTAX:
 *   `> [!NOTE]` / `[!WARNING]` / `[!DM]` / `[!VIBE]` / `[!ORIGIN]` / `[!LOCATION]` / `[!VISIT]`
 *   / `[!FLAVOR]` / `[!PULLQUOTE]` blockquotes are transformed
 *   into `<div class="dc-alert dc-<type>">`.
 *
 * SPECIALTY VARIANTS:
 *   Skill card and learning-path variants are controlled by the .specialty.<name>
 *   parent container (CSS parent-selector model), not per-card attributes.
 *   Authors wrap the entire specialty section in @specialty augmerc and every
 *   card inside automatically inherits the shape and accent colors.
 *
 * ATTRIBUTE SUPPORT (core's marker grammar: .class, #id, key=value, {.class}):
 *
 *   @learning-path data-foo="bar"
 *     → <div class="dc-learning-path dc-path-block" data-foo="bar" data-path-ref="PRX1">
 *
 *   @skill {.dc-avoid-split}
 *     → every card of the skill: <div class="dc-skill-card dc-avoid-split" ...>
 *
 * LEARNING PATH FORMAT:
 *   @learning-path
 *   ### Title
 *   > Subtitle/description
 *   - Skill A
 *   - Skill B
 *   - Skill C
 *   @skill … (the skills follow, inside the path)
 *
 * SKILL FORMAT:
 *   @skill
 *   #### Skill Name
 *   > Flavor text
 *   1. **0 AP** *Ability Name:* Description
 *   2. **2 AP** *Another:* Description
 *   ##### Outcomes (optional sub-header)
 *   | Roll | Outcome |
 *   | --- | --- |
 *   | 20 | Critical |
 *
 * A skill ends at @end-skill, the next @skill, or when what holds it closes
 * (@end-learning-path, a new @learning-path, @end-specialty, @page, EOF).
 */

// The "continued" mark on a continuation card's tab: a drawn triangle, not a
// ▸ character. No Dimm City font has that glyph, so Chromium borrowed one
// from a system font and printed it as a Type 3 font, which Gutterpress's
// PDF/X preserve-text split cannot keep. It takes the tab title's colour.
const CONTINUED_MARK =
  '<svg class="dc-tab-cont-mark" viewBox="0 0 6 8" aria-hidden="true"><path d="M0 0 6 4 0 8z" fill="currentColor"/></svg>';

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;')
          .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// markdown-it's Token class, taken from a parser state when the plugin is
// installed: a plugin cannot import it, and rules need real tokens.
let Token;

function makeToken(type, content = '') {
  const tok = new Token(type, '', 0);
  tok.block = true;
  tok.content = content;
  return tok;
}

const classesOf = (tok) => (tok.attrGet('class') || '').split(/\s+/).filter(Boolean);
const hasClass = (tok, cls) => classesOf(tok).includes(cls);

// Add one class to a token's existing `class` attribute, keeping the others.
function addTokenClass(tok, cls) {
  const current = classesOf(tok);
  if (!current.includes(cls)) {
    current.push(cls);
    tok.attrSet('class', current.join(' '));
  }
}

// Add `cls` to a token's classes right after `anchor`, so a state class keeps
// its place beside the class core wrote first.
function addTokenClassAfter(tok, anchor, cls) {
  const current = classesOf(tok);
  current.splice(current.indexOf(anchor) + 1, 0, cls);
  tok.attrSet('class', current.join(' '));
}

// The index of the token that closes the one opening at tokens[i].
function closeIndex(tokens, i) {
  let depth = 0;
  for (let j = i; j < tokens.length; j++) {
    depth += tokens[j].nesting;
    if (depth <= 0) return j;
  }
  return tokens.length - 1;
}

// The attributes of an element that replaces a token: `cls` first, then what the
// token carried (its classes join `cls`; the rest follow in order).
function mergeAttrs(cls, attrs) {
  const merged = [['class', cls]];
  for (const [name, value] of attrs) {
    if (name === 'class') merged[0][1] += ' ' + value;
    else merged.push([name, value]);
  }
  return merged;
}

// A paragraph that is one bold run and closes right before tokens[at] (and is
// not the first thing after a `firstType` token) is a kicker: `.dc-kicker`.
function markKickerBefore(tokens, at, firstType) {
  if (at >= 4 && tokens[at - 1].type === 'paragraph_close' && tokens[at - 3].type === 'paragraph_open' &&
      tokens[at - 4].type !== firstType && isBoldOnlyInline(tokens[at - 2])) {
    addTokenClass(tokens[at - 3], 'dc-kicker');
  }
}

function parseSkillTitle(text) {
  // Parse "Skill Name" or "Skill Name | T0". Anything after a second "|" is
  // not part of the title and is dropped.
  const parts = text.split('|');
  const name = parts[0].trim();
  const tier = parts.length > 1 ? parts[1].trim() : '';
  return { name, tier };
}

function slugify(text) {
  return (text || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// The specialties and the prefix their learning paths are numbered with
// (AUG1, AUG2, …). `dualist` and `generalist` are specialties too but have no
// code, so their paths number as PATH1, PATH2, … like a path outside any specialty.
const SPECIALTY_CODES = {
  augmerc: 'AUG',
  proxy: 'PRX',
  streetwarden: 'STW',
  gutterdruid: 'GDR',
  cybersurgeon: 'CBS',
  wirephreak: 'WPH',
  technosorcerer: 'TNS',
  etherlock: 'ETH',
};
const SPECIALTIES = [...Object.keys(SPECIALTY_CODES), 'dualist', 'generalist'];

function specialtyCodeFromClass(tok) {
  const name = classesOf(tok).find((cls) => Object.hasOwn(SPECIALTY_CODES, cls));
  return name ? SPECIALTY_CODES[name] : 'PATH';
}

function buildStickerChain(items) {
  let html = '<div class="dc-stickers">';
  items.forEach((item, i) => {
    html += '<span class="dc-sticker"><span class="dc-sticker-ref">' + esc(String(i + 1)) + '</span>' + item.html.trim() + '</span>';
    if (i < items.length - 1) {
      // The word joiner keeps the arrow with the chip after it, so a wrap never
      // leaves a » at the end of a line.
      html += '<span class="dc-arrow">»</span>\u2060';
    }
  });
  html += '</div>\n';
  return html;
}

// ROLL THE DIE! / ROLL A DIE! / ROLLS A DIE! / ROLLING THE DIE! / ROLL THE DIE TWICE! / ROLL TWO DICE! — uppercase only.
const ROLL_THE_DIE_PATTERN = /ROLL(?:S|ING)? (?:(?:A|THE) DIE(?: TWICE)?|(?:TWO|THREE) DICE)!/;

function isWordChar(char) {
  return /[A-Za-z0-9_]/.test(char);
}

function copyTextToken(token, content, state) {
  const copy = new state.Token(token.type, token.tag, token.nesting);
  Object.assign(copy, token);
  copy.content = content;
  return copy;
}

function splitRollDieText(token, state) {
  const content = token.content || '';
  const replacement = [];
  let cursor = 0;
  const pattern = new RegExp(ROLL_THE_DIE_PATTERN.source, 'g');
  let match;

  while ((match = pattern.exec(content)) !== null) {
    const index = match.index;
    const before = index > 0 ? content[index - 1] : '';
    const end = index + match[0].length;
    const after = end < content.length ? content[end] : '';
    if (isWordChar(before) || isWordChar(after)) {
      pattern.lastIndex = index + 1;
      continue;
    }

    if (index > cursor) {
      replacement.push(copyTextToken(token, content.slice(cursor, index), state));
    }

    const rollToken = copyTextToken(token, match[0], state);
    rollToken.type = 'dc_roll_the_die';
    rollToken.tag = 'span';
    rollToken.nesting = 0;
    replacement.push(rollToken);

    cursor = end;
  }

  if (replacement.length === 0) return null;
  if (cursor < content.length) {
    replacement.push(copyTextToken(token, content.slice(cursor), state));
  }
  return replacement;
}

const VOID_HTML_TAGS = new Set([
  'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
  'link', 'meta', 'param', 'source', 'track', 'wbr',
]);

function updateRawHtmlStack(html, stack) {
  const match = html.match(/^<\s*(\/?)\s*([A-Za-z][A-Za-z0-9:-]*)\b/);
  if (!match) return;

  const tagName = match[2].toLowerCase();
  if (match[1]) {
    const openIndex = stack.lastIndexOf(tagName);
    if (openIndex !== -1) stack.length = openIndex;
    return;
  }

  if (!VOID_HTML_TAGS.has(tagName) && !/\/\s*>$/.test(html)) {
    stack.push(tagName);
  }
}

function dcRollDieTransform(state) {
  state.tokens.forEach((token, i) => {
    if (token.type !== 'inline' || !Array.isArray(token.children)) return;
    // A heading is already display type: its wording stays plain heading text.
    if (i > 0 && state.tokens[i - 1].type === 'heading_open') return;

    const children = [];
    const rawHtmlStack = [];
    token.children.forEach(child => {
      if (child.type === 'html_inline') {
        updateRawHtmlStack(child.content || '', rawHtmlStack);
        children.push(child);
        return;
      }

      const replacement = child.type === 'text' && rawHtmlStack.length === 0
        ? splitRollDieText(child, state)
        : null;
      if (replacement) children.push(...replacement);
      else children.push(child);
    });
    token.children = children;
  });
}

function renderInlineChildren(inlineTok, md) {
  if (!inlineTok?.children) return esc(inlineTok?.content || '');
  return md.renderer.render(inlineTok.children, md.options, {});
}

// The blockquote opening at tokens[i], as rendered text (the last paragraph in
// it, which is how every component that turns a quote into a line reads it),
// and the index of its close.
function quoteHtml(tokens, i, md) {
  let html = '';
  let end = i + 1;
  while (end < tokens.length && tokens[end].type !== 'blockquote_close') {
    if (tokens[end].type === 'inline') html = renderInlineChildren(tokens[end], md);
    end++;
  }
  return { html, end };
}

function collectTableTokens(tokens, start) {
  const result = [];
  let depth = 0;
  for (let i = start; i < tokens.length; i++) {
    result.push(tokens[i]);
    if (tokens[i].type === 'table_open') depth++;
    if (tokens[i].type === 'table_close') {
      depth--;
      if (depth === 0) break;
    }
  }
  return result;
}

function skipToTableClose(tokens, start) {
  for (let i = start; i < tokens.length; i++) {
    if (tokens[i].type === 'table_close') return i;
  }
  return tokens.length - 1;
}

// The header cells, the body rows and each row's cells of a table's tokens, as
// the markdown the author wrote in them.
function readTable(tableTokens) {
  const head = [];
  const rows = [];
  let part = '';
  let row = null;
  for (let i = 0; i < tableTokens.length; i++) {
    const t = tableTokens[i];
    if (t.type === 'thead_open') part = 'head';
    else if (t.type === 'tbody_open') part = 'body';
    else if (t.type === 'tr_open' && part === 'body') row = [];
    else if (t.type === 'tr_close' && part === 'body') rows.push(row);
    else if ((t.type === 'th_open' || t.type === 'td_open') && tableTokens[i + 1]?.type === 'inline') {
      (part === 'head' ? head : row).push(tableTokens[i + 1].content);
    }
  }
  return { head, rows };
}

// Every dash an author may type between the ends of a range: the hyphen,
// U+2010–U+2015 (hyphen, en and em dash, bar) and the minus sign. As the inside
// of a regex character class.
const DASH_CLASS = '\\-\\u2010-\\u2015\\u2212';
const DASH_RUN = new RegExp('-{2,3}|[' + DASH_CLASS + ']', 'g');
const enDashed = (text) => text.replace(new RegExp('[' + DASH_CLASS + ']', 'g'), '\u2013');

// "11 – 19" and "11--19" read as "11-19".
const hyphenated = (text) => text.replace(DASH_RUN, '-');

const OUTCOME_TIERS = ['crit', 'hit', 'mixed', 'miss', 'fail'];
const OUTCOME_NAMES = { crit: 'Crit', hit: 'Hit', mixed: 'Hard Choice', miss: 'Miss', fail: 'Catastrophe' };

// The d20 outcome ladder is recognised by its bands, not by what its columns
// are called: a two-column table whose first column holds a d20 result on every
// row is the ladder, so a roll's results read the same wherever the book states
// them. The five standard bands (20, 11-19, 6-10, 2-5, 1) are the usual set; an
// ability's own set is a ladder too (six bands, 16-19 over 11-15, 1-5 or 2-10,
// 11+), each row in the colour of the tier its band falls in. A band is typed any
// way an author types one ("11-19", "11 – 19", "**20**", "On 11–19", "11+"), may
// carry a label ("20: Total Wholeness", "20 – Triumph", "Triumph (20)"), or be the
// tier's word alone ("Success", "Hard Choice"). A table whose bands overlap, run
// past 1-20 or straddle 10/11 is not a ladder.
const LADDER_TIER_OF_BAND = { '20': 'crit', '11-19': 'hit', '6-10': 'mixed', '2-5': 'miss', '1': 'fail' };
const TIER_OF_WORD = { triumph: 'crit', crit: 'crit', critical: 'crit', success: 'hit', hit: 'hit', 'hard choice': 'mixed', mixed: 'mixed', failure: 'miss', fail: 'miss', miss: 'miss', catastrophe: 'fail' };

// "11 – 19" → [11, 19], "11--19" → [11, 19], "**20**" → [20, 20]; anything that is not a number or a range → null.
function parseBand(cell) {
  const text = hyphenated(cell.replace(/[*_`\s]/g, ''));
  const m = /^(\d{1,3})(?:-(\d{1,3}))?$/.exec(text);
  if (!m) return null;
  const [lo, hi] = [Number(m[1]), Number(m[2] ?? m[1])];
  return lo <= hi ? [lo, hi] : null;
}

// The tier a band falls in, or null when it straddles two (6-14) or is no d20 result.
function tierOfBand(lo, hi) {
  if (lo < 1 || hi > 20) return null;
  if (lo === 20) return 'crit';
  if (lo === 1 && hi === 1) return 'fail';
  if (lo >= 11) return 'hit';
  if (lo >= 6 && hi <= 10) return 'mixed';
  if (hi <= 10 && lo <= 5) return 'miss';
  return null;
}

// One result cell of a ladder → { tier, lo, hi, roll, label }, or null.
function parseResultCell(cell) {
  const text = hyphenated(cell.replace(/[*_`]/g, '')).replace(/\s+/g, ' ').trim();
  const word = TIER_OF_WORD[text.toLowerCase()];
  if (word) return { tier: word, lo: null, hi: null, roll: '', label: text };
  let m = /^(?:on )?(\d{1,2})(?: ?- ?(\d{1,2}))?(\+)?(?: ?[:-] ?(.+))?$/i.exec(text);
  let label = m?.[4] || '';
  if (!m) {
    m = /^(.+?) ?\((\d{1,2})(?: ?- ?(\d{1,2}))?\)$/.exec(text);
    if (!m) return null;
    m = [m[0], m[2], m[3], undefined, m[1]];
    label = m[4];
  }
  const lo = Number(m[1]);
  const hi = m[3] ? 20 : Number(m[2] ?? m[1]);
  if (lo > hi) return null;
  const tier = tierOfBand(lo, hi);
  if (!tier) return null;
  const roll = m[3] ? lo + '+' : lo === hi ? String(lo) : lo + '–' + hi;
  return { tier, lo, hi, roll, label: label.trim() };
}

// The ladder of a table — its header cells and its rows — or null when it is
// not a ladder: two columns, at least three rows, every first cell a result,
// three tiers or more, no two bands overlapping.
function ladderRows(table) {
  const { head, rows } = table;
  if (head.length !== 2 || rows.length < 3 || rows.some((r) => r.length !== 2)) return null;
  const cells = rows.map((r) => parseResultCell(r[0]));
  if (cells.some((c) => !c)) return null;
  if (new Set(cells.map((c) => c.tier)).size < 3) return null;
  const banded = cells.filter((c) => c.lo !== null).sort((x, y) => x.lo - y.lo);
  for (let i = 1; i < banded.length; i++) if (banded[i].lo <= banded[i - 1].hi) return null;
  return {
    head,
    rows: rows.map((r, i) => {
      const { tier, roll, label } = cells[i];
      return { tier, name: label || OUTCOME_NAMES[tier], roll, text: r[1].trim() };
    }),
  };
}

// The ladder's label bar and one row per `{ tier, name, roll, text }`; `text`
// is markdown, so **bold** and ROLL THE DIE! render as they do anywhere else.
// A ladder made from a table keeps the table's header: its two cells sit in the
// label bar over the two columns. With no header text the bar says "Outcomes".
function outcomeRowsHtml(rows, md, head = []) {
  let html = head.some((cell) => cell.trim())
    ? '  <div class="dc-outcomes-label dc-outcomes-head">' + head.map((cell) => '<span>' + md.renderInline(cell.trim()) + '</span>').join('') + '</div>\n'
    : '  <div class="dc-outcomes-label">Outcomes</div>\n';
  rows.forEach(({ tier, name, roll, text }) => {
    html += '  <div class="dc-outcome-row ' + tier + '">\n';
    html += '    <span class="dc-outcome-key tier-' + tier + '"><span class="dc-outcome-name">' + esc(name) + '</span><span class="dc-outcome-roll">' + esc(roll.replace(/(\d)\s*--\s*(\d)/g, '$1\u2013$2')) + '</span></span>\n';
    html += '    <span class="dc-outcome-text">' + md.renderInline(text) + '</span>\n';
    html += '  </div>\n';
  });
  return html;
}

// A table of the five standard bands: tier and name come from the band. The
// ladder replaces the table, so what the author wrote on the table (`{#id
// .class}`) and what the renderer threaded on it move to the ladder.
function buildLadderBlock({ head, rows }, md, table) {
  const attrs = mergeAttrs('dc-outcomes', table.attrs || []);
  return '<div' + md.renderer.renderAttrs({ attrs }) + '>\n' + outcomeRowsHtml(rows, md, head) + '</div>\n';
}

// The items of the list opening at tokens[startIndex] (ordered or bullet),
// at that list's own level: each is its first line (inline HTML) and `rest`,
// whatever else the item holds (a nested list, a second paragraph), rendered as
// it would be anywhere else so it stays what it is. `endIndex` is the list's close.
function collectListItems(tokens, startIndex, md, env) {
  const open = tokens[startIndex];
  const closeType = open.type.replace('_open', '_close');
  const items = [];
  let i = startIndex + 1;
  while (i < tokens.length && !(tokens[i].type === closeType && tokens[i].level === open.level)) {
    if (tokens[i].type === 'list_item_open' && tokens[i].level === open.level + 1) {
      const number = tokens[i].info || String(items.length + 1);
      let end = i + 1;
      while (!(tokens[end].type === 'list_item_close' && tokens[end].level === tokens[i].level)) end++;
      const body = tokens.slice(i + 1, end);
      // The item's own first line: a paragraph at the item's level that opens it.
      // An item that opens with a nested list has no lead of its own.
      const own = tokens[i].level + 2;
      const first = body[0]?.type === 'paragraph_open' && body[1]?.type === 'inline' && body[1].level === own ? 1 : -1;
      let after = first + 1;
      if (first >= 0 && body[after]?.type === 'paragraph_close') after++;
      items.push({
        number,
        html: first >= 0 ? renderInlineChildren(body[first], md) : '',
        src: first >= 0 ? body[first].content : '',
        rest: first >= 0 ? (after < body.length ? md.renderer.render(body.slice(after), md.options, env || {}) : '') : md.renderer.render(body, md.options, env || {}),
      });
      i = end;
    }
    i++;
  }
  return { items, endIndex: i };
}

// A skill card's ordered list, read by what each bold lead says:
//   - every item leads with a die result: not abilities but a ladder (the five
//     standard bands: the outcome ladder) or a `.dc-roll-table` plate;
//   - a cost leads an ability row (chip + text);
//   - a name (or no bold lead) is an option or a plain item: a bulleted list
//     with the name in bold and a colon when any item has a name, else an <ol>
//     numbered as the author numbered it.
function skillListHtml(items, md) {
  const rolls = dieResultListHtml(items, md);
  if (rolls) return rolls;
  const parsed = items.map((item) => ({ ...item, ability: parseAbilityFromListItem(item.html) }));
  const costs = parsed.filter((p) => p.ability).length;
  let html = '';
  let plain = [];
  const flush = () => {
    if (!plain.length) return;
    // A bold lead makes an item a named option. Options bullet; so does any run
    // that does not start at 1 (a table split the source list) or that sits
    // among cost rows. Only a plain list from 1 stays numbered.
    const named = plain.some((p) => /^\s*<strong>/i.test(p.html));
    const bulleted = named || plain[0].number !== '1' || costs > 0;
    html += bulleted
      ? '<ul>\n' + plain.map((p) => '<li>' + optionHtml(p.html) + p.rest + '</li>\n').join('') + '</ul>\n'
      : '<ol>\n' + plain.map((p) => '<li>' + p.html + p.rest + '</li>\n').join('') + '</ol>\n';
    plain = [];
  };
  parsed.forEach((item) => {
    const { ability } = item;
    if (!ability) {
      plain.push(item);
      return;
    }
    flush();
    const text = '<p class="dc-ability-text">' + ability.text + '</p>\n';
    const leadIn = /:$/.test(ability.text.replace(/<[^>]*>/g, '').trim()); // "…the restoration:": the row introduces the block after it
    html += '<div class="dc-ability' + (ability.titleOnly && !item.rest ? ' dc-ability-title' : '') + (leadIn ? ' dc-lead-in' : '') + '">\n' +
      '  <span class="' + ability.apClass + '">' + esc(ability.apVal) + '</span>\n' +
      (item.rest ? '  <div class="dc-ability-body">\n' + text + item.rest + '  </div>\n' : '  ' + text) +
      '</div>\n';
  });
  flush();
  return html;
}

// An option's bold name takes its colon inside the bold ("**Name:** text"); a
// colon the author wrote after the bold ("**Name**: text") moves in, never doubles.
function optionHtml(html) {
  const m = html.match(/^(\s*)<strong>([^<]+)<\/strong>/i);
  if (!m) return html;
  let name = m[2].trim();
  let rest = html.slice(m[0].length);
  if (/^:/.test(rest)) {
    rest = rest.slice(1);
    if (!name.endsWith(':')) name += ':';
  } else if (!/[:.!?]$/.test(name) && !name.includes(':')) {
    name += ':';
  }
  return m[1] + '<strong>' + name + '</strong>' + rest;
}

// A bold die result in markdown: **20**, **11-19**, **6–10:**, **16–19: Name**.
const DIE_RESULT_MD = new RegExp(String.raw`^\*\*\s*(\d{1,3}(?:\s*[${DASH_CLASS}]\s*\d{1,3})?)\s*(?::|(?::|\s[\u2013\u2014-])\s*([^*]+?))?\s*\*\*\s*`);

// The die a set of results is the faces of: ranges that do not overlap and
// cover 1 to N with no gap (any order), N one of the usual dice. Else 0.
function dieOfResults(leads) {
  const spans = leads.map((l) => {
    const n = l.match(/\d+/g).map(Number);
    return [n[0], n[n.length - 1]];
  });
  if (spans.some(([lo, hi]) => lo > hi)) return 0;
  spans.sort((x, y) => x[0] - y[0]);
  let next = 1;
  for (const [lo, hi] of spans) {
    if (lo !== next) return 0;
    next = hi + 1;
  }
  const top = next - 1;
  return [4, 6, 8, 10, 12, 20, 100].includes(top) ? top : 0;
}

// A list whose items ALL lead with a die result is a roll list, not an ability
// list: the five standard bands are the outcome ladder (the same component a
// table of them makes); any other set is a `.dc-roll-table` plate. Both are built
// from the same table reading the plugin already does.
function dieResultListHtml(items, md) {
  if (items.length < 2 || items.some((item) => item.rest)) return '';
  const rows = [];
  for (const item of items) {
    const m = DIE_RESULT_MD.exec(item.src || '');
    if (!m) return '';
    const bold = m[0].replace(/\*\*/g, '').trim();
    if (COST_LEAD.test(bold) || BARE_VARIABLE_COST.test(bold)) return ''; // "1-3 AP" is a cost, not a roll
    const text = item.src.slice(m[0].length).trim();
    rows.push([m[1], (m[2] ? '**' + m[2].trim() + '** ' : '') + text]);
  }
  const die = dieOfResults(rows.map((r) => r[0]));
  if (!die) return '';
  const ladder = ladderRows({ head: ['Roll', 'Outcome'], rows });
  if (ladder) return buildLadderBlock(ladder, md, { attrs: [] });
  const cell = (c) => md.renderInline(c.trim()).replace(new RegExp(String.raw`\s*[${DASH_CLASS}]\s*`), '–');
  return '<div class="dc-roll-table">\n<div class="dc-roll-table-caption"><span class="dc-roll-table-die">d' + die + '</span></div>\n<table>\n<thead>\n<tr><th>Roll</th><th>Outcome</th></tr>\n</thead>\n<tbody>\n' +
    rows.map(([r, t]) => '<tr><td>' + cell(r) + '</td><td>' + md.renderInline(t.trim()) + '</td></tr>\n').join('') +
    '</tbody>\n</table>\n</div>\n';
}

// A numbered item in a skill card whose text opens with a bold lead is read by
// what the lead says, never by its shape alone:
//   - a COST: a number, range (hyphen or dash), X or VAR, optional +, then "AP".
//     It becomes the AP chip, and the chip carries only that readout ("3 AP").
//     What follows the cost leaves the chip for the start of the row's text, as
//     an italic run-in with a colon: a name ("3 AP — Butcher Roach" → "Butcher
//     Roach:") or a qualifier ("+1 AP per passenger." → "Per passenger:"; a
//     "/"-qualifier keeps its cost: "1 AP/100 DC Per Ego Point…:"). The one bare
//     form kept is the variable "3-X".
//   - anything else (a die result, a name, a sentence) is not a cost.
const COST_LEAD = new RegExp(String.raw`^(\+?\s*(?:\d+|X|VAR)(?:\s*[${DASH_CLASS}]\s*(?:\d+|X))?\+?)\s*AP\b(.*)$`, 'i');
const BARE_VARIABLE_COST = new RegExp(String.raw`^\d+\s*[${DASH_CLASS}]\s*X$`, 'i');
const LEADING_DASH = new RegExp('^[' + DASH_CLASS + ']');
const VARIABLE_COST = new RegExp('[' + DASH_CLASS + ']|X|VAR|\\+$', 'i'); // a range, X, VAR or a trailing +

// A rendered list item's text → { apVal, apClass, text } | null (not a cost).
function parseAbilityFromListItem(html) {
  const lead = html.match(/^\s*<strong>([^<]+)<\/strong>\s*/i);
  if (!lead) return null;

  const label = lead[1].replace(/\s+/g, ' ').trim().replace(/[.]+$/, '').trim();
  let text = html.slice(lead[0].length);

  let costPart;
  let apVal;
  let perUnit = false;
  const cost = COST_LEAD.exec(label);
  if (cost) {
    costPart = cost[1].replace(/\s+/g, '');
    apVal = enDashed(costPart) + ' AP';
    let tail = cost[2].replace(/^\s*[:,]\s*/, '').trim();
    // a per-unit rate ("per passenger", "/100 DC Per Ego Point") makes the cost one you choose;
    // a parenthetical ("(once per scene)") is a qualifier, not a rate
    perUnit = !(tail.startsWith('(') || LEADING_DASH.test(tail)) && /^\/?.*\bper\b/i.test(tail);
    if (tail.startsWith('(')) {
      text = tail + ' ' + text;
    } else if (tail) {
      let runIn;
      if (LEADING_DASH.test(tail)) runIn = tail.slice(1).trimStart();
      else if (tail.startsWith('/')) runIn = apVal + tail;
      else runIn = tail.charAt(0).toUpperCase() + tail.slice(1);
      runIn = runIn.replace(/[.:]+$/, '').trim();
      if (runIn) text = '<em>' + runIn + ':</em> ' + text;
    }
  } else if (BARE_VARIABLE_COST.test(label)) {
    costPart = label.replace(/\s+/g, '');
    apVal = enDashed(costPart) + ' AP';
  } else {
    return null;
  }

  const bare = costPart.replace(/^\+/, '');
  let apClass = 'dc-ap';
  if (/^0+$/.test(bare)) apClass += ' free';
  else if (VARIABLE_COST.test(bare) || perUnit) apClass += ' variable';

  // A row that is only a name (`**3 AP — Butcher Roach**`, its text in the
  // paragraphs that follow) is the title of what follows: `titleOnly`.
  const titleOnly = !html.slice(lead[0].length).trim();
  return { apVal, apClass, text, titleOnly };
}


// Gutterpress owns bare @continue as a generic section marker and parses it
// before custom core rules run. Claim the exact bare marker first, then decide
// before Gutterpress's layout transform whether it belongs to a skill card or
// should retain the generic section-continuation behavior.
function dcContinueCandidateBlock(state, startLine, endLine, silent) {
  const pos = state.bMarks[startLine] + state.tShift[startLine];
  const max = state.eMarks[startLine];
  if (state.src.slice(pos, max).trim() !== '@continue') return false;
  if (silent) return true;

  state.env.__layoutMarkersUsed = true;
  const token = state.push('dc_continue_candidate', '', 0);
  token.block = true;
  token.map = [startLine, startLine + 1];
  token.meta = { kind: 'continue', attrs: {}, __line: startLine + 1 };
  state.line = startLine + 1;
  return true;
}

// Markers that end a skill: its own closer, the markers that start the next
// path or specialty, and the layout scopes core closes every declared
// component at. At this point core has not run yet, so each one is still a
// `layout_marker` token carrying `meta.kind`.
const SKILL_ENDS = new Set([
  'end-skill', 'learning-path', 'end-learning-path', 'specialty', 'end-specialty',
  'chapter', 'spread', 'page', 'section', 'end-section',
]);

function dcContinueClassifier(state) {
  let inSkill = false;
  let inCard = false;

  for (const token of state.tokens) {
    const kind = token.type === 'layout_marker' ? token.meta.kind : null;
    if (kind === 'skill') {
      inSkill = true;
      inCard = false;
    } else if (SKILL_ENDS.has(kind)) {
      inSkill = false;
      inCard = false;
    } else if (inSkill && token.type === 'heading_open' && token.tag === 'h4') {
      inCard = true;
    } else if (token.type === 'dc_continue_candidate') {
      token.type = inCard ? 'dc_skill_continue' : 'layout_marker';
    }
  }
}

function registerSkillContinueBridge(md) {
  // Without Gutterpress's layout_transform (bare markdown-it) there is no section @continue to share the marker with.
  if (!md.core.ruler.__rules__.some((rule) => rule.name === 'layout_transform')) return;
  md.core.ruler.before('layout_transform', 'dc_continue_classifier', dcContinueClassifier);
  md.block.ruler.before('layout_marker', 'dc_continue_candidate', dcContinueCandidateBlock, {
    alt: ['paragraph', 'reference', 'blockquote', 'list'],
  });
}


// `attrs` are what the author wrote on the `@procedure` line: the wrapper
// renders nothing, so the list takes them.
function buildProcedureList(items, attrs, md) {
  let html = '<ol' + md.renderer.renderAttrs({ attrs: mergeAttrs('dc-steps', attrs) }) + '>\n';
  items.forEach(({ html: step, rest }, idx) => {
    const stepNo = String(idx + 1).padStart(2, '0');
    html += '  <li><span class="dc-step-no">' + esc(stepNo) + '</span><span>' + step.trimEnd() + rest + '</span></li>\n';
  });
  html += '</ol>\n';
  return html;
}

const CALLOUTS = {
  note: { class: 'dc-note', label: 'Note' },
  warning: { class: 'dc-note warning', label: 'Warning' },
  dm: { class: 'dc-dm-note', label: 'Dream Master Note' },
  vibe: { class: 'dc-vibe-callout', label: 'Vibe' },
  origin: { class: 'dc-origin-callout', label: 'Origin' },
  location: { class: 'dc-location-callout', label: 'Location' },
  visit: { class: 'dc-visit-callout', label: 'Visit' },
  example: { class: 'dc-example-callout', label: 'Example' },
};

/**
 * GFM-style blockquote alert types — Dimm City branded: the classes and labels
 * are DC-specific, so core does not know them.
 */
// The callout variants that also have a `> [!TYPE]` form.
const ALERT_CALLOUTS = ['note', 'warning', 'dm', 'vibe', 'origin', 'location', 'visit'];

const DC_ALERT_TYPES = {
  ...Object.fromEntries(ALERT_CALLOUTS.map((variant) => [
    variant.toUpperCase(),
    { classes: 'dc-alert ' + CALLOUTS[variant].class, label: CALLOUTS[variant].label },
  ])),
  FLAVOR:    { classes: "dc-flavor" },
  PULLQUOTE: { classes: "dc-pullquote dc-flush" },
};

// `[!TYPE]` and the blanks after it.
const DC_ALERT_MARKER = /^\[!([A-Z_]+)\][ \t]*/i;

/**
 * Transform `> [!TYPE]` blockquotes into DC-branded styled divs.
 *
 * This is a markdown-it core rule that consumes the `[!TYPE]` marker and
 * wraps the blockquote contents in a `<div>` carrying the corresponding
 * DC alert classes and an optional label span.
 */
function dcAlertsTransform(state) {
  const tokens = state.tokens;
  const newTokens = [];

  for (let i = 0; i < tokens.length; i++) {
    const tok = tokens[i];
    if (tok.type !== 'blockquote_open') {
      newTokens.push(tok);
      continue;
    }

    let closeIdx = -1;
    let firstInlineIdx = -1;
    let depth = 0;
    for (let j = i; j < tokens.length; j++) {
      const jt = tokens[j];
      if (jt.type === 'blockquote_open') depth++;
      if (jt.type === 'blockquote_close') {
        depth--;
        if (depth === 0) { closeIdx = j; break; }
      }
      if (firstInlineIdx === -1 && jt.type === 'inline') firstInlineIdx = j;
    }

    if (firstInlineIdx === -1) { newTokens.push(tok); continue; }

    const inlineTok = tokens[firstInlineIdx];
    const lead = inlineTok.children?.[0];
    const match = lead?.type === 'text' && inlineTok.content.match(DC_ALERT_MARKER);
    if (!match) { newTokens.push(tok); continue; }

    const alertType = match[1].toUpperCase();
    const config = DC_ALERT_TYPES[alertType];
    if (!config) { newTokens.push(tok); continue; }

    // A title: the text between the marker and the first line break INSIDE the
    // first paragraph, with body text after the break, replaces the variant's
    // default label. A first paragraph of one line stays body text, whatever
    // follows it. Bold in a title is dropped: the label is already a bold chip.
    let titleHtml = '';
    let titleCount = 0;
    if (config.label) {
      const kids = inlineTok.children;
      const afterMarker = lead.content.replace(DC_ALERT_MARKER, '').replace(/^\s+/, '');
      const brk = kids.findIndex((c) => c.type === 'softbreak' || c.type === 'hardbreak');
      if (brk > 0 && (afterMarker !== '' || brk > 1)) {
        const titleKids = kids.slice(0, brk)
          .filter((c) => c.type !== 'strong_open' && c.type !== 'strong_close')
          .map((c) => (c === lead ? Object.assign(Object.create(Object.getPrototypeOf(c)), c, { content: afterMarker }) : c));
        const rendered = state.md.renderer.renderInline(titleKids, state.md.options, state.env).trim();
        if (rendered !== '') {
          titleCount = brk;
          titleHtml = rendered;
        }
      }
    }

    // Open div
    const openTok = new state.Token('html_block', '', 0);
    openTok.block = true;
    let openHtml = `<div class="${config.classes}">`;
    if (config.label) openHtml += `<span class="dc-alert-label">${titleHtml || config.label}</span>`;
    openHtml += '\n';
    openTok.content = openHtml;
    newTokens.push(openTok);

    // Strip [!TYPE] prefix from first inline; suppress its paragraph wrapper if empty.
    let stripped = inlineTok.content.slice(match[0].length).trim();
    if (titleHtml) {
      // the title line leaves the paragraph: what is left is the text after its line break
      const nl = stripped.search(/\r?\n/);
      stripped = nl === -1 ? '' : stripped.slice(nl).trim();
    }

    const paragraphOpenIdx = firstInlineIdx - 1;
    const paragraphCloseIdx = firstInlineIdx + 1;
    const wrapsInParagraph =
      paragraphOpenIdx > i &&
      tokens[paragraphOpenIdx].type === 'paragraph_open' &&
      tokens[paragraphCloseIdx].type === 'paragraph_close';

    for (let j = i + 1; j < closeIdx; j++) {
      const t = tokens[j];
      if (j === firstInlineIdx) {
        if (stripped === '') continue;
        // The core rules have already typeset the children, so take the marker
        // off the lead text (and the line break it leaves at the front) and
        // keep the rest; re-parsing would skip replacements, smartquotes and
        // text_join.
        if (titleCount) {
          inlineTok.children.splice(0, titleCount);
          const next = inlineTok.children[0];
          if (next && (next.type === 'softbreak' || next.type === 'hardbreak')) inlineTok.children.shift();
        } else {
          lead.content = lead.content.replace(DC_ALERT_MARKER, '');
        }
        if (lead.content === '' && !titleCount) {
          inlineTok.children.shift();
          const next = inlineTok.children[0];
          if (next && (next.type === 'softbreak' || next.type === 'hardbreak')) inlineTok.children.shift();
        }
        inlineTok.content = stripped;
        newTokens.push(inlineTok);
        continue;
      }
      if (stripped === '' && wrapsInParagraph) {
        if (j === paragraphOpenIdx || j === paragraphCloseIdx) continue;
      }
      newTokens.push(t);
    }

    const closeTok = new state.Token('html_block', '', 0);
    closeTok.block = true;
    closeTok.content = '</div>\n';
    newTokens.push(closeTok);

    i = closeIdx;
  }

  state.tokens = newTokens;
}

/**
 * Mark image-only paragraphs with `.dc-img-wrapper`, so layout rules can
 * target them without relying on `p:has(img)`.
 */
function dcImageParagraphs(state) {
  const tokens = state.tokens;
  for (let i = 0; i + 2 < tokens.length; i++) {
    const [open, inline, close] = [tokens[i], tokens[i + 1], tokens[i + 2]];
    if (open.type !== 'paragraph_open' || inline.type !== 'inline' || close.type !== 'paragraph_close') continue;
    if (inline.children?.length === 1 && inline.children[0].type === 'image') open.attrSet('class', 'dc-img-wrapper');
  }
}

// The title of a front-matter page is a chevron banner because of where it
// sits: the `h1` straight under `@page intro | credits | contents` is a
// `.dc-chevron`, so the author writes no `{.dc-chevron}`. The class stays
// available on any other heading.
const FRONT_MATTER_PAGES = ['dc-page-intro', 'dc-page-credits', 'dc-page-contents'];

function dcFrontMatterTitles(state) {
  let front = false;
  let depth = 0; // layout containers open inside the page: a heading in one is not the page's title
  for (const tok of state.tokens) {
    if (tok.type === 'layout_page_open') {
      front = classesOf(tok).some((c) => FRONT_MATTER_PAGES.includes(c));
      depth = 0;
    } else if (tok.type === 'layout_page_close') {
      front = false;
    } else if (/^layout_.+_open$/.test(tok.type)) {
      depth++;
    } else if (/^layout_.+_close$/.test(tok.type)) {
      depth--;
    } else if (front && !depth && tok.type === 'heading_open' && tok.tag === 'h1') {
      addTokenClass(tok, 'dc-chevron');
    }
  }
}

/**
 * `data-position="odd|even"` on every @specialty-card, counted across the
 * document in order so the card grid alternates its tilt/offset. The wrapper
 * itself is a declared marker (see `markers` below); this rule only numbers
 * the open tokens core produced. It never runs under bare markdown-it, which
 * has no declared markers.
 */
function dcSpecialtyCardPositions(state) {
  let count = 0;
  for (const tok of state.tokens) {
    if (tok.type !== 'layout_component_open') continue;
    if (!hasClass(tok, 'dc-specialty-card')) continue;
    count++;
    tok.attrSet('data-position', count % 2 === 0 ? 'even' : 'odd');
  }
}

// ── Declared components: @specialty, @learning-path, @skill ────────────────
//
// All three are declared in `markers` below, so core opens, nests and closes
// them: each use is a `layout_component_open` … `layout_component_close` pair
// whose open token's `meta.kind` is the marker name. The rules here are
// ordinary core rules that rewrite what sits between a pair.

/**
 * Call `rewrite(run, enclosing)` for every declared component of `kind`, in
 * document order. `run` is the component's tokens, open token to close token;
 * `enclosing` is the open tokens of the components it sits in, outermost first.
 * Return a replacement run, or nothing to leave it as it is.
 */
function forEachComponent(tokens, kind, rewrite) {
  const enclosing = [];
  for (let i = 0; i < tokens.length; i++) {
    const tok = tokens[i];
    if (tok.type === 'layout_component_close') {
      enclosing.pop();
      continue;
    }
    if (tok.type !== 'layout_component_open') continue;
    if (tok.meta.kind !== kind) {
      enclosing.push(tok);
      continue;
    }
    const end = closeIndex(tokens, i) + 1;
    const run = rewrite(tokens.slice(i, end), enclosing) || tokens.slice(i, end);
    tokens.splice(i, end - i, ...run);
    i += run.length - 1;
  }
}

// What sits in a learning path before its first skill — the title, the
// subtitle and the sticker chain — rewritten into the path's header markup.
function pathShell(tokens, ref, md) {
  const out = [];
  let titled = false;
  for (let i = 0; i < tokens.length; i++) {
    const tok = tokens[i];

    // H3 = learning path title (banner). Emitted as an h3, the level it was
    // written at: the outline (the app's contents panel, PDF bookmarks) nests
    // specialty (##) > learning path (###) > skill (####). .dc-path-sep is a
    // real space between the sticker and the title, so the heading's text
    // reads "PRX1 Refuse Finality" (outline, bookmarks, copy, search, screen
    // readers); chrome.css gives it the printed gap.
    if (tok.type === 'heading_open' && tok.tag === 'h3') {
      out.push(makeToken('html_block', '<h3 class="dc-spray"><span class="dc-path-sticker">' + esc(ref) + '</span><span class="dc-path-sep"> </span>' + renderInlineChildren(tokens[i + 1], md) + '</h3>\n'));
      titled = true;
      i += 2; // skip inline + heading_close
      continue;
    }

    // Blockquote after the title = subtitle.
    if (tok.type === 'blockquote_open' && titled) {
      const quote = quoteHtml(tokens, i, md);
      out.push(makeToken('html_block', '<div class="dc-intro">' + quote.html + '</div>\n'));
      i = quote.end;
      continue;
    }

    // Bullet list = sticker chain.
    if (tok.type === 'bullet_list_open') {
      const { items, endIndex } = collectListItems(tokens, i, md);
      const stickers = items.filter((item) => item.html);
      if (stickers.length > 0) out.push(makeToken('html_block', buildStickerChain(stickers)));
      i = endIndex;
      continue;
    }

    out.push(tok);
  }
  return out;
}

/**
 * `@learning-path`: number it (`data-path-ref`, from the enclosing
 * `@specialty`'s name — its variant word or its author class — and the path's
 * place in it) and wrap the path's header in `.dc-path-shell`.
 */
function dcLearningPaths(state) {
  const numbered = new Map(); // enclosing @specialty (or null) → paths numbered so far
  forEachComponent(state.tokens, 'learning-path', (run, enclosing) => {
    const [open, close] = [run[0], run[run.length - 1]];
    const specialty = enclosing.findLast((c) => c.meta.kind === 'specialty') || null;
    const n = (numbered.get(specialty) || 0) + 1;
    numbered.set(specialty, n);
    const ref = (specialty ? specialtyCodeFromClass(specialty) : '') + n;
    open.attrSet('data-path-ref', ref);

    const body = run.slice(1, -1);
    let end = body.findIndex((t) => t.type === 'layout_component_open' && t.meta.kind === 'skill');
    if (end < 0) end = body.length;
    return [
      open,
      makeToken('html_block', '<div class="dc-path-shell">\n'),
      ...pathShell(body.slice(0, end), ref, state.md),
      makeToken('html_block', '</div>\n'),
      ...body.slice(end),
      close,
    ];
  });
}

// A card's closing paragraph shorter than this (text characters) is a sign-off: it stays with the block above it.
const SIGNOFF_MAX = 120; // one line at the card's measure

/** The characters an inline token prints as plain text or code (markup and spans not counted). */
function inlineTextLength(inline) {
  return (inline?.children || []).reduce((n, k) => n + (k.type === 'text' || k.type === 'code_inline' ? k.content.length : 0), 0);
}

/** True when a paragraph's source ends in a colon (outside its emphasis marks): it introduces what follows. */
function endsWithColon(inline) {
  return inline?.type === 'inline' && /:$/.test((inline.content || '').replace(/[\s*_`]+$/, ''));
}

/** True when an inline token's whole content is one `<strong>` run. */
function isBoldOnlyInline(inline) {
  const kids = (inline?.type === 'inline' ? inline.children || [] : []).filter((k) => k.type !== 'text' || k.content);
  return kids.length > 2 && kids[0].type === 'strong_open' && kids[kids.length - 1].type === 'strong_close' &&
    kids.filter((k) => k.type === 'strong_open' || k.type === 'strong_close').length === 2;
}

// A card's tab, body and inner wrapper openers. The first card of a skill
// names the skill in a real heading, so the outline lists it under its learning
// path; a continuation's repeated title is a span with the continued mark.
function cardTabHtml({ name, tier }, cont) {
  const title = cont
    ? '    <span class="dc-tab-title">' + esc(name) + ' ' + CONTINUED_MARK + '</span>\n'
    : '    <h4 class="dc-tab-title">' + esc(name) + '</h4>\n';
  return '  <div class="dc-card-tab' + (cont ? ' dc-card-tab-cont' : '') + '">\n' +
    title +
    (tier ? '    <span class="dc-tab-tier">' + esc(tier) + '</span>\n' : '') +
    '  </div>\n' +
    '  <div class="dc-card-body">\n' +
    '    <div class="dc-card-inner">\n';
}

/**
 * `@skill`: every `####` heading inside it starts a card. The declared
 * wrapper only carries the author's classes and attributes (`{.dc-avoid-split}`,
 * `id=…`) — it renders nothing itself; each card is rendered from them.
 *
 *   h4 title     → card tab (name, tier); a skill in a learning path gets the
 *                  automatic tier PATHREF.N when it names none
 *   h5           → sub-header (an "Outcomes" one is dropped: the table has its own label)
 *   blockquote   → flavor line
 *   ordered list → ability rows
 *   Roll | Outcome table → outcomes ladder
 *   @continue    → closes the card (`.dc-skill-card-cut`: a straight foot and a ▸ flag)
 *                  and opens a "{name} ▸" continuation card with the same ID
 */
function dcSkillCards(state) {
  const md = state.md;
  const numbered = new Map(); // learning-path open token → cards numbered so far
  forEachComponent(state.tokens, 'skill', (run, enclosing) => {
    const [open, close] = [run[0], run[run.length - 1]];
    open.hidden = close.hidden = true;
    const path = enclosing.findLast((c) => c.meta.kind === 'learning-path');
    const content = run.slice(1, -1);
    const cardLevel = content.find((t) => t.type === 'heading_open' && t.tag === 'h4')?.level;
    const out = [];
    // The card's last block while it is still a paragraph: marked a sign-off when short (below).
    let tail = null;
    const emit = (html) => {
      tail = null;
      seenBlock = true;
      out.push(makeToken('html_block', html));
    };
    let inCard = false;
    const belongsToCard = new Set(); // open/close tokens of the components that stay in the card
    let columnsDepth = 0; // how many `@columns` runs sit open inside the current card
    const columnsCloses = new Set(); // their close tokens
    let title = { name: '', tier: '' }; // the current card's title, for @continue

    // The card's opening markup, for the title it shows: the first card of a
    // skill, or a continuation (`cont`); `cut` ends the card in a straight foot.
    const cardOpen = (cont, cut = false) => {
      const card = makeToken('html_block');
      card.attrs = open.attrs.map(([k, v]) => [k, v]);
      if (cont) addTokenClassAfter(card, 'dc-skill-card', 'dc-skill-card-cont');
      if (cut) addTokenClassAfter(card, 'dc-skill-card', 'dc-skill-card-cut');
      card.attrs.push(['name', slugify(title.name)]);
      return '<div' + md.renderer.renderAttrs(card) + '>\n' + cardTabHtml(title, cont);
    };
    // A card's closing sign-off is marked only when the card truly ends there: not
    // when it is cut for a continuation, and never its first paragraph.
    let seenBlock = false;
    let compDepth = 0; // how many components (callout, columns) are open inside the card
    const endCard = (continuing = false) => {
      if (inCard && tail && !tail.first && !continuing && tail.len <= SIGNOFF_MAX) addTokenClass(tail.tok, 'dc-card-signoff');
      // .dc-card-inner, the two seam markers (cards.css, "The seam"), .dc-card-body, .dc-skill-card
      if (inCard) emit('</div><span class="dc-card-start"></span><span class="dc-card-end"></span></div></div>\n');
      inCard = false;
    };
    let cardTok = null; // the html token that opened the current card
    let cardCont = false; // is the current card a continuation?

    for (let i = 0; i < content.length; i++) {
      const tok = content[i];

      // An h4 inside a `@columns` run in a card is a plain heading: a card
      // cannot start in the middle of another card's columns.
      if (tok.type === 'heading_open' && tok.tag === 'h4' && columnsDepth === 0) {
        endCard();
        const parsed = parseSkillTitle(content[i + 1].content || '');
        let autoTier = '';
        if (path) {
          const n = (numbered.get(path) || 0) + 1;
          numbered.set(path, n);
          autoTier = path.attrGet('data-path-ref') + '.' + n;
        }
        // The continuation card repeats the ID the card shows, written or automatic.
        title = { name: parsed.name, tier: parsed.tier || autoTier };
        // The skill's name is its `####` heading, kept a heading so the
        // outline lists it under its learning path. (A continuation card's
        // repeated title stays a span: it is not a new entry.)
        emit(cardOpen(false));
        cardTok = out[out.length - 1];
        cardCont = false;
        inCard = true;
        seenBlock = false;
        i += 2; // skip inline + heading_close
        continue;
      }

      if (tok.type === 'dc_skill_continue') {
        endCard(true);
        // The part before an explicit continuation closes straight (a foot, a
        // bolt, a flag); the specialty's cut stays the mark of a card's real end.
        if (cardTok) cardTok.content = cardOpen(cardCont, true);
        cardCont = true;
        emit(cardOpen(true));
        cardTok = out[out.length - 1];
        inCard = true;
        seenBlock = false;
        continue;
      }

      // A @callout, @card, @outcome, @procedure or @roll-table is content of the skill's card;
      // a break or another component (@specialty-art, @gear, …) ends it.
      if (tok.type === 'layout_component_open' && CARD_CONTENT.has(tok.meta.kind)) {
        belongsToCard.add(tok).add(content[closeIndex(content, i)]);
      }
      // `@columns` … `@end-columns` and the `@column-break`s between are content of
      // the card too when they sit inside one: the columns run stays in the
      // card's body, in place. (A run that opens before the card, around
      // several cards, is not the card's: it ends the card as any layout token does.)
      if (inCard && tok.type === 'layout_component_open' && tok.meta.kind === 'columns') {
        const close = content[closeIndex(content, i)];
        belongsToCard.add(tok).add(close);
        columnsCloses.add(close);
        columnsDepth++;
      }
      if (columnsCloses.has(tok)) columnsDepth--;
      if (tok.type === 'layout_column_break' && columnsDepth > 0) belongsToCard.add(tok);
      if (tok.type.startsWith('layout_') && !belongsToCard.has(tok)) endCard();

      if (inCard && belongsToCard.has(tok)) {
        if (tok.type === 'layout_component_open') compDepth++;
        else if (tok.type === 'layout_component_close') compDepth--;
      }

      if (!inCard) {
        out.push(tok);
        continue;
      }

      if (tok.type === 'heading_open' && tok.tag === 'h5') {
        const h5Text = content[i + 1].content || '';
        if (h5Text.toLowerCase() !== 'outcomes') emit('<div class="dc-sub-header">' + esc(h5Text) + '</div>\n');
        i += 2;
        continue;
      }

      if (tok.type === 'blockquote_open') {
        const quote = quoteHtml(content, i, md);
        emit('<p class="dc-flavor">' + quote.html + '</p>\n');
        i = quote.end;
        continue;
      }

      if (tok.type === 'ordered_list_open') {
        const { items, endIndex } = collectListItems(content, i, md, state.env);
        emit(skillListHtml(items, md));
        i = endIndex;
        continue;
      }

      if (tok.type === 'table_open') {
        // A table of the five standard bands is the ladder; any other table
        // passes through untouched, thead and all.
        const tableTokens = collectTableTokens(content, i);
        const ladder = tok.meta?.rollTable ? null : ladderRows(readTable(tableTokens));
        if (ladder) {
          emit(buildLadderBlock(ladder, md, tok));
          i = skipToTableClose(content, i);
          continue;
        }
      }

      // A paragraph that is nothing but one bold run is the card's pseudo
      // heading (`**Full Merge**`); CSS cannot see text nodes, so only the
      // plugin can tell it from a run-in `**Shared Senses:** text`.
      if (tok.type === 'paragraph_open' && !tok.hidden && tok.level === cardLevel && compDepth === 0) {
        const inline = content[i + 1];
        if (isBoldOnlyInline(inline)) addTokenClass(tok, 'dc-card-subhead');
        // A paragraph that ends in a colon introduces the next block.
        if (endsWithColon(inline)) addTokenClass(tok, 'dc-lead-in');
        tail = { tok, len: inlineTextLength(inline), first: !seenBlock };
      } else if (tok.type !== 'inline' && tok.type !== 'paragraph_close') {
        tail = null;
      }

      if (tok.type !== 'paragraph_open') seenBlock = true;
      out.push(tok);
    }
    endCard();
    return [open, ...out, close];
  });
}

/**
 * A section or panel that ends in a paragraph that is only a bold run, or has one
 * right before a heading, closes on a kicker (`**Just don't confuse a good time with a safe one.**`): `.dc-kicker`,
 * so it never opens a page alone.
 */
function dcKickers(state) {
  const t = state.tokens;
  let depth = 0; // sections open around the token
  for (let i = 0; i < t.length; i++) {
    if (t[i].type === 'layout_section_open') depth++;
    if (t[i].type === 'layout_section_close') {
      depth--;
      markKickerBefore(t, i, 'layout_section_open');
    }
    // A bold-only paragraph right before a heading in the same section also closes
    // its stretch of text. Before ordinary text it is a run-in sub-heading: not a kicker.
    if (depth > 0 && t[i].type === 'paragraph_open' && !t[i].hidden && t[i + 3]?.type === 'heading_open' && t[i + 2]?.type === 'paragraph_close' && isBoldOnlyInline(t[i + 1])) {
      addTokenClass(t[i], 'dc-kicker');
    }
  }
}

/**
 * A paragraph that is only the die call (`**ROLL THE DIE!**`, or the bare words,
 * or any form of the phrase the inline rule picks out) is the table's imperative
 * moment, not a sentence: `.dc-die-call`, a raised chip. Mid-sentence it stays the
 * inline mark. A paragraph in a list or a quote is not set apart.
 */
function dcDieCalls(state) {
  const t = state.tokens;
  let quoted = 0;
  for (let i = 0; i < t.length; i++) {
    if (t[i].type === 'blockquote_open' || t[i].type === 'list_item_open') quoted++;
    else if (t[i].type === 'blockquote_close' || t[i].type === 'list_item_close') quoted--;
    else if (t[i].type === 'paragraph_open' && !quoted && !t[i].hidden && t[i + 1]?.type === 'inline') {
      const kids = (t[i + 1].children || []).filter((k) => k.type !== 'text' || k.content.trim());
      const types = kids.map((k) => k.type).join();
      if (types === 'dc_roll_the_die' || types === 'strong_open,dc_roll_the_die,strong_close') addTokenClass(t[i], 'dc-die-call');
    }
  }
}

// ── Declared component: @ladder ─────────────────────────────────────────────
//
// The outcome ladder unfolded: one rung per band, each a `###` whose heading
// ends in its band in parentheses (`### Triumphs (20)`, `(11–19)`, `(6-10)`,
// `(2–5)`, `(1)`; a hyphen, an en dash or `--` all read). The headings stay as
// written; the tier is read from the band, the way the ladder table reads it
// (LADDER_TIER_OF_BAND), and gets the ladder's own colour. A `###` with any
// other ending is not a rung: it is left as it is, and closes the rung before it.

/** `Triumphs (20)`, `Hard Choice (6-10)`, `Success (11–19)` → 'crit' | 'hit' | 'mixed' | 'miss' | 'fail'; any other heading → null. */
function rungTier(text) {
  const m = /\(([^()]*)\)\s*$/.exec(text || '');
  const band = m && parseBand(m[1]);
  if (!band) return null;
  const [lo, hi] = band;
  return LADDER_TIER_OF_BAND[lo === hi ? String(lo) : lo + '-' + hi] || null;
}

// The trailing "(20)" of a rung heading is wrapped in `span.dc-rung-band`, so
// the band can be set in the label face: the display font has no parentheses.
function markRungBand(inline) {
  const kids = inline.children || [];
  const last = kids[kids.length - 1];
  const m = last?.type === 'text' && /^([\s\S]*?)(\([^()]*\))(\s*)$/.exec(last.content);
  if (!m) return;
  const text = (content) => Object.assign(makeToken('text', content), { level: last.level });
  const html = (content) => Object.assign(makeToken('html_inline', content), { level: last.level });
  kids.splice(kids.length - 1, 1, ...(m[1] ? [text(m[1])] : []), html('<span class="dc-rung-band">'), text(m[2]), html('</span>'), ...(m[3] ? [text(m[3])] : []));
}

function dcLadders(state) {
  forEachComponent(state.tokens, 'ladder', (run) => {
    const out = [run[0]];
    let depth = 0; // blocks open at the ladder's own level
    let rung = false;
    const endRung = () => {
      if (!rung) return;
      // a rung's closing bold line is the rung's kicker
      markKickerBefore(out, out.length, 'html_block');
      out.push(makeToken('html_block', '</div>\n</div>\n'));
      rung = false;
    };
    for (let i = 1; i < run.length - 1; i++) {
      const tok = run[i];
      if (depth === 0 && tok.type === 'heading_open' && tok.tag === 'h3') {
        endRung();
        const tier = rungTier(run[i + 1]?.content);
        if (tier) {
          out.push(makeToken('html_block', '<div class="dc-rung ' + tier + '">\n'));
          addTokenClass(tok, 'dc-rung-title');
          markRungBand(run[i + 1]);
          out.push(tok, run[i + 1], run[i + 2], makeToken('html_block', '<div class="dc-rung-body">\n'));
          rung = true;
          i += 2;
          continue;
        }
      }
      depth += tok.nesting;
      out.push(tok);
    }
    endRung();
    out.push(run[run.length - 1]);
    return out;
  });
}

function validateLadder({ blocks }) {
  if (blocks.some((b) => b.type === 'heading' && b.level === 3 && rungTier(b.text))) return [];
  return ['It has no rungs. Each starts with a `###` heading that ends in its band: `### Triumphs (20)`, `(11–19)`, `(6-10)`, `(2–5)`, `(1)`.'];
}

// ── Declared components: @card, @outcome, @procedure ───────────────────────
//
// Declared in `markers` like the three above, rewritten by core rules that
// run BEFORE dcLearningPaths and dcSkillCards: a card, outcome or procedure
// inside a skill must already be in its final form when the skill's rule
// reads it. They stay inside the skill's card (see CARD_CONTENT).
const CARD_CONTENT = new Set(['callout', 'card', 'outcome', 'procedure', 'roll-table', 'field']);

/**
 * `@card`: the wrapper is `div.dc-card` (the declared token itself). Inside it,
 * the first `####` becomes `.dc-card-heading`, a blockquote straight after it
 * becomes `.dc-card-pull`, and everything else goes in `.dc-card-body`; the
 * last blockquote in the body is tagged `.dc-card-footer` (dc#44). A card with
 * nothing after its heading has no body.
 */
function dcCards(state) {
  const md = state.md;
  const html = (text) => makeToken('html_block', text);
  forEachComponent(state.tokens, 'card', (run) => {
    const out = [];
    let headed = false;
    let bodied = false;
    let footer = null;
    const openBody = () => {
      if (!bodied) out.push(html('<div class="dc-card-body">\n'));
      bodied = true;
    };

    const content = run.slice(1, -1);
    for (let i = 0; i < content.length; i++) {
      const tok = content[i];
      if (tok.type === 'heading_open' && tok.tag === 'h4' && !headed) {
        out.push(html('<div class="dc-card-heading">' + renderInlineChildren(content[i + 1], md) + '</div>\n'));
        headed = true;
        i += 2; // skip inline + heading_close
        continue;
      }
      if (tok.type === 'blockquote_open' && headed && !bodied) {
        const quote = quoteHtml(content, i, md);
        out.push(html('<div class="dc-card-pull">' + quote.html + '</div>\n'));
        openBody();
        i = quote.end;
        continue;
      }
      openBody();
      if (tok.type === 'blockquote_open') footer = tok;
      out.push(tok);
    }
    if (footer) addTokenClass(footer, 'dc-card-footer');
    if (bodied) out.push(html('</div>\n'));
    return [run[0], ...out, run[run.length - 1]];
  });
}

/**
 * `@outcome [flush]`: the wrapper is `div.dc-outcomes` (`flush` adds
 * `.dc-flush`). Each `roll | name | text` line becomes a row, coloured by
 * position: crit, hit, mixed, miss, fail.
 */
function dcOutcomes(state) {
  forEachComponent(state.tokens, 'outcome', (run) => {
    const lines = [];
    let depth = 0;
    for (let i = 1; i < run.length - 1; i++) {
      // a row is a line of the outcome's own paragraphs; a list or heading in it is not
      if (run[i].type === 'inline' && depth === 1 && run[i - 1].type === 'paragraph_open') lines.push(...run[i].content.split('\n'));
      depth += run[i].nesting;
    }
    const rows = lines
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith('#'))
      .map((line, i) => {
        const [roll = '', name = '', text = ''] = line.split('|').map((cell) => cell.trim());
        return { tier: OUTCOME_TIERS[i] || 'hit', name, roll, text };
      });
    return [run[0], makeToken('html_block', outcomeRowsHtml(rows, state.md)), run[run.length - 1]];
  });
}

/**
 * A table of the five standard bands (see `ladderRows`) anywhere outside a skill
 * card (the skill rule rewrites those with their card) is the same ladder, so
 * the d20 mechanic reads the same wherever the book states it. A table inside
 * `@roll-table` is not a ladder: its bands are the author's own.
 */
function dcLadderTables(state) {
  const tokens = state.tokens;
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i].type !== 'table_open' || tokens[i].meta?.rollTable) continue;
    const tableTokens = collectTableTokens(tokens, i);
    const ladder = ladderRows(readTable(tableTokens));
    if (!ladder) continue;
    tokens.splice(i, tableTokens.length, makeToken('html_block', buildLadderBlock(ladder, state.md, tokens[i])));
  }
}

/**
 * A table with an HP column and a Damage column is a creature's stat line
 * (`Name | HP | Damage | Traits`, `Type | Size | HP | Damage`): it gets
 * `.dc-stat-strip`, the stat-strip look, wherever it sits, and each cell that
 * holds only a number gets `.dc-stat-num` (the big figures). It is recognised by
 * its shape, not a marker, because a creature's table lives inside a skill's
 * ability text, and a section marker there (`@npc-stat compact`) would end
 * the skill.
 */
function dcStatStrips(state) {
  const tokens = state.tokens;
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i].type !== 'table_open') continue;
    const table = collectTableTokens(tokens, i);
    const head = readTable(table).head.map((cell) => cell.replace(/[*_`]/g, '').trim().toLowerCase());
    if (!head.includes('hp') || !head.includes('damage')) continue;
    addTokenClass(tokens[i], 'dc-stat-strip');
    table.forEach((tok, k) => {
      if (tok.type === 'td_open' && /^\d+$/.test((table[k + 1]?.content || '').trim())) addTokenClass(tok, 'dc-stat-num');
    });
  }
}

/**
 * `@roll-table [die=d12] [label="Wild Magic"]`: a random table in neutral
 * colours. The wrapper is `div.dc-roll-table`; the rule adds the caption (the
 * die chip, d20 unless `die=` says otherwise, and the label) above the author's
 * own pipe table, which stays a plain `<table>`. It is not the outcome ladder:
 * its bands are the author's (`1-4`, `5-8`, ...), all of equal weight.
 */
function dcRollTables(state) {
  forEachComponent(state.tokens, 'roll-table', (run) => {
    const [open, ...rest] = run;
    const attrs = open.meta.attrs || {};
    const die = /^d\d{1,3}$/i.test(attrs.die || '') ? attrs.die.toLowerCase() : 'd20';
    const label = attrs.label ? '<span class="dc-roll-table-name">' + esc(String(attrs.label)) + '</span>' : '';
    const caption = makeToken('html_block', '<div class="dc-roll-table-caption"><span class="dc-roll-table-die">' + esc(die) + '</span>' + label + '</div>\n');
    for (const tok of rest) if (tok.type === 'table_open') tok.meta = { ...tok.meta, rollTable: true };
    return [open, caption, ...rest];
  });
}

function validateRollTable({ blocks }) {
  if (blocks.some((b) => b.type === 'table')) return [];
  return ['It has no table, so nothing is drawn. Write the random table as a pipe table between @roll-table and @end-roll-table.'];
}

/**
 * `@procedure`: every numbered list inside becomes the zero-padded step list
 * (`ol.dc-steps`). The declared wrapper renders nothing itself: the list is
 * the element.
 */
function dcProcedures(state) {
  forEachComponent(state.tokens, 'procedure', (run) => {
    const [open, close] = [run[0], run[run.length - 1]];
    open.hidden = close.hidden = true;
    const out = [];
    let attrs = open.attrs || []; // the first list takes them: an id stays unique
    for (let i = 1; i < run.length - 1; i++) {
      if (run[i].type !== 'ordered_list_open') {
        out.push(run[i]);
        continue;
      }
      const { items, endIndex } = collectListItems(run, i, state.md, state.env);
      if (items.length > 0) {
        out.push(makeToken('html_block', buildProcedureList(items, attrs, state.md)));
        attrs = [];
      }
      i = endIndex;
    }
    return [open, ...out, close];
  });
}

// ── Declared component: @callout (and its alias @dm-note) ──────────────────
//
// `@callout note|warning|dm|vibe|origin|location|visit|example` is a declared wrapper:
// core adds `dc-alert`, the variant's class and any author classes. What core
// cannot know is each variant's default label, so a rule adds it when the
// author wrote no `label="…"`. A missing or unrecognised variant is a plain
// note.

function dcCallouts(state) {
  forEachComponent(state.tokens, 'callout', ([open, ...rest]) => {
    const variant = Object.hasOwn(CALLOUTS, open.meta.variant) ? open.meta.variant : 'note';
    if (variant !== open.meta.variant) {
      // no variant class came from core: the default note keeps its place right after dc-alert
      addTokenClassAfter(open, 'dc-alert', 'dc-note');
    }
    if (open.meta.labelled) return; // an explicit label="…" wins
    // An example that opens with its own heading ("### Example: Toxic Evolution")
    // is titled by it: the heading is set as the example's label, words as
    // written, and no default "Example" is added beside it. Every example then
    // reads the same, a box under one label.
    if (variant === 'example' && rest[0]?.type === 'heading_open') {
      addTokenClass(rest[0], 'dc-alert-label');
      return;
    }
    const label = makeToken('html_block', '<span class="dc-alert-label">' + esc(CALLOUTS[variant].label) + '</span>\n');
    return [open, label, ...rest];
  });
}

/**
 * `@faction megacorp|cabal|cult|enforcer`: core adds the card, the kind class and
 * a badge from `label="…"`. With no label the badge names the kind, as a
 * callout's label names its variant.
 */
function dcFactions(state) {
  forEachComponent(state.tokens, 'faction', ([open, ...rest]) => {
    const kind = open.meta.variant;
    if (open.meta.labelled || !Object.hasOwn(FACTION_KINDS, kind)) return;
    return [open, makeToken('html_block', '<span class="dc-faction-kind">' + esc(FACTION_KINDS[kind]) + '</span>\n'), ...rest];
  });
}

// `variant=` was the old way to pick one; it now reads as a plain attribute
// and would silently render a note, so say so once, on the marker's line.
function validateCallout({ attrs }) {
  if (attrs.variant === undefined) return [];
  return [`no longer takes variant=${attrs.variant}; write "@callout ${attrs.variant}" instead.`];
}

/**
 * Structure checks (core runs these on the declared markers below and reports
 * them as layout warnings). They are the plugin's rules, not core's: core
 * only knows that declared markers nest.
 */
function validateSpecialty({ blocks }) {
  // One problem per run of skills sitting directly in the specialty: the
  // first skill after a learning path (or at the start). The usual cause is a
  // single early `@end-learning-path`, which strands every skill after it.
  const components = blocks.filter((b) => b.type === 'component');
  return components
    .filter((b, i) => b.name === 'skill' && components[i - 1]?.name !== 'skill')
    .map((b) => ({
      line: b.line,
      message:
        'This skill (and any right after it) is outside a learning path. If an `@end-learning-path` above it ' +
        'closed the path early, remove that line; otherwise move the skills into a `@learning-path`.',
    }));
}

function validateSkill({ blocks }) {
  return blocks
    .filter((b) => b.type === 'component' && (b.name === 'learning-path' || b.name === 'specialty'))
    .map((b) => ({
      line: b.line,
      message:
        `This @${b.name} starts inside the skill above it, so it is nested in that skill's card. ` +
        `Close the skill with \`@end-skill\` before it.`,
    }));
}

const GEAR_KINDS = ['augment', 'treasure', 'vehicle', 'drug', 'program'];

// A bare `@gear` (or an unrecognised word, which core reports) is general gear:
// core added only the shared card, so the general-gear class goes right after it.
function dcGear(state) {
  forEachComponent(state.tokens, 'gear', ([open]) => {
    if (GEAR_KINDS.includes(open.meta.variant)) return;
    addTokenClassAfter(open, 'dc-entry', 'dc-gear');
  });
}

// A paragraph in an entry that is only one bold run is its cost line
// (`**1 AP. ATTACK PROGRAM, 2 SesHP**`, a price): `.dc-entry-cost`, stamped as a tag.
// A paragraph with a bold run and other text is body text.
function dcEntryCosts(state) {
  forEachComponent(state.tokens, 'gear', (run) => {
    let depth = 0;
    run.forEach((tok, i) => {
      if (depth === 1 && tok.type === 'paragraph_open' && isBoldOnlyInline(run[i + 1])) addTokenClass(tok, 'dc-entry-cost');
      depth += tok.nesting;
    });
  });
}

/**
 * Entry cards (`@gear` and its kinds `augment`, `treasure`, `vehicle`, `drug`, `program`):
 * one entry is one name. The name is the entry's first heading (`####`, or
 * `###`). An entry without one has no title bar, and one with a second heading
 * is usually two entries run together: a declared marker that opens again
 * closes the one before it, so each entry starts with its own marker line.
 */
function validateEntry({ name, blocks }) {
  const headings = blocks.filter((b) => b.type === 'heading' && b.level <= 4);
  if (!headings.length) {
    return [`This @${name} has no name. Start it with a \`#### Name\` heading.`];
  }
  return headings.slice(1).map((b) => ({
    line: b.line,
    message: `"${b.text}" is a second name inside this @${name}. Put each entry under its own @${name} line.`,
  }));
}

// ── Declared component: @field (and the bold labels that mean it) ──────────
//
// `@field specs` … `@end-field` is a labelled field: `div.dc-field.dc-field-specs`
// holding `span.dc-field-label` and the author's paragraphs. The label is the
// variant's default (below) or `label="…"`, the way `@callout` does it.
//
// The bold-label shortcut is the same component written shorter: a paragraph
// that opens with a known label (`**SPECS:** …`), inside an entry card, an NPC
// stat block or a skill card, is rewritten to exactly the markup the marker
// gives (`dcFieldLines`), so one set of rules styles both. Everywhere else it
// stays a paragraph, and a callout inside a card is not a card.
//
// FIELD_LABELS is the one table. Each line is a label as the books write it
// (matched case-insensitively, colon inside the bold) and the variant it
// means. A new label is a line here; a new field type is a new variant name
// here plus a token-setter rule in styles/components/entries.css. The first
// label listed for a variant is that variant's default label.
const FIELD_LABELS = {
  'SPECS': 'specs',
  'Traits': 'traits',
  'Equipment': 'equipment',
  'Effects': 'effects',
  'Side Effects': 'side-effects',
  'Requires': 'requires',
  'Wirephreak Gear': 'requires',
  'Cybersurgeon Instrument': 'requires',
  'Cybersurgeon Instruments': 'requires',
  'Cybersurgeon Instrument(s)': 'requires',
  'TECHNOENHANCEMENT': 'requires',
};
const FIELD_VARIANTS = [...new Set(Object.values(FIELD_LABELS))];
const FIELD_DEFAULT_LABEL = Object.fromEntries(
  FIELD_VARIANTS.map((v) => [v, Object.keys(FIELD_LABELS).find((l) => FIELD_LABELS[l] === v)]),
);
const FIELD_BY_LABEL = new Map(Object.entries(FIELD_LABELS).map(([label, v]) => [label.toLowerCase(), v]));

// The cards whose paragraphs may be field lines.
const FIELD_HOSTS = new Set(['gear', 'skill']);

const fieldLabelHtml = (label) => '<span class="dc-field-label">' + esc(label) + '</span>\n';

// An explicit `@field specs` with no `label="…"` gets the variant's default label.
function dcFields(state) {
  forEachComponent(state.tokens, 'field', ([open, ...rest]) => {
    const label = FIELD_DEFAULT_LABEL[open.meta.variant];
    if (open.meta.labelled || !label) return; // an explicit label wins; a bare @field has none
    return [open, makeToken('html_block', fieldLabelHtml(label)), ...rest];
  });
}

function isFieldHost(open) {
  if (FIELD_HOSTS.has(open.meta?.kind)) return true;
  // `@npc-stat` and `@section npc` are one section; its class is the record (`@section npc` carries no kind)
  return hasClass(open, 'dc-npc-stat');
}

/** `**Label:** …` → { label, variant }, or null when the paragraph does not open with a known label. */
function fieldLabelOf(inline) {
  // core leaves an empty text node ahead of a leading `**…**`
  const lead = inline?.children?.[0]?.type === 'text' && !inline.children[0].content ? 1 : 0;
  const [open, text, close] = inline?.children?.slice(lead) ?? [];
  if (open?.type !== 'strong_open' || text?.type !== 'text' || close?.type !== 'strong_close') return null;
  const written = text.content.trim();
  if (!written.endsWith(':')) return null;
  const label = written.slice(0, -1).trim();
  const variant = FIELD_BY_LABEL.get(label.toLowerCase());
  return variant ? { label, variant, lead } : null;
}

function dcFieldLines(state) {
  const tokens = state.tokens;
  const out = [];
  const hosts = []; // one entry per open layout container: is its content a field host?
  let quoted = 0; // inside a blockquote or a list item, a paragraph is not a field line
  for (let i = 0; i < tokens.length; i++) {
    const tok = tokens[i];
    if (/^layout_.+_open$/.test(tok.type)) {
      // `@columns` only arranges its content: the container around it still decides
      hosts.push(tok.meta?.kind === 'columns' ? hosts.at(-1) ?? false : isFieldHost(tok));
    } else if (/^layout_.+_close$/.test(tok.type)) {
      hosts.pop();
    } else if (tok.type === 'blockquote_open' || tok.type === 'list_item_open') {
      quoted++;
    } else if (tok.type === 'blockquote_close' || tok.type === 'list_item_close') {
      quoted--;
    } else if (tok.type === 'paragraph_open' && !quoted && hosts.at(-1)) {
      const inline = tokens[i + 1];
      const field = fieldLabelOf(inline);
      if (field) {
        // Same markup as `@field <variant> label="…"`: the label is the author's own words.
        out.push(makeToken('html_block',
          '<div class="dc-field dc-field-' + field.variant + '" data-field="' + field.variant + '"' +
          ' data-label="' + esc(field.label) + '">' + fieldLabelHtml(field.label)));
        inline.children.splice(0, field.lead + 3);
        const first = inline.children[0];
        if (first?.type === 'text') first.content = first.content.replace(/^\s+/, '');
        inline.content = inline.content.replace(/^\*\*[^*]+\*\*\s*/, '');
        const bare = inline.children.every((c) => c.type === 'text' && !c.content); // the label was all there was
        const rest = bare ? [] : tokens.slice(i, i + 3);
        out.push(...rest, makeToken('html_block', '</div>\n'));
        i += 2; // the paragraph's inline and close
        continue;
      }
    }
    out.push(tok);
  }
  state.tokens = out;
}

function validateOutcome({ blocks }) {
  const problems = [];
  let rows = 0;
  for (const block of blocks) {
    if (block.type !== 'paragraph') {
      problems.push({
        line: block.line,
        message: `Only lines written as \`roll | name | text\` are used here, so this ${block.type} is left out.`,
      });
      continue;
    }
    block.text.split('\n').forEach((raw, k) => {
      const row = raw.trim();
      if (!row || row.startsWith('#')) return;
      rows++;
      if (row.split('|').length < 3) {
        problems.push({
          line: block.line + k,
          message: `"${row.length > 40 ? row.slice(0, 40) + '…' : row}" is not a row. Write each one as \`roll | name | text\`, for example \`20 | Crit | You flow.\``,
        });
      }
    });
  }
  if (!rows && !problems.length) problems.push('This outcome has no rows. Add one `roll | name | text` line per result.');
  return problems;
}

function validateProcedure({ blocks }) {
  if (blocks.some((b) => b.type === 'list' && b.ordered)) return [];
  return ['It has no numbered list, so no steps are drawn. Write the steps as `1.`, `2.`, `3.` between @procedure and @end-procedure.'];
}

/**
 * Main plugin function - the default export Gutterpress loads
 */
// ── Raw HTML in the markdown ────────────────────────────────────────────────
//
// HTML an author writes into the markdown is reported, one warning per tag, on
// its line: the package cannot check it, and a stray tag does damage far from
// where it is written (`<small>…<small>` in one ladder row set the rest of a
// book small). Write markdown or a marker instead. An HTML comment is not
// reported: it renders nothing. Runs first, before any rule of this plugin
// rewrites a table or adds HTML of its own, so only the author's is seen.
// `rawHtml: 'off'` in the extension's options turns it off for a book that
// means its HTML (the design guide's specimen stages).
function rawHtmlWarnings(state) {
  const report = (tok, line) => {
    const html = tok.content.trim();
    if (!html || html.startsWith('<!--')) return;
    const tag = (/^<\/?[a-zA-Z][a-zA-Z0-9-]*/.exec(html) || [html.slice(0, 20)])[0];
    (state.env.layoutWarnings ??= []).push({
      line,
      type: 'raw_html',
      message: `Raw HTML (${tag}${html.startsWith('</') ? '' : '…'}>): write markdown or a marker instead. The package cannot check HTML, and a tag left open styles everything after it.`,
    });
  };
  // Only what is written in the source counts: Gutterpress adds HTML of its own
  // (a marker's label="…"), which is not on the author's line.
  const lines = state.src.split('\n');
  const written = (map, html) => map && lines.slice(map[0], map[1]).join('\n').includes(html.trim().slice(0, 12));
  let near = null; // a table cell's inline has no map of its own: its row's is the nearest
  for (const tok of state.tokens) {
    if (tok.map) near = tok.map;
    if (tok.type === 'html_block' && written(tok.map, tok.content)) report(tok, tok.map[0] + 1);
    else if (tok.type === 'inline') {
      for (const child of tok.children || []) if (child.type === 'html_inline' && written(near, child.content)) report(child, near[0] + 1);
    }
  }
}

// ── Steps: a numbered `##` standing on the page ─────────────────────────────
//
// A `##` that stands on the page (in no section or component) and opens with a
// step number, `## 4. Ideal`, is a step of the book's procedure (the Citizen
// File's 0-7). Its number, written as it is, goes in `span.dc-step-num`, which
// the page slip sets as a chip in the chapter's colour, so the steps read as one
// sequence. The heading keeps no class of its own, so it stays the slip.
function dcSteps(state) {
  let depth = 0;
  const t = state.tokens;
  for (let i = 0; i < t.length; i++) {
    const tok = t[i];
    if (tok.type === 'layout_section_open' || tok.type === 'layout_component_open') depth++;
    else if (tok.type === 'layout_section_close' || tok.type === 'layout_component_close') depth--;
    else if (depth === 0 && tok.type === 'heading_open' && tok.tag === 'h2' && !tok.attrGet('class')) {
      const first = t[i + 1]?.children?.[0];
      const m = first?.type === 'text' && /^(\d{1,2}\.)\s+/.exec(first.content);
      if (!m) continue;
      const num = makeToken('html_inline', '<span class="dc-step-num">' + esc(m[1]) + '</span> ');
      first.content = first.content.slice(m[0].length);
      t[i + 1].children.unshift(num);
    }
  }
}

// ── Paste-up: rows and continuation sheets ──────────────────────────────────
//
// A sheet says its own width: `.dc-half`, `.dc-narrow` (38%) or `.dc-wide` (62%)
// on its section line. Two sheets side by side are a row: when a sheet
// with a width is followed straight away by one whose width completes it (half
// and half, narrow and wide, wide and narrow), the plugin wraps the two in
// `div.dc-pu-row`, and section.css reads the widths off them. There is no row
// marker to write. A sheet with a width and no partner is reported, and prints
// at the full width.
const PU_WIDTHS = { 'dc-half': 50, 'dc-narrow': 38, 'dc-wide': 62 };

function widthOf(tok) {
  if (tok?.type !== 'layout_section_open') return 0;
  const cls = classesOf(tok).find((c) => c in PU_WIDTHS);
  return cls ? PU_WIDTHS[cls] : 0;
}

function dcRows(state) {
  const t = state.tokens;
  const ends = new Map(); // a section's open index → its close index
  const stack = [];
  t.forEach((tok, i) => {
    if (tok.type === 'layout_section_open') stack.push(i);
    else if (tok.type === 'layout_section_close') ends.set(stack.pop(), i);
  });
  const out = [];
  for (let i = 0; i < t.length; i++) {
    const width = widthOf(t[i]);
    if (!width) {
      out.push(t[i]);
      continue;
    }
    const firstEnd = ends.get(i);
    const next = firstEnd + 1;
    if (firstEnd !== undefined && widthOf(t[next]) === 100 - width && ends.has(next)) {
      const secondEnd = ends.get(next);
      out.push(makeToken('html_block', '<div class="dc-pu-row">\n'), ...t.slice(i, secondEnd + 1), makeToken('html_block', '</div>\n'));
      i = secondEnd;
      continue;
    }
    (state.env.layoutWarnings ??= []).push({
      line: t[i].map ? t[i].map[0] + 1 : t[i].meta?.line ?? t[i].meta?.__line ?? 0,
      type: 'row_unpaired',
      message: 'This sheet has a width (.dc-half, .dc-narrow or .dc-wide) but the sheet straight after it does not complete the row, so it prints full width. Give the next sheet the other half (.dc-half), or the other side of 38/62 (.dc-wide after .dc-narrow, .dc-narrow after .dc-wide).',
    });
    out.push(t[i]);
  }
  state.tokens = out;
}

// `@section … .dc-pu-cont` is a sheet that carries on from the one before it,
// so it has no title tag. Its first `##` or `###` would otherwise be read as the
// sheet's title (every `:first-child` heading rule in the package), so the plugin
// puts a zero-height `.dc-pu-spacer` ahead of it and the heading stays a sub-head.
// The author writes nothing extra.
const PU_SPACER = '<div class="dc-pu-spacer"></div>\n';

function dcContinuations(state) {
  const t = state.tokens;
  for (let i = 0; i < t.length; i++) {
    if (t[i].type !== 'layout_section_open') continue;
    if (!hasClass(t[i], 'dc-pu-cont')) continue;
    const next = t[i + 1];
    if (next?.type !== 'heading_open' || !['h2', 'h3'].includes(next.tag)) continue;
    t.splice(i + 1, 0, makeToken('html_block', PU_SPACER));
  }
}

// ── Neon signs ──────────────────────────────────────────────────────────────
// A sign is the city's own fixture, not the pack's paper (docs/plans/
// 2026-11-11-neon-signage.md). It is placed, never written: a chapter opener
// (`@page chapter-start` in an `@chapter <word>`) whose title banner comes
// first hangs one above the banner, spelling its chapter's word (an opener
// that starts with a sheet, such as a fiction excerpt, has no headroom for
// one), and a specialty's art page (`@specialty-art`) hangs one
// spelling the specialty. The word is drawn four times as SVG paths, stacked
// (outer ring, inner ring, tube, core): stroked text would print as a Type 3
// font, which the PDF/X build flattens to an image. One letter of each sign
// is a dead tube. The Dream Master's sign is mostly dark: only the D and the
// M are lit.
const NEON_CHAPTER_WORDS = { rules: 'RULES', dm: 'DREAM MASTER', gear: 'GEAR', 'citizen-file': 'CITIZEN FILE' };
const NEON_LAYERS = ['dc-neon-ring-2', 'dc-neon-ring-1', 'dc-neon-tube', 'dc-neon-core'];

/** Letter indexes left unlit: all but D and M on the DM's sign, else one letter picked from the word. */
function neonDeadLetters(word) {
  const letters = [...word].map((c, i) => (c === ' ' ? -1 : i)).filter((i) => i > 0);
  if (word === 'DREAM MASTER') return new Set(letters.filter((i) => i !== 6));
  const sum = [...word].reduce((n, c) => n + c.charCodeAt(0), 0);
  return new Set([letters[sum % letters.length]]);
}

// BEGIN NEON_FONT (generated by scripts/neon-glyphs.py; do not edit)
// Tomorrow 400's capitals (SIL OFL, fonts/tomorrow/OFL.txt) as SVG paths:
// font units, y down, baseline at 0.
const NEON_FONT = {
  upm: 1000,
  cap: 737,
  glyphs: {
  'A': { w: 667, d: 'M14 0 263 -737H404L653 0H558L495 -192H172L110 0ZM199 -272H469L345 -651H322Z' },
  'B': { w: 690, d: 'M87 0V-737H482L586 -632V-459L540 -397L625 -311V-105L520 0ZM178 -428H453L495 -485V-601L441 -657L178 -656ZM178 -81H479L534 -136V-287L476 -347H178Z' },
  'C': { w: 647, d: 'M173 0 68 -105V-632L173 -737H506L608 -635L550 -576L470 -656H214L159 -601V-136L214 -81H478L559 -162L617 -103L513 0Z' },
  'D': { w: 705, d: 'M87 0V-737H487L640 -582V-155L487 0ZM178 -81H446L549 -186V-551L446 -656H178Z' },
  'E': { w: 625, d: 'M87 0V-737H573V-653H178V-429H531V-346H178V-84H573V0Z' },
  'F': { w: 577, d: 'M87 0V-737H562V-653H178V-415H515V-332H178V0Z' },
  'G': { w: 711, d: 'M171 0 68 -105V-632L173 -737H523L625 -635L567 -576L487 -656H214L159 -601V-136L214 -81H435L549 -187V-307H379V-387H625V0H549V-85L458 0Z' },
  'H': { w: 720, d: 'M87 0V-737H178V-428H543V-737H634V0H543V-347H178V0Z' },
  'I': { w: 395, d: 'M62 0V-84H152V-653H62V-737H333V-653H243V-84H333V0Z' },
  'J': { w: 577, d: 'M154 0 50 -105V-274H141V-136L196 -81H345L400 -136V-737H491V-105L386 0Z' },
  'K': { w: 656, d: 'M87 0V-737H178V-344L526 -737H634L358 -421L639 0H530L295 -350L178 -216V0Z' },
  'L': { w: 559, d: 'M87 0V-737H178V-84H549V0Z' },
  'M': { w: 887, d: 'M87 0V-737H211L443 -148L676 -737H801V0H709V-598L469 0H418L178 -597V0Z' },
  'N': { w: 718, d: 'M87 0V-737H211L540 -144V-737H631V0H523L200 -582H178V0Z' },
  'O': { w: 694, d: 'M173 0 68 -105V-632L173 -737H521L626 -632V-105L521 0ZM214 -81H480L535 -136V-601L480 -656H214L159 -601V-136Z' },
  'P': { w: 610, d: 'M87 0V-737H476L580 -632V-379L476 -274H178V0ZM178 -355H435L489 -410V-601L435 -657L178 -656Z' },
  'Q': { w: 694, d: 'M307 102V0H173L68 -105V-632L173 -737H521L626 -632V-105L521 0H387V102ZM214 -81H307V-187H387V-81H480L535 -136V-601L480 -656H214L159 -601V-136Z' },
  'R': { w: 677, d: 'M87 0V-737H490L594 -632V-397L490 -292H487L620 0H519L388 -292H178V0ZM178 -373H449L503 -428V-601L449 -656H178Z' },
  'S': { w: 658, d: 'M88 0V-84H451L505 -139V-286L451 -341H166L62 -445V-632L166 -737H558V-653H207L152 -598L153 -476L207 -421H492L596 -316V-105L492 0Z' },
  'T': { w: 555, d: 'M232 0V-653H13V-737H542V-653H323V0Z' },
  'U': { w: 703, d: 'M178 0 73 -105V-737H164V-136L219 -81H484L539 -136V-737H630V-105L525 0Z' },
  'V': { w: 666, d: 'M263 0 13 -737H109L322 -87H344L557 -737H653L403 0Z' },
  'W': { w: 909, d: 'M194 0 13 -737H109L254 -87H276L413 -737H496L633 -87H655L800 -737H896L715 0H572L454 -544L337 0Z' },
  'X': { w: 632, d: 'M13 0 235 -377 15 -737H118L304 -427H328L514 -737H618L397 -377L619 0H515L328 -324H305L118 0Z' },
  'Y': { w: 633, d: 'M271 0V-295L13 -737H117L306 -401H326L516 -737H619L362 -295V0Z' },
  'Z': { w: 663, d: 'M72 0V-92L469 -631V-653H93V-737H587V-645L191 -106V-84H591V0Z' },
  ' ': { w: 222, d: '' },
  },
};
// END NEON_FONT

const NEON_TRACKING = 160; // letter spacing, font units (0.16em)

/** The sign's HTML: an ink plate and one SVG of the word's letters as paths
 * (NEON_FONT), four layers back to front; the dead letters are a fifth. */
function neonSign(word) {
  const { cap, upm, glyphs } = NEON_FONT;
  const dead = neonDeadLetters(word);
  const letters = [];
  let x = 0;
  [...word].forEach((c, i) => {
    const g = glyphs[c];
    if (!g) return;
    if (g.d) letters.push({ x, d: g.d, dead: dead.has(i) });
    x += g.w + NEON_TRACKING;
  });
  const w = x - NEON_TRACKING;
  const layer = (cls, set) => `<g class="${cls}">` +
    set.map((l) => `<path transform="translate(${l.x} 0)" d="${l.d}"/>`).join('') + '</g>';
  const lit = letters.filter((l) => !l.dead);
  const off = letters.filter((l) => l.dead);
  const svg = NEON_LAYERS.map((cls) => layer(cls, lit)).join('') + (off.length ? layer('dc-neon-dead', off) : '');
  const em = (n) => +(n / upm).toFixed(3);
  return `<div class="dc-neon" aria-hidden="true"><svg class="dc-neon-word" xmlns="http://www.w3.org/2000/svg" ` +
    `width="${em(w)}em" height="${em(cap)}em" viewBox="0 ${-cap} ${w} ${cap}">${svg}</svg></div>\n`;
}

function dcNeonSigns(state) {
  const t = state.tokens;
  let chapterWord = null;
  const components = []; // the declared components around the token: their kind, and a specialty's name
  for (let i = 0; i < t.length; i++) {
    const tok = t[i];
    if (tok.type === 'layout_chapter_open') {
      chapterWord = classesOf(tok).find((c) => c.startsWith('dc-chapter-'))?.slice('dc-chapter-'.length) ?? null;
    } else if (tok.type === 'layout_chapter_close') {
      chapterWord = null;
    } else if (tok.type === 'layout_page_open' && hasClass(tok, 'dc-page-chapter-start') && NEON_CHAPTER_WORDS[chapterWord] &&
               t[i + 1]?.type === 'heading_open' && t[i + 1].tag === 'h1') {
      t.splice(++i, 0, makeToken('html_block', neonSign(NEON_CHAPTER_WORDS[chapterWord])));
    } else if (tok.type === 'layout_component_open') {
      const kind = tok.meta?.kind;
      const specialty = kind === 'specialty' ? classesOf(tok).find((c) => SPECIALTIES.includes(c)) ?? null : null;
      components.push({ kind, specialty });
      if (kind === 'specialty-art') {
        const name = components.findLast((c) => c.kind === 'specialty')?.specialty;
        if (name) t.splice(++i, 0, makeToken('html_block', neonSign(name.toUpperCase())));
      }
    } else if (tok.type === 'layout_component_close') {
      components.pop();
    }
  }
}

export default function dimmCityPlugin(md, options = {}) {
  Token ??= new md.core.State('', md, {}).Token;
  registerSkillContinueBridge(md);

  // GFM-style `> [!NOTE]` alerts. Registered on the core ruler since the
  // transform operates on already-parsed token streams.
  if (options.rawHtml !== 'off') md.core.ruler.push('dc_raw_html', rawHtmlWarnings);
  md.core.ruler.push('dc_alerts', dcAlertsTransform);
  md.core.ruler.push('dc_rows', dcRows);
  md.core.ruler.push('dc_steps', dcSteps);
  md.core.ruler.push('dc_continuations', dcContinuations);
  md.core.ruler.push('dc_neon_signs', dcNeonSigns);

  // Transform the canonical roll instruction while it is still structured
  // inline content. This covers every markdown context without rewriting
  // rendered HTML, code spans, raw HTML, or partial words.
  md.renderer.rules.dc_roll_the_die = (tokens, idx) =>
    '<span class="dc-roll-the-die">' + esc(tokens[idx].content) + '</span>';
  md.core.ruler.push('dc_roll_the_die', dcRollDieTransform);
  md.core.ruler.push('dc_die_calls', dcDieCalls);

  md.core.ruler.push('dc_specialty_card_positions', dcSpecialtyCardPositions);

  // Mark image-only paragraphs so layout rules can target them without
  // relying on p:has(img). The base CSS rule
  // (p.dc-img-wrapper { padding:0; margin:0 }) lives in components/data.css.
  // Per-page rules can further refine position via .page.my-class p.dc-img-wrapper.
  md.core.ruler.push('dc_image_paragraphs', dcImageParagraphs);
  md.core.ruler.push('dc_front_matter_titles', dcFrontMatterTitles);

  // Declared components. Callouts, cards, outcomes and procedures go first so
  // one inside a skill is already rewritten when the skill's rule looks at it.
  md.core.ruler.push('dc_callouts', dcCallouts);
  md.core.ruler.push('dc_factions', dcFactions);
  md.core.ruler.push('dc_gear', dcGear);
  md.core.ruler.push('dc_entry_costs', dcEntryCosts);
  md.core.ruler.push('dc_fields', dcFields);
  md.core.ruler.push('dc_cards', dcCards);
  md.core.ruler.push('dc_outcomes', dcOutcomes);
  md.core.ruler.push('dc_roll_tables', dcRollTables);
  md.core.ruler.push('dc_procedures', dcProcedures);
  md.core.ruler.push('dc_learning_paths', dcLearningPaths);
  md.core.ruler.push('dc_skill_cards', dcSkillCards);
  md.core.ruler.push('dc_ladders', dcLadders);
  md.core.ruler.push('dc_kickers', dcKickers);
  md.core.ruler.push('dc_ladder_tables', dcLadderTables);
  md.core.ruler.push('dc_stat_strips', dcStatStrips);
  md.core.ruler.push('dc_field_lines', dcFieldLines);
}

/**
 * Declared markers — plain data Gutterpress core reads off this module (the
 * same relationship `metadata` has). Core parses `@name … @end-name`, merges
 * author classes, threads `data-source-range`, nests containers as a stack and
 * closes them at the next `@page`/`@section`/`@chapter`, so none of this is
 * hand-written in a marker parser. A bare markdown-it instance never
 * reads this table: declared markers exist only under Gutterpress.
 *
 * A `section: true` entry declares a section-styled component: core treats it
 * as a real `@section` carrying the entry's classes (see below).
 *
 * To add a plain wrapper, add one line here (element + classes), a snippet in
 * `snippets/<name>.md`, and the usual catalog/guide entries — see
 * docs/adding-macros.md.
 *
 * Variants are a bare word on the marker line (`@block panel`) and only add
 * a class, so class shorthand (`@block .dc-panel`) keeps working beside them.
 * `autoCloseAt: ['eof']` keeps these silent at end-of-document: they have
 * never needed an explicit `@end-…`.
 */
const wrapper = (cls, extra = {}) => ({ class: cls, autoCloseAt: ['eof'], ...extra });

const FACTION_KINDS = { megacorp: 'Megacorp', cabal: 'Cabal', cult: 'Cult', enforcer: 'Enforcer' };

export const markers = {
  // Specialty > learning path > skill. Core nests them as a stack; the rules
  // above rewrite their content and `validate` checks their structure.
  // `@specialty augmerc` and `@specialty .augmerc` both add the class the
  // styles key on (`.dc-specialty.augmerc`).
  specialty: wrapper('dc-specialty', {
    variants: Object.fromEntries(SPECIALTIES.map((name) => [name, name])),
    validate: validateSpecialty,
  }),
  'learning-path': wrapper('dc-learning-path dc-path-block'),
  skill: wrapper('dc-skill-card', { validate: validateSkill }),

  // Content components. `@card` closes silently at the end of a document.
  // `@outcome` and `@procedure` carry no `autoCloseAt`, so one left
  // open at the end gets core's `declared_marker_eof_close` warning: what
  // follows an open one is read as its rows or its steps. `@procedure` has no
  // class (its rule hides the wrapper: the step list is the element).
  card: wrapper('dc-card'),
  outcome: { class: 'dc-outcomes', variants: { flush: 'dc-flush' }, validate: validateOutcome },
  procedure: { validate: validateProcedure },
  'roll-table': wrapper('dc-roll-table', { validate: validateRollTable }),
  ladder: wrapper('dc-ladder', { validate: validateLadder }),

  // `@callout` takes its variant as a bare word (`@callout vibe`); `@dm-note` is
  // the same marker with the `dm` variant preset. A default label comes from
  // `dcCallouts`, an explicit `label="…"` from core.
  callout: wrapper('dc-alert', {
    variants: Object.fromEntries(Object.entries(CALLOUTS).map(([name, { class: cls }]) => [name, cls])),
    label: { tag: 'span', class: 'dc-alert-label', from: 'attr:label' },
    validate: validateCallout,
  }),
  'dm-note': { alias: 'callout', preset: { variant: 'dm' } },

  // A labelled field (`@field specs`), and the target of the bold-label shortcut
  // (`**SPECS:** …` inside a card, see FIELD_LABELS). The default label per
  // variant comes from `dcFields`, an explicit `label="…"` from core.
  field: wrapper('dc-field', {
    variants: Object.fromEntries(FIELD_VARIANTS.map((v) => [v, 'dc-field-' + v])),
    label: { tag: 'span', class: 'dc-field-label', from: 'attr:label' },
  }),

  // A term, or a glossary. `lucid` and `surreal` are the two states of a roll,
  // set as opposites (light, crisp, aligned / dark, skewed, off-register).
  definition: wrapper('dc-prose-panel dc-definition-block', {
    variants: { lucid: 'dc-definition-lucid', surreal: 'dc-definition-surreal' },
  }),
  'specialty-intro': wrapper('dc-specialty-intro'),
  'specialty-art': wrapper('dc-specialty-art'),
  'specialty-card': wrapper('dc-specialty-card'),
  // Entry cards: one card family (`.dc-entry`); `@gear` is general gear and its
  // bare word picks a kind, a token setter on that family
  // (styles/components/entries.css). Each starts with the entry's name.
  gear: wrapper('dc-card dc-entry', {
    variants: Object.fromEntries(GEAR_KINDS.map((kind) => [kind, `dc-${kind}`])),
    validate: validateEntry,
  }),
  // An organization's profile: a card with a kind badge. The kind is the bare
  // word (`@faction cult`) and the badge reads it unless `label="…"` names its own.
  faction: wrapper('dc-card dc-faction', {
    variants: Object.fromEntries(Object.keys(FACTION_KINDS).map((kind) => [kind, `dc-faction-${kind}`])),
    label: { tag: 'span', class: 'dc-faction-kind', from: 'attr:label' },
  }),
  toc: wrapper('dc-toc'),
  lede: wrapper('dc-intro'),
  block: wrapper('dc-block', {
    variants: { panel: 'dc-panel', slate: 'dc-slate', shard: 'dc-shard' },
    label: { tag: 'div', class: 'dc-block-title', from: 'attr:label' },
  }),

  // Section variants: `@section panel` is `<div class="section dc-section-panel">`.
  // A bare `@section` is core's plain box and gets no styling from this package.
  // `panel` and `flat` are general. `reference`, `lore`, `dm` and `choose` are
  // panels that say what kind of text they hold (a look-up, the world, advice
  // for the Dream Master, a choice): each is `dc-section-panel` plus a class that
  // sets the panel's tokens, and has no marker of its own. The rest are the
  // section-styled components below, each reachable by its own marker
  // (`@npc-stat`) or by word (`@section npc`), and both write the same classes so
  // one CSS rule serves both. A component that is a card (npc, walkthrough, flaws,
  // ideals, dreams) carries `dc-section-panel` beside its own class (the three
  // choice runs are `choose` too); fiction and cards are not panels. The CSS is
  // in styles/components/section.css.
  section: {
    variants: {
      panel: 'dc-section-panel',
      flat: 'dc-section-flat',
      reference: 'dc-section-panel dc-section-reference',
      lore: 'dc-section-panel dc-section-lore',
      dm: 'dc-section-panel dc-section-dm',
      choose: 'dc-section-panel dc-section-choose',
      catalog: 'dc-section-panel dc-catalog',
      weapons: 'dc-section-panel dc-catalog dc-section-weapons',
      explosives: 'dc-section-panel dc-catalog dc-section-explosives',
      armor: 'dc-section-panel dc-catalog dc-section-armor',
      npc: 'dc-section-panel dc-npc-stat',
      fiction: 'dc-fiction-excerpt',
      walkthrough: 'dc-section-panel dc-citizen-walkthrough',
      cards: 'dc-card-grid',
      flaws: 'dc-section-panel dc-section-choose dc-flaws',
      ideals: 'dc-section-panel dc-section-choose dc-ideals',
      dreams: 'dc-section-panel dc-section-choose dc-dreams',
    },
  },

  // Locations: where the content sits. A location only adjusts components, by
  // setting tokens (styles/page-templates.css); it never supplies chrome of its
  // own. `@page chapter-start` is `<div class="page dc-page-chapter-start">`;
  // `@chapter rules` is `<div class="chapter dc-chapter-rules">` (any other word
  // after `@chapter` stays its label). Core also ships `@page blank` and
  // `@page full-bleed`.
  page: {
    variants: {
      'chapter-start': 'dc-page-chapter-start',
      intro: 'dc-page-intro',
      credits: 'dc-page-credits',
      contents: 'dc-page-contents',
      'citizen-file': 'dc-page-citizen-file',
      'specialty-catalog': 'dc-page-specialty-catalog',
      // Stone walls instead of the brick (page-rules.css, dc-native.css §2d).
      'wall-1': 'dc-page-wall-1',
      'wall-2': 'dc-page-wall-2',
      'wall-3': 'dc-page-wall-3',
      'wall-4': 'dc-page-wall-4',
      'wall-5': 'dc-page-wall-5',
      'wall-6': 'dc-page-wall-6',
    },
  },
  chapter: {
    variants: {
      rules: 'dc-chapter-rules',
      lore: 'dc-chapter-lore',
      'citizen-file': 'dc-chapter-citizen-file',
      specialty: 'dc-chapter-specialty',
      dm: 'dc-chapter-dm',
      gear: 'dc-chapter-gear',
    },
  },

  // Section-styled components. `section: true` makes each one a real core
  // @section: `@npc-stat` is exactly `@section npc` (same element, same
  // classes). None is styled per specialty (that lives on
  // `.dc-specialty.<name>`, from `@specialty`); the only variant is
  // `@npc-stat compact`, and modifiers such as `.dc-snug`, `.dc-avoid-split`
  // and `.gp-columns-2` stay author classes.
  'card-grid': { section: true, class: 'dc-card-grid' },
  'citizen-walkthrough': { section: true, class: 'dc-section-panel dc-citizen-walkthrough' },
  'fiction-excerpt': { section: true, class: 'dc-fiction-excerpt' },
  'npc-stat': { section: true, class: 'dc-section-panel dc-npc-stat', variants: { compact: 'dc-npc-compact' } },
  // Citizen-file choices: `@section choose` with the class that sets the accent
  // of every `@card` inside (`@flaws`, `@ideals`, `@dreams` are `choose` plus their own).
  flaws: { section: true, class: 'dc-section-panel dc-section-choose dc-flaws' },
  ideals: { section: true, class: 'dc-section-panel dc-section-choose dc-ideals' },
  dreams: { section: true, class: 'dc-section-panel dc-section-choose dc-dreams' },
};

/**
 * Plugin metadata (the package version in package.json is the only version).
 */
export const metadata = {
  name: 'Dimm City',
  description: 'Dimm City TTRPG macros: specialties, learning paths, skill cards, callouts, page templates',
  author: 'Dimm City',
  keywords: ['ttrpg', 'rpg', 'skills', 'dimm-city'],
};
