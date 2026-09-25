// plugin.test.js — what the plugin emits.
//
// Two layers of protection:
//   1. A fixture snapshot: test/fixtures/all-macros.md exercises every macro
//      the plugin ships, and all-macros.expected.html is what the plugin
//      produced for it the day this package was cut from the book repo. Any
//      change to the plugin's output fails here until the snapshot is updated
//      ON PURPOSE (`bun run test:update-snapshot`) and the diff reviewed.
//   2. Behavioural tests carried over from the book repo — the edge cases that
//      earned a regression test at the time (table pass-through, ROLL THE DIE!
//      boundaries, alert ordering, inline formatting, outcome/distance tables,
//      @continue before core's layout transform, @card footers).
//
// `gutterpress/render` is a devDependency used here to run the plugin inside
// core's own markdown pipeline (core markers such as @section/@page/@chapter
// are not this plugin's to render). It is never imported at runtime — see
// conventions.test.js.
import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import MarkdownIt from "markdown-it";
import { createMarkdownRenderer } from "gutterpress/render";

import dimmCityPlugin, { metadata } from "../plugin.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (rel) => readFileSync(path.join(ROOT, rel), "utf8");

const ROLL_HTML = '<span class="dc-roll-the-die">ROLL THE DIE!</span>';

function createMarkdown() {
  return new MarkdownIt({ html: true }).use(dimmCityPlugin);
}

function createGutterpressMarkdown() {
  return createMarkdownRenderer([{ name: "gp-dimm-city", plugin: dimmCityPlugin, options: {} }]);
}

function countRolls(html) {
  return html.split('class="dc-roll-the-die"').length - 1;
}

describe("fixture snapshot", () => {
  test("all-macros.md renders exactly to all-macros.expected.html", () => {
    const env = {};
    const html = createGutterpressMarkdown().render(read("test/fixtures/all-macros.md"), env);
    expect(env.layoutWarnings ?? []).toEqual([]);
    expect(html).toBe(read("test/fixtures/all-macros.expected.html"));
  });

  test("the fixture leaves no marker unrendered", () => {
    const html = createGutterpressMarkdown().render(read("test/fixtures/all-macros.md"), {});
    expect(html.match(/^@[a-z]/gm) ?? []).toEqual([]);
  });
});

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
    const html = createMarkdown().render(source);

    expect(html).toContain(expectedTable);
    expect(html).toMatch(/<thead>[\s\S]*<th style="text-align:left">Name<\/th>/);
    expect(html).toMatch(/<tbody>[\s\S]*<strong>Alpha<\/strong>/);
    expect(html).not.toMatch(/dc-outcomes|dc-distance-tags/);
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

    const learningPathHtml = createMarkdown().render(learningPath);
    const skillHtml = createMarkdown().render(skill);

    expect(learningPathHtml).toContain(`<div class="dc-intro"><em>Formatted route</em> says ${ROLL_HTML}</div>`);
    expect(skillHtml).toContain(`<p class="dc-flavor"><strong>Formatted flavor</strong> says ${ROLL_HTML}</p>`);
    expect(skillHtml).toContain(`<p class="dc-ability-text"><em>Move:</em> Keep <em>ability formatting</em> and ${ROLL_HTML}</p>`);
  });

  test("retains custom outcome and distance rendering with safe inline rolls", () => {
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
    const distanceTable = ["@skill", "", "#### Close In", "", "| Distance | AP |", "| --- | --- |", "| **Near** | *1 AP* |", "", "@end-skill"].join("\n");
    const outcomeMacro = ["@outcome", "20 | Triumph | **ROLL THE DIE!** but not `ROLL THE DIE!`.", "@end-outcome"].join("\n");

    const outcomeHtml = createMarkdown().render(outcomeTable);
    const distanceHtml = createMarkdown().render(distanceTable);
    const macroHtml = createMarkdown().render(outcomeMacro);

    expect(outcomeHtml).toMatch(/<div class="dc-outcomes" data-break-inside="avoid">/);
    expect(outcomeHtml).toContain(`<strong>${ROLL_HTML}</strong> but not <code>ROLL THE DIE!</code>`);
    expect(outcomeHtml).not.toMatch(/<table>/);
    expect(distanceHtml).toMatch(
      /<div class="dc-distance-tags">[\s\S]*<span class="dc-dist-ap"><em>1 AP<\/em><\/span>[\s\S]*<span class="dc-dist-name"><strong>Near<\/strong><\/span>/,
    );
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

    const singleHtml = createMarkdown().render(singleFooter);
    const twoHtml = createMarkdown().render(twoBodyBlockquotes);

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
