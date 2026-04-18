#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import fs from "node:fs";
import { readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  DEFAULT_MAX_CHARS_PER_PART,
  bytesUtf8,
  canonicalUrlForDocsPath,
  docsRelToPagesRel,
  extractFrontmatter,
  extractYamlScalar,
  normalizeSlashes,
  pickCorePages,
  renderPageOutput,
  sha256Utf8,
  transformMintlifyMdx,
} from "./lib-hermes.mjs";

function parseArgs(argv) {
  /** @type {{ includeI18n: boolean; sourceRoot?: string; distRoot?: string }} */
  const out = { includeI18n: false };

  for (let index = 0; index < argv.length; index++) {
    const arg = argv[index];
    if (arg === "--include-i18n") {
      out.includeI18n = true;
      continue;
    }
    if (arg === "--source") {
      const next = argv[index + 1];
      if (!next) {
        throw new Error("Missing value for --source");
      }
      out.sourceRoot = next;
      index++;
      continue;
    }
    if (arg === "--dist") {
      const next = argv[index + 1];
      if (!next) {
        throw new Error("Missing value for --dist");
      }
      out.distRoot = next;
      index++;
      continue;
    }
  }

  return out;
}

/** @param {string} cwd */
function git(cmdArgs, cwd) {
  return execFileSync("git", cmdArgs, { encoding: "utf8", cwd }).trim();
}

function safeGit(cmdArgs, cwd) {
  try {
    return git(cmdArgs, cwd);
  } catch {
    return null;
  }
}

/** @param {string} dir */
async function walkMarkdownFiles(dir, skipDirs) {
  /** @type {string[]} */
  const out = [];
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith(".")) {
      continue;
    }
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (skipDirs.has(entry.name)) {
        continue;
      }
      out.push(...(await walkMarkdownFiles(full, skipDirs)));
      continue;
    }
    if (entry.isFile() && /\.(md|mdx)$/i.test(entry.name)) {
      out.push(full);
    }
  }
  return out.sort((a, b) => normalizeSlashes(a).localeCompare(normalizeSlashes(b)));
}

/** @param {string} filePath */
async function readJson(filePath) {
  const raw = await readFile(filePath, "utf8");
  return JSON.parse(raw);
}

/**
 * Detect supported MDX tags outside code fences.
 * @param {string} text
 */
function findMdxTagsOutsideFences(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  let fence = null;
  /** @type {{ line: number; text: string }[]} */
  const hits = [];

  /** @param {string} line */
  function fenceMarker(line) {
    const match = line.match(/^\s*(```+|~~~+)/);
    return match ? match[1] : null;
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const marker = fenceMarker(line);
    if (marker) {
      if (!fence) {
        fence = marker;
      } else if (line.trim().startsWith(fence)) {
        fence = null;
      }
      continue;
    }
    if (fence) {
      continue;
    }

    if (
      /<\/?(Columns|CardGroup|Card|Check|Steps|Step|Tabs|Tab|AccordionGroup|Accordion|Frame|Note|Tip|Warning|Info|Tooltip)\b/.test(
        line,
      )
    ) {
      hits.push({ line: i + 1, text: line });
      if (hits.length >= 20) {
        break;
      }
    }
  }

  return hits;
}

/** @param {string} dir */
async function listMarkdownFilesAbs(dir) {
  /** @type {string[]} */
  const out = [];
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith(".")) {
      continue;
    }
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...(await listMarkdownFilesAbs(full)));
      continue;
    }
    if (entry.isFile() && /\.md$/i.test(entry.name)) {
      out.push(full);
    }
  }
  return out;
}

/**
 * @param {{ distRoot: string; prefix: string; pageRelPaths: string[]; maxChars: number; }} opts
 */
async function computeBundleParts(opts) {
  /** @type {{ path: string; sha256: string; bytes: number }[]} */
  const parts = [];

  let partIndex = 1;
  let current = "";

  function flush() {
    if (!current) {
      return;
    }
    const name = `${opts.prefix}.part${String(partIndex).padStart(2, "0")}.md`;
    const rel = normalizeSlashes(path.join("ctx", name));
    const text = current.trimEnd() + "\n";
    parts.push({ path: rel, sha256: sha256Utf8(text), bytes: bytesUtf8(text) });
    partIndex++;
    current = "";
  }

  for (const pageRel of opts.pageRelPaths) {
    const pageAbs = path.join(opts.distRoot, pageRel);
    const content = fs.existsSync(pageAbs) ? await readFile(pageAbs, "utf8") : "";
    const chunk = `# ${pageRel}\n\n${content.trimEnd()}\n\n`;

    if (current && current.length + chunk.length > opts.maxChars) {
      flush();
    }

    if (!current && chunk.length > opts.maxChars) {
      current = chunk;
      flush();
      continue;
    }

    current += chunk;
  }

  flush();
  return parts;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  const here = path.dirname(fileURLToPath(import.meta.url));
  const toolsRoot = path.resolve(here, "..");
  const workspaceRoot = path.resolve(toolsRoot, "..");

  const sourceRoot = path.resolve(
    toolsRoot,
    args.sourceRoot ? args.sourceRoot : "../hermes",
  );
  const distRoot = path.resolve(toolsRoot, args.distRoot ? args.distRoot : "../hermes-docs-capsule");

  const docsRoot = path.join(sourceRoot, "docs");
  const changelogAbs = path.join(sourceRoot, "CHANGELOG.md");
  const hasChangelog = fs.existsSync(changelogAbs) && fs.statSync(changelogAbs).isFile();

  const manifestAbs = path.join(distRoot, "manifest.json");
  const llmsAbs = path.join(distRoot, "llms.txt");
  const llmsFullAbs = path.join(distRoot, "llms_FULL.txt");
  const atlasAbs = path.join(distRoot, "ATLAS.md");
  const atlasFullAbs = path.join(distRoot, "ATLAS_FULL.md");
  const indexConfigAbs = path.join(distRoot, "INDEX_CONFIG_KEYS.md");
  const indexCliAbs = path.join(distRoot, "INDEX_CLI_COMMANDS.md");
  const pagesMetaAbs = path.join(distRoot, "meta", "pages.json");

  if (!fs.existsSync(manifestAbs)) {
    console.error(`Missing manifest: ${normalizeSlashes(path.relative(workspaceRoot, manifestAbs))}`);
    process.exitCode = 1;
    return;
  }

  /** @type {string[]} */
  const errors = [];

  for (const required of [
    llmsAbs,
    llmsFullAbs,
    atlasAbs,
    atlasFullAbs,
    indexConfigAbs,
    indexCliAbs,
    pagesMetaAbs,
  ]) {
    if (!fs.existsSync(required)) {
      errors.push(`missing file: ${normalizeSlashes(path.relative(workspaceRoot, required))}`);
    }
  }

  const manifest = await readJson(manifestAbs);
  const maxCharsPerPart = Number(manifest?.maxCharsPerPart ?? DEFAULT_MAX_CHARS_PER_PART);

  const currentHead = safeGit(["rev-parse", "HEAD"], sourceRoot);
  const manifestHead = manifest?.hermes?.gitHead ?? null;
  if (manifestHead && currentHead && manifestHead !== currentHead) {
    console.error(`Hermes git head changed: manifest=${manifestHead} current=${currentHead}`);
    console.error("Rebuild the dist pack to match the current Hermes checkout.");
    process.exitCode = 1;
    return;
  }

  const skipDirs = args.includeI18n ? new Set() : new Set(["zh-CN", "ja-JP"]);
  const docsAbs = await walkMarkdownFiles(docsRoot, skipDirs);

  /** @type {Array<{ abs: string; sourcePath: string; relFromDocs: string | null; kind: "docs" | "changelog" }>} */
  const sources = docsAbs.map((abs) => {
    const relFromDocs = normalizeSlashes(path.relative(docsRoot, abs));
    return {
      kind: "docs",
      abs,
      sourcePath: normalizeSlashes(path.join("hermes", "docs", relFromDocs)),
      relFromDocs,
    };
  });
  if (hasChangelog) {
    sources.push({
      kind: "changelog",
      abs: changelogAbs,
      sourcePath: "hermes/CHANGELOG.md",
      relFromDocs: null,
    });
  }

  /** @type {Map<string, any>} */
  const bySource = new Map();
  for (const entry of manifest.files || []) {
    if (entry?.sourcePath) {
      bySource.set(String(entry.sourcePath), entry);
    }
  }

  /** @type {Array<{ outputPath: string; sourcePath: string; canonicalUrl: string | null; title: string | null; summary: string | null; frontmatterPath: string | null }>} */
  const expectedPagesMeta = [];
  /** @type {Set<string>} */
  const expectedFrontmatterPaths = new Set();

  // 1) Pages exist + content hash matches generator output.
  for (const source of sources) {
    const entry = bySource.get(source.sourcePath);
    if (!entry) {
      errors.push(`manifest missing sourcePath: ${source.sourcePath}`);
      continue;
    }

    const sourceText = await readFile(source.abs, "utf8");
    const sourceSha = sha256Utf8(sourceText);
    if (String(entry.sourceSha256) !== sourceSha) {
      errors.push(`source sha mismatch: ${source.sourcePath}`);
    }

    let pagesRel;
    let canonicalUrl;
    let frontmatter = null;
    let title = null;
    let summary = null;
    let body;
    if (source.kind === "changelog") {
      pagesRel = "extra/CHANGELOG.md";
      body = sourceText.replace(/\r\n/g, "\n").trimEnd() + "\n";
    } else {
      pagesRel = docsRelToPagesRel(source.relFromDocs);
      canonicalUrl = canonicalUrlForDocsPath(source.relFromDocs);
      const extracted = extractFrontmatter(sourceText);
      frontmatter = extracted.frontmatter;
      title = extractYamlScalar(frontmatter, "title");
      summary = extractYamlScalar(frontmatter, "summary");
      body = transformMintlifyMdx(extracted.body);
    }

    const expected = renderPageOutput({
      sourcePath: source.sourcePath,
      canonicalUrl,
      frontmatter,
      body,
    });

    const outputPath = String(entry.outputPath || pagesRel);
    const outputAbs = path.join(distRoot, outputPath);
    if (!fs.existsSync(outputAbs)) {
      errors.push(`missing output page: ${outputPath}`);
      continue;
    }
    const actual = await readFile(outputAbs, "utf8");
    const expectedSha = sha256Utf8(expected);
    const actualSha = sha256Utf8(actual);
    if (expectedSha !== actualSha) {
      errors.push(`output mismatch: ${outputPath}`);
    }

    const hits = findMdxTagsOutsideFences(actual);
    if (hits.length) {
      errors.push(`unconverted MDX tags in ${outputPath} (e.g. line ${hits[0].line})`);
    }

    // Frontmatter output (stored separately under meta/frontmatter/).
    const expectedFrontmatterRel = pagesRel.startsWith("pages/")
      ? normalizeSlashes(path.join("meta", "frontmatter", pagesRel.slice("pages/".length).replace(/\.md$/i, ".yaml")))
      : null;

    if (frontmatter) {
      if (String(entry.frontmatterPath || "") !== expectedFrontmatterRel) {
        errors.push(`frontmatterPath mismatch (manifest): ${source.sourcePath}`);
      }
      if (!expectedFrontmatterRel) {
        errors.push(`frontmatter expected but path mapping failed: ${source.sourcePath}`);
      } else {
        expectedFrontmatterPaths.add(expectedFrontmatterRel);
        const fmAbs = path.join(distRoot, expectedFrontmatterRel);
        if (!fs.existsSync(fmAbs)) {
          errors.push(`missing frontmatter: ${expectedFrontmatterRel}`);
        } else {
          const expectedFm = frontmatter.trimEnd() + "\n";
          const actualFm = await readFile(fmAbs, "utf8");
          if (sha256Utf8(expectedFm) !== sha256Utf8(actualFm)) {
            errors.push(`frontmatter mismatch: ${expectedFrontmatterRel}`);
          }
        }
      }
    } else {
      if (entry.frontmatterPath) {
        errors.push(`unexpected frontmatterPath (manifest): ${source.sourcePath}`);
      }
      if (expectedFrontmatterRel && fs.existsSync(path.join(distRoot, expectedFrontmatterRel))) {
        errors.push(`unexpected frontmatter file: ${expectedFrontmatterRel}`);
      }
    }

    expectedPagesMeta.push({
      outputPath: pagesRel,
      sourcePath: source.sourcePath,
      canonicalUrl: canonicalUrl ?? null,
      title,
      summary,
      frontmatterPath: frontmatter ? expectedFrontmatterRel : null,
    });
  }

  // 1.5) meta/pages.json matches expected mapping.
  if (fs.existsSync(pagesMetaAbs)) {
    const hermesGitHead = safeGit(["rev-parse", "HEAD"], sourceRoot);
    const hermesGitDescribe = safeGit(["describe", "--tags", "--always"], sourceRoot);
    const expectedMeta = {
      hermes: { gitHead: hermesGitHead, gitDescribe: hermesGitDescribe },
      pages: expectedPagesMeta.sort((a, b) => a.outputPath.localeCompare(b.outputPath)),
    };
    const expectedText = JSON.stringify(expectedMeta, null, 2) + "\n";
    const actualText = await readFile(pagesMetaAbs, "utf8");
    if (sha256Utf8(expectedText) !== sha256Utf8(actualText)) {
      errors.push(`meta/pages.json mismatch: ${normalizeSlashes(path.relative(workspaceRoot, pagesMetaAbs))}`);
    }
  }

  // 1.6) No unexpected frontmatter files.
  async function listYamlFilesAbs(dir) {
    /** @type {string[]} */
    const out = [];
    if (!fs.existsSync(dir)) {
      return out;
    }
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith(".")) {
        continue;
      }
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        out.push(...(await listYamlFilesAbs(full)));
        continue;
      }
      if (entry.isFile() && /\.ya?ml$/i.test(entry.name)) {
        out.push(full);
      }
    }
    return out;
  }

  const frontmatterRoot = path.join(distRoot, "meta", "frontmatter");
  if (fs.existsSync(frontmatterRoot)) {
    const actualFrontmatter = (await listYamlFilesAbs(frontmatterRoot))
      .map((abs) => normalizeSlashes(path.relative(distRoot, abs)))
      .sort((a, b) => a.localeCompare(b));
    const actualSet = new Set(actualFrontmatter);

    for (const rel of actualFrontmatter) {
      if (!expectedFrontmatterPaths.has(rel)) {
        errors.push(`unexpected frontmatter file: ${rel}`);
      }
    }
    for (const rel of expectedFrontmatterPaths) {
      if (!actualSet.has(rel)) {
        errors.push(`missing frontmatter file: ${rel}`);
      }
    }
  }

  // 2) Count output pages.
  const pagesDir = path.join(distRoot, "pages");
  if (fs.existsSync(pagesDir)) {
    const allPages = (await listMarkdownFilesAbs(pagesDir))
      .map((abs) => normalizeSlashes(path.relative(distRoot, abs)))
      .sort((a, b) => a.localeCompare(b));
    const expectedPageCount = sources.filter((s) => s.kind !== "changelog").length;
    if (allPages.length !== expectedPageCount) {
      errors.push(`pages count mismatch: expected=${expectedPageCount} actual=${allPages.length}`);
    }

    // 3) Bundles match expected sharding.
    const corePages = pickCorePages(allPages);
    const fullPages = allPages;

    const expectedCore = await computeBundleParts({
      distRoot,
      prefix: "core",
      pageRelPaths: corePages,
      maxChars: maxCharsPerPart,
    });
    const expectedFull = await computeBundleParts({
      distRoot,
      prefix: "full",
      pageRelPaths: fullPages,
      maxChars: maxCharsPerPart,
    });

    for (const part of [...expectedCore, ...expectedFull]) {
      const abs = path.join(distRoot, part.path);
      if (!fs.existsSync(abs)) {
        errors.push(`missing ctx part: ${part.path}`);
        continue;
      }
      const content = await readFile(abs, "utf8");
      const sha = sha256Utf8(content);
      if (sha !== part.sha256) {
        errors.push(`ctx sha mismatch: ${part.path}`);
      }
    }

    const expectedPartPaths = new Set([...expectedCore, ...expectedFull].map((p) => p.path));
    const ctxDir = path.join(distRoot, "ctx");
    const existing = await readdir(ctxDir, { withFileTypes: true }).catch(() => []);
    for (const entry of existing) {
      if (!entry.isFile()) {
        continue;
      }
      if (!/^(core|full)\.part\d+\.md$/.test(entry.name)) {
        continue;
      }
      const rel = normalizeSlashes(path.join("ctx", entry.name));
      if (!expectedPartPaths.has(rel)) {
        errors.push(`unexpected ctx part: ${rel}`);
      }
    }
  }

  if (errors.length) {
    for (const error of errors) {
      console.error(error);
    }
    process.exitCode = 1;
    return;
  }

  console.log(
    JSON.stringify(
      {
        ok: true,
        distRoot: normalizeSlashes(path.relative(workspaceRoot, distRoot)) || ".",
        checkedSources: sources.length,
      },
      null,
      2,
    ),
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
