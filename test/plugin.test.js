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
      "@skill {.dc-allow-split}",
      "",
      "#### Risk It",
      "",
      "| Roll | Outcome |",
      "| --- | --- |",
      "| 20 | **ROLL THE DIE!** but not `ROLL THE DIE!` |",
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
      "@skill {.dc-allow-split}",
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
    expect(skillHtml).toMatch(/class="dc-skill-card dc-skill-card-cont dc-allow-split"/);
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
    const rewritten = ["specialty", "learning-path", "skill", "card", "outcome", "procedure"]; // declared too, but their content is rewritten: see the next describe blocks
    expect(Object.keys(markers).filter((k) => k !== "specialty-card" && !rewritten.includes(k) && !markers[k].section).sort()).toEqual(Object.keys(expected).sort());
    for (const [name, cls] of Object.entries(expected)) {
      const { html, warnings } = render(wrap(`@${name}`, `@end-${name}`));
      expect(html, name).toContain(`<div class="${cls}">`);
      expect(warnings, name).toEqual([]);
    }
  });

  test("@sidebar inset and @sidebar .inset both add the inset class", () => {
    expect(render(wrap("@sidebar inset", "@end-sidebar")).html).toMatch(/<div class="dc-sidebar inset"/);
    expect(render(wrap("@sidebar .inset", "@end-sidebar")).html).toMatch(/<div class="dc-sidebar inset"/);
    expect(render(wrap("@sidebar {.top-right .inset}", "@end-sidebar")).html).toMatch(/<div class="dc-sidebar top-right inset"/);
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

  test("section markers are core sections: same HTML as the @section spelling", () => {
    const expected = {
      "column-panel": "dc-column-panel",
      tabbed: "dc-tabbed",
      "card-grid": "dc-card-grid",
      "citizen-walkthrough": "dc-citizen-walkthrough",
      "fiction-excerpt": "dc-fiction-excerpt",
      "npc-stat": "dc-npc-stat",
      flaws: "dc-flaws",
      ideals: "dc-ideals",
      dreams: "dc-dreams",
    };
    expect(Object.keys(markers).filter((k) => markers[k].section).sort()).toEqual(Object.keys(expected).sort());
    for (const [name, cls] of Object.entries(expected)) {
      const declared = render(wrap(`@${name} .gp-columns-2`, `@end-${name}`, "## T"));
      const written = render(wrap(`@section .${cls} .gp-columns-2`, "@end-section", "## T"));
      expect(declared.html, name).toContain(`<div class="section ${cls} gp-columns-2"`);
      expect(declared.html, name).toBe(written.html);
      expect(declared.warnings, name).toEqual([]);
    }
  });

  test("a section marker closes at the next @section like any section, and @continue keeps its class", () => {
    const { html, warnings } = render(["@npc-stat", "", "x", "", "@section", "", "y", "", "@end-section"].join("\n"));
    expect(html).toMatch(/<div class="section dc-npc-stat"><p>x<\/p>\s*<\/div><div class="section"/);
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
      const { html } = renderGp(doc("@specialty .augmerc .dc-cards-two-col #spec-aug", "", "x"));
      expect(html).toMatch(/<div class="dc-specialty augmerc dc-cards-two-col" id="spec-aug"/);
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

    test("hand-written components and wrappers keep working inside a specialty", () => {
      const src = doc(
        "@specialty .augmerc", "",
        "@specialty-intro", "", "## Augmerc", "", "@end-specialty-intro", "",
        "@card", "", "#### Title", "", "> Pull", "", "Body.", "", "@end-card", "",
        "@callout variant=note", "", "Careful.", "", "@end-callout", "",
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
      const src = doc("@skill {.dc-allow-split .dc-two-col} id=sk variant=2", "", card("First | T1"), "", card("Second | T2 | highlight"));
      const { html } = renderGp(src);
      expect(count(html, /class="dc-skill-card dc-allow-split dc-two-col"/g)).toBe(2);
      expect(html).toContain('id="sk" data-variant="2" name="first"');
      expect(html).toContain('name="second"');
      // `.dc-allow-split` opts out of the default avoid
      expect(html).not.toContain("data-break-inside");
      expect(html).toContain('<div class="dc-card-tab dc-highlight">');
      expect(html).toContain('<h4 class="dc-tab-title">Second</h4>');
      expect(html).toContain('<span class="dc-tab-tier">T2</span>');
    });

    test("a card is kept whole by default and named after its title", () => {
      const { html } = renderGp(doc("@skill", "", card("Hold the Line")));
      expect(html).toContain('<div class="dc-skill-card" name="hold-the-line" data-break-inside="avoid">');
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
        "| Roll | Outcome |", "| --- | --- |", "| 20 | Crit |", "| 1 | Boom |", "",
        "##### A real sub-header", "",
        "- one", "- two",
      );
      const { html } = renderGp(src);
      expect(html).toContain('<p class="dc-flavor">Flavor.</p>');
      expect(html).toContain('<div class="dc-ability" data-ability-penultimate="true">');
      expect(html).toContain('<div class="dc-ability" data-ability-last="true">');
      expect(html).toContain('<span class="dc-ap variable">2-X AP</span>');
      expect(html).toContain('<div class="dc-outcomes">');
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
      const src = doc("@specialty .augmerc", "", "@learning-path", "", "### P", "", skill("@skill {.dc-allow-split}", "@end-skill"), "@end-learning-path", "@end-specialty");
      const { html, warnings } = renderGp(src);
      expect(count(html, /class="dc-skill-card/g)).toBe(2);
      expect(html).toContain('<div class="dc-skill-card dc-skill-card-cont dc-allow-split" name="long-skill">');
      expect(html).toContain('<div class="dc-card-tab dc-card-tab-cont">');
      expect(html).toContain('<span class="dc-tab-title">Long Skill ▸</span>');
      expect(html).toContain('<span class="dc-tab-tier">T2</span>');
      expect(html).not.toMatch(/gp-continued/);
      expect(warnings).toEqual([]);
    });

    test("a card that is not splittable keeps its avoid on the continuation too", () => {
      expect(renderGp(skill("@skill", "@end-skill")).html).toMatch(/dc-skill-card-cont" name="long-skill" data-break-inside="avoid"/);
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
      const table = ["| Roll | Outcome |", "| --- | --- |", "| 20 | Crit |"];
      const { html } = renderGp(skill(...table, "", "@outcome", "", "20 | Crit | Yes.", "", "@end-outcome"));
      expect(count(html, /class="dc-skill-card/g)).toBe(1);
      expect(count(html, /<div class="dc-outcomes"/g)).toBe(2);
      expect(html).toMatch(/<div class="dc-card-inner">[\s\S]*<div class="dc-outcomes">[\s\S]*Crit<\/span>[\s\S]*<div class="dc-outcomes">[\s\S]*Yes\.[\s\S]*(<\/div>\s*){4}$/);
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

    test("inside a hand-written @callout it nests there, and the callout closes at its own @end-callout", () => {
      const src = doc("@callout variant=note", "", "Before.", "", "@procedure", "", "1. One", "2. Two", "@end-procedure", "", "After.", "", "@end-callout", "", "Outside.");
      const { html, warnings } = renderGp(src);
      expect(squash(html)).toMatch(/dc-alert dc-note"><span[^>]*>Note<\/span><p>Before\.<\/p><ol class="dc-steps">.*<\/ol><p>After\.<\/p><\/div><p>Outside\.<\/p>$/);
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
