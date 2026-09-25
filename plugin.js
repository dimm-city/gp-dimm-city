/**
 * Dimm City Field Guide — Server-Side Only Plugin for print-md
 *
 * IMPORTANT: This plugin only transforms content marked with special markers.
 * Regular markdown content passes through unchanged.
 *
 * MARKERS (support optional key="value" attributes):
 *   @sidebar            → Start a dc-sidebar wrapper
 *   @end-sidebar        → End sidebar wrapper
 *   @sidebar-box        → Start a dc-sidebar-box wrapper
 *   @end-sidebar-box    → End sidebar-box wrapper
 *   @specialty          → Start a specialty wrapper (auto-closes any prior specialty,
 *                          learning-path, or skill)
 *   @end-specialty      → Manually end a specialty wrapper
 *   @definition         → Start a dc-definition-block wrapper
 *   @end-definition     → End definition wrapper
 *   @procedure          → Start a dc-steps procedure wrapper
 *   @end-procedure      → End procedure wrapper (auto-closes on EOF with a warning)
 *   @callout            → Start a dc-alert callout (variant=note|warning|dm|vibe|origin|visit|gear)
 *   @end-callout        → End callout wrapper
 *   @dm-note            → Start a Dream Master note (sugar for @callout variant=dm)
 *   @end-dm-note        → End dm-note wrapper
 *   @block              → Section enclosure card (.dc-panel|.dc-slate|.dc-shard|.dc-codex label="Title")
 *   @end-block          → End block enclosure
 *   @lede               → Start a dc-intro lede wrapper
 *   @end-lede           → End lede wrapper
 *   @learning-path      → Start a learning path section (auto-closes previous sections)
 *   @end-learning-path  → Manually end a learning path section
 *   @skill              → Start a skill card (auto-closes previous skill)
 *   @end-skill          → End skill transformation mode
 *   @continue           → Continuation marker — emits a card with a "{name} ▸"
 *                          tab so an oversized skill card can be split across pages
 *                          while keeping a visible link to its origin card
 *   @specialty-intro    → Cosmetic specialty intro wrapper
 *   @end-specialty-intro
 *   @specialty-card     → Individual specialty card
 *   @end-specialty-card
 *   @specialty-art      → Full-bleed specialty art panel (.dc-specialty-art)
 *   @end-specialty-art
 *   @gear               → Gear card (shorthand for @card .dc-gear)
 *   @end-gear
 *   (chapter-opener composite is now markup-driven — see CSS notes below)
 *   @toc                → Table-of-contents wrapper
 *   @end-toc
 *   @glossary           → Glossary wrapper
 *   @end-glossary
 *   @outcome            → 5-rung d20 outcome ladder block
 *   @end-outcome
 *   @tape               → Inline tape divider (`<div class="dc-tape">— § —</div>`)
 *
 * GFM ALERT SYNTAX:
 *   `> [!NOTE]` / `[!WARNING]` / `[!DM]` / `[!VIBE]` / `[!ORIGIN]` / `[!VISIT]`
 *   / `[!GEAR]` / `[!FLAVOR]` / `[!PULLQUOTE]` blockquotes are transformed
 *   into `<div class="dc-alert dc-<type>">` (moved from print-md core 2026-05-17).
 *
 * SPECIALTY VARIANTS:
 *   Skill card and learning-path variants are controlled by the .specialty.<name>
 *   parent container (CSS parent-selector model), not per-card attributes.
 *   Authors wrap the entire specialty section in @specialty .augmerc and every
 *   card inside automatically inherits the shape and accent colors.
 *
 * ATTRIBUTE SUPPORT:
 *   Markers can include key="value", key='value', or key=value pairs:
 *
 *   @learning-path data-foo="bar"
 *     → <div class="dc-learning-path dc-path-block" data-foo="bar">
 *
 *   @skill id="my-skill" data-category="combat"
 *     → Extra attributes added to skill-card wrapper
 *
 *   @skill {.dc-allow-split}
 *     → <div class="dc-skill-card dc-allow-split" ...>
 *
 *   @learning-path {.custom-path}
 *     → <div class="dc-learning-path dc-path-block custom-path" ...>
 *
 * LEARNING PATH FORMAT:
 *   @learning-path
 *   ### Title
 *   > Subtitle/description
 *   - Skill A
 *   - Skill B
 *   - Skill C
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
 * Auto-closes at: EOF, @end-skill, @end-learning-path, @learning-path, or @skill
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

// Add/remove one class on a token's existing `class` attribute without
// disturbing any other class already there. Used to tag the LAST blockquote
// in a @card body as `.dc-card-footer` (dc#44): the plugin sees each body
// blockquote as it streams past and has no lookahead, so it tags the
// current one and untags whichever one it previously tagged — the tag
// only ever sits on the most recently seen blockquote, which is exactly
// the one `blockquote:last-of-type` will match once the card closes.
function addTokenClass(tok, cls) {
  const current = (tok.attrGet('class') || '').split(/\s+/).filter(Boolean);
  if (!current.includes(cls)) {
    current.push(cls);
    tok.attrSet('class', current.join(' '));
  }
}

function removeTokenClass(tok, cls) {
  const current = (tok.attrGet('class') || '').split(/\s+/).filter(Boolean);
  const next = current.filter((c) => c !== cls);
  if (next.length === current.length) return;
  if (next.length) {
    tok.attrSet('class', next.join(' '));
  } else {
    const idx = tok.attrIndex('class');
    if (idx >= 0) tok.attrs.splice(idx, 1);
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
  if (headers.includes('distance')) {
    return 'distance';
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

function buildOutcomesBlock(rows, md, needsAvoid = true) {
  // data-break-inside="avoid" is added when the parent card can be split (has
  // allow-split) — the polyfill needs this to keep the
  // outcomes table together when the card itself isn't protected. When the card
  // already has data-break-inside="avoid" (non-splittable cards), adding a
  // nested avoid creates a conflicting inner break that the polyfill resolves
  // by splitting the card at the outcomes boundary, leaving a headless
  // card-body on one page and the outcomes-only continuation on the next.
  const avoidAttr = needsAvoid ? ' data-break-inside="avoid"' : '';
  let html = '<div class="dc-outcomes"' + avoidAttr + '>\n';
  html += '  <div class="dc-outcomes-label">Outcomes</div>\n';

  rows.forEach(row => {
    if (row.length < 2) return;
    const rollVal = row[0].trim();
    const outcomeText = row[1].trim();
    const tier = getRollTier(rollVal);

    // Render markdown inline content (e.g., **bold**, *italic*)
    const renderedOutcome = md.renderInline(outcomeText);

    const outcomeNameMap = {
      crit: 'Crit',
      hit: 'Hit',
      mixed: 'Hard Choice',
      miss: 'Miss',
      fail: 'Catastrophe',
    };

    html += '  <div class="dc-outcome-row ' + tier + '">\n';
    html += '    <span class="dc-outcome-key tier-' + tier + '"><span class="dc-outcome-name">' + outcomeNameMap[tier] + '</span><span class="dc-outcome-roll">' + esc(rollVal) + '</span></span>\n';
    html += '    <span class="dc-outcome-text">' + renderedOutcome + '</span>\n';
    html += '  </div>\n';
  });

  html += '</div>\n';
  return html;
}

function buildDistanceTags(rows, md) {
  let html = '<div class="dc-sub-header">AP Cost × Distance</div>\n';
  html += '<div class="dc-distance-tags">\n';

  rows.forEach(row => {
    if (row.length < 2) return;
    const distance = row[0].trim();
    const cost = row[1].trim();

    // Render markdown inline content
    const renderedDistance = md.renderInline(distance);
    const renderedCost = md.renderInline(cost);

    html += '  <span class="dc-dist-tag">\n';
    html += '    <span class="dc-dist-ap">' + renderedCost + '</span>\n';
    html += '    <span class="dc-dist-name">' + renderedDistance + '</span>\n';
    html += '  </span>\n';
  });

  html += '</div>\n';
  return html;
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

  if (tableClass === 'outcomes') {
    return buildOutcomesBlock(rows, md, needsAvoid);
  }
  return buildDistanceTags(rows, md);
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
  else if (apVal.includes('-') || apVal.toUpperCase().includes('X')) apClass += ' variable';

  return {
    apVal: apVal,
    apClass: apClass,
    text: rest
  };
}


// Parse key="value", key='value', key=value, bare .class / #id tokens,
// and {.class #id} attribute blocks from the body string following a marker keyword.
//
// Grammar matches parseMarkerLine() in Gutterpress's markers.js — inlined here
// rather than imported, because plugin code cannot resolve Gutterpress at runtime:
//   - Quote-aware tokenization: key="a b" and key='a b' preserve spaces inside quotes
//   - .classname  — shorthand class (multiple allowed)
//   - #id         — shorthand id
//   - key=value   — arbitrary attribute; key="class" splits on whitespace/commas
//   - bare token  — treated as a class (DC markers have no positional "name" slot)
//
// Back-compat: brace blocks {.class #id} are stripped and injected as tokens
// before the main pass so @specialty {.augmerc} continues to work alongside
// the new bare-token form @specialty .augmerc.
function parseAttrs(str) {
  // Pre-pass: extract brace blocks {.class1 .class2 #id} for back-compat,
  // then remove them from the string so the main tokenizer doesn't see them.
  const braceClasses = [];
  const braceIds = [];
  const strNoBraces = str.replace(/\{([^}]+)\}/g, (_, inside) => {
    for (const part of inside.trim().split(/\s+/)) {
      if (part.startsWith('.')) braceClasses.push(part.slice(1));
      else if (part.startsWith('#')) braceIds.push(part.slice(1));
    }
    return ' ';
  });

  // Tokenize the remaining string using the same quote-aware tokenizer as
  // markers.js's parseMarkerLine().
  const tokens = [];
  let buf = '';
  let quote = null;
  for (let i = 0; i < strNoBraces.length; i++) {
    const ch = strNoBraces[i];
    if (quote) {
      if (ch === quote) quote = null;
      else buf += ch;
      continue;
    }
    if (ch === '"' || ch === "'") {
      quote = ch;
      continue;
    }
    if (/\s/.test(ch)) {
      if (buf) tokens.push(buf);
      buf = '';
      continue;
    }
    buf += ch;
  }
  if (buf) tokens.push(buf);

  // Process tokens: mirrors parseMarkerLine's attr-accumulation loop.
  // DC markers have no positional "name" slot — bare tokens become classes.
  const attrs = {};
  const classes = [...braceClasses];
  if (braceIds.length) attrs['id'] = braceIds[braceIds.length - 1];

  for (const t of tokens) {
    if (t.startsWith('.')) {
      const c = t.slice(1).trim();
      if (c) classes.push(c);
      continue;
    }
    if (t.startsWith('#')) {
      const id = t.slice(1).trim();
      if (id) attrs['id'] = id;
      continue;
    }
    const eq = t.indexOf('=');
    if (eq > 0) {
      const key = t.slice(0, eq).trim();
      const val = t.slice(eq + 1).trim();
      if (!key) continue;
      if (key === 'class') {
        val.split(/[,\s]+/).filter(Boolean).forEach((c) => classes.push(c));
      } else if (key === 'id') {
        if (val) attrs['id'] = val;
      } else {
        attrs[key] = val;
      }
      continue;
    }
    // Bare token (no . # =) — becomes a class for DC markers
    if (t) classes.push(t);
  }

  if (classes.length) attrs['class'] = classes.join(' ');
  return attrs;
}

// Check if a paragraph contains a marker and extract any attributes
// Returns { matched: true, attrs: {...} } or { matched: false }
function parseMarker(tok, tokens, i, marker) {
  if (tok.type !== 'paragraph_open') return { matched: false };
  const inline = tokens[i + 1];
  if (!inline || inline.type !== 'inline') return { matched: false };

  const content = inline.content.trim();

  // Exact match (no attributes)
  if (content === marker) {
    return { matched: true, attrs: {} };
  }

  // Check if starts with marker followed by space
  if (content.startsWith(marker + ' ')) {
    const rest = content.slice(marker.length + 1).trim();
    return { matched: true, attrs: parseAttrs(rest) };
  }

  return { matched: false };
}

// Legacy helper for simple marker checks (no attrs needed)
function isMarker(tok, tokens, i, marker) {
  return parseMarker(tok, tokens, i, marker).matched;
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

function dcContinueClassifier(state) {
  let inSkillMode = false;
  let inSkillCard = false;

  for (let i = 0; i < state.tokens.length; i++) {
    const token = state.tokens[i];
    if (parseMarker(token, state.tokens, i, '@skill').matched) {
      inSkillMode = true;
      inSkillCard = false;
      continue;
    }
    if (isMarker(token, state.tokens, i, '@end-skill') ||
        isMarker(token, state.tokens, i, '@end-skills') ||
        isMarker(token, state.tokens, i, '@learning-path') ||
        isMarker(token, state.tokens, i, '@end-learning-path') ||
        isMarker(token, state.tokens, i, '@specialty') ||
        isMarker(token, state.tokens, i, '@end-specialty')) {
      inSkillMode = false;
      inSkillCard = false;
      continue;
    }
    if (token.type === 'layout_marker' &&
        ['chapter', 'spread', 'page', 'section'].includes(token.meta && token.meta.kind)) {
      inSkillMode = false;
      inSkillCard = false;
      continue;
    }
    if (inSkillMode && token.type === 'heading_open' && token.tag === 'h4') {
      inSkillCard = true;
      continue;
    }
    if (token.type !== 'dc_continue_candidate') continue;

    token.type = inSkillMode && inSkillCard ? 'dc_skill_continue' : 'layout_marker';
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

// Attributes that should be emitted verbatim (real HTML attributes).
// Everything else gets a `data-` prefix to avoid colliding with HTML semantics
// (e.g. an author writing `title=foo` shouldn't produce a real `title` tooltip;
// they meant `data-title="foo"`). markers.js does the same for marker attributes.
const PASSTHROUGH_HTML_ATTRS = new Set(['class', 'id', 'lang', 'dir', 'role', 'tabindex']);

function buildAttrs(userAttrs, baseClass) {
  let attrs = ' class="' + esc(baseClass + (userAttrs['class'] ? ' ' + userAttrs['class'] : '')) + '"';
  for (const [key, val] of Object.entries(userAttrs)) {
    if (key === 'class') continue;
    if (key.startsWith('data-') || key.startsWith('aria-') || PASSTHROUGH_HTML_ATTRS.has(key)) {
      attrs += ' ' + key + '="' + esc(val) + '"';
    } else {
      attrs += ' data-' + key + '="' + esc(val) + '"';
    }
  }
  return attrs;
}

function buildProcedureList(items) {
  let html = '<ol class="dc-steps">\n';
  items.forEach((itemHtml, idx) => {
    const stepNo = String(idx + 1).padStart(2, '0');
    // Strip @end-procedure if markdown-it consumed it as continuation of the last item
    const cleaned = itemHtml.replace(/\n?@end-procedure\s*$/g, '').trimEnd();
    html += '  <li><span class="dc-step-no">' + esc(stepNo) + '</span><span>' + cleaned + '</span></li>\n';
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
 * Main plugin function - default export for print-md
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
  // selectors in dc-components.css matching this structure.

  // Transform tokens after parsing
   md.core.ruler.push('dimm_city_transform', function (state) {
     const tokens = state.tokens;
     const newTokens = [];

     // State tracking
     let inSpecialty = false;
     let inLearningPath = false;
     let inSkillMode = false;
     let inSkillCard = false;
      let inOutcomeBlock = false;
      let outcomeBlockItems = [];
      let outcomeBlockFlush = false;
      let inLede = false;
      let inSidebar = false;
      let inSidebarBox = false;
      let inDefinition = false;
      let inProcedure = false;
      let inCallout = false;
      let inDmNote = false;
      let inBlock = false;
      let inCard = false;
      let inGear = false;
      let inToc = false;
      let inGlossary = false;
      let inSpecialtyCard = false;
      let inSpecialtyIntro = false;
      let inSpecialtyArt = false;
      let cardHeadingDone = false;
      let cardPullDone = false;
      let cardBodyOpen = false;
      /* dc#44: the real markdown-it blockquote_open token most recently seen
         inside the current @card's body — the candidate for `.dc-card-footer`.
         Re-pointed every time a new body blockquote appears (see addTokenClass/
         removeTokenClass below), so whichever one is open when the card closes
         is the one CSS's own `blockquote:last-of-type` would have picked. */
      let lastCardBodyBlockquote = null;
     let learningPathHasTitle = false;
     let inLearningPathShell = false;
     let currentSkillAttrs = {};
     let currentSpecialtyCode = '';
     let currentLearningPathIndex = 0;
     let currentLearningPathRef = '';
     let currentLearningPathName = '';
      let currentSkillIndex = 0;
      /* Whether the current skill card allows splitting (has .dc-allow-split).
         Used by outcomes-table to decide if it needs its own break-inside:avoid. */
      let currentCardCanSplit = false;
      /* Last skill-card title (parsed name + tier). Used by @continue to render
        a continuation card with a "{name} ▸" tab so the reader sees the link
        between Part 1 and the continuation. */
     let lastCardTitle = '';
     let lastCardTier = '';
     let specialtyCardCount = 0;  // resets per-specialty; used to emit data-position="even/odd"

     // Helper to close all open structures EXCEPT specialty (specialty
     // wraps the entire chapter section and is closed separately).
      function closeAll() {
        if (inCard) {
          if (cardBodyOpen) {
            newTokens.push(makeToken('html_block', '</div>\n')); // close .dc-card-body
            cardBodyOpen = false;
          }
          newTokens.push(makeToken('html_block', '</div>\n')); // close .dc-card
          inCard = false;
          cardHeadingDone = false;
          cardPullDone = false;
          lastCardBodyBlockquote = null;
        }
        if (inLede) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inLede = false;
        }
        if (inSidebar) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebar = false;
        }
        if (inSidebarBox) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebarBox = false;
        }
        if (inDefinition) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inDefinition = false;
        }
        if (inSkillCard) {
          newTokens.push(makeToken('html_block', '</div></div></div>\n'));
          inSkillCard = false;
       }
       if (inLearningPathShell) {
         newTokens.push(makeToken('html_block', '</div>\n'));
         inLearningPathShell = false;
       }
        if (inLearningPath) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inLearningPath = false;
        }
        if (inCallout) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inCallout = false;
        }
        if (inDmNote) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inDmNote = false;
        }
        if (inBlock) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inBlock = false;
        }
        if (inGear) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inGear = false;
        }
        if (inSpecialtyCard) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSpecialtyCard = false;
        }
        if (inSpecialtyIntro) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSpecialtyIntro = false;
        }
        if (inSpecialtyArt) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSpecialtyArt = false;
        }
        if (inToc) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inToc = false;
        }
        if (inGlossary) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inGlossary = false;
        }
        inProcedure = false;
        learningPathHasTitle = false;
        inSkillMode = false;
        currentSkillAttrs = {};
       currentCardCanSplit = false;
       currentLearningPathRef = '';
       currentLearningPathName = '';
      currentSkillIndex = 0;
    }

    function closeSpecialty() {
      closeAll();
      if (inSpecialty) {
        newTokens.push(makeToken('html_block', '</div>\n'));
        inSpecialty = false;
      }
       currentSpecialtyCode = '';
      currentLearningPathIndex = 0;
      // specialtyCardCount intentionally NOT reset here — it counts
      // all cards emitted in the current section so even/odd alternation
      // works across multiple @specialty blocks in the same card-grid.
    }

    for (let i = 0; i < tokens.length; i++) {
      const tok = tokens[i];

      // --- @sidebar / @end-sidebar ---
      const sidebarMarker = parseMarker(tok, tokens, i, '@sidebar');
      if (sidebarMarker.matched) {
        if (inSidebar) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebar = false;
        }
        if (inSidebarBox) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebarBox = false;
        }
        if (inDefinition) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inDefinition = false;
        }
        newTokens.push(makeToken('html_block', '<div' + buildAttrs(sidebarMarker.attrs, 'dc-sidebar') + '>\n'));
        inSidebar = true;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-sidebar')) {
        if (inSidebar) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebar = false;
        }
        i += 2;
        continue;
      }

      // --- @roll-table / @options-table (DEPRECATED 17.3.0) ---
      // These macros emitted tier-colored classes (dc-roll-table*, dc-options-table*)
      // with ZERO backing CSS and had zero usage in the book. They are now no-ops:
      // the markers (and their @end- counterparts) are stripped so any stray
      // occurrence renders nothing. Use standard GFM pipe tables instead — they are
      // auto-styled by dc-core.
      if (isMarker(tok, tokens, i, '@roll-table') ||
          isMarker(tok, tokens, i, '@end-roll-table') ||
          isMarker(tok, tokens, i, '@options-table') ||
          isMarker(tok, tokens, i, '@end-options-table')) {
        i += 2;
        continue;
      }

      // --- @outcome / @end-outcome ---
      // Collects pipe-separated rows and emits a styled dc-outcomes block.
      // Syntax:
      //   @outcome [flush]
      //   20 | Crit | You flow. Automatic success — no roll needed.
      //   11–19 | Hit | You succeed cleanly.
      //   @end-outcome
      // Row ordering determines tier class: crit, hit, mixed, miss, fail.
      // Also handles the compact form where @outcome, rows, and @end-outcome
      // are all in one paragraph block (no blank lines between them).
      //
      // The compact form arrives as ONE multi-line inline token, so it must
      // fall through to the compact handler below. Without the multi-line
      // guard `@outcome flush` + rows matches here (content starts with
      // "@outcome ") and `i += 2` skips the whole inline — swallowing every
      // row AND the inline @end-outcome, and leaving inOutcomeBlock stuck on.
      const ocInline = tokens[i + 1];
      const ocIsCompact = tok.type === 'paragraph_open' && ocInline
        && ocInline.type === 'inline' && ocInline.content.indexOf('\n') !== -1;
      if (!ocIsCompact && isMarker(tok, tokens, i, '@outcome')) {
        inOutcomeBlock = true;
        outcomeBlockItems = [];
        // Check for flush modifier
        const ocContent = ocInline ? ocInline.content.trim() : '';
        outcomeBlockFlush = /\bflush\b/.test(ocContent.replace('@outcome', ''));
        i += 2;
        continue;
      }

      // Handle compact multiline @outcome block: all rows + @end-outcome in one paragraph
      if (tok.type === 'paragraph_open' && !inOutcomeBlock) {
        const inlineTok = tokens[i + 1];
        if (inlineTok && inlineTok.type === 'inline') {
          const firstLine = inlineTok.content.split('\n')[0].trim();
          if (firstLine === '@outcome' || firstLine.startsWith('@outcome ')) {
            // This is a compact outcome block — process all lines inline
            inOutcomeBlock = false; // We'll handle it fully here
            const isFlush = /\bflush\b/.test(firstLine.replace('@outcome', ''));
            const rows = [];
            const allLines = inlineTok.content.split('\n');
            let inBlock = false;
            for (const line of allLines) {
              const trimmed = line.trim();
              if (trimmed === '@outcome' || trimmed.startsWith('@outcome ')) { inBlock = true; continue; }
              if (trimmed === '@end-outcome') { inBlock = false; continue; }
              if (inBlock && trimmed && !trimmed.startsWith('#')) rows.push(trimmed);
            }
            if (rows.length > 0) {
              const tierClasses = ['crit', 'hit', 'mixed', 'miss', 'fail'];
              const wrapperClass = 'dc-outcomes' + (isFlush ? ' dc-flush' : '');
              let html = '<div class="' + wrapperClass + '">\n';
              html += '  <div class="dc-outcomes-label">Outcomes</div>\n';
              rows.forEach((line, idx) => {
                const parts = line.split('|').map(s => s.trim());
                const range = parts[0] || '';
                const name  = parts[1] || '';
                const desc  = parts[2] || '';
                const tier  = tierClasses[idx] || 'hit';
                html += '  <div class="dc-outcome-row ' + tier + '">\n';
                html += '    <span class="dc-outcome-key tier-' + tier + '">';
                html += '<span class="dc-outcome-name">' + esc(name) + '</span>';
                html += '<span class="dc-outcome-roll">' + esc(range) + '</span>';
                html += '</span>\n';
                html += '    <span class="dc-outcome-text">' + md.renderInline(desc) + '</span>\n';
                html += '  </div>\n';
              });
              html += '</div>\n';
              newTokens.push(makeToken('html_block', html));
              i += 2; // skip inline + paragraph_close
              continue;
            }
          }
        }
      }

      if (inOutcomeBlock) {
        // Collect inline tokens (each inline contains one or more lines)
        if (tok.type === 'inline') {
          // Each inline token can have newlines — split into lines
          const lines = tok.content.split('\n');
          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed && !trimmed.startsWith('#')) {
              outcomeBlockItems.push(trimmed);
            }
          }
          continue;
        }
        // @end-outcome — emit the block
        if (isMarker(tok, tokens, i, '@end-outcome')) {
          inOutcomeBlock = false;
          const tierClasses = ['crit', 'hit', 'mixed', 'miss', 'fail'];
          const wrapperClass = 'dc-outcomes' + (outcomeBlockFlush ? ' dc-flush' : '');
          let html = '<div class="' + wrapperClass + '">\n';
          html += '  <div class="dc-outcomes-label">Outcomes</div>\n';
          outcomeBlockItems.forEach((line, idx) => {
            const parts = line.split('|').map(s => s.trim());
            const range = parts[0] || '';
            const name  = parts[1] || '';
            const desc  = parts[2] || '';
            const tier  = tierClasses[idx] || 'hit';
            html += '  <div class="dc-outcome-row ' + tier + '">\n';
            html += '    <span class="dc-outcome-key tier-' + tier + '">';
            html += '<span class="dc-outcome-name">' + esc(name) + '</span>';
            html += '<span class="dc-outcome-roll">' + esc(range) + '</span>';
            html += '</span>\n';
            html += '    <span class="dc-outcome-text">' + md.renderInline(desc) + '</span>\n';
            html += '  </div>\n';
          });
          html += '</div>\n';
          newTokens.push(makeToken('html_block', html));
          outcomeBlockItems = [];
          i += 2;
          continue;
        }
        // Skip paragraph open/close wrapper tokens — we only want inline content
        if (tok.type === 'paragraph_open' || tok.type === 'paragraph_close') {
          continue;
        }
        // Pass through anything else (shouldn't normally occur)
        continue;
      }

      // Check for @specialty marker (must come before @learning-path/@skill
      // since it auto-closes everything else)
      const sidebarBoxMarker = parseMarker(tok, tokens, i, '@sidebar-box');
      if (sidebarBoxMarker.matched) {
        if (inSidebarBox) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebarBox = false;
        }
        if (inSidebar) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebar = false;
        }
        if (inDefinition) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inDefinition = false;
        }
        newTokens.push(makeToken('html_block', '<div' + buildAttrs(sidebarBoxMarker.attrs, 'dc-prose-panel dc-sidebar-box') + '>\n'));
        inSidebarBox = true;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-sidebar-box')) {
        if (inSidebarBox) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebarBox = false;
        }
        i += 2;
        continue;
      }

      const definitionMarker = parseMarker(tok, tokens, i, '@definition');
      if (definitionMarker.matched) {
        if (inDefinition) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inDefinition = false;
        }
        if (inSidebar) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebar = false;
        }
        if (inSidebarBox) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSidebarBox = false;
        }
        newTokens.push(makeToken('html_block', '<div' + buildAttrs(definitionMarker.attrs, 'dc-prose-panel dc-definition-block') + '>\n'));
        inDefinition = true;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-definition')) {
        if (inDefinition) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inDefinition = false;
        }
        i += 2;
        continue;
      }

      const procedureMarker = parseMarker(tok, tokens, i, '@procedure');
      if (procedureMarker.matched) {
        // @procedure auto-closes any prior open section so a forgotten
        // @end-procedure can't strand the previous transform open. closeAll()
        // also clears inProcedure, so set the flag AFTER closing.
        closeAll();
        inProcedure = true;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-procedure')) {
        inProcedure = false;
        i += 2;
        continue;
      }

      // --- @callout / @end-callout ---
      // Block-level alert wrapper. variant="note|warning|dm|vibe|origin|visit|gear"
      const calloutMarker = parseMarker(tok, tokens, i, '@callout');
      if (calloutMarker.matched) {
        closeAll();
        const variant = (calloutMarker.attrs['variant'] || 'note').toLowerCase();
        const CALLOUT_VARIANTS = {
          'note':    { classes: 'dc-note',           label: 'Note' },
          'warning': { classes: 'dc-note warning',   label: 'Warning' },
          'dm':      { classes: 'dc-dm-note',        label: 'Dream Master Note' },
          'vibe':    { classes: 'dc-vibe-callout',   label: 'Vibe' },
          'origin':  { classes: 'dc-origin-callout', label: 'Origin' },
          'visit':   { classes: 'dc-visit-callout',  label: 'Visit' },
          'gear':    { classes: 'dc-gear-callout',   label: 'Gear' },
        };
        const cfg = CALLOUT_VARIANTS[variant] || CALLOUT_VARIANTS['note'];
        const labelOverride = calloutMarker.attrs['label'];
        const labelText = labelOverride ? esc(labelOverride) : cfg.label;
        const calloutClass = 'dc-alert ' + cfg.classes +
          (calloutMarker.attrs['class'] ? ' ' + esc(calloutMarker.attrs['class']) : '');
        newTokens.push(makeToken('html_block',
          '<div class="' + calloutClass + '">\n' +
          '<span class="dc-alert-label">' + labelText + '</span>\n'
        ));
        inCallout = true;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-callout')) {
        if (inCallout) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inCallout = false;
        }
        i += 2;
        continue;
      }

      // --- @dm-note / @end-dm-note ---
      // Block-level DM note wrapper. Equivalent to > [!DM] but supports multi-paragraph content.
      const dmNoteMarker = parseMarker(tok, tokens, i, '@dm-note');
      if (dmNoteMarker.matched) {
        closeAll();
        const labelOverride = dmNoteMarker.attrs['label'];
        const labelText = labelOverride ? esc(labelOverride) : 'Dream Master Note';
        newTokens.push(makeToken('html_block',
          '<div class="dc-alert dc-dm-note">\n' +
          '<span class="dc-alert-label">' + labelText + '</span>\n'
        ));
        inDmNote = true;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-dm-note')) {
        if (inDmNote) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inDmNote = false;
        }
        i += 2;
        continue;
      }

      // --- @block (section enclosures) ---
      // Reusable card-like text section enclosures. Four variants with distinct
      // clip-path geometry, surface, and accent colors. Each emits a .dc-block
      // container with an optional titled header band (.dc-block-title).
      //
      // Syntax:   @block .dc-panel|.dc-slate|.dc-shard|.dc-codex label="Title"

      const blockUnifiedMarker = parseMarker(tok, tokens, i, '@block');
      if (blockUnifiedMarker.matched) {
        closeAll();
        const blockLabel = blockUnifiedMarker.attrs['label'] ? esc(blockUnifiedMarker.attrs['label']) : '';
        const blockTitleHtml = blockLabel ? '<div class="dc-block-title">' + blockLabel + '</div>\n' : '';
        let blockClass = 'dc-block';
        if (blockUnifiedMarker.attrs['class']) {
          blockClass += ' ' + blockUnifiedMarker.attrs['class'];
        } else if (blockUnifiedMarker.attrs['variant']) {
          blockClass += ' dc-' + blockUnifiedMarker.attrs['variant'].toLowerCase();
        }
        newTokens.push(makeToken('html_block', '<div class="' + blockClass + '">\n' + blockTitleHtml));
        inBlock = true;
        i += 2;
        continue;
      }


      if (isMarker(tok, tokens, i, '@end-block')) {
        if (inBlock) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inBlock = false;
        }
        i += 2;
        continue;
      }

      // --- @card / @end-card ---
      // Generic card primitive. Emits .dc-card with optional sub-elements:
      //   .dc-card-heading  — first h4 after @card
      //   .dc-card-pull     — first blockquote after the heading (move outside body)
      //   .dc-card-body     — all remaining content
      // Author syntax:
      //   @card .dc-flaws
      //   #### Title
      //   > Pull quote
      //   Body paragraph.
      //   > Footer blockquote
      //
      //   @end-card
      //
      // IMPORTANT: @end-card must be preceded by a blank line when the last
      // content before it is a blockquote. Without the blank line markdown-it
      // lazily continues the blockquote and absorbs the @end-card marker.
      const cardMarker = parseMarker(tok, tokens, i, '@card');
      if (cardMarker.matched) {
        closeAll();
        const userAttrs = cardMarker.attrs;
        const extraClass = userAttrs['class'] ? ' ' + userAttrs['class'] : '';
        const extraId = userAttrs['id'] ? ' id="' + esc(userAttrs['id']) + '"' : '';
        newTokens.push(makeToken('html_block', '<div class="dc-card' + extraClass + '"' + extraId + '>\n'));
        inCard = true;
        cardHeadingDone = false;
        cardPullDone = false;
        cardBodyOpen = false;
        lastCardBodyBlockquote = null;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-card')) {
        if (inCard) {
          if (cardBodyOpen) {
            newTokens.push(makeToken('html_block', '</div>\n')); // close .dc-card-body
            cardBodyOpen = false;
          }
          newTokens.push(makeToken('html_block', '</div>\n')); // close .dc-card
          inCard = false;
          cardHeadingDone = false;
          cardPullDone = false;
          lastCardBodyBlockquote = null;
        }
        i += 2;
        continue;
      }

      // --- @specialty-card / @end-specialty-card ---
      // Summary card used in the choose-specialty overview grid.
      // Shape and color inherited from .specialty.<name> parent container.
      const specialtyCardMarker = parseMarker(tok, tokens, i, '@specialty-card');
      if (specialtyCardMarker.matched) {
        closeAll();
        specialtyCardCount++;
        const positionAttr = ' data-position="' + (specialtyCardCount % 2 === 0 ? 'even' : 'odd') + '"';
        newTokens.push(makeToken('html_block', '<div' + buildAttrs(specialtyCardMarker.attrs, 'dc-specialty-card') + positionAttr + '>\n'));
        inSpecialtyCard = true;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-specialty-card')) {
        if (inSpecialtyCard) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSpecialtyCard = false;
        }
        i += 2;
        continue;
      }

      // --- @specialty-intro / @end-specialty-intro ---
      // Full-page specialty intro panel. Shape/color from .specialty.<name> parent.
      const specialtyIntroMarker = parseMarker(tok, tokens, i, '@specialty-intro');
      if (specialtyIntroMarker.matched) {
        closeAll();
        newTokens.push(makeToken('html_block', '<div' + buildAttrs(specialtyIntroMarker.attrs, 'dc-specialty-intro') + '>\n'));
        inSpecialtyIntro = true;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-specialty-intro')) {
        if (inSpecialtyIntro) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSpecialtyIntro = false;
        }
        i += 2;
        continue;
      }

      // --- @specialty-art / @end-specialty-art ---
      // Full-bleed art panel for a specialty profile. Emits .dc-specialty-art
      // (CSS: dc-components.css + page-rules.css `.dc-specialty-art { page: full; }`).
      const specialtyArtMarker = parseMarker(tok, tokens, i, '@specialty-art');
      if (specialtyArtMarker.matched) {
        closeAll();
        newTokens.push(makeToken('html_block', '<div' + buildAttrs(specialtyArtMarker.attrs, 'dc-specialty-art') + '>\n'));
        inSpecialtyArt = true;
        i += 2;
        continue;
      }

      if (isMarker(tok, tokens, i, '@end-specialty-art')) {
        if (inSpecialtyArt) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inSpecialtyArt = false;
        }
        i += 2;
        continue;
      }


      // --- @toc / @end-toc ---
      const tocMarker = parseMarker(tok, tokens, i, '@toc');
      if (tocMarker.matched) {
        closeAll();
        newTokens.push(makeToken('html_block', '<div class="dc-toc">\n'));
        inToc = true;
        i += 2; continue;
      }
      if (isMarker(tok, tokens, i, '@end-toc')) {
        if (inToc) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inToc = false;
        }
        i += 2; continue;
      }

      // Removed 2026-05-17: @two-column / @three-column / @no-break.
      // Use @section .gp-columns-2 / @section .gp-columns-3 / @section .pmd-no-break
      // instead — markers.js emits identical layout semantics, with the
      // added `.section` class that picks up `break-inside: avoid` from MARKER_CSS.
      // See docs/migrations/2026-05-removing-container-syntax.md for the rationale.

      // --- @gear / @end-gear ---
      // Shorthand for @card .dc-gear — emits a bare `.dc-card.dc-gear`.
      // NOTE: there is NO .section.dc-gear-list wrapper (an earlier comment
      // claimed one, and dc-components.css carried ~40 lines of CSS keyed on
      // it that could never match). Style `.dc-card.dc-gear` directly.
      const gearMarker = parseMarker(tok, tokens, i, '@gear');
      if (gearMarker.matched) {
        closeAll();
        newTokens.push(makeToken('html_block', '<div' + buildAttrs(gearMarker.attrs, 'dc-card dc-gear') + '>\n'));
        inGear = true;
        i += 2; continue;
      }
      if (isMarker(tok, tokens, i, '@end-gear')) {
        if (inGear) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inGear = false;
        }
        i += 2; continue;
      }

      // --- @tape (single-line tape divider) ---
      const tapeMarker = parseMarker(tok, tokens, i, '@tape');
      if (tapeMarker.matched) {
        const labelAttr = tapeMarker.attrs['label'] || '';
        const extraClass = tapeMarker.attrs['class'] ? ' ' + esc(tapeMarker.attrs['class']) : '';
        newTokens.push(makeToken('html_block', '<div class="dc-tape' + extraClass + '">' + esc(labelAttr) + '</div>\n'));
        i += 2; continue;
      }

      // --- @lede / @end-lede ---
      // Emits .dc-intro (canonical). The legacy bare `lede` class was removed
      // 2026-05-17 — there were no CSS rules using it, only the dc-prefixed
      // form is styled.
      const ledeMarker = parseMarker(tok, tokens, i, '@lede');
      if (ledeMarker.matched) {
        closeAll();
        newTokens.push(makeToken('html_block', '<div class="dc-intro">\n'));
        inLede = true;
        i += 2; continue;
      }
      if (isMarker(tok, tokens, i, '@end-lede')) {
        if (inLede) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inLede = false;
        }
        i += 2; continue;
      }

      // --- @glossary / @end-glossary ---
      const glossaryMarker = parseMarker(tok, tokens, i, '@glossary');
      if (glossaryMarker.matched) {
        closeAll();
        newTokens.push(makeToken('html_block', '<div class="dc-terms">\n'));
        inGlossary = true;
        i += 2; continue;
      }
      if (isMarker(tok, tokens, i, '@end-glossary')) {
        if (inGlossary) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inGlossary = false;
        }
        i += 2; continue;
      }

      const specialtyMarker = parseMarker(tok, tokens, i, '@specialty');
      if (specialtyMarker.matched) {
        closeSpecialty();
        const userAttrs = specialtyMarker.attrs;
        const specClass = 'dc-specialty' + (userAttrs['class'] ? ' ' + userAttrs['class'] : '');
        newTokens.push(makeToken('html_block', '<div' + buildAttrs(userAttrs, 'dc-specialty') + '>\n'));
        inSpecialty = true;
        currentSpecialtyCode = specialtyCodeFromClass(specClass);
        currentLearningPathIndex = 0;
        i += 2;
        continue;
      }

      // Check for @end-specialty marker
      if (isMarker(tok, tokens, i, '@end-specialty')) {
        closeSpecialty();
        i += 2;
        continue;
      }

      // Check for @learning-path marker
      const learningPathMarker = parseMarker(tok, tokens, i, '@learning-path');
      if (learningPathMarker.matched) {
        closeAll();
        inLearningPath = true;
        inLearningPathShell = true;
        learningPathHasTitle = false;
        currentLearningPathIndex++;
        currentLearningPathRef = currentSpecialtyCode + currentLearningPathIndex;
        currentLearningPathName = '';
        currentSkillIndex = 0;

        // Build opening tag with any custom attributes (no variant= — use .specialty.<name> parent)
        const lpUserAttrs = learningPathMarker.attrs;
        newTokens.push(makeToken('html_block', '<div' + buildAttrs(lpUserAttrs, 'dc-learning-path dc-path-block') + ' data-path-ref="' + esc(currentLearningPathRef) + '">\n<div class="dc-path-shell">\n'));
        i += 2; // Skip paragraph_open, inline, paragraph_close
        continue;
      }

      // Check for @skill marker
      const skillMarker = parseMarker(tok, tokens, i, '@skill');
      if (skillMarker.matched) {
        if (inLearningPathShell) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inLearningPathShell = false;
        }
        // Close previous skill card if open
        if (inSkillCard) {
          newTokens.push(makeToken('html_block', '</div></div></div>\n'));
          inSkillCard = false;
        }
        inSkillMode = true;
        // Store skill attrs for use when building the card
        currentSkillAttrs = skillMarker.attrs;
        i += 2;
        continue;
      }

      // Check for @end-skill marker
      if (isMarker(tok, tokens, i, '@end-skill') || isMarker(tok, tokens, i, '@end-skills')) {
        closeAll();
        inSkillMode = false;
        i += 2;
        continue;
      }

      // The bridge above protects skill-card @continue from Gutterpress's
      // earlier generic section-marker transform. Bare markdown-it instances
      // still reach this branch as the original paragraph marker.
      const isBridgedSkillContinue = tok.type === 'dc_skill_continue';
      if (isBridgedSkillContinue || isMarker(tok, tokens, i, '@continue')) {
        if (inSkillMode && inSkillCard) {
          // Close current card
          newTokens.push(makeToken('html_block', '</div></div></div>\n'));
          inSkillCard = false;

          // No variant class — shape inherited from .specialty.<name> parent container

          // Honor allow-split on continuation cards too
          const userClassList = (currentSkillAttrs['class'] || '').split(/\s+/).filter(Boolean);
          const allowSplitCont = userClassList.includes('dc-allow-split');
          const breakInsideContAttr = allowSplitCont ? '' : ' data-break-inside="avoid"';

          let cardHtml = '<div' + buildAttrs(currentSkillAttrs, 'dc-skill-card dc-skill-card-cont') + ' name="' + esc(slugify(lastCardTitle)) + '"' + breakInsideContAttr + '>\n';
          const fullTabClassCont = 'dc-card-tab dc-card-tab-cont';
          cardHtml += '  <div class="' + fullTabClassCont + '">\n';
          cardHtml += '    <span class="dc-tab-title">' + esc(lastCardTitle) + ' ▸</span>\n';
          if (lastCardTier) {
            cardHtml += '    <span class="dc-tab-tier">' + esc(lastCardTier) + '</span>\n';
          }
          cardHtml += '  </div>\n';
          const fullBodyClassCont = 'dc-card-body';
          cardHtml += '  <div class="' + fullBodyClassCont + '">\n';
          cardHtml += '    <div class="dc-card-inner">\n';

          newTokens.push(makeToken('html_block', cardHtml));
          inSkillCard = true;
          if (!isBridgedSkillContinue) i += 2;
          continue;
        }
      }

      // Check for @end-learning-path marker
      if (isMarker(tok, tokens, i, '@end-learning-path')) {
        if (inLearningPathShell) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inLearningPathShell = false;
        }
        if (inLearningPath) {
          newTokens.push(makeToken('html_block', '</div>\n'));
          inLearningPath = false;
          learningPathHasTitle = false;
        }
        i += 2;
        continue;
      }

      // Inside @learning-path section
      if (inLearningPath && !inSkillMode) {
        // H3 = Learning path title (banner)
        if (tok.type === 'heading_open' && tok.tag === 'h3') {
          const inlineTok = tokens[i + 1];
          const titleText = inlineTok && inlineTok.content ? inlineTok.content : '';
          currentLearningPathName = titleText;
          newTokens.push(makeToken('html_block', '<h2 class="dc-spray"><span class="dc-path-sticker">' + esc(currentLearningPathRef) + '</span>' + esc(titleText) + '</h2>\n'));
          learningPathHasTitle = true;
          i += 2; // Skip heading_open, inline, heading_close
          continue;
        }

        // Blockquote = Subtitle/description (after title)
        if (tok.type === 'blockquote_open' && learningPathHasTitle) {
          let bqContent = '';
          let j = i + 1;
          while (j < tokens.length && tokens[j].type !== 'blockquote_close') {
            if (tokens[j].type === 'inline') {
              bqContent = renderInlineChildren(tokens[j], md);
            }
            j++;
          }
          newTokens.push(makeToken('html_block', '<div class="dc-intro">' + bqContent + '</div>\n'));
          i = j;
          continue;
        }

        // Bullet list = Sticker chain
        if (tok.type === 'bullet_list_open') {
          const { items, endIndex } = collectBulletListItems(tokens, i);
          if (items.length > 0) {
            newTokens.push(makeToken('html_block', buildStickerChain(items)));
          }
          i = endIndex;
          continue;
        }

        // Paragraphs = body prose within the learning path block
        if (tok.type === 'paragraph_open') {
          const inlineTok = tokens[i + 1];
          const closeTok = tokens[i + 2];
          if (inlineTok && inlineTok.type === 'inline' && closeTok && closeTok.type === 'paragraph_close') {
            const bodyHtml = renderInlineChildren(inlineTok, md);
            newTokens.push(makeToken('html_block', '<p>' + bodyHtml + '</p>\n'));
            i += 2;
            continue;
          }
        }

        // Pass through other content in learning-path
        newTokens.push(tok);
        continue;
      }

      // Inside @card section
      // (@end-card is handled by the top-level dispatch above, which runs
      // unconditionally before this block is ever reached.)
      if (inCard) {
        // h4 = card heading (first h4 only)
        if (tok.type === 'heading_open' && tok.tag === 'h4' && !cardHeadingDone) {
          const inlineTok = tokens[i + 1];
          const headingHtml = inlineTok && inlineTok.children
            ? md.renderer.render(inlineTok.children, md.options, {})
            : esc(inlineTok ? inlineTok.content || '' : '');
          newTokens.push(makeToken('html_block', '<div class="dc-card-heading">' + headingHtml + '</div>\n'));
          cardHeadingDone = true;
          i += 2; // skip inline + heading_close
          continue;
        }

        // First blockquote after heading (before body opens) = pull quote
        if (tok.type === 'blockquote_open' && cardHeadingDone && !cardPullDone && !cardBodyOpen) {
          let bqContent = '';
          let j = i + 1;
          let blockquoteCloseIdx = -1;
          while (j < tokens.length && tokens[j].type !== 'blockquote_close') {
            if (tokens[j].type === 'inline') {
              // The inline content may have @end-card appended as a lazy continuation.
              // Extract text, strip the trailing marker, render the inline children.
              let rawText = tokens[j].content || '';
              // Remove lazy continuation @end-card from the end
              rawText = rawText.replace(/\n@end-card\s*$/, '').replace(/\s+@end-card\s*$/, '').trim();

              // Render children, but strip @end-card from the rendered HTML if it appears
              bqContent = tokens[j].children
                ? md.renderer.render(tokens[j].children, md.options, {})
                : esc(rawText);
              // Strip @end-card from rendered output as a fallback
              bqContent = bqContent.replace(/\s*@end-card\s*$/, '').replace(/@end-card\s*<\/p>/, '</p>');
            }
            j++;
          }
          blockquoteCloseIdx = j;
          newTokens.push(makeToken('html_block', '<div class="dc-card-pull">' + bqContent + '</div>\n'));
          newTokens.push(makeToken('html_block', '<div class="dc-card-body">\n'));
          cardPullDone = true;
          cardBodyOpen = true;
          i = blockquoteCloseIdx; // for-loop i++ lands at token after blockquote_close
          continue;
        }

        // Open body for any non-heading, non-pull content that arrived before body was opened
        if (!cardBodyOpen) {
          newTokens.push(makeToken('html_block', '<div class="dc-card-body">\n'));
          cardBodyOpen = true;
          // Do NOT skip tok — fall through to passthrough below
        }

        // Inside body: strip @end-card from blockquotes (lazy continuation artifact)
        if (tok.type === 'blockquote_open') {
          let j = i + 1;
          let blockquoteCloseIdx = -1;
          while (j < tokens.length && tokens[j].type !== 'blockquote_close') {
            if (tokens[j].type === 'inline') {
              // Strip @end-card from inline content
              let rawText = tokens[j].content || '';
              rawText = rawText.replace(/\n@end-card\s*$/, '').replace(/\s+@end-card\s*$/, '').trim();
              tokens[j].content = rawText;
            }
            j++;
          }

          // dc#44: tag the current blockquote as the card-footer candidate and
          // untag whichever one held that title before. The plugin streams
          // tokens once with no lookahead, so it can't know in advance which
          // body blockquote will turn out to be last — instead it keeps the
          // tag on exactly one token at a time, moving it forward on every
          // new body blockquote, so whichever one is tagged when the card
          // closes is the one `blockquote:last-of-type` would also match.
          // The CSS selector stays as the fallback for one release (dc#44).
          if (lastCardBodyBlockquote) {
            removeTokenClass(lastCardBodyBlockquote, 'dc-card-footer');
          }
          addTokenClass(tok, 'dc-card-footer');
          lastCardBodyBlockquote = tok;
        }

        // Pass through card body content unchanged
        newTokens.push(tok);
        continue;
      }

      // Mark image-only paragraphs so layout rules can target them without
      // relying on p:has(img). The base CSS rule
      // (p.dc-img-wrapper { padding:0; margin:0 }) lives in components.css.
      // Per-page rules can further refine position via .page.my-class p.dc-img-wrapper.
      if (tok.type === 'paragraph_open') {
        const inlineTok = tokens[i + 1];
        const closeTok = tokens[i + 2];
        if (inlineTok && inlineTok.type === 'inline' && closeTok && closeTok.type === 'paragraph_close') {
          const hasOnlyImage = Array.isArray(inlineTok.children)
            && inlineTok.children.length === 1
            && inlineTok.children[0].type === 'image';
          if (hasOnlyImage) {
            tok.attrSet('class', 'dc-img-wrapper');
          }
        }
      }

      // Inside @skill section
      if (inSkillMode) {
        // Auto-close skill mode before any layout marker.
        // Example: chapter-02's inline example skill is followed directly by
        // `@page` with no explicit `@end-skill`. If we pass the layout marker
        // through while the card is still open, the next page wrapper and all
        // following content are emitted inside the current .dc-skill-card,
        // producing malformed HTML.
        //
        // This single check covers `@page`, `@section`, `@chapter` and
        // `@spread`: markers.js tokenizes those lines as `layout_marker`
        // block tokens and rewrites them into `layout_*` tokens in a core rule
        // registered with `md.core.ruler.after('block', ...)`, whereas this
        // plugin registers with `md.core.ruler.push(...)` — so the marker
        // transform ALWAYS runs first and the raw marker paragraphs no longer
        // exist by the time we get here.
        if (tok.type && tok.type.startsWith('layout_')) {
          closeAll();
          newTokens.push(tok);
          continue;
        }

        // H4 = Skill card title
        if (tok.type === 'heading_open' && tok.tag === 'h4') {
          // Close previous card if open
          if (inSkillCard) {
            newTokens.push(makeToken('html_block', '</div></div></div>\n'));
          }

          const inlineTok = tokens[i + 1];
          const h4Text = inlineTok && inlineTok.content ? inlineTok.content : '';
          const parsed = parseSkillTitle(h4Text);
          currentSkillIndex++;

          // No variant class — shape is inherited from .specialty.<name> parent container

          // Card splitting strategy:
          //   - `.dc-allow-split`: omit `data-break-inside="avoid"` so the card
          //     can split across pages (for cards taller than a page).
          //   - Default: `data-break-inside="avoid"` keeps card intact.
          const userClasses = (currentSkillAttrs['class'] || '').split(/\s+/);
          const allowSplit = userClasses.includes('dc-allow-split');
          const breakInsideAttr = allowSplit ? '' : ' data-break-inside="avoid"';

          // Track allowSplit for outcomes-table (needs avoid only when card can split)
          currentCardCanSplit = allowSplit;

          // Track for @continue continuation cards.
          lastCardTitle = parsed.name;
          lastCardTier = parsed.tier || '';

          // Build card structure
          let cardHtml = '<div' + buildAttrs(currentSkillAttrs, 'dc-skill-card') + ' name="' + esc(slugify(parsed.name)) + '"' + breakInsideAttr + '>\n';
          const tabBaseClass = 'dc-card-tab' + (parsed.highlight ? ' dc-highlight' : '');
          cardHtml += '  <div class="' + tabBaseClass + '">\n';
          const autoTier = currentLearningPathRef ? currentLearningPathRef + '.' + currentSkillIndex : '';
          cardHtml += '    <span class="dc-tab-title">' + esc(parsed.name) + '</span>\n';
          cardHtml += '    <span class="dc-tab-tier">' + esc(parsed.tier || autoTier) + '</span>\n';
          cardHtml += '  </div>\n';

          const bodyBaseClass = 'dc-card-body' + (parsed.highlight ? ' dc-highlight-body' : '');
          cardHtml += '  <div class="' + bodyBaseClass + '">\n';
          cardHtml += '    <div class="dc-card-inner">\n';

          newTokens.push(makeToken('html_block', cardHtml));
          inSkillCard = true;
          i += 2;
          continue;
        }

        // H5 = Sub-header (like "Outcomes")
        if (tok.type === 'heading_open' && tok.tag === 'h5' && inSkillCard) {
          const inlineTok = tokens[i + 1];
          const h5Text = inlineTok && inlineTok.content ? inlineTok.content : '';
          // Skip "Outcomes" header since the table will have its own label
          if (h5Text.toLowerCase() !== 'outcomes') {
            newTokens.push(makeToken('html_block', '<div class="dc-sub-header">' + esc(h5Text) + '</div>\n'));
          }
          i += 2;
          continue;
        }

        // Blockquote = Flavor text (inside skill card)
        if (tok.type === 'blockquote_open' && inSkillCard) {
          let bqContent = '';
          let j = i + 1;
          while (j < tokens.length && tokens[j].type !== 'blockquote_close') {
            if (tokens[j].type === 'inline') {
              bqContent = renderInlineChildren(tokens[j], md);
            }
            j++;
          }
          newTokens.push(makeToken('html_block', '<p class="dc-flavor">' + bqContent + '</p>\n'));
          i = j;
          continue;
        }

        // Ordered list = Abilities
        if (tok.type === 'ordered_list_open' && inSkillCard) {
          const { items, endIndex } = collectOrderedListItems(tokens, i, md);

          items.forEach((itemHtml, idx) => {
            const ability = parseAbilityFromListItem(itemHtml);
            if (ability) {
              let posAttrs = '';
              if (items.length > 1) {
                if (idx === items.length - 1) posAttrs = ' data-ability-last="true"';
                if (idx === items.length - 2) posAttrs = ' data-ability-penultimate="true"';
              }
              let output = '<div class="dc-ability"' + posAttrs + '>\n';
              output += '  <span class="' + ability.apClass + '">' + esc(ability.apVal) + '</span>\n';
              output += '  <p class="dc-ability-text">' + ability.text + '</p>\n';
              output += '</div>\n';
              newTokens.push(makeToken('html_block', output));
            } else {
              // Fallback: render as paragraph
              newTokens.push(makeToken('html_block', '<p>' + itemHtml + '</p>\n'));
            }
          });

          i = endIndex;
          continue;
        }

        // Bullet list inside skill card (e.g., sub-points)
        if (tok.type === 'bullet_list_open' && inSkillCard) {
          // When the card can split (allow-split → no card-level avoid), keep
          // short sub-lists whole so a break can't strand e.g. the "Arm:" bullet
          // on one page and "Leg:" on the next. Mirrors the table logic below
          // (buildTable receives currentCardCanSplit as needsAvoid). When the card
          // is NOT splittable it already carries card-level avoid, so adding a
          // nested list avoid would create a conflicting inner break boundary.
          if (currentCardCanSplit) {
            tok.attrSet('data-break-inside', 'avoid');
          }
          newTokens.push(tok);
          continue;
        }

        // Table = Outcomes or Distance
        if (tok.type === 'table_open' && inSkillCard) {
          const tableTokens = collectTableTokens(tokens, i);
          const headers = getTableHeaders(tableTokens);
          const tableClass = classifyTable(headers);
          // Tables this plugin does not transform pass through untouched.
          // They used to fall into buildTable()'s generic branch, which
          // rebuilt markup from tbody rows only and dropped the <thead> core
          // had already emitted correctly — every ordinary table in a skill
          // card printed headerless (86 tables, only 22 keeping a thead).
          if (!tableClass) {
            newTokens.push(tok);
            continue;
          }
          // Pass currentCardCanSplit: outcomes-block needs data-break-inside="avoid"
          // only when the parent card can be split (no card-level avoid). When the
          // card already has card-level avoid, a nested outcomes-block avoid creates
          // a conflicting inner break that splits the card at the outcomes boundary.
          const tableHtml = buildTable(tableTokens, tableClass, md, currentCardCanSplit);

          newTokens.push(makeToken('html_block', tableHtml));
          i = skipToTableClose(tokens, i);
          continue;
        }

        // Pass through other tokens in skill mode
        newTokens.push(tok);
        continue;
      }

      if (inProcedure && tok.type === 'ordered_list_open') {
        const { items, endIndex } = collectOrderedListItems(tokens, i, md);
        if (items.length > 0) {
          newTokens.push(makeToken('html_block', buildProcedureList(items)));
        }
        i = endIndex;
        continue;
      }

      if (inProcedure && tok.type === 'ordered_list_close') {
        continue;
      }

      // Outside any special section - pass through unchanged
      newTokens.push(tok);
    }

    // Close any open structures at EOF

    // Warn if @procedure was opened without a matching @end-procedure.
    // The transform is stateless (no open <div> to close) but every ordered
    // list after the marker was being silently hijacked into step-list mode.
    if (inProcedure) {
      if (!state.env.layoutWarnings) state.env.layoutWarnings = [];
      state.env.layoutWarnings.push({
        type: 'unclosed_procedure',
        message: '@procedure was opened but never closed with @end-procedure. ' +
                 'Ordered lists after the marker may have been transformed into ' +
                 'step-lists unintentionally.',
      });
      inProcedure = false;
    }

    closeSpecialty();

    state.tokens = newTokens;
  });

}

/**
 * Plugin metadata for print-md
 */
export const metadata = {
  name: 'dimm-city-plugin',
  version: '17.3.0',
  description: 'Dimm City TTRPG skill cards - supports H3/H4, bullet lists, numbered abilities',
  author: 'Dimm City',
  keywords: ['ttrpg', 'rpg', 'skills', 'dimm-city'],
};
