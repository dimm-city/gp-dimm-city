/**
 * Dimm City — the gp-dimm-city Gutterpress plugin (server-side markdown-it)
 *
 * IMPORTANT: This plugin only transforms content marked with special markers.
 * Regular markdown content passes through unchanged.
 *
 * DECLARED MARKERS (the `markers` export at the bottom of this file — core
 * Gutterpress parses, nests, closes and source-maps these; this file only
 * names the element, classes and variants). Each also has an `@end-<name>`:
 *   @sidebar [inset]     → div.dc-sidebar (`.inset` shorthand works too)
 *   @sidebar-box         → div.dc-prose-panel.dc-sidebar-box
 *   @definition          → div.dc-prose-panel.dc-definition-block
 *   @specialty-intro     → div.dc-specialty-intro
 *   @specialty-art       → div.dc-specialty-art (full-bleed art panel)
 *   @specialty-card      → div.dc-specialty-card[data-position=odd|even]
 *   @gear                → div.dc-card.dc-gear
 *   @toc                 → div.dc-toc
 *   @lede                → div.dc-intro
 *   @glossary            → div.dc-terms
 *   @block [panel|slate|shard|codex] label="Title"
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
 *                          visit, gear; none is a note. The label is `label="…"`,
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
 *   (chapter-opener composite is now markup-driven — see CSS notes below)
 *   `ROLL THE DIE!`      → span.dc-roll-the-die
 *   an image-only paragraph gets p.dc-img-wrapper
 *
 * GFM ALERT SYNTAX:
 *   `> [!NOTE]` / `[!WARNING]` / `[!DM]` / `[!VIBE]` / `[!ORIGIN]` / `[!VISIT]`
 *   / `[!GEAR]` / `[!FLAVOR]` / `[!PULLQUOTE]` blockquotes are transformed
 *   into `<div class="dc-alert dc-<type>">` (moved from print-md core 2026-05-17).
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
 *   @skill {.dc-allow-split}
 *     → every card of the skill: <div class="dc-skill-card dc-allow-split" ...>
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
  // Parse "Skill Name" or "Skill Name | T0" or "Skill Name | T0 | highlight"
  const parts = text.split('|');
  const name = parts[0].trim();
  const tier = parts.length > 1 ? parts[1].trim() : '';
  const flags = parts.slice(2).map(f => f.trim().toLowerCase());
  const highlight = flags.includes('highlight');
  return { name, tier, highlight };
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

/**
 * Skill card variants are now controlled by the .specialty.<name> parent
 * container (CSS parent-selector model). The variant= attribute on @skill,
 * @continue, and @learning-path has been removed. No SKILL_VARIANTS map.
 */

function buildStickerChain(items) {
  let html = '<div class="dc-stickers">';
  items.forEach((name, i) => {
    // The first sticker used to get .active treatment, rendering it in
    // --blood while siblings rendered in --ink-dark. User feedback:
    // "there's no reason for the first skill in the learning path list
    // to be marked as active or a different color than the other skills.
    // For example, under biting distance, punishing counter is red, and
    // the rest are black. It should also be black." Removed.
    const cls = 'dc-sticker';
    html += '<span class="' + cls + '"><span class="dc-sticker-ref">' + esc(String(i + 1)) + '</span>' + esc(name.trim()) + '</span>';
    if (i < items.length - 1) {
      html += '<span class="dc-arrow">»</span>';
    }
  });
  html += '</div>\n';
  return html;
}

const ROLL_THE_DIE_TEXT = 'ROLL THE DIE!';

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
  let searchFrom = 0;

  while (searchFrom < content.length) {
    const index = content.indexOf(ROLL_THE_DIE_TEXT, searchFrom);
    if (index === -1) break;

    const before = index > 0 ? content[index - 1] : '';
    const end = index + ROLL_THE_DIE_TEXT.length;
    const after = end < content.length ? content[end] : '';
    if (isWordChar(before) || isWordChar(after)) {
      searchFrom = index + 1;
      continue;
    }

    if (index > cursor) {
      replacement.push(copyTextToken(token, content.slice(cursor, index), state));
    }

    const rollToken = copyTextToken(token, ROLL_THE_DIE_TEXT, state);
    rollToken.type = 'dc_roll_the_die';
    rollToken.tag = 'span';
    rollToken.nesting = 0;
    replacement.push(rollToken);

    cursor = end;
    searchFrom = end;
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
  state.tokens.forEach(token => {
    if (token.type !== 'inline' || !Array.isArray(token.children)) return;

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
// it, the way every component that turns a quote into a line has always read
// it), and the index of its close.
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

function getTableHeaders(tableTokens) {
  const headers = [];
  let inHead = false;
  for (let i = 0; i < tableTokens.length; i++) {
    if (tableTokens[i].type === 'thead_open') inHead = true;
    if (tableTokens[i].type === 'thead_close') break;
    if (inHead && tableTokens[i].type === 'inline') {
      headers.push(tableTokens[i].content.toLowerCase().trim());
    }
  }
  return headers;
}

function classifyTable(headers) {
  if (headers.includes('roll') && headers.includes('outcome')) {
    return 'outcomes';
  }
  return '';
}

function getRollTier(text) {
  const clean = text.replace(/[\u2013\u2014]/g, '-').trim();
  if (clean === '20') return 'crit';
  if (clean === '1') return 'fail';
  // Handle ranges like "11 - 19" or "11-19"
  const rangeMatch = clean.match(/^(\d+)/);
  if (rangeMatch) {
    const n = parseInt(rangeMatch[1], 10);
    if (n >= 11) return 'hit';
    if (n >= 6) return 'mixed';
    if (n >= 2) return 'miss';
  }
  return 'hit';
}

const OUTCOME_TIERS = ['crit', 'hit', 'mixed', 'miss', 'fail'];
const OUTCOME_NAMES = { crit: 'Crit', hit: 'Hit', mixed: 'Hard Choice', miss: 'Miss', fail: 'Catastrophe' };

// The ladder's label bar and one row per `{ tier, name, roll, text }`; `text`
// is markdown, so **bold** and ROLL THE DIE! render as they do anywhere else.
function outcomeRowsHtml(rows, md) {
  let html = '  <div class="dc-outcomes-label">Outcomes</div>\n';
  rows.forEach(({ tier, name, roll, text }) => {
    html += '  <div class="dc-outcome-row ' + tier + '">\n';
    html += '    <span class="dc-outcome-key tier-' + tier + '"><span class="dc-outcome-name">' + esc(name) + '</span><span class="dc-outcome-roll">' + esc(roll) + '</span></span>\n';
    html += '    <span class="dc-outcome-text">' + md.renderInline(text) + '</span>\n';
    html += '  </div>\n';
  });
  return html;
}

// A `| Roll | Outcome |` table in a skill card: tier and name come from the roll.
function buildOutcomesBlock(rows, md, needsAvoid = true) {
  // data-break-inside="avoid" is added when the parent card can be split (has
  // allow-split) — the polyfill needs this to keep the
  // outcomes table together when the card itself isn't protected. When the card
  // already has data-break-inside="avoid" (non-splittable cards), adding a
  // nested avoid creates a conflicting inner break that the polyfill resolves
  // by splitting the card at the outcomes boundary, leaving a headless
  // card-body on one page and the outcomes-only continuation on the next.
  const avoidAttr = needsAvoid ? ' data-break-inside="avoid"' : '';
  const ladder = rows
    .filter((row) => row.length >= 2)
    .map((row) => {
      const roll = row[0].trim();
      const tier = getRollTier(roll);
      return { tier, name: OUTCOME_NAMES[tier], roll, text: row[1].trim() };
    });
  return '<div class="dc-outcomes"' + avoidAttr + '>\n' + outcomeRowsHtml(ladder, md) + '</div>\n';
}

function buildTable(tableTokens, tableClass, md, needsAvoid = true) {
  const rows = [];
  let currentRow = [];
  let inBody = false;

  for (let i = 0; i < tableTokens.length; i++) {
    const t = tableTokens[i];
    if (t.type === 'tbody_open') inBody = true;
    if (t.type === 'tbody_close') inBody = false;
    if (t.type === 'tr_open' && inBody) currentRow = [];
    if (t.type === 'tr_close' && inBody) {
      rows.push(currentRow);
    }
    if (t.type === 'td_open' && inBody) {
      const contentTok = tableTokens[i + 1];
      if (contentTok && contentTok.type === 'inline') {
        currentRow.push(contentTok.content);
      }
    }
  }

  return buildOutcomesBlock(rows, md, needsAvoid);
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

function buildProcedureList(items) {
  let html = '<ol class="dc-steps">\n';
  items.forEach((itemHtml, idx) => {
    const stepNo = String(idx + 1).padStart(2, '0');
    html += '  <li><span class="dc-step-no">' + esc(stepNo) + '</span><span>' + itemHtml.trimEnd() + '</span></li>\n';
  });
  html += '</ol>\n';
  return html;
}

/**
 * GFM-style blockquote alert types — Dimm City branded.
 *
 * Moved from print-md core (src/lib/markdown/alerts.ts) on 2026-05-17 because
 * the classes and labels are DC-specific. Core no longer leaks DC identifiers.
 */
const DC_ALERT_TYPES = {
  NOTE:      { classes: "dc-alert dc-note",                 label: "Note" },
  WARNING:   { classes: "dc-alert dc-note warning",         label: "Warning" },
  DM:        { classes: "dc-alert dc-dm-note",              label: "Dream Master Note" },
  VIBE:      { classes: "dc-alert dc-vibe-callout",         label: "Vibe" },
  ORIGIN:    { classes: "dc-alert dc-origin-callout",       label: "Origin" },
  VISIT:     { classes: "dc-alert dc-visit-callout",        label: "Visit" },
  GEAR:      { classes: "dc-alert dc-gear-callout",         label: "Gear" },
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
 * wrapper only carries the author's classes and attributes (`{.dc-allow-split}`,
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
    // `.dc-allow-split` lets a card taller than a page split; every other card
    // carries data-break-inside="avoid". An outcomes table or sub-list inside a
    // splittable card needs its own avoid, because the card has none.
    const canSplit = (open.attrGet('class') || '').split(/\s+/).includes('dc-allow-split');
    const content = run.slice(1, -1);
    const out = [];
    const emit = (html) => out.push(makeToken('html_block', html));
    let inCard = false;
    const belongsToCard = new Set(); // open/close tokens of the components that stay in the card
    let title = { name: '', tier: '' }; // the current card's title, for @continue

    const cardOpen = (cont) => {
      const attrs = open.attrs.map(([k, v]) => [k, k === 'class' && cont ? v.replace('dc-skill-card', 'dc-skill-card dc-skill-card-cont') : v]);
      attrs.push(['name', slugify(title.name)]);
      if (!canSplit) attrs.push(['data-break-inside', 'avoid']);
      return '<div' + md.renderer.renderAttrs({ attrs }) + '>\n';
    };
    const endCard = () => {
      if (inCard) emit('</div></div></div>\n'); // .dc-card-inner, .dc-card-body, .dc-skill-card
      inCard = false;
    };

    for (let i = 0; i < content.length; i++) {
      const tok = content[i];

      if (tok.type === 'heading_open' && tok.tag === 'h4') {
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
          '  <div class="dc-card-tab' + (parsed.highlight ? ' dc-highlight' : '') + '">\n' +
          '    <h4 class="dc-tab-title">' + esc(parsed.name) + '</h4>\n' +
          '    <span class="dc-tab-tier">' + esc(parsed.tier || autoTier) + '</span>\n' +
          '  </div>\n' +
          '  <div class="dc-card-body' + (parsed.highlight ? ' dc-highlight-body' : '') + '">\n' +
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

      // A @callout, @card, @outcome or @procedure is content of the skill's card;
      // a break or another component (@sidebar, @specialty-art, …) ends it.
      if (tok.type === 'layout_component_open' && CARD_CONTENT.has(tok.meta.kind)) {
        let end = i;
        let depth = 0;
        do depth += content[end++].nesting; while (depth > 0);
        belongsToCard.add(tok).add(content[end - 1]);
      }
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

      // Keep short sub-lists whole (e.g. an "Arm:" bullet stranded from "Leg:").
      if (tok.type === 'bullet_list_open' && canSplit) tok.attrSet('data-break-inside', 'avoid');

      if (tok.type === 'table_open') {
        const tableTokens = collectTableTokens(content, i);
        const tableClass = classifyTable(getTableHeaders(tableTokens));
        // Tables this plugin does not transform pass through untouched, thead
        // and all (rebuilding them from tbody rows once left 64 of 86 tables
        // headerless).
        if (tableClass) {
          emit(buildTable(tableTokens, tableClass, md, canSplit));
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
const CARD_CONTENT = new Set(['callout', 'card', 'outcome', 'procedure']);

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
 * `@procedure`: every numbered list inside becomes the zero-padded step list
 * (`ol.dc-steps`). The declared wrapper renders nothing itself: the list is
 * the element, as it has always been.
 */
function dcProcedures(state) {
  forEachComponent(state.tokens, 'procedure', (run) => {
    const [open, close] = [run[0], run[run.length - 1]];
    open.hidden = close.hidden = true;
    const out = [];
    for (let i = 1; i < run.length - 1; i++) {
      if (run[i].type !== 'ordered_list_open') {
        out.push(run[i]);
        continue;
      }
      const { items, endIndex } = collectOrderedListItems(run, i, state.md);
      if (items.length > 0) out.push(makeToken('html_block', buildProcedureList(items)));
      i = endIndex;
    }
    return [open, ...out, close];
  });
}

// ── Declared component: @callout (and its alias @dm-note) ──────────────────
//
// `@callout note|warning|dm|vibe|origin|visit|gear` is a declared wrapper:
// core adds `dc-alert`, the variant's class and any author classes. What core
// cannot know is each variant's default label, so a rule adds it when the
// author wrote no `label="…"`. A missing or unrecognised variant is a plain
// note, as it always was.
const CALLOUTS = {
  note: { class: 'dc-note', label: 'Note' },
  warning: { class: 'dc-note warning', label: 'Warning' },
  dm: { class: 'dc-dm-note', label: 'Dream Master Note' },
  vibe: { class: 'dc-vibe-callout', label: 'Vibe' },
  origin: { class: 'dc-origin-callout', label: 'Origin' },
  visit: { class: 'dc-visit-callout', label: 'Visit' },
  gear: { class: 'dc-gear-callout', label: 'Gear' },
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

  // GFM-style `> [!NOTE]` alerts (moved from core 2026-05-17).
  // Must run before markdown-it-attrs so attrs don't interfere with `[!TYPE]`
  // detection inside blockquotes. We register on the core ruler since the
  // transform operates on already-parsed token streams.
  md.core.ruler.push('dc_alerts', dcAlertsTransform);

  // Transform the canonical roll instruction while it is still structured
  // inline content. This covers every markdown context without rewriting
  // rendered HTML, code spans, raw HTML, or partial words.
  md.renderer.rules.dc_roll_the_die = (tokens, idx) =>
    '<span class="dc-roll-the-die">' + esc(tokens[idx].content) + '</span>';
  md.core.ruler.push('dc_roll_the_die', dcRollDieTransform);

  md.core.ruler.push('dc_specialty_card_positions', dcSpecialtyCardPositions);

  // NOTE: Chapter-opener composite behaviour is intentionally NOT handled
  // by the plugin. The author markdown
  //
  //     @chapter C.01
  //     @page intro
  //     @section
  //     # Who Do You Dream to Be?
  //
  // produces the standard marker DOM:
  //
  //     .chapter[data-chapter-label="C.01"]
  //       .page[data-page="intro"][data-chapter-label="C.01"]
  //         .section
  //           h1
  //           ...
  //
  // All chapter-opener visual treatment (the C.NN badge, the section
  // variant chrome, the chevron-styled h1) is provided by CSS attribute
  // selectors in components/*.css matching this structure.

  // Mark image-only paragraphs so layout rules can target them without
  // relying on p:has(img). The base CSS rule
  // (p.dc-img-wrapper { padding:0; margin:0 }) lives in components/data.css.
  // Per-page rules can further refine position via .page.my-class p.dc-img-wrapper.
  md.core.ruler.push('dc_image_paragraphs', dcImageParagraphs);

  // Declared components. Callouts, cards, outcomes and procedures go first so
  // one inside a skill is already rewritten when the skill's rule looks at it.
  md.core.ruler.push('dc_callouts', dcCallouts);
  md.core.ruler.push('dc_cards', dcCards);
  md.core.ruler.push('dc_outcomes', dcOutcomes);
  md.core.ruler.push('dc_procedures', dcProcedures);
  md.core.ruler.push('dc_learning_paths', dcLearningPaths);
  md.core.ruler.push('dc_skill_cards', dcSkillCards);
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
 * as a real `@section` carrying the entry's class (see below).
 *
 * To add a plain wrapper, add one line here (element + classes), a snippet in
 * `snippets/<name>.md`, and the usual catalog/guide entries — see
 * docs/adding-macros.md.
 *
 * Variants are a bare word on the marker line (`@sidebar inset`) and only add
 * a class, so `.inset`-style class shorthand keeps working beside them.
 * `autoCloseAt: ['eof']` keeps these silent at end-of-document: they have
 * never needed an explicit `@end-…`.
 */
const wrapper = (cls, extra = {}) => ({ class: cls, autoCloseAt: ['eof'], ...extra });

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

  // Content components. `@card` closes silently at the end of a document, as it
  // always has. `@outcome` and `@procedure` carry no `autoCloseAt`, so one left
  // open at the end gets core's `declared_marker_eof_close` warning: what
  // follows an open one is read as its rows or its steps. `@procedure` has no
  // class (its rule hides the wrapper: the step list is the element).
  card: wrapper('dc-card'),
  outcome: { class: 'dc-outcomes', variants: { flush: 'dc-flush' }, validate: validateOutcome },
  procedure: { validate: validateProcedure },

  // `@callout` takes its variant as a bare word (`@callout vibe`); `@dm-note` is
  // the same marker with the `dm` variant preset. A default label comes from
  // `dcCallouts`, an explicit `label="…"` from core.
  callout: wrapper('dc-alert', {
    variants: Object.fromEntries(Object.entries(CALLOUTS).map(([name, { class: cls }]) => [name, cls])),
    label: { tag: 'span', class: 'dc-alert-label', from: 'attr:label' },
    validate: validateCallout,
  }),
  'dm-note': { alias: 'callout', preset: { variant: 'dm' } },

  sidebar: wrapper('dc-sidebar', { variants: { inset: 'inset' } }),
  'sidebar-box': wrapper('dc-prose-panel dc-sidebar-box'),
  definition: wrapper('dc-prose-panel dc-definition-block'),
  'specialty-intro': wrapper('dc-specialty-intro'),
  'specialty-art': wrapper('dc-specialty-art'),
  'specialty-card': wrapper('dc-specialty-card'),
  gear: wrapper('dc-card dc-gear'),
  toc: wrapper('dc-toc'),
  lede: wrapper('dc-intro'),
  glossary: wrapper('dc-terms'),
  block: wrapper('dc-block', {
    variants: { panel: 'dc-panel', slate: 'dc-slate', shard: 'dc-shard', codex: 'dc-codex' },
    label: { tag: 'div', class: 'dc-block-title', from: 'attr:label' },
  }),

  // Section-styled components. `section: true` makes each one a real core
  // @section: `@npc-stat` is exactly `@section .dc-npc-stat` (same element, same
  // classes), so the books' existing `@section .dc-…` spellings keep working
  // unchanged. Each class has its CSS on `.section.dc-…` in
  // styles/components/section.css. No variants: none of these is styled per
  // specialty (that lives on `.dc-specialty.<name>`, from `@specialty`), and
  // modifiers such as `.dc-plain`, `.dc-snug`, `.dc-allow-split` and
  // `.gp-columns-2` stay author classes (`@column-panel .gp-columns-2`).
  'column-panel': { section: true, class: 'dc-column-panel' },
  tabbed: { section: true, class: 'dc-tabbed' },
  'card-grid': { section: true, class: 'dc-card-grid' },
  'citizen-walkthrough': { section: true, class: 'dc-citizen-walkthrough' },
  'fiction-excerpt': { section: true, class: 'dc-fiction-excerpt' },
  'npc-stat': { section: true, class: 'dc-npc-stat' },
  // Citizen-file card runs: the class sets the accent of every `@card` inside.
  flaws: { section: true, class: 'dc-flaws' },
  ideals: { section: true, class: 'dc-ideals' },
  dreams: { section: true, class: 'dc-dreams' },
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
