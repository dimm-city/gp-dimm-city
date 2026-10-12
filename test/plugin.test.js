// plugin.test.js — what the plugin emits: the loader contract and the
// behavioural edge cases that earned a regression test (table pass-through,
// ROLL THE DIE! boundaries, alert ordering, inline formatting,
// outcome tables, @continue before core's layout transform, @card
// footers). The whole-document regression check is design-guide.test.js,
// which snapshots every chapter of the design guide.
//
// `gutterpress/render` is a devDependency used here to run the plugin inside
// core's own markdown pipeline (core markers such as @section/@page/@chapter
// are not this plugin's to render). It is never imported at runtime — see
// conventions.test.js.
import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";

import MarkdownIt from "markdown-it";
import { createMarkdownRenderer } from "gutterpress/render";

import dimmCityPlugin, { markers, metadata } from "../plugin.js";

const ROLL_HTML = '<span class="dc-roll-the-die">ROLL THE DIE!</span>';

function createMarkdown() {
  return new MarkdownIt({ html: true }).use(dimmCityPlugin);
}

function createGutterpressMarkdown() {
  return createMarkdownRenderer([{ name: "gp-dimm-city", plugin: dimmCityPlugin, options: {}, markers }]);
}

/** Core stamps source ranges and link tokens on blocks; they say nothing about the structure under test. */
const stripSource = (html) => html.replace(/ data-(source-range|source-line|gp-source-token|gp-source-occurrence)="[^"]*"/g, "");

/** Render through Gutterpress (declared markers need it), with source stamps removed. */
function renderGp(src) {
  const env = {};
  const html = stripSource(createGutterpressMarkdown().render(src, env));
  return { html, warnings: env.layoutWarnings ?? [] };
}

/** A two-column pipe table of the five standard bands, with the given header and result texts. */
const bandTable = (head = ["Roll", "Outcome"], bands = ["20", "11-19", "6-10", "2-5", "1"], texts = ["A", "B", "C", "D", "E"]) => [
  `| ${head[0]} | ${head[1]} |`,
  "| --- | --- |",
  ...bands.map((b, i) => `| ${b} | ${texts[i] ?? "text"} |`),
];

function countRolls(html) {
  return html.split('class="dc-roll-the-die"').length - 1;
}

describe("loader contract", () => {
  test("the default export is a plain (md, options) function", () => {
    expect(typeof dimmCityPlugin).toBe("function");
    expect(dimmCityPlugin.length).toBeLessThanOrEqual(2);
  });

  test("metadata names the package and carries no private version", () => {
    expect(typeof metadata.name).toBe("string");
    expect(metadata.name.length).toBeGreaterThan(0);
    expect("version" in metadata).toBe(false);
  });
});

describe("behaviour carried from the book repo", () => {
  test("preserves unclassified skill tables as native markdown-it tables", () => {
    const table = ["| Name | Detail |", "| :--- | ---: |", "| **Alpha** | [Linked](https://example.test) |"].join("\n");
    const source = ["@skill", "", "#### Test Skill | T0", "", table, "", "@end-skill"].join("\n");
    const expectedTable = new MarkdownIt({ html: true }).render(table);
    const { html } = renderGp(source);

    expect(html).toContain(expectedTable);
    expect(html).toMatch(/<thead>[\s\S]*<th style="text-align:left">Name<\/th>/);
    expect(html).toMatch(/<tbody>[\s\S]*<strong>Alpha<\/strong>/);
    expect(html).not.toMatch(/dc-outcomes/);
  });

  test("renders a Distance table inside a skill as a plain table", () => {
    const source = ["@skill", "", "#### Close In", "", "| Distance | AP |", "| --- | --- |", "| **Near** | *1 AP* |", "", "@end-skill"].join("\n");
    const { html } = renderGp(source);

    expect(html).toMatch(/<table>[\s\S]*<strong>Near<\/strong>/);
    expect(html).not.toMatch(/dc-distance-tags|dc-dist-/);
  });

  test("transforms only complete roll instructions in markdown text tokens", () => {
    const source = [
      "ROLL THE DIE! and **ROLL THE DIE!** and *ROLL THE DIE!* and [ROLL THE DIE!](#roll).",
      "",
      "REROLL THE DIE! ROLL THE DIE!S PREROLL THE DIE!",
      "",
      "`ROLL THE DIE!` and <code>ROLL THE DIE!</code>.",
      "",
      '<span data-copy="ROLL THE DIE!">ROLL THE DIE!</span> then ROLL THE DIE!',
      "",
      "<br> ROLL THE DIE!",
      "",
      '<span class="dc-roll-the-die">ROLL THE DIE!</span>',
      "",
      "<div>",
      "ROLL THE DIE!",
      "</div>",
      "",
      "```text",
      "ROLL THE DIE!",
      "```",
    ].join("\n");
    const md = createMarkdown();
    const html = md.render(source);

    expect(countRolls(html)).toBe(7);
    expect(html).toContain(`<strong>${ROLL_HTML}</strong>`);
    expect(html).toContain(`<em>${ROLL_HTML}</em>`);
    expect(html).toContain(`<a href="#roll">${ROLL_HTML}</a>`);
    expect(html).toContain("REROLL THE DIE! ROLL THE DIE!S PREROLL THE DIE!");
    expect(html).toContain("<code>ROLL THE DIE!</code>");
    expect(html).toContain('<span data-copy="ROLL THE DIE!">ROLL THE DIE!</span>');
    expect(html).toContain('<pre><code class="language-text">ROLL THE DIE!\n</code></pre>');

    const renderedOnce = md.renderInline("ROLL THE DIE!");
    expect(md.renderInline(renderedOnce)).toBe(renderedOnce);
  });

  test.each(["ROLL THE DIE!", "ROLL A DIE!", "ROLLS A DIE!", "ROLLING THE DIE!"])("wraps the wording %s exactly as written", (wording) => {
    const html = createMarkdown().render(`When it says ${wording} read the ladder.`);

    expect(html).toContain(`<span class="dc-roll-the-die">${wording}</span> read the ladder.`);
    expect(countRolls(html)).toBe(1);
  });

  test("leaves lowercase, other tenses and mid-word wordings alone", () => {
    const source = [
      "roll the die! Roll A Die! roll a die!",
      "",
      "ROLLED THE DIE! ROLLED A DIE! ROLLINGS A DIE! ROLL AN DIE! ROLL THE DICE! ROLL A DIE",
      "",
      "REROLL A DIE! ROLL A DIE!S PREROLLS A DIE! ROLLING THE DIE!X _ROLL A DIE!",
    ].join("\n");
    const html = createMarkdown().render(source);

    expect(countRolls(html)).toBe(0);
    expect(html).toContain("roll the die! Roll A Die! roll a die!");
    expect(html).toContain("ROLLED THE DIE! ROLLED A DIE!");
  });

  test("wraps each wording inside bold and several in one paragraph", () => {
    const source = "**ROLL A DIE!** to hit, ROLLS A DIE! for damage, ROLLING THE DIE! twice, then ROLL THE DIE! and `ROLL A DIE!` stays code.";
    const html = createMarkdown().render(source);
    const span = (text) => `<span class="dc-roll-the-die">${text}</span>`;

    expect(countRolls(html)).toBe(4);
    expect(html).toContain(`<strong>${span("ROLL A DIE!")}</strong> to hit, ${span("ROLLS A DIE!")} for damage, ${span("ROLLING THE DIE!")} twice, then ${span("ROLL THE DIE!")} and`);
    expect(html).toContain("<code>ROLL A DIE!</code>");
  });

  test("leaves headings as plain text", () => {
    const html = createMarkdown().render(["## ROLLING THE DIE!", "", "Setext ROLL A DIE!", "---", "", "### Before ROLL A DIE! after", "", "Body ROLL A DIE! text."].join("\n"));

    expect(countRolls(html)).toBe(1);
    expect(html).toMatch(/<h2>ROLLING THE DIE!<\/h2>/);
    expect(html).toMatch(/<h3>Before ROLL A DIE! after<\/h3>/);
    expect(html).toContain(`Body ${ROLL_HTML.replace("ROLL THE DIE!", "ROLL A DIE!")} text.`);
  });

  test("runs after alert parsing and handles ordinary blockquotes", () => {
    const source = ["> [!NOTE]", "> **ROLL THE DIE!** and `ROLL THE DIE!`.", "", "> *Ordinary* ROLL THE DIE!"].join("\n");
    const html = createMarkdown().render(source);

    expect(countRolls(html)).toBe(2);
    expect(html).toMatch(
      /<div class="dc-alert dc-note"><span class="dc-alert-label">Note<\/span>[\s\S]*<strong><span class="dc-roll-the-die">ROLL THE DIE!<\/span><\/strong> and <code>ROLL THE DIE!<\/code>/,
    );
    expect(html).toMatch(/<blockquote>[\s\S]*<em>Ordinary<\/em> <span class="dc-roll-the-die">ROLL THE DIE!<\/span>[\s\S]*<\/blockquote>/);
  });

  test("preserves inline formatting in transformed learning-path and skill content", () => {
    const learningPath = ["@learning-path", "", "### Ghost Route", "", "> *Formatted route* says ROLL THE DIE!", "", "@end-learning-path"].join("\n");
    const skill = [
      "@skill",
      "",
      "#### Signal Cut | T1",
      "",
      "> **Formatted flavor** says ROLL THE DIE!",
      "",
      "1. **0 AP** *Move:* Keep *ability formatting* and ROLL THE DIE!",
      "",
      "@end-skill",
    ].join("\n");

    const learningPathHtml = renderGp(learningPath).html;
    const skillHtml = renderGp(skill).html;

    expect(learningPathHtml).toContain(`<div class="dc-intro"><em>Formatted route</em> says ${ROLL_HTML}</div>`);
    expect(skillHtml).toContain(`<p class="dc-flavor"><strong>Formatted flavor</strong> says ${ROLL_HTML}</p>`);
    expect(skillHtml).toContain(`<p class="dc-ability-text"><em>Move:</em> Keep <em>ability formatting</em> and ${ROLL_HTML}</p>`);
  });

  test("retains custom outcome rendering with safe inline rolls", () => {
    const outcomeTable = [
      "@skill",
      "",
      "#### Risk It",
      "",
      ...bandTable(["Roll", "Outcome"], undefined, ["**ROLL THE DIE!** but not `ROLL THE DIE!`"]),
      "",
      "@end-skill",
    ].join("\n");
    const outcomeMacro = ["@outcome", "20 | Triumph | **ROLL THE DIE!** but not `ROLL THE DIE!`.", "@end-outcome"].join("\n");

    const outcomeHtml = renderGp(outcomeTable).html;
    const macroHtml = renderGp(outcomeMacro).html;

    expect(outcomeHtml).toMatch(/<div class="dc-outcomes" data-break-inside="avoid">/);
    expect(outcomeHtml).toContain(`<strong>${ROLL_HTML}</strong> but not <code>ROLL THE DIE!</code>`);
    expect(outcomeHtml).not.toMatch(/<table>/);
    expect(countRolls(macroHtml)).toBe(1);
    expect(macroHtml).toContain(`<strong>${ROLL_HTML}</strong> but not <code>ROLL THE DIE!</code>`);
  });

  test("claims skill continuations before the Gutterpress layout transform", () => {
    const skill = [
      "@skill",
      "",
      "#### Long Skill | T2",
      "",
      "1. **0 AP** *First:* Opening text.",
      "",
      "@continue",
      "",
      "2. **1 AP** *Second:* Continued text.",
      "",
      "@end-skill",
    ].join("\n");
    const section = ["@section .panel", "", "First section fragment.", "", "@continue", "", "Second section fragment.", "", "@end-section"].join("\n");
    const md = createGutterpressMarkdown();
    const skillEnv = {};
    const sectionEnv = {};
    const skillHtml = md.render(skill, skillEnv);
    const sectionHtml = md.render(section, sectionEnv);

    expect((skillHtml.match(/class="dc-skill-card/g) ?? []).length).toBe(2);
    expect(skillHtml).toMatch(/class="dc-skill-card dc-skill-card-cont"/);
    expect(skillHtml).toContain('<span class="dc-tab-title">Long Skill ▸</span>');
    expect(JSON.stringify(skillEnv.layoutWarnings ?? [])).not.toMatch(/continue_without_section/);

    expect(sectionHtml).toMatch(/class="section panel gp-continued"/);
    expect(JSON.stringify(sectionEnv.layoutWarnings ?? [])).not.toMatch(/continue_without_section/);
  });

  test("tags only the last @card body blockquote as dc-card-footer (dc#44)", () => {
    const singleFooter = ["@card .dc-flaws", "", "#### Title", "", "> Pull quote", "", "Body paragraph.", "", "> Footer blockquote", "", "@end-card"].join("\n");
    const twoBodyBlockquotes = ["@card", "", "#### Title", "", "> Pull quote", "", "> Not the footer", "", "> The real footer", "", "@end-card"].join("\n");

    const singleHtml = renderGp(singleFooter).html;
    const twoHtml = renderGp(twoBodyBlockquotes).html;

    // The pull quote (first blockquote, before the body opens) renders as a
    // plain .dc-card-pull div, so it is never a footer candidate.
    expect(singleHtml).toMatch(/<div class="dc-card-pull">Pull quote<\/div>/);
    expect((singleHtml.match(/dc-card-footer/g) ?? []).length).toBe(1);
    expect(singleHtml).toMatch(/<blockquote class="dc-card-footer">\s*<p>Footer blockquote<\/p>/);

    // Of the two body blockquotes only the last carries the tag.
    expect(twoHtml).toMatch(/<blockquote>\s*<p>Not the footer<\/p>\s*<\/blockquote>/);
    expect(twoHtml).toMatch(/<blockquote class="dc-card-footer">\s*<p>The real footer<\/p>/);
    expect((twoHtml.match(/dc-card-footer/g) ?? []).length).toBe(1);
  });
});

// Declared wrappers are a Gutterpress core feature: core reads the plugin's
// `markers` table, so a bare markdown-it instance never sees them.
describe("declared wrapper markers", () => {
  const render = (src) => {
    const env = {};
    const html = createGutterpressMarkdown().render(src, env);
    return { html: html.replace(/ data-source-(range|line)="[^"]*"/g, ""), warnings: env.layoutWarnings ?? [] };
  };
  const wrap = (open, close, body = "x") => [open, "", body, "", close].join("\n");

  test("each wrapper emits its element and classes", () => {
    const expected = {
      sidebar: "dc-sidebar",
      "sidebar-box": "dc-prose-panel dc-sidebar-box",
      definition: "dc-prose-panel dc-definition-block",
      "specialty-intro": "dc-specialty-intro",
      "specialty-art": "dc-specialty-art",
      gear: "dc-card dc-gear",
      toc: "dc-toc",
      lede: "dc-intro",
      glossary: "dc-terms",
      block: "dc-block",
    };
    const rewritten = ["specialty", "learning-path", "skill", "card", "outcome", "procedure", "callout", "dm-note", "roll-table"]; // declared too, but their content is rewritten: see the next describe blocks
    expect(Object.keys(markers).filter((k) => k !== "specialty-card" && !rewritten.includes(k) && !markers[k].section && !["section", "page", "chapter"].includes(k)).sort()).toEqual(Object.keys(expected).sort());
    for (const [name, cls] of Object.entries(expected)) {
      const { html, warnings } = render(wrap(`@${name}`, `@end-${name}`));
      expect(html, name).toContain(`<div class="${cls}">`);
      expect(warnings, name).toEqual([]);
    }
  });

  test("@block takes a variant word or a class, plus a title from label", () => {
    for (const [open, cls] of [
      ['@block panel label="A & B"', "dc-block dc-panel"],
      ['@block .dc-panel label="A & B"', "dc-block dc-panel"],
      ['@block slate label="A & B"', "dc-block dc-slate"],
      ['@block .dc-shard label="A & B"', "dc-block dc-shard"],
      ['@block codex label="A & B"', "dc-block dc-codex"],
    ]) {
      const { html } = render(wrap(open, "@end-block"));
      expect(html, open).toContain(`<div class="${cls}"`);
      expect(html, open).toContain('<div class="dc-block-title">A &amp; B</div>');
    }
    expect(render(wrap("@block .dc-codex", "@end-block")).html).not.toContain("dc-block-title");
  });

  test("section markers are core sections: same HTML as their @section <word> alias", () => {
    // marker -> [the word that aliases it, the classes both write]
    const expected = {
      "card-grid": ["cards", "dc-card-grid"],
      "citizen-walkthrough": ["walkthrough", "dc-section-panel dc-citizen-walkthrough"],
      "fiction-excerpt": ["fiction", "dc-fiction-excerpt"],
      "npc-stat": ["npc", "dc-section-panel dc-npc-stat"],
      flaws: ["flaws", "dc-section-panel dc-flaws"],
      ideals: ["ideals", "dc-section-panel dc-ideals"],
      dreams: ["dreams", "dc-section-panel dc-dreams"],
    };
    expect(Object.keys(markers).filter((k) => markers[k].section).sort()).toEqual(Object.keys(expected).sort());
    for (const [name, [word, cls]] of Object.entries(expected)) {
      const declared = render(wrap(`@${name} .gp-columns-2`, `@end-${name}`, "## T"));
      const aliased = render(wrap(`@section ${word} .gp-columns-2`, "@end-section", "## T"));
      expect(declared.html, name).toContain(`<div class="section ${cls} gp-columns-2"`);
      // The alias also writes data-section="<word>"; everything else is the same element.
      expect(aliased.html.replace(` data-section="${word}"`, ""), name).toBe(declared.html);
      expect(declared.warnings, name).toEqual([]);
      expect(aliased.warnings, name).toEqual([]);
    }
  });

  test("@section takes the general variant words panel, flat and aside, and a class beside them", () => {
    for (const [word, cls] of [["panel", "dc-section-panel"], ["flat", "dc-section-flat"], ["aside", "dc-section-aside"]]) {
      const { html, warnings } = render(wrap(`@section ${word} .dc-avoid-split`, "@end-section"));
      expect(html, word).toContain(`<div class="section ${cls} dc-avoid-split"`);
      expect(warnings, word).toEqual([]);
    }
    // A bare @section stays core's plain box.
    expect(render(wrap("@section", "@end-section")).html).toContain('<div class="section">');
  });

  test("@page and @chapter take the location words, and a class or the raw spelling beside them", () => {
    const pages = { "chapter-start": "dc-page-chapter-start", intro: "dc-page-intro", credits: "dc-page-credits", contents: "dc-page-contents", "citizen-file": "dc-page-citizen-file" };
    for (const [word, cls] of Object.entries(pages)) {
      const { html, warnings } = render(`@page ${word} .dg-x\n\nx`);
      expect(html, word).toContain(`<div class="page ${cls} dg-x" data-page="${word}"`);
      expect(warnings, word).toEqual([]);
    }
    const chapters = { rules: "dc-chapter-rules", lore: "dc-chapter-lore", "citizen-file": "dc-chapter-citizen-file", specialty: "dc-chapter-specialty" };
    for (const [word, cls] of Object.entries(chapters)) {
      const { html, warnings } = render(`@chapter ${word} #ch-x ch="2"\n\n@page\n\nx`);
      expect(html, word).toContain(`<div class="chapter ${cls}"`);
      expect(html, word).not.toContain("data-chapter-label");
      expect(html, word).toContain("chapter-2");
      expect(warnings, word).toEqual([]);
    }
    // The raw spelling the books still write renders as before: classes only, no variant.
    const raw = render("@page .page-chapter-start .dc-chapter-start\n\nx").html;
    expect(raw).toContain('<div class="page page-chapter-start dc-chapter-start"');
    expect(raw).not.toContain("dc-page-");
    // Any other word after @chapter is still its label.
    expect(render("@chapter C.01 ch=\"1\"\n\n@page\n\nx").html).toContain('data-chapter-label="C.01"');
  });

  test("a section marker closes at the next @section like any section, and @continue keeps its class", () => {
    const { html, warnings } = render(["@npc-stat", "", "x", "", "@section", "", "y", "", "@end-section"].join("\n"));
    expect(html).toMatch(/<div class="section dc-section-panel dc-npc-stat"><p>x<\/p>\s*<\/div><div class="section"/);
    expect(warnings).toEqual([]);
  });

  test("a wrapper left open closes at the next @section and at end of document without a warning", () => {
    const { html, warnings } = render(["@lede", "", "x", "", "@section", "", "y", "", "@end-section"].join("\n"));
    expect(html).toMatch(/<div class="dc-intro"><p>x<\/p>\s*<\/div><div class="section"/);
    expect(render("@toc\n\nz\n").warnings).toEqual([]);
    expect(warnings).toEqual([]);
  });

  test("@specialty-card numbers its cards odd/even across the document", () => {
    const card = (t) => wrap("@specialty-card", "@end-specialty-card", t);
    const { html } = render([card("a"), card("b"), card("c")].join("\n\n"));
    expect([...html.matchAll(/data-position="(\w+)"/g)].map((m) => m[1])).toEqual(["odd", "even", "odd"]);
  });

  test("hand-written markers next to declared ones raise no unknown_marker warnings", () => {
    const src = ["@specialty .augmerc", "", "@lede", "", "x", "", "@end-lede", "", "@learning-path", "", "### T", "", "@end-learning-path", "", "@end-specialty"].join("\n");
    expect(render(src).warnings).toEqual([]);
  });

  test("a bare markdown-it instance ignores the table (declared markers are a Gutterpress feature)", () => {
    expect(createMarkdown().render(wrap("@lede", "@end-lede"))).toContain("@lede");
  });
});

// @specialty, @learning-path and @skill are declared markers whose content the
// plugin rewrites ("declare, then transform"): core opens, nests and closes
// them, and the plugin's core rules rebuild what sits between each pair.
describe("declared specialty, learning path and skill", () => {
  const doc = (...lines) => lines.join("\n");
  const count = (html, re) => (html.match(re) ?? []).length;
  const card = (name, ...more) => doc(`#### ${name}`, "", "> Flavor.", "", "1. **1 AP** *Move:* Do it.", ...more);
  const warningTypes = (warnings) => warnings.map((w) => w.type);

  describe("@specialty", () => {
    test("the variant word and both class spellings give the same wrapper", () => {
      for (const open of ["@specialty augmerc", "@specialty .augmerc", "@specialty {.augmerc}"]) {
        const { html, warnings } = renderGp(doc(open, "", "x", "", "@end-specialty"));
        expect(html, open).toContain('<div class="dc-specialty augmerc"');
        expect(warnings, open).toEqual([]);
      }
    });

    test("every variant is a specialty the stylesheets style", () => {
      const css = readFileSync(new URL("../styles/components/specialty-identity.css", import.meta.url), "utf8");
      const variants = Object.keys(markers.specialty.variants);
      expect(variants.length).toBe(10);
      for (const name of variants) {
        expect(markers.specialty.variants[name], name).toBe(name);
        expect(css, name).toContain(`.dc-specialty.${name}`);
      }
    });

    test("author classes and attributes ride along", () => {
      const { html } = renderGp(doc("@specialty .augmerc .my-class #spec-aug", "", "x"));
      expect(html).toMatch(/<div class="dc-specialty augmerc my-class" id="spec-aug"/);
    });

    test("a new @specialty, @end-specialty and @page each close it with everything inside", () => {
      const inner = doc("@learning-path", "", "### P", "", "@skill", "", card("S"));
      for (const closer of ["@specialty proxy\n\ny", "@end-specialty", "@page"]) {
        const { html, warnings } = renderGp(doc("@specialty augmerc", "", inner, "", closer));
        const balanced = count(html, /<div[\s>]/g) === count(html, /<\/div>/g);
        expect(balanced, closer).toBe(true);
        // the skill card sits inside the augmerc wrapper, which ends before whatever closed it
        expect(html, closer).toMatch(/<div class="dc-specialty augmerc"[\s\S]*dc-skill-card[\s\S]*<\/div>\s*(<div class="(dc-specialty proxy|page)"|$)/);
        expect(warnings, closer).toEqual([]);
      }
    });

    test("cards, wrappers and callouts keep working inside a specialty", () => {
      const src = doc(
        "@specialty .augmerc", "",
        "@specialty-intro", "", "## Augmerc", "", "@end-specialty-intro", "",
        "@card", "", "#### Title", "", "> Pull", "", "Body.", "", "@end-card", "",
        "@callout note", "", "Careful.", "", "@end-callout", "",
        "@end-specialty",
      );
      const { html, warnings } = renderGp(src);
      expect(html).toMatch(/<div class="dc-specialty augmerc"[\s\S]*dc-specialty-intro[\s\S]*<div class="dc-card-heading">Title<\/div>[\s\S]*dc-alert dc-note[\s\S]*<\/div>\s*$/);
      expect(warnings).toEqual([]);
    });
  });

  describe("@learning-path", () => {
    const path = (title, ...rest) => doc("@learning-path", "", `### ${title}`, "", "> Subtitle *here*.", "", "- Alpha", "- Beta", "", ...rest);

    test("the header is rewritten into the shell: title, subtitle, sticker chain", () => {
      const { html } = renderGp(doc("@specialty .proxy", "", path("Refuse Finality", "@skill", "", card("Alpha"), "", "@end-skill", "", "@end-learning-path")));
      expect(html).toContain('<div class="dc-learning-path dc-path-block" data-path-ref="PRX1">');
      expect(html).toContain('<div class="dc-path-shell">');
      expect(html).toContain('<h3 class="dc-spray"><span class="dc-path-sticker">PRX1</span><span class="dc-path-sep"> </span>Refuse Finality</h3>');
      expect(html).toContain('<div class="dc-intro">Subtitle <em>here</em>.</div>');
      expect(html).toContain('<div class="dc-stickers"><span class="dc-sticker"><span class="dc-sticker-ref">1</span>Alpha</span><span class="dc-arrow">»</span>');
      // the shell closes right before the first skill, which sits in the path
      expect(html).toMatch(/<\/span><\/div>\n<\/div>\n<div class="dc-skill-card"/);
    });

    test("data-path-ref comes from the enclosing specialty: variant or class, counted per specialty", () => {
      const refs = (html) => [...html.matchAll(/data-path-ref="([^"]*)"/g)].map((m) => m[1]);
      const specialty = (open, n) => doc(open, "", ...Array.from({ length: n }, (_, i) => doc("@learning-path", "", `### P${i}`, "")), "@end-specialty", "");
      const src = doc(
        specialty("@specialty augmerc", 2),
        specialty("@specialty .augmerc", 1),
        specialty("@specialty {.wirephreak}", 1),
        specialty("@specialty .proxy", 2),
        specialty("@specialty .dualist", 1), // no code for it: PATH
      );
      expect(refs(renderGp(src).html)).toEqual(["AUG1", "AUG2", "AUG1", "WPH1", "PRX1", "PRX2", "PATH1"]);
    });

    test("a path outside any specialty is numbered on its own", () => {
      expect([...renderGp(doc("@learning-path", "", "### A", "", "@learning-path", "", "### B")).html.matchAll(/data-path-ref="([^"]*)"/g)].map((m) => m[1])).toEqual(["1", "2"]);
    });

    test("author classes and attributes land on the path wrapper", () => {
      const { html } = renderGp(doc("@learning-path {.custom-path} data-foo=bar", "", "### T"));
      expect(html).toMatch(/<div class="dc-learning-path dc-path-block custom-path" data-foo="bar" data-path-ref="1">/);
    });

    test("an @end-skill leaves the path open; @end-learning-path closes the skills inside it", () => {
      const src = doc(
        "@specialty .proxy", "", path("P", "@skill", "", card("One"), "", "@end-skill", "", "![plate](plate.png)", "", "@end-learning-path"),
        "![after](after.png)",
      );
      const { html, warnings } = renderGp(src);
      expect(html.indexOf("plate.png")).toBeLessThan(html.indexOf("after.png"));
      // the plate is inside the path (before its closing div); the later image is not
      expect(html).toMatch(/plate\.png[\s\S]*<\/p>\s*<\/div>\s*<p class="dc-img-wrapper"><img[^>]*after\.png/);
      expect(warnings).toEqual([]);
    });

    test("a second @learning-path closes the first (and its skills)", () => {
      const { html, warnings } = renderGp(doc("@specialty .proxy", "", path("One", "@skill", "", card("A")), path("Two"), "@end-specialty"));
      expect(count(html, /<div class="dc-learning-path/g)).toBe(2);
      expect(html).toMatch(/dc-skill-card[\s\S]*<\/div>\s*<div class="dc-learning-path dc-path-block" data-path-ref="PRX2">/);
      expect(warnings).toEqual([]);
    });
  });

  describe("@skill", () => {
    test("each #### heading is its own card, with the author's classes and attributes on all of them", () => {
      const src = doc("@skill {.dc-highlight .my-class} id=sk variant=2", "", card("First | T1"), "", card("Second | T2 | highlight"));
      const { html } = renderGp(src);
      expect(count(html, /class="dc-skill-card dc-highlight my-class"/g)).toBe(2);
      expect(html).toContain('id="sk" data-variant="2" name="first"');
      expect(html).toContain('name="second"');
      expect(html).toContain('<div class="dc-card-tab dc-highlight">');
      expect(html).toContain('<h4 class="dc-tab-title">Second</h4>');
      expect(html).toContain('<span class="dc-tab-tier">T2</span>');
    });

    test("a card splits across pages by default and is named after its title", () => {
      const { html } = renderGp(doc("@skill", "", card("Hold the Line")));
      expect(html).toContain('<div class="dc-skill-card" name="hold-the-line">');
      expect(html).not.toContain("data-break-inside");
    });

    test(".dc-avoid-split keeps every card of the skill whole", () => {
      const { html } = renderGp(doc("@skill .dc-avoid-split", "", card("First | T1"), "", card("Second | T2")));
      expect(count(html, /<div class="dc-skill-card dc-avoid-split" name="(first|second)" data-break-inside="avoid">/g)).toBe(2);
    });

    test("tiers in a path run PATHREF.N across its skills unless the heading names one", () => {
      const src = doc("@specialty .augmerc", "", "@learning-path", "", "### P", "", "@skill", "", card("A"), "", "@skill", "", card("B | AUG9.9"), "", card("C"), "", "@end-learning-path");
      const tiers = [...renderGp(src).html.matchAll(/<span class="dc-tab-tier">([^<]*)<\/span>/g)].map((m) => m[1]);
      expect(tiers).toEqual(["AUG1.1", "AUG9.9", "AUG1.3"]);
      // outside a path there is nothing to compute
      expect(renderGp(doc("@skill", "", card("A"))).html).toContain('<span class="dc-tab-tier"></span>');
    });

    test("the card body: flavor, abilities, sub-headers, outcome tables", () => {
      const src = doc(
        "@skill", "", card("Gamble"), "",
        "2. **2-X AP** *Push:* More.", "",
        "##### Outcomes", "",
        ...bandTable(["Roll", "Outcome"], undefined, ["Crit", "", "", "", "Boom"]), "",
        "##### A real sub-header", "",
        "- one", "- two",
      );
      const { html } = renderGp(src);
      expect(html).toContain('<p class="dc-flavor">Flavor.</p>');
      expect(html).toContain('<div class="dc-ability" data-ability-penultimate="true">');
      expect(html).toContain('<div class="dc-ability" data-ability-last="true">');
      expect(html).toContain('<span class="dc-ap variable">2-X AP</span>');
      expect(html).toContain('<div class="dc-outcomes" data-break-inside="avoid">');
      expect(html).toContain('<div class="dc-outcomes-label">Outcomes</div>');
      expect(count(html, />Outcomes</g)).toBe(1); // the "##### Outcomes" sub-header is swallowed: the table carries its own label
      expect(html).not.toContain("<h5");
      expect(html).toContain('<div class="dc-sub-header">A real sub-header</div>');
    });

    test("content before the first #### stays outside the card", () => {
      const { html } = renderGp(doc("@skill", "", "---", "", card("Join")));
      expect(html).toMatch(/<hr[^>]*>\s*<div class="dc-skill-card"/);
    });

    test("a page break or another component ends the card; later content is outside it", () => {
      const { html } = renderGp(doc("@skill", "", card("A"), "", "@page-break", "", "after the break"));
      expect(html).toMatch(/<\/div><\/div><\/div>\s*<div[^>]*gp-page-break[^>]*><\/div>\s*<p>after the break<\/p>/);
    });

    test("@columns, @column-break and @end-columns inside a card stay in its body, in place", () => {
      const src = doc(
        "@skill", "", card("Split"), "",
        "@columns 2", "", "- one", "- two", "", "@column-break", "", "- three", "", "@end-columns", "",
        "Closing line.", "", card("Next"),
      );
      const { html, warnings } = renderGp(src);
      expect(warnings).toEqual([]);
      expect(count(html, /class="dc-skill-card"/g)).toBe(2);
      // the run sits inside the first card's .dc-card-inner, before the card closes
      expect(html).toMatch(
        /<div class="dc-card-inner">[\s\S]*<div class="gp-columns gp-columns-2"[^>]*>[\s\S]*<li>two<\/li>[\s\S]*<div class="gp-column-break"[^>]*><\/div>[\s\S]*<li>three<\/li>[\s\S]*<\/div>\s*<p>Closing line\.<\/p>\s*<\/div><\/div><\/div>/,
      );
      // the first card holds the whole run and the closing line: nothing leaks out between the cards
      const firstCard = html.slice(html.indexOf('name="split"'), html.indexOf('name="next"'));
      expect(firstCard).toContain("<li>three</li>");
      expect(firstCard).toContain("Closing line.");
    });

    test("a card after a columns run still starts as a card, and a stray @column-break still ends one", () => {
      const { html } = renderGp(doc("@skill", "", card("A"), "", "@columns 2", "", "text", "", "@end-columns", "", card("B"), "", "@column-break", "", "after"));
      expect(count(html, /class="dc-skill-card"/g)).toBe(2);
      expect(html).toMatch(/<\/div><\/div><\/div>\s*<div[^>]*gp-column-break[^>]*><\/div>\s*<p>after<\/p>/);
    });

    test("a columns run opened before the cards wraps them; the cards are not inside the card of an earlier one", () => {
      const { html } = renderGp(doc("@columns 2", "", "@skill", "", card("A"), "", card("B"), "", "@end-skill", "", "@end-columns"));
      expect(html).toMatch(/<div class="gp-columns gp-columns-2"[^>]*>\s*<div class="dc-skill-card"[\s\S]*name="b"[\s\S]*<\/div><\/div><\/div>\s*<\/div>/);
    });

    test("@card, @outcome and @procedure inside a skill are rewritten like anywhere else", () => {
      const src = doc(
        "@skill", "", card("Mixed"), "",
        "@procedure", "", "1. First step.", "2. Second step.", "", "@end-procedure", "",
        "@outcome", "20 | Crit | Yes.", "@end-outcome", "",
      );
      const { html } = renderGp(src);
      expect(html).toContain('<ol class="dc-steps">');
      expect(html).toContain('<div class="dc-outcomes">');
    });

    test("@end-skill closes only the skill; stray closers warn", () => {
      const { warnings } = renderGp(doc("@learning-path", "", "### P", "", "@skill", "", card("A"), "", "@end-skill", "", "@end-skill", "", "@end-learning-path", "", "@end-learning-path", "", "@end-specialty"));
      expect(warnings.map((w) => w.type)).toEqual(["declared_marker_close_without_open", "declared_marker_close_without_open", "declared_marker_close_without_open"]);
      expect(warnings.map((w) => w.message.match(/@end-[a-z-]+/)[0])).toEqual(["@end-skill", "@end-learning-path", "@end-specialty"]);
    });

    test("@end-skills is gone: it is not a marker", () => {
      expect(renderGp(doc("@skill", "", card("A"), "", "@end-skills")).html).toContain("@end-skills");
    });

    test("a skill, path or specialty left open closes at the end of the document without a warning", () => {
      expect(renderGp(doc("@specialty .proxy", "", "@learning-path", "", "### P", "", "@skill", "", card("A"))).warnings).toEqual([]);
    });
  });

  describe("@continue inside a skill", () => {
    const skill = (open, ...after) =>
      doc(open, "", "#### Long Skill | T2", "", "1. **0 AP** *First:* Opening text.", "", "@continue", "", "2. **1 AP** *Second:* Continued text.", "", ...after);

    test("opens a continuation card that keeps the skill's classes, in a specialty and path", () => {
      const src = doc("@specialty .augmerc", "", "@learning-path", "", "### P", "", skill("@skill", "@end-skill"), "@end-learning-path", "@end-specialty");
      const { html, warnings } = renderGp(src);
      expect(count(html, /class="dc-skill-card/g)).toBe(2);
      expect(html).toContain('<div class="dc-skill-card dc-skill-card-cont" name="long-skill">');
      expect(html).toContain('<div class="dc-card-tab dc-card-tab-cont">');
      expect(html).toContain('<span class="dc-tab-title">Long Skill ▸</span>');
      expect(html).toContain('<span class="dc-tab-tier">T2</span>');
      expect(html).not.toMatch(/gp-continued/);
      expect(warnings).toEqual([]);
    });

    test("a card kept whole with .dc-avoid-split keeps its avoid on the continuation too", () => {
      expect(renderGp(skill("@skill .dc-avoid-split", "@end-skill")).html).toMatch(/dc-skill-card-cont dc-avoid-split" name="long-skill" data-break-inside="avoid"/);
    });

    test("the continuation is claimed only inside a skill's card; elsewhere @continue is core's section continuation", () => {
      const afterSkill = doc("@section .panel", "", "first", "", "@skill", "", card("A"), "", "@end-skill", "", "@continue", "", "second", "", "@end-section");
      const beforeCard = doc("@section .panel", "", "@skill", "", "no heading yet", "", "@continue", "", "second", "", "@end-section");
      for (const src of [afterSkill, beforeCard]) {
        const { html, warnings } = renderGp(src);
        expect(html).toMatch(/class="section panel gp-continued"/);
        expect(html).not.toContain("dc-skill-card-cont");
        expect(warningTypes(warnings)).not.toContain("continue_without_section");
      }
    });

    test("a @continue after the next @learning-path or @specialty is not a skill continuation", () => {
      for (const closer of ["@end-learning-path", "@learning-path", "@end-specialty", "@specialty .proxy"]) {
        const { html } = renderGp(doc("@section", "", "@specialty .augmerc", "", skill("@skill").replace(/@continue[\s\S]*$/, ""), closer, "", "@continue", "", "z"));
        expect(html, closer).not.toContain("dc-skill-card-cont");
      }
    });
  });

  describe("validate (structure rules)", () => {
    const problems = (src) => renderGp(src).warnings.filter((w) => w.type === "component_invalid");

    test("a well-formed specialty > path > skill reports nothing", () => {
      const src = doc("@specialty .augmerc", "", "@specialty-intro", "", "## A", "", "@end-specialty-intro", "", "@learning-path", "", "### P", "", "@skill", "", card("A"), "", "@skill", "", card("B"), "", "@end-learning-path", "", "@learning-path", "", "### Q", "", "@skill", "", card("C"), "", "@end-specialty");
      expect(renderGp(src).warnings).toEqual([]);
    });

    test("a skill directly in a specialty is reported at the skill's line", () => {
      const src = doc("@specialty .augmerc", "", "@learning-path", "", "### P", "", "@end-learning-path", "", "@skill", "", card("Loose"), "", "@end-specialty");
      const found = problems(src);
      expect(found).toHaveLength(1);
      expect(found[0].line).toBe(9);
      expect(found[0].message).toBe(
        "@specialty: This skill (and any right after it) is outside a learning path. If an `@end-learning-path` above it closed the path early, remove that line; otherwise move the skills into a `@learning-path`.",
      );
    });

    test("an early @end-learning-path is one problem for the skills it strands, plus one for the path that then nests in a skill", () => {
      // The shape several Field Guide chapters had: a path closed before its skills.
      const lines = [
        "@specialty .proxy", "",
        "@learning-path", "", "### One", "", "@end-learning-path", "",
        "@skill", "", ...card("A").split("\n"), "", "@skill", "", ...card("B").split("\n"), "",
        "@learning-path", "", "### Two", "", "@skill", "", ...card("C").split("\n"), "", "@end-learning-path", "",
        "@end-specialty",
      ];
      const at = (marker, n) => lines.map((l, i) => (l === marker ? i + 1 : 0)).filter(Boolean)[n];
      const found = problems(lines.join("\n"));
      // every skill sits directly in the specialty (the @skill inside "Two" closes the skill that held Two),
      // reported once, at the first skill of the run ...
      const loose = found.filter((p) => p.message.startsWith("@specialty:"));
      expect(loose.map((p) => p.line)).toEqual([at("@skill", 0)]);
      // ... and "Two" itself starts inside skill B
      const nested = found.filter((p) => p.message.startsWith("@skill:"));
      expect(nested.map((p) => p.line)).toEqual([at("@learning-path", 1)]);
      expect(nested[0].message).toBe(
        "@skill: This @learning-path starts inside the skill above it, so it is nested in that skill's card. Close the skill with `@end-skill` before it.",
      );
      expect(found).toHaveLength(2);
    });

    test("a specialty that starts inside a skill is reported too", () => {
      const found = problems(doc("@skill", "", card("A"), "", "@specialty .proxy", "", "x"));
      expect(found).toHaveLength(1);
      expect(found[0].message).toMatch(/^@skill: This @specialty starts inside the skill above it/);
    });

    test("skills outside any specialty are fine (a book may set skills without one)", () => {
      expect(renderGp(doc("@skill", "", card("A"), "", "@skill", "", card("B"))).warnings).toEqual([]);
    });

    test("the rule belongs to the plugin: a bare declaration with no validate says nothing", () => {
      expect(typeof markers.specialty.validate).toBe("function");
      expect(typeof markers.skill.validate).toBe("function");
      expect(markers["learning-path"].validate).toBeUndefined();
    });
  });

  test("a bare markdown-it instance leaves the three markers as text (declared markers are a Gutterpress feature)", () => {
    const html = createMarkdown().render(doc("@specialty .augmerc", "", "@skill", "", card("A")));
    expect(html).toContain("@specialty .augmerc");
    expect(html).not.toContain("dc-skill-card");
  });
});

// @card, @outcome and @procedure are declared the same way: core opens, nests
// and closes them, and ordinary core rules rewrite what sits inside.
describe("declared card, outcome and procedure", () => {
  const doc = (...lines) => lines.join("\n");
  const count = (html, re) => (html.match(re) ?? []).length;
  /** Markup only: core writes no newline after a component's tags. */
  const squash = (html) => html.replace(/>\s+</g, "><").trim();
  const types = (warnings) => warnings.map((w) => w.type);
  const problems = (src) => renderGp(src).warnings.filter((w) => w.type === "component_invalid");
  const skill = (...inside) => doc("@skill", "", "#### Skill | T1", "", "> Flavor.", "", "1. **1 AP** *Move:* Do it.", "", ...inside);

  describe("@card", () => {
    const body = ["#### Title", "", "> Pull *quote*", "", "Body.", "", "> Footer", ""];

    test("heading, pull quote, body and footer", () => {
      const { html, warnings } = renderGp(doc("@card", "", ...body, "@end-card"));
      expect(squash(html)).toBe(
        '<div class="dc-card"><div class="dc-card-heading">Title</div>' +
          '<div class="dc-card-pull">Pull <em>quote</em></div>' +
          '<div class="dc-card-body"><p>Body.</p><blockquote class="dc-card-footer"><p>Footer</p></blockquote></div></div>',
      );
      expect(warnings).toEqual([]);
    });

    test("the classes, id and attributes a card could always take", () => {
      for (const open of ["@card .dc-flaws .wide", "@card {.dc-flaws .wide}", "@card class=dc-flaws,wide"]) {
        expect(renderGp(doc(open, "", "x", "", "@end-card")).html, open).toContain('<div class="dc-card dc-flaws wide">');
      }
      expect(renderGp(doc("@card #pick data-tone=red", "", "x", "", "@end-card")).html).toContain('<div class="dc-card" id="pick" data-tone="red">');
    });

    test("a card with only a heading has no body; one with no #### heading is all body", () => {
      expect(squash(renderGp(doc("@card", "", "#### Only", "", "@end-card")).html)).toBe('<div class="dc-card"><div class="dc-card-heading">Only</div></div>');
      expect(squash(renderGp(doc("@card", "", "### Not an h4", "", "Text.", "", "@end-card")).html)).toBe('<div class="dc-card"><div class="dc-card-body"><h3>Not an h4</h3><p>Text.</p></div></div>');
    });

    test("an @end-card straight under a quote is a closer, not part of the quote", () => {
      const { html, warnings } = renderGp(doc("@card", "", "#### T", "", "> pull", "", "Body", "", "> footer", "@end-card", "", "after"));
      expect(html).toContain('<blockquote class="dc-card-footer">');
      expect(html).not.toContain("@end-card");
      expect(squash(html)).toMatch(/<\/blockquote><\/div><\/div><p>after<\/p>$/);
      expect(warnings).toEqual([]);
    });

    test("a new @card closes the one before it; one left open closes at the end of the document without a warning", () => {
      const { html, warnings } = renderGp(doc("@card", "", "#### One", "", "@card", "", "#### Two"));
      expect(squash(html)).toBe('<div class="dc-card"><div class="dc-card-heading">One</div></div><div class="dc-card"><div class="dc-card-heading">Two</div></div>');
      expect(warnings).toEqual([]);
    });

    test("a stray @end-card warns", () => {
      expect(types(renderGp("@end-card").warnings)).toEqual(["declared_marker_close_without_open"]);
    });

    test("a card after a skill's card stays inside it, and its own #### is not a new skill card", () => {
      const { html } = renderGp(skill("@card", "", ...body, "@end-card"));
      expect(count(html, /class="dc-skill-card/g)).toBe(1);
      expect(html).toMatch(/dc-card-inner">[\s\S]*<div class="dc-card"><div class="dc-card-heading">Title<\/div>[\s\S]*dc-card-body[\s\S]*(<\/div>\s*){4}$/);
      expect(count(html, /<div[\s>]/g)).toBe(count(html, /<\/div>/g));
    });
  });

  describe("@outcome", () => {
    const rows = ["20 | Triumph | Best **case**.", "11–19 | Success | You do it.", "6–10 | Hard Choice | It costs.", "2–5 | Failure | Nope.", "1 | Catastrophe | Worse."];

    test("one row per line, coloured by position, with the label bar", () => {
      const { html, warnings } = renderGp(doc("@outcome", "", ...rows, "", "@end-outcome"));
      expect(html).toContain('<div class="dc-outcomes">');
      expect(html).toContain('<div class="dc-outcomes-label">Outcomes</div>');
      expect([...html.matchAll(/class="dc-outcome-row (\w+)"/g)].map((m) => m[1])).toEqual(["crit", "hit", "mixed", "miss", "fail"]);
      expect([...html.matchAll(/dc-outcome-name">([^<]*)</g)].map((m) => m[1])).toEqual(["Triumph", "Success", "Hard Choice", "Failure", "Catastrophe"]);
      expect([...html.matchAll(/dc-outcome-roll">([^<]*)</g)].map((m) => m[1])).toEqual(["20", "11–19", "6–10", "2–5", "1"]);
      expect(html).toContain('<span class="dc-outcome-text">Best <strong>case</strong>.</span>');
      expect(warnings).toEqual([]);
    });

    test("a sixth row is a plain hit; rows in separate paragraphs and the compact form read the same", () => {
      const six = renderGp(doc("@outcome", "", ...rows, "0 | Extra | More.", "", "@end-outcome")).html;
      expect([...six.matchAll(/class="dc-outcome-row (\w+)"/g)].map((m) => m[1]).at(-1)).toBe("hit");
      const apart = renderGp(doc("@outcome", "", "20 | A | one", "", "1 | B | two", "", "@end-outcome"));
      const compact = renderGp(doc("@outcome", "20 | A | one", "", "1 | B | two", "@end-outcome"));
      expect(squash(compact.html)).toBe(squash(apart.html));
      expect(count(apart.html, /dc-outcome-row/g)).toBe(2);
      expect(compact.warnings).toEqual([]);
    });

    test("flush, and any class, ride on the wrapper", () => {
      for (const open of ["@outcome flush", "@outcome .flush-me .dc-flush", "@outcome {.dc-flush}"]) {
        expect(renderGp(doc(open, "", "20 | A | x", "", "@end-outcome")).html, open).toMatch(/<div class="dc-outcomes [^"]*dc-flush/);
      }
      expect(renderGp(doc("@outcome", "", "20 | A | x", "", "@end-outcome")).html).not.toContain("dc-flush");
    });

    test("an outcome table in a skill card and an @outcome in it sit side by side in the card", () => {
      const { html } = renderGp(skill(...bandTable(), "", "@outcome", "", "20 | Crit | Yes.", "", "@end-outcome"));
      expect(count(html, /class="dc-skill-card/g)).toBe(1);
      expect(count(html, /<div class="dc-outcomes"/g)).toBe(2);
      expect(html).toMatch(/<div class="dc-card-inner">[\s\S]*<div class="dc-outcomes" data-break-inside="avoid">[\s\S]*Crit<\/span>[\s\S]*<div class="dc-outcomes">[\s\S]*Yes\.[\s\S]*(<\/div>\s*){4}$/);
    });

    test("one left open at the end of the document warns, with core's own message", () => {
      const { warnings } = renderGp(doc("@outcome", "", "20 | A | x"));
      expect(types(warnings)).toEqual(["declared_marker_eof_close"]);
      expect(warnings[0].message).toMatch(/^An open @outcome reached end-of-document/);
    });

    test("a stray @end-outcome warns", () => {
      expect(types(renderGp("@end-outcome").warnings)).toEqual(["declared_marker_close_without_open"]);
    });

    describe("validate", () => {
      test("a well-formed ladder reports nothing", () => {
        expect(problems(doc("@outcome", "", ...rows, "", "@end-outcome"))).toEqual([]);
      });

      test("a line that is not roll | name | text is one problem, at its own line", () => {
        const found = problems(doc("@outcome", "", "20 | Crit | Yes.", "11 Hit You do it", "1 | Fumble", "", "@end-outcome"));
        expect(found.map((p) => p.line)).toEqual([4, 5]);
        expect(found[0].message).toBe('@outcome: "11 Hit You do it" is not a row. Write each one as `roll | name | text`, for example `20 | Crit | You flow.`');
      });

      test("anything but rows (a table, a list, a heading) is reported once and left out", () => {
        const found = problems(doc("@outcome", "", "20 | Crit | Yes.", "", "| Roll | Outcome |", "| --- | --- |", "| 1 | Boom |", "", "- stray", "", "@end-outcome"));
        expect(found.map((p) => p.message)).toEqual([
          "@outcome: Only lines written as `roll | name | text` are used here, so this table is left out.",
          "@outcome: Only lines written as `roll | name | text` are used here, so this list is left out.",
        ]);
        const html = renderGp(doc("@outcome", "", "20 | Crit | Yes.", "", "- stray", "", "@end-outcome")).html;
        expect(count(html, /dc-outcome-row/g)).toBe(1);
      });

      test("an outcome with nothing in it says so", () => {
        const found = problems(doc("@outcome", "", "@end-outcome"));
        expect(found).toHaveLength(1);
        expect(found[0].message).toBe("@outcome: This outcome has no rows. Add one `roll | name | text` line per result.");
      });
    });
  });

  describe("the outcome ladder, recognised by its band values", () => {
    const ladder = (...lines) => renderGp(lines.join("\n")).html;
    const isLadder = (html) => html.includes('<div class="dc-outcomes"');
    const tiers = (html) => [...html.matchAll(/class="dc-outcome-row (\w+)"/g)].map((m) => m[1]);
    const rolls = (html) => [...html.matchAll(/dc-outcome-roll">([^<]*)</g)].map((m) => m[1]);

    test("the five standard bands are the ladder whatever the headers say, in a skill card and outside one", () => {
      for (const head of [["Roll", "Outcome"], ["Roll", "Result"], ["Result", "Effect"], ["Roll Result", "Effect"], ["", ""], ["d20", "What happens"]]) {
        const out = ladder(...bandTable(head));
        expect(isLadder(out), head.join("|")).toBe(true);
        expect(tiers(out)).toEqual(["crit", "hit", "mixed", "miss", "fail"]);
        expect(out).not.toContain("<table>");
        const inSkill = ladder("@skill", "", "#### Risk It", "", ...bandTable(head), "", "@end-skill");
        expect(isLadder(inSkill), `skill ${head.join("|")}`).toBe(true);
      }
    });

    test("a band is read however it is typed, and shown the same way", () => {
      const out = ladder(...bandTable(["Roll", "Result"], ["**20**", "11 \u2013 19", "6\u201410", "2 - 5", "1"]));
      expect(rolls(out)).toEqual(["20", "11\u201319", "6\u201310", "2\u20135", "1"]);
      expect(tiers(out)).toEqual(["crit", "hit", "mixed", "miss", "fail"]);
    });

    test("the bands in ascending order are the ladder; each row keeps its own tier and text", () => {
      const out = ladder(...bandTable(["Result", "Effect"], ["1", "2-5", "6-10", "11-19", "20"], ["worst", "bad", "mixed", "good", "best"]));
      expect(tiers(out)).toEqual(["fail", "miss", "mixed", "hit", "crit"]);
      expect(out).toMatch(/dc-outcome-text">worst<[\s\S]*dc-outcome-text">best</);
    });

    test("any other set of bands is a plain table, even under a Roll | Outcome header", () => {
      const others = [
        ["20", "16-19", "11-15", "6-10", "2-5", "1"], // six bands
        ["20", "11-19", "2-10", "1"], // a split at 10
        ["1-5", "6-10", "11-19", "20"], // four
        ["20", "11-19", "6-10", "2-5", "2-5"], // a repeated band
        ["20", "11-19", "6-10", "2-5", "0"], // a wrong band
        ["20", "11-19", "6-10", "2-5", "one"], // not numbers
      ];
      for (const bands of others) {
        const out = ladder(...bandTable(["Roll", "Outcome"], bands));
        expect(isLadder(out), bands.join(",")).toBe(false);
        expect(out).toContain("<table>");
      }
    });

    test("a table that is not two columns is not a ladder", () => {
      const three = ["| Roll | Outcome | Notes |", "| --- | --- | --- |", ...["20", "11-19", "6-10", "2-5", "1"].map((b) => `| ${b} | text | more |`)];
      expect(isLadder(ladder(...three))).toBe(false);
    });

    test("a table inside @roll-table is never a ladder, even with the standard bands", () => {
      const out = ladder("@roll-table", "", ...bandTable(["Roll", "Result"]), "", "@end-roll-table");
      expect(isLadder(out)).toBe(false);
      expect(out).toContain("<table>");
    });

    test("the result text keeps its inline markdown", () => {
      const out = ladder(...bandTable(["Roll", "Result"], undefined, ["**Triumph.** You win", "B", "C", "D", "E"]));
      expect(out).toContain('<span class="dc-outcome-text"><strong>Triumph.</strong> You win</span>');
    });
  });

  describe("@roll-table", () => {
    const table = ["| Roll | Result |", "| --- | --- |", "| 1-4 | One |", "| 5-8 | Two |"];

    test("wraps the author's own table under a caption with the die chip and the label", () => {
      const { html, warnings } = renderGp(doc('@roll-table label="Wild Magic" die=d12', "", ...table, "", "@end-roll-table"));
      expect(html).toContain('<div class="dc-roll-table" data-label="Wild Magic" data-die="d12">');
      expect(html).toContain('<div class="dc-roll-table-caption"><span class="dc-roll-table-die">d12</span><span class="dc-roll-table-name">Wild Magic</span></div>');
      expect(html).toMatch(/<table>[\s\S]*<td>1-4<\/td>[\s\S]*<td>Two<\/td>[\s\S]*<\/table>/);
      expect(html).not.toContain("dc-outcome");
      expect(warnings).toEqual([]);
    });

    test("the die is d20 unless one is named, the label is optional and escaped", () => {
      const bare = renderGp(doc("@roll-table", "", ...table, "", "@end-roll-table")).html;
      expect(bare).toContain('<div class="dc-roll-table-caption"><span class="dc-roll-table-die">d20</span></div>');
      expect(renderGp(doc('@roll-table label="A & B"', "", ...table, "", "@end-roll-table")).html).toContain('<span class="dc-roll-table-name">A &amp; B</span>');
      expect(renderGp(doc("@roll-table die=banana", "", ...table, "", "@end-roll-table")).html).toContain('dc-roll-table-die">d20<');
    });

    test("it stays in a skill's card", () => {
      const { html } = renderGp(skill("@roll-table", "", ...table, "", "@end-roll-table", "", "After the table."));
      expect(count(html, /class="dc-skill-card/g)).toBe(1);
      expect(html).toMatch(/dc-card-inner">[\s\S]*<div class="dc-roll-table"[\s\S]*<p>After the table\.<\/p>[\s\S]*(<\/div>\s*){3}$/);
    });

    test("an @roll-table with no table in it says so", () => {
      const { warnings } = renderGp(doc("@roll-table", "", "just text", "", "@end-roll-table"));
      expect(warnings.map((w) => w.message)).toEqual(["@roll-table: It has no table, so nothing is drawn. Write the random table as a pipe table between @roll-table and @end-roll-table."]);
    });
  });

  describe("@procedure", () => {
    test("a numbered list becomes the zero-padded step list, with no wrapper of its own", () => {
      const { html, warnings } = renderGp(doc("@procedure", "", "1. First *step*.", "2. Second step.", "", "@end-procedure"));
      expect(squash(html)).toBe(
        '<ol class="dc-steps"><li><span class="dc-step-no">01</span><span>First <em>step</em>.</span></li>' +
          '<li><span class="dc-step-no">02</span><span>Second step.</span></li></ol>',
      );
      expect(warnings).toEqual([]);
    });

    test("an @end-procedure straight under the last step closes it, so later lists are left alone", () => {
      const { html, warnings } = renderGp(doc("@procedure", "", "1. One", "2. Two", "@end-procedure", "", "1. Plain", "2. List"));
      expect(count(html, /class="dc-steps"/g)).toBe(1);
      expect(html).not.toContain("@end-procedure");
      expect(html).toMatch(/<\/ol>\s*<ol>\s*<li>Plain<\/li>/);
      expect(warnings).toEqual([]);
    });

    test("one left open at the end of the document warns, with core's own message", () => {
      const { warnings } = renderGp(doc("@procedure", "", "1. One"));
      expect(types(warnings)).toEqual(["declared_marker_eof_close"]);
      expect(warnings[0].message).toMatch(/^An open @procedure reached end-of-document/);
    });

    test("a stray @end-procedure warns", () => {
      expect(types(renderGp("@end-procedure").warnings)).toEqual(["declared_marker_close_without_open"]);
    });

    test("inside a skill's card it stays in the card", () => {
      const { html } = renderGp(skill("@procedure", "", "1. One", "", "@end-procedure"));
      expect(count(html, /class="dc-skill-card/g)).toBe(1);
      expect(html).toMatch(/dc-card-inner">[\s\S]*<ol class="dc-steps">[\s\S]*<\/ol>\s*<\/div>\s*<\/div>\s*<\/div>\s*$/);
    });

    test("inside a @callout it nests there, and the callout closes at its own @end-callout", () => {
      const src = doc("@callout note", "", "Before.", "", "@procedure", "", "1. One", "2. Two", "@end-procedure", "", "After.", "", "@end-callout", "", "Outside.");
      const { html, warnings } = renderGp(src);
      expect(squash(html)).toMatch(/dc-alert dc-note"[^>]*><span[^>]*>Note<\/span><p>Before\.<\/p><ol class="dc-steps">.*<\/ol><p>After\.<\/p><\/div><p>Outside\.<\/p>$/);
      expect(warnings).toEqual([]);
    });

    describe("validate", () => {
      test("a procedure with a numbered list reports nothing", () => {
        expect(problems(doc("@procedure", "", "Intro.", "", "1. One", "", "@end-procedure"))).toEqual([]);
      });

      test("a procedure with no numbered list is one problem (a bullet list does not count)", () => {
        const message = "@procedure: It has no numbered list, so no steps are drawn. Write the steps as `1.`, `2.`, `3.` between @procedure and @end-procedure.";
        expect(problems(doc("@procedure", "", "- a", "- b", "", "@end-procedure")).map((p) => [p.line, p.message])).toEqual([[1, message]]);
        expect(problems(doc("x", "", "@procedure", "", "Just text.", "", "@end-procedure")).map((p) => p.line)).toEqual([3]);
      });
    });
  });

  test("a bare markdown-it instance leaves the three markers as text (declared markers are a Gutterpress feature)", () => {
    const html = createMarkdown().render(doc("@procedure", "", "1. One", "", "@end-procedure"));
    expect(html).toContain("@procedure");
    expect(html).not.toContain("dc-steps");
  });
});

// @callout is a declared wrapper (variant = a bare word) and @dm-note is its
// alias with the `dm` variant preset. The only plugin code is the default label.
describe("declared callout and dm-note", () => {
  const doc = (...lines) => lines.join("\n");
  const problems = (src) => renderGp(src).warnings.filter((w) => w.type === "component_invalid");
  const callout = (open, body = "Body.", close = "@end-callout") => doc(open, "", body, "", close);
  const VARIANTS = {
    note: ["dc-note", "Note"],
    warning: ["dc-note warning", "Warning"],
    dm: ["dc-dm-note", "Dream Master Note"],
    vibe: ["dc-vibe-callout", "Vibe"],
    origin: ["dc-origin-callout", "Origin"],
    visit: ["dc-visit-callout", "Visit"],
    gear: ["dc-gear-callout", "Gear"],
  };

  test("each variant word gives its class and default label", () => {
    expect(Object.keys(markers.callout.variants)).toEqual(Object.keys(VARIANTS));
    for (const [variant, [cls, label]] of Object.entries(VARIANTS)) {
      const { html, warnings } = renderGp(callout(`@callout ${variant}`));
      expect(html, variant).toMatch(new RegExp(`^<div class="dc-alert ${cls}" data-callout="${variant}"><span class="dc-alert-label">${label}</span>\n<p>Body\\.</p>\n</div>$`));
      expect(warnings, variant).toEqual([]);
    }
  });

  test("no variant is a note", () => {
    const { html, warnings } = renderGp(callout("@callout"));
    expect(html).toBe('<div class="dc-alert dc-note"><span class="dc-alert-label">Note</span>\n<p>Body.</p>\n</div>');
    expect(warnings).toEqual([]);
  });

  test("an explicit label wins, escaped, and the variant keeps its class", () => {
    const { html } = renderGp(callout('@callout vibe label="Hot & <loud>"'));
    expect(html).toContain('<div class="dc-alert dc-vibe-callout" data-callout="vibe" data-label="Hot &amp; &lt;loud&gt;"><span class="dc-alert-label">Hot &amp; &lt;loud&gt;</span>');
    expect(html).not.toContain(">Vibe<");
  });

  test("the default class does not depend on the label: a labelled callout with no variant is still a note", () => {
    const { html } = renderGp(callout('@callout label="Careful"'));
    expect(html).toContain('<div class="dc-alert dc-note" data-label="Careful"><span class="dc-alert-label">Careful</span>');
    expect(renderGp(callout('@callout vibes label="Careful"')).html).toContain('<div class="dc-alert dc-note" data-callout="vibes"');
  });

  test("author classes sit after the variant's, with the compact or the braces spelling", () => {
    for (const open of ['@callout .float-right origin label="Image Is Everything"', '@callout {.float-right} origin label="Image Is Everything"']) {
      const { html, warnings } = renderGp(callout(open));
      expect(html, open).toContain('<div class="dc-alert dc-origin-callout float-right"');
      expect(html, open).toContain('<span class="dc-alert-label">Image Is Everything</span>');
      expect(warnings, open).toEqual([]);
    }
    expect(renderGp(callout("@callout .float-right")).html).toContain('<div class="dc-alert dc-note float-right">');
  });

  test("@dm-note is @callout dm: same HTML, default label, own label, and its own closer", () => {
    const dm = renderGp(callout("@dm-note", "Body.", "@end-dm-note"));
    expect(dm.html).toBe(renderGp(callout("@callout dm")).html);
    expect(dm.html).toContain('<div class="dc-alert dc-dm-note" data-callout="dm"><span class="dc-alert-label">Dream Master Note</span>');
    expect(dm.warnings).toEqual([]);
    expect(renderGp(callout('@dm-note label="Running the Setup"', "Body.", "@end-dm-note")).html).toContain('<span class="dc-alert-label">Running the Setup</span>');
    // the closer ends it: what follows is outside
    expect(renderGp(doc("@dm-note", "", "In.", "", "@end-dm-note", "", "Out.")).html).toMatch(/<p>In\.<\/p>\n<\/div><p>Out\.<\/p>/);
  });

  test("a new callout closes the one still open; one left open closes at the end without a warning", () => {
    const { html, warnings } = renderGp(doc("@callout vibe", "", "A.", "", "@dm-note", "", "B."));
    expect(html.match(/<div class="dc-alert/g)).toHaveLength(2);
    expect(html.match(/<\/div>/g)).toHaveLength(2);
    expect(html).toMatch(/A\.<\/p>\n<\/div><div class="dc-alert dc-dm-note"/);
    expect(warnings).toEqual([]);
  });

  test("a stray closer warns", () => {
    expect(renderGp("@end-callout").warnings.map((w) => w.type)).toEqual(["declared_marker_close_without_open"]);
    expect(renderGp("@end-dm-note").warnings.map((w) => w.type)).toEqual(["declared_marker_close_without_open"]);
  });

  test("an unrecognised variant word is a note, and core says so", () => {
    const { html, warnings } = renderGp(callout("@callout vibes"));
    expect(html).toContain('<div class="dc-alert dc-note" data-callout="vibes"><span class="dc-alert-label">Note</span>');
    expect(warnings.map((w) => w.type)).toEqual(["unknown_variant"]);
    expect(warnings[0].message).toContain('"vibes" is not a variant of @callout');
  });

  describe("validate: variant= is gone", () => {
    test("one problem per callout, on the marker's line, naming the bare word to write", () => {
      const src = doc("Intro.", "", '@callout .float-right variant="origin" label="Image"', "", "A.", "", "@end-callout", "", "@callout variant=note", "", "B.", "", "@end-callout");
      expect(problems(src).map((p) => [p.line, p.message])).toEqual([
        [3, '@callout: no longer takes variant=origin; write "@callout origin" instead.'],
        [9, '@callout: no longer takes variant=note; write "@callout note" instead.'],
      ]);
    });

    test("it is not read as a variant: the callout is a plain note, never silently another variant", () => {
      const { html } = renderGp(callout("@callout variant=vibe"));
      expect(html).toContain('<div class="dc-alert dc-note" data-variant="vibe">');
      expect(html).not.toContain("dc-vibe-callout");
    });

    test("@dm-note says it too, and a bare word raises nothing", () => {
      expect(problems(callout("@dm-note variant=vibe", "x", "@end-dm-note")).map((p) => p.message)).toEqual(['@dm-note: no longer takes variant=vibe; write "@callout vibe" instead.']);
      expect(problems(callout("@callout vibe"))).toEqual([]);
      expect(problems(callout("@dm-note"))).toEqual([]);
    });
  });

  test("a callout in a skill's card stays in the card", () => {
    const { html, warnings } = renderGp(doc("@skill", "", "#### Skill | T1", "", "> Flavor.", "", "1. **1 AP** *Move:* Do it.", "", "@callout gear", "", "Tip.", "", "@end-callout"));
    expect(html).toMatch(/dc-card-inner">[\s\S]*<div class="dc-alert dc-gear-callout"[\s\S]*<\/div>\s*<\/div>\s*<\/div>\s*<\/div>\s*$/);
    expect(warnings).toEqual([]);
  });

  test("image-only paragraphs are marked, inside a callout too", () => {
    expect(renderGp(callout("@callout", "![alt](a.png)")).html).toContain('<p class="dc-img-wrapper"><img');
    expect(renderGp("text ![alt](a.png) text").html).not.toContain("dc-img-wrapper");
  });
});
