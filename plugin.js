/**
 * Dimm City — the gp-dimm-city Gutterpress plugin (server-side markdown-it)
 *
 * IMPORTANT: This plugin only transforms content marked with special markers.
 * Regular markdown content passes through unchanged.
 *
 * DECLARED MARKERS (the `markers` export at the bottom of this file — core
 * Gutterpress parses, nests, closes and source-maps these; this file only
 * names the element, classes and variants). Each also has an `@end-<name>`:
 *   @definition          → div.dc-prose-panel.dc-definition-block (a term, or a run of `####` terms)
 *   @faction [megacorp|cabal|cult|enforcer]
 *                        → div.dc-card.dc-faction[.dc-faction-<kind>] + span.dc-faction-kind
 *   @roll-table [die=d20] [label="…"]
 *                        → div.dc-roll-table + div.dc-roll-table-caption, over the author's table
 *   @specialty-intro     → div.dc-specialty-intro
 *   @specialty-art       → div.dc-specialty-art (full-bleed art panel)
 *   @specialty-card      → div.dc-specialty-card[data-position=odd|even]
 *   @gear [augment|treasure|vehicle|drug]
 *                        → div.dc-card.dc-entry.dc-gear (general gear), or
 *                          div.dc-card.dc-entry.dc-<kind>: augment (cybernetics, mods),
 *                          treasure (magic items, relics), vehicle, drug (drugs,
 *                          elixirs, consumables)
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
 *   @outcome [flush]     → div.dc-outcomes[.dc-flush]: the d20 ladder, one row
 *                          per `roll | name | text` line (crit, hit, mixed, miss, fail)
 *   @procedure           → ol.dc-steps: each numbered list inside becomes the
 *                          zero-padded step list (the wrapper renders nothing)
 *   @callout [variant]   → div.dc-alert.<variant class> > span.dc-alert-label.
 *                          Variants (bare word): note, warning, dm, vibe, origin,
 *                          visit, example; none is a note. The label is `label="…"`,
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
 *   `ROLL THE DIE!` (also ROLL A DIE!, ROLLS A DIE!, ROLLING THE DIE!)
 *                        → span.dc-roll-the-die
 *   an image-only paragraph gets p.dc-img-wrapper
 *   the h1 under `@page intro | credits | contents` gets .dc-chevron
 *   a table of the five standard bands is the outcome ladder (it keeps the
 *                          table's `{#id .class}`); `@procedure` keeps the
 *                          attributes written on its line, on its list
 *
 * GFM ALERT SYNTAX:
 *   `> [!NOTE]` / `[!WARNING]` / `[!DM]` / `[!VIBE]` / `[!ORIGIN]` / `[!VISIT]`
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

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;')
          .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function makeToken(type, content, nesting) {
  return {
    type: type,
    tag: '',
    nesting: nesting || 0,
    attrs: null,
    map: null,
    level: 0,
    children: null,
    content: typeof content === 'string' ? content : '',
    markup: '',
    info: '',
    meta: null,
    block: true,
    hidden: false,
    attrSet: function(name, value) {
      if (!this.attrs) this.attrs = [];
      const idx = this.attrIndex(name);
      if (idx < 0) {
        this.attrs.push([name, value]);
      } else {
        this.attrs[idx][1] = value;
      }
    },
    attrIndex: function(name) {
      if (!this.attrs) return -1;
      for (let j = 0; j < this.attrs.length; j++) {
        if (this.attrs[j][0] === name) return j;
      }
      return -1;
    }
  };
}

// Add one class to a token's existing `class` attribute, keeping the others.
function addTokenClass(tok, cls) {
  const current = (tok.attrGet('class') || '').split(/\s+/).filter(Boolean);
  if (!current.includes(cls)) {
    current.push(cls);
    tok.attrSet('class', current.join(' '));
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

function specialtyCodeFromClass(className) {
  const classList = (className || '').split(/\s+/).filter(Boolean);
  const specialtyMap = {
    augmerc: 'AUG',
    proxy: 'PRX',
    streetwarden: 'STW',
    gutterdruid: 'GDR',
    cybersurgeon: 'CBS',
    wirephreak: 'WPH',
    technosorcerer: 'TNS',
    etherlock: 'ETH',
  };

  for (const cls of classList) {
    if (specialtyMap[cls]) return specialtyMap[cls];
  }

  return 'PATH';
}

function buildStickerChain(items) {
  let html = '<div class="dc-stickers">';
  items.forEach((name, i) => {
    const cls = 'dc-sticker';
    html += '<span class="' + cls + '"><span class="dc-sticker-ref">' + esc(String(i + 1)) + '</span>' + esc(name.trim()) + '</span>';
    if (i < items.length - 1) {
      html += '<span class="dc-arrow">»</span>';
    }
  });
  html += '</div>\n';
  return html;
}

// ROLL THE DIE! / ROLL A DIE! / ROLLS A DIE! / ROLLING THE DIE! — uppercase only.
const ROLL_THE_DIE_PATTERN = /ROLL(?:S|ING)? (?:A|THE) DIE!/g;

function isWordChar(char) {
  return char !== '' && /[A-Za-z0-9_]/.test(char);
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
  if (!inlineTok || !inlineTok.children) return esc(inlineTok.content || '');
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

const OUTCOME_TIERS = ['crit', 'hit', 'mixed', 'miss', 'fail'];
const LADDER_BANDS_COUNT = OUTCOME_TIERS.length;
const OUTCOME_NAMES = { crit: 'Crit', hit: 'Hit', mixed: 'Hard Choice', miss: 'Miss', fail: 'Catastrophe' };

// The d20 outcome ladder is recognised by its bands, not by what its columns
// are called: a two-column table whose first column holds exactly the five
// standard bands (20, 11-19, 6-10, 2-5, 1), in either order, is the ladder. A
// band is typed any way an author types one ("11-19", "11 – 19", "**20**").
// Any other set of bands (six bands, three, a split at 10) is NOT a ladder.
const LADDER_TIER_OF_BAND = { '20': 'crit', '11-19': 'hit', '6-10': 'mixed', '2-5': 'miss', '1': 'fail' };

// "11 – 19" → [11, 19], "**20**" → [20, 20]; anything that is not a number or a range → null.
function parseBand(cell) {
  const text = cell.replace(/[*_`\s]/g, '').replace(/[\u2010-\u2015\u2212]/g, '-');
  const m = /^(\d{1,3})(?:-(\d{1,3}))?$/.exec(text);
  if (!m) return null;
  const [lo, hi] = [Number(m[1]), Number(m[2] ?? m[1])];
  return lo <= hi ? [lo, hi] : null;
}

// The ladder of a table — its header cells and its rows — or null when it is
// not a ladder.
function ladderRows(table) {
  const { head, rows } = table;
  if (head.length !== 2 || rows.length !== LADDER_BANDS_COUNT || rows.some((r) => r.length !== 2)) return null;
  const bands = rows.map((r) => parseBand(r[0]));
  if (bands.some((b) => !b)) return null;
  const keys = bands.map(([lo, hi]) => (lo === hi ? String(lo) : lo + '-' + hi));
  if (new Set(keys).size !== LADDER_BANDS_COUNT || keys.some((k) => !Object.hasOwn(LADDER_TIER_OF_BAND, k))) return null;
  return {
    head,
    rows: rows.map((r, i) => {
      const tier = LADDER_TIER_OF_BAND[keys[i]];
      return { tier, name: OUTCOME_NAMES[tier], roll: keys[i].replace('-', '\u2013'), text: r[1].trim() };
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
    html += '    <span class="dc-outcome-key tier-' + tier + '"><span class="dc-outcome-name">' + esc(name) + '</span><span class="dc-outcome-roll">' + esc(roll) + '</span></span>\n';
    html += '    <span class="dc-outcome-text">' + md.renderInline(text) + '</span>\n';
    html += '  </div>\n';
  });
  return html;
}

// A table of the five standard bands: tier and name come from the band. The
// ladder replaces the table, so what the author wrote on the table (`{#id
// .class}`) and what the renderer threaded on it move to the ladder.
function buildLadderBlock({ head, rows }, md, table) {
  const attrs = [['class', 'dc-outcomes']];
  for (const [name, value] of table.attrs || []) {
    if (name === 'class') attrs[0][1] += ' ' + value;
    else attrs.push([name, value]);
  }
  return '<div' + md.renderer.renderAttrs({ attrs }) + '>\n' + outcomeRowsHtml(rows, md, head) + '</div>\n';
}

// Parse ability from list item - handles rendered HTML: "<strong>0 AP</strong> <em>Name:</em> Description"
function parseAbilityFromListItem(html) {
  // Match <strong>N AP</strong> or <strong>N-X AP</strong> at the start (rendered HTML)
  const apMatch = html.match(/^\s*<strong>([^<]+)<\/strong>\s*/i);
  if (!apMatch) return null;

  let apVal = apMatch[1].trim();
  // Normalize: ensure "AP" suffix
  if (!apVal.toUpperCase().includes('AP')) {
    apVal = apVal + ' AP';
  }

  const rest = html.slice(apMatch[0].length);

  // Determine AP class
  let apClass = 'dc-ap';
  if (apVal === '0 AP' || apVal === '0AP') apClass += ' free';
  else if (apVal.includes('-') || /X|VAR/.test(apVal.toUpperCase())) apClass += ' variable';

  return {
    apVal: apVal,
    apClass: apClass,
    text: rest
  };
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
  try {
    md.core.ruler.before('layout_transform', 'dc_continue_classifier', dcContinueClassifier);
  } catch (error) {
    if (/Parser rule not found/.test(String(error))) return;
    throw error;
  }
  md.block.ruler.before('layout_marker', 'dc_continue_candidate', dcContinueCandidateBlock, {
    alt: ['paragraph', 'reference', 'blockquote', 'list'],
  });
}


// Collect bullet list items
function collectBulletListItems(tokens, startIndex) {
  const items = [];
  let i = startIndex;

  // Find bullet_list_open
  while (i < tokens.length && tokens[i].type !== 'bullet_list_open') {
    i++;
  }
  if (i >= tokens.length) return { items: [], endIndex: startIndex };

  i++; // Skip bullet_list_open

  while (i < tokens.length && tokens[i].type !== 'bullet_list_close') {
    if (tokens[i].type === 'list_item_open') {
      // Find the inline content
      let j = i + 1;
      while (j < tokens.length && tokens[j].type !== 'list_item_close') {
        if (tokens[j].type === 'inline') {
          items.push(tokens[j].content);
        }
        j++;
      }
      i = j;
    }
    i++;
  }

  return { items: items, endIndex: i };
}

// Collect ordered list items for abilities
function collectOrderedListItems(tokens, startIndex, md) {
  const items = [];
  let i = startIndex;

  // Find ordered_list_open
  while (i < tokens.length && tokens[i].type !== 'ordered_list_open') {
    i++;
  }
  if (i >= tokens.length) return { items: [], endIndex: startIndex };

  i++; // Skip ordered_list_open

  while (i < tokens.length && tokens[i].type !== 'ordered_list_close') {
    if (tokens[i].type === 'list_item_open') {
      // Find the inline content
      let j = i + 1;
      while (j < tokens.length && tokens[j].type !== 'list_item_close') {
        if (tokens[j].type === 'inline') {
          const html = renderInlineChildren(tokens[j], md);
          items.push(html);
        }
        j++;
      }
      i = j;
    }
    i++;
  }

  return { items: items, endIndex: i };
}

// `attrs` are what the author wrote on the `@procedure` line: the wrapper
// renders nothing, so the list takes them.
function buildProcedureList(items, attrs, md) {
  const list = [['class', 'dc-steps']];
  for (const [name, value] of attrs) {
    if (name === 'class') list[0][1] += ' ' + value;
    else list.push([name, value]);
  }
  let html = '<ol' + md.renderer.renderAttrs({ attrs: list }) + '>\n';
  items.forEach((itemHtml, idx) => {
    const stepNo = String(idx + 1).padStart(2, '0');
    html += '  <li><span class="dc-step-no">' + esc(stepNo) + '</span><span>' + itemHtml.trimEnd() + '</span></li>\n';
  });
  html += '</ol>\n';
  return html;
}

/**
 * GFM-style blockquote alert types — Dimm City branded: the classes and labels
 * are DC-specific, so core does not know them.
 */
const DC_ALERT_TYPES = {
  NOTE:      { classes: "dc-alert dc-note",                 label: "Note" },
  WARNING:   { classes: "dc-alert dc-note warning",         label: "Warning" },
  DM:        { classes: "dc-alert dc-dm-note",              label: "Dream Master Note" },
  VIBE:      { classes: "dc-alert dc-vibe-callout",         label: "Vibe" },
  ORIGIN:    { classes: "dc-alert dc-origin-callout",       label: "Origin" },
  VISIT:     { classes: "dc-alert dc-visit-callout",        label: "Visit" },
  FLAVOR:    { classes: "dc-flavor" },
  PULLQUOTE: { classes: "dc-pullquote dc-flush" },
};

const DC_ALERT_PATTERN = /^\[!([A-Z_]+)\]/i;

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
    if (!tok || tok.type !== 'blockquote_open') {
      newTokens.push(tok);
      continue;
    }

    let closeIdx = -1;
    let firstInlineIdx = -1;
    let depth = 0;
    for (let j = i; j < tokens.length; j++) {
      const jt = tokens[j];
      if (!jt) continue;
      if (jt.type === 'blockquote_open') depth++;
      if (jt.type === 'blockquote_close') {
        depth--;
        if (depth === 0) { closeIdx = j; break; }
      }
      if (firstInlineIdx === -1 && jt.type === 'inline') firstInlineIdx = j;
    }

    if (closeIdx === -1 || firstInlineIdx === -1) { newTokens.push(tok); continue; }

    const inlineTok = tokens[firstInlineIdx];
    const match = inlineTok && inlineTok.content.match(DC_ALERT_PATTERN);
    if (!match) { newTokens.push(tok); continue; }

    const alertType = match[1].toUpperCase();
    const config = DC_ALERT_TYPES[alertType];
    if (!config) { newTokens.push(tok); continue; }

    // Open div
    const openTok = new state.Token('html_block', '', 0);
    openTok.block = true;
    let openHtml = `<div class="${config.classes}">`;
    if (config.label) openHtml += `<span class="dc-alert-label">${config.label}</span>`;
    openHtml += '\n';
    openTok.content = openHtml;
    newTokens.push(openTok);

    // Strip [!TYPE] prefix from first inline; suppress its paragraph wrapper if empty.
    const prefixMatch = inlineTok.content.match(/^\[![A-Z_]+\][ \t]*/i);
    const stripped = prefixMatch
      ? inlineTok.content.slice(prefixMatch[0].length).trim()
      : inlineTok.content;

    const paragraphOpenIdx = firstInlineIdx - 1;
    const paragraphCloseIdx = firstInlineIdx + 1;
    const wrapsInParagraph =
      paragraphOpenIdx > i &&
      tokens[paragraphOpenIdx] && tokens[paragraphOpenIdx].type === 'paragraph_open' &&
      tokens[paragraphCloseIdx] && tokens[paragraphCloseIdx].type === 'paragraph_close';

    for (let j = i + 1; j < closeIdx; j++) {
      const t = tokens[j];
      if (!t) continue;
      if (j === firstInlineIdx) {
        if (stripped === '') continue;
        const strippedTok = new state.Token('inline', '', 0);
        strippedTok.content = stripped;
        strippedTok.children = [];
        state.md.inline.parse(stripped, state.md, state.env, strippedTok.children);
        newTokens.push(strippedTok);
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
      front = (tok.attrGet('class') || '').split(/\s+/).some((c) => FRONT_MATTER_PAGES.includes(c));
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
    if (!(tok.attrGet('class') || '').split(/\s+/).includes('dc-specialty-card')) continue;
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
    let end = i;
    let depth = 0;
    do depth += tokens[end++].nesting; while (depth > 0);
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
      const titleText = tokens[i + 1].content || '';
      out.push(makeToken('html_block', '<h3 class="dc-spray"><span class="dc-path-sticker">' + esc(ref) + '</span><span class="dc-path-sep"> </span>' + esc(titleText) + '</h3>\n'));
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
      const { items, endIndex } = collectBulletListItems(tokens, i);
      if (items.length > 0) out.push(makeToken('html_block', buildStickerChain(items)));
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
    const ref = (specialty ? specialtyCodeFromClass(specialty.attrGet('class')) : '') + n;
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
 *   @continue    → closes the card and opens a "{name} ▸" continuation card
 */
function dcSkillCards(state) {
  const md = state.md;
  const numbered = new Map(); // learning-path open token → cards numbered so far
  forEachComponent(state.tokens, 'skill', (run, enclosing) => {
    const [open, close] = [run[0], run[run.length - 1]];
    open.hidden = close.hidden = true;
    const path = enclosing.findLast((c) => c.meta.kind === 'learning-path');
    const content = run.slice(1, -1);
    const out = [];
    const emit = (html) => out.push(makeToken('html_block', html));
    let inCard = false;
    const belongsToCard = new Set(); // open/close tokens of the components that stay in the card
    let columnsDepth = 0; // how many `@columns` runs sit open inside the current card
    const columnsCloses = new Set(); // their close tokens
    let title = { name: '', tier: '' }; // the current card's title, for @continue

    const cardOpen = (cont) => {
      const attrs = open.attrs.map(([k, v]) => [k, k === 'class' && cont ? v.replace('dc-skill-card', 'dc-skill-card dc-skill-card-cont') : v]);
      attrs.push(['name', slugify(title.name)]);
      return '<div' + md.renderer.renderAttrs({ attrs }) + '>\n';
    };
    const endCard = () => {
      if (inCard) emit('</div></div></div>\n'); // .dc-card-inner, .dc-card-body, .dc-skill-card
      inCard = false;
    };

    for (let i = 0; i < content.length; i++) {
      const tok = content[i];

      // An h4 inside a `@columns` run in a card is a plain heading: a card
      // cannot start in the middle of another card's columns.
      if (tok.type === 'heading_open' && tok.tag === 'h4' && columnsDepth === 0) {
        endCard();
        const parsed = parseSkillTitle(content[i + 1].content || '');
        title = { name: parsed.name, tier: parsed.tier };
        let autoTier = '';
        if (path) {
          const n = (numbered.get(path) || 0) + 1;
          numbered.set(path, n);
          autoTier = path.attrGet('data-path-ref') + '.' + n;
        }
        // The skill's name is its `####` heading, kept a heading so the
        // outline lists it under its learning path. (A continuation card's
        // repeated title stays a span: it is not a new entry.)
        emit(
          cardOpen(false) +
          '  <div class="dc-card-tab">\n' +
          '    <h4 class="dc-tab-title">' + esc(parsed.name) + '</h4>\n' +
          '    <span class="dc-tab-tier">' + esc(parsed.tier || autoTier) + '</span>\n' +
          '  </div>\n' +
          '  <div class="dc-card-body">\n' +
          '    <div class="dc-card-inner">\n'
        );
        inCard = true;
        i += 2; // skip inline + heading_close
        continue;
      }

      if (tok.type === 'dc_skill_continue') {
        endCard();
        emit(
          cardOpen(true) +
          '  <div class="dc-card-tab dc-card-tab-cont">\n' +
          '    <span class="dc-tab-title">' + esc(title.name) + ' ▸</span>\n' +
          (title.tier ? '    <span class="dc-tab-tier">' + esc(title.tier) + '</span>\n' : '') +
          '  </div>\n' +
          '  <div class="dc-card-body">\n' +
          '    <div class="dc-card-inner">\n'
        );
        inCard = true;
        continue;
      }

      // A @callout, @card, @outcome, @procedure or @roll-table is content of the skill's card;
      // a break or another component (@specialty-art, @gear, …) ends it.
      if (tok.type === 'layout_component_open' && CARD_CONTENT.has(tok.meta.kind)) {
        let end = i;
        let depth = 0;
        do depth += content[end++].nesting; while (depth > 0);
        belongsToCard.add(tok).add(content[end - 1]);
      }
      // `@columns` … `@end-columns` and the `@column-break`s between are content of
      // the card too when they sit inside one: the columns run stays in the
      // card's body, in place. (A run that opens before the card, around
      // several cards, is not the card's: it ends the card as any layout token does.)
      if (inCard && tok.type === 'layout_component_open' && tok.meta.kind === 'columns') {
        let end = i;
        let depth = 0;
        do depth += content[end++].nesting; while (depth > 0);
        belongsToCard.add(tok).add(content[end - 1]);
        columnsCloses.add(content[end - 1]);
        columnsDepth++;
      }
      if (columnsCloses.has(tok)) columnsDepth--;
      if (tok.type === 'layout_column_break' && columnsDepth > 0) belongsToCard.add(tok);
      if (tok.type.startsWith('layout_') && !belongsToCard.has(tok)) endCard();

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
        const { items, endIndex } = collectOrderedListItems(content, i, md);
        items.forEach((itemHtml, idx) => {
          const ability = parseAbilityFromListItem(itemHtml);
          if (!ability) {
            emit('<p>' + itemHtml + '</p>\n'); // not "**N AP** *Name:* text": keep it as a paragraph
            return;
          }
          let posAttrs = '';
          if (items.length > 1) {
            if (idx === items.length - 1) posAttrs = ' data-ability-last="true"';
            if (idx === items.length - 2) posAttrs = ' data-ability-penultimate="true"';
          }
          emit(
            '<div class="dc-ability"' + posAttrs + '>\n' +
            '  <span class="' + ability.apClass + '">' + esc(ability.apVal) + '</span>\n' +
            '  <p class="dc-ability-text">' + ability.text + '</p>\n' +
            '</div>\n'
          );
        });
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

      out.push(tok);
    }
    endCard();
    return [open, ...out, close];
  });
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
      const { items, endIndex } = collectOrderedListItems(run, i, state.md);
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
// `@callout note|warning|dm|vibe|origin|visit|example` is a declared wrapper:
// core adds `dc-alert`, the variant's class and any author classes. What core
// cannot know is each variant's default label, so a rule adds it when the
// author wrote no `label="…"`. A missing or unrecognised variant is a plain
// note.
const CALLOUTS = {
  note: { class: 'dc-note', label: 'Note' },
  warning: { class: 'dc-note warning', label: 'Warning' },
  dm: { class: 'dc-dm-note', label: 'Dream Master Note' },
  vibe: { class: 'dc-vibe-callout', label: 'Vibe' },
  origin: { class: 'dc-origin-callout', label: 'Origin' },
  visit: { class: 'dc-visit-callout', label: 'Visit' },
  example: { class: 'dc-example-callout', label: 'Example' },
};

function dcCallouts(state) {
  forEachComponent(state.tokens, 'callout', ([open, ...rest]) => {
    const variant = Object.hasOwn(CALLOUTS, open.meta.variant) ? open.meta.variant : 'note';
    if (variant !== open.meta.variant) {
      // no variant class came from core: the default note keeps its place right after dc-alert
      open.attrSet('class', open.attrGet('class').replace('dc-alert', 'dc-alert dc-note'));
    }
    if (open.meta.labelled) return; // an explicit label="…" wins
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

const GEAR_KINDS = ['augment', 'treasure', 'vehicle', 'drug'];

// A bare `@gear` (or an unrecognised word, which core reports) is general gear:
// core added only the shared card, so the general-gear class goes right after it.
function dcGear(state) {
  forEachComponent(state.tokens, 'gear', ([open]) => {
    if (GEAR_KINDS.includes(open.meta.variant)) return;
    open.attrSet('class', open.attrGet('class').replace('dc-entry', 'dc-entry dc-gear'));
  });
}

/**
 * Entry cards (`@gear` and its kinds `augment`, `treasure`, `vehicle`, `drug`):
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
  return (open.attrGet('class') || '').split(/\s+/).includes('dc-npc-stat');
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
export default function dimmCityPlugin(md, options = {}) {
  registerSkillContinueBridge(md);

  // GFM-style `> [!NOTE]` alerts. Registered on the core ruler since the
  // transform operates on already-parsed token streams.
  md.core.ruler.push('dc_alerts', dcAlertsTransform);

  // Transform the canonical roll instruction while it is still structured
  // inline content. This covers every markdown context without rewriting
  // rendered HTML, code spans, raw HTML, or partial words.
  md.renderer.rules.dc_roll_the_die = (tokens, idx) =>
    '<span class="dc-roll-the-die">' + esc(tokens[idx].content) + '</span>';
  md.core.ruler.push('dc_roll_the_die', dcRollDieTransform);

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
  md.core.ruler.push('dc_fields', dcFields);
  md.core.ruler.push('dc_cards', dcCards);
  md.core.ruler.push('dc_outcomes', dcOutcomes);
  md.core.ruler.push('dc_roll_tables', dcRollTables);
  md.core.ruler.push('dc_procedures', dcProcedures);
  md.core.ruler.push('dc_learning_paths', dcLearningPaths);
  md.core.ruler.push('dc_skill_cards', dcSkillCards);
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

const SPECIALTIES = [
  'augmerc', 'proxy', 'streetwarden', 'gutterdruid', 'cybersurgeon',
  'wirephreak', 'technosorcerer', 'etherlock', 'dualist', 'generalist',
];

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

  definition: wrapper('dc-prose-panel dc-definition-block'),
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
    },
  },
  chapter: {
    variants: {
      rules: 'dc-chapter-rules',
      lore: 'dc-chapter-lore',
      'citizen-file': 'dc-chapter-citizen-file',
      specialty: 'dc-chapter-specialty',
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
