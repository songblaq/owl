#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import fs from "node:fs";
import { mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  AI_PACK_VERSION,
  DEFAULT_MAX_CHARS_PER_PART,
  bytesUtf8,
  canonicalUrlForDocsPath,
  docsRelToPagesRel,
  extractCliCommands,
  extractConfigKeys,
  extractFrontmatter,
  extractYamlScalar,
  formatDateYYYYMMDD,
  normalizeSlashes,
  pickCorePages,
  renderPageOutput,
  sha256Utf8,
  transformMintlifyMdx,
} from "./lib-openclaw.mjs";

function parseArgs(argv) {
  /** @type {{ includeI18n: boolean; openclawRoot?: string; distRoot?: string; maxCharsPerPart: number }} */
  const out = { includeI18n: false, maxCharsPerPart: DEFAULT_MAX_CHARS_PER_PART };

  for (let index = 0; index < argv.length; index++) {
    const arg = argv[index];
    if (arg === "--include-i18n") {
      out.includeI18n = true;
      continue;
    }
    if (arg === "--openclaw") {
      const next = argv[index + 1];
      if (!next) {
        throw new Error("Missing value for --openclaw");
      }
      out.openclawRoot = next;
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
    if (arg === "--max-chars-per-part") {
      const next = argv[index + 1];
      if (!next || Number.isNaN(Number(next))) {
        throw new Error("Missing/invalid value for --max-chars-per-part");
      }
      out.maxCharsPerPart = Number(next);
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

async function readJsonIfExists(filePath) {
  if (!fs.existsSync(filePath)) {
    return null;
  }
  const raw = await readFile(filePath, "utf8");
  return JSON.parse(raw);
}

async function writeTextIfChanged(filePath, content) {
  const existing = await readFile(filePath, "utf8").catch(() => null);
  if (existing === content) {
    return { changed: false };
  }
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, content, "utf8");
  return { changed: true };
}

/** @param {string} rootDir */
async function listFilesRecursive(rootDir) {
  /** @type {string[]} */
  const out = [];
  if (!fs.existsSync(rootDir)) {
    return out;
  }
  const entries = await readdir(rootDir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(rootDir, entry.name);
    if (entry.isDirectory()) {
      out.push(...(await listFilesRecursive(full)));
    } else if (entry.isFile()) {
      out.push(full);
    }
  }
  return out;
}

/**
 * Remove files under rootDir that are not in keepRelPaths.
 * @param {string} rootDir
 * @param {Set<string>} keepRelPaths
 */
async function pruneExtraFiles(rootDir, keepRelPaths) {
  const existingAbs = await listFilesRecursive(rootDir);
  const prunable = existingAbs.filter((abs) => {
    const rel = normalizeSlashes(path.relative(rootDir, abs));
    return !keepRelPaths.has(rel);
  });
  await Promise.all(prunable.map((abs) => rm(abs, { recursive: true, force: true })));
  return prunable.length;
}

/**
 * Remove empty directories under rootDir (best-effort).
 * @param {string} rootDir
 */
async function pruneEmptyDirs(rootDir) {
  if (!fs.existsSync(rootDir)) {
    return 0;
  }
  let removed = 0;
  const entries = await readdir(rootDir, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }
    const full = path.join(rootDir, entry.name);
    removed += await pruneEmptyDirs(full);
  }
  const after = await readdir(rootDir, { withFileTypes: true });
  if (after.length === 0) {
    await rm(rootDir, { recursive: true, force: true });
    removed++;
  }
  return removed;
}

/**
 * @param {{ distRoot: string; prefix: string; pageRelPaths: string[]; maxChars: number; }} opts
 */
async function buildBundleParts(opts) {
  /** @type {{ path: string; sha256: string; bytes: number }[]} */
  const parts = [];
  const ctxRoot = path.join(opts.distRoot, "ctx");
  await mkdir(ctxRoot, { recursive: true });

  /** @type {string[]} */
  const keep = [];

  let partIndex = 1;
  let current = "";

  async function flush() {
    if (!current) {
      return;
    }
    const name = `${opts.prefix}.part${String(partIndex).padStart(2, "0")}.md`;
    const rel = normalizeSlashes(path.join("ctx", name));
    const abs = path.join(opts.distRoot, rel);
    const text = current.trimEnd() + "\n";
    const sha = sha256Utf8(text);
    const bytes = bytesUtf8(text);
    await writeTextIfChanged(abs, text);
    parts.push({ path: rel, sha256: sha, bytes });
    keep.push(name);
    partIndex++;
    current = "";
  }

  for (const pageRel of opts.pageRelPaths) {
    const pageAbs = path.join(opts.distRoot, pageRel);
    const content = await readFile(pageAbs, "utf8");
    const chunk = `# ${pageRel}\n\n${content.trimEnd()}\n\n`;

    if (current && current.length + chunk.length > opts.maxChars) {
      await flush();
    }

    if (!current && chunk.length > opts.maxChars) {
      current = chunk;
      await flush();
      continue;
    }

    current += chunk;
  }

  await flush();

  // Prune stale parts for this prefix.
  const existing = await readdir(ctxRoot, { withFileTypes: true }).catch(() => []);
  for (const entry of existing) {
    if (!entry.isFile()) {
      continue;
    }
    if (!entry.name.startsWith(`${opts.prefix}.part`)) {
      continue;
    }
    if (keep.includes(entry.name)) {
      continue;
    }
    await rm(path.join(ctxRoot, entry.name), { force: true });
  }

  return parts;
}

function renderLlmsTxt(corePages) {
  const lines = [];
  lines.push("# OpenClaw Docs — Capsule (compact)");
  lines.push("");
  lines.push("Lossless, LLM-friendly mirror of `openclaw/docs/**`.");
  lines.push("pages/** are body-only; metadata is in meta/**.");
  lines.push("For a full navigation map, see ATLAS_FULL.md and llms_FULL.txt.");
  lines.push("");
  lines.push("## Start");
  lines.push("- ATLAS.md (compact navigation map)");
  lines.push("- ATLAS_FULL.md (full navigation map)");
  lines.push("- INDEX_CONFIG_KEYS.md (config-key lookup)");
  lines.push("- INDEX_CLI_COMMANDS.md (CLI command lookup)");
  lines.push("");
  lines.push("## Core");
  for (const p of corePages) {
    lines.push(`- ${p}`);
  }
  lines.push("");
  lines.push("## Bundles");
  lines.push("- ctx/core.part*.md (core, sharded)");
  lines.push("- ctx/full.part*.md (full, sharded)");
  lines.push("");
  lines.push("## Metadata");
  lines.push("- meta/pages.json (page → source/canonical/title/summary/frontmatter mapping)");
  lines.push("- meta/frontmatter/** (frontmatter YAML per page)");
  lines.push("");
  lines.push("## Extra");
  lines.push("- extra/CHANGELOG.md (version history, load only when needed)");
  lines.push("");
  lines.push("## Delta");
  lines.push("- delta/delta-YYYY-MM-DD.md (only when OpenClaw git head changes)");
  lines.push("");
  lines.push("## Index");
  lines.push("- manifest.json (source/output hashes + OpenClaw git head)");
  lines.push("");
  return lines.join("\n");
}

function renderLlmsFullTxt(corePages) {
  const lines = [];
  lines.push("# OpenClaw Docs — Capsule (full)");
  lines.push("");
  lines.push("Lossless, LLM-friendly mirror of `openclaw/docs/**`.");
  lines.push("Start with ATLAS_FULL.md, then open specific pages as needed.");
  lines.push("");
  lines.push("## Start");
  lines.push("- ATLAS_FULL.md (full navigation map — read this first)");
  lines.push("- ATLAS.md (compact navigation map)");
  lines.push("- INDEX_CONFIG_KEYS.md (config-key lookup)");
  lines.push("- INDEX_CLI_COMMANDS.md (CLI command lookup)");
  lines.push("");
  lines.push("## Core");
  for (const p of corePages) {
    lines.push(`- ${p}`);
  }
  lines.push("");
  lines.push("## Bundles");
  lines.push("- ctx/core.part*.md (core, sharded)");
  lines.push("- ctx/full.part*.md (full, sharded)");
  lines.push("");
  lines.push("## Metadata");
  lines.push("- meta/pages.json (page → source/canonical/title/summary/frontmatter mapping)");
  lines.push("- meta/frontmatter/** (frontmatter YAML per page)");
  lines.push("");
  lines.push("## Extra");
  lines.push("- extra/CHANGELOG.md (version history, load only when needed)");
  lines.push("");
  lines.push("## Delta");
  lines.push("- delta/delta-YYYY-MM-DD.md (only when OpenClaw git head changes)");
  lines.push("");
  lines.push("## Index");
  lines.push("- manifest.json (source/output hashes + OpenClaw git head)");
  lines.push("");
  return lines.join("\n");
}

/**
 * @param {{
 *   openclawGitHead: string | null;
 *   openclawGitDescribe: string | null;
 *   includeI18n: boolean;
 * }} opts
 */
function renderAtlas(opts) {
  const lines = [];
  lines.push("# OpenClaw Capsule Atlas (compact)");
  lines.push("");
  lines.push(
    "This folder is for LLM agents. It mirrors OpenClaw docs with layout stripped but content preserved.",
  );
  lines.push("pages/** contain only the doc body. Frontmatter/provenance is in meta/**.");
  lines.push("For the full navigation map, see ATLAS_FULL.md.");
  lines.push("");
  if (opts.openclawGitDescribe || opts.openclawGitHead) {
    lines.push("OpenClaw source:");
    if (opts.openclawGitDescribe) lines.push(`- gitDescribe: ${opts.openclawGitDescribe}`);
    if (opts.openclawGitHead) lines.push(`- gitHead: ${opts.openclawGitHead}`);
    lines.push("");
  }
  lines.push("Start here:");
  lines.push("- llms.txt (compact)");
  lines.push("- llms_FULL.txt (full)");
  lines.push("- pages/start/docs-directory.md (curated index)");
  lines.push("- pages/start/hubs.md (full map / hubs)");
  lines.push("");
  lines.push("When you need titles/summary/canonical/source paths:");
  lines.push("- meta/pages.json");
  lines.push("- meta/frontmatter/**");
  lines.push("");
  lines.push("Extras:");
  lines.push("- extra/CHANGELOG.md (version history; excluded from ctx bundles)");
  lines.push("");
  lines.push("Lookup:");
  lines.push("- INDEX_CONFIG_KEYS.md (backticked dotted keys, filtered to config-like roots)");
  lines.push("- INDEX_CLI_COMMANDS.md (lines that start with `openclaw ...`)");
  lines.push("");
  lines.push("Route → file mapping (Mintlify style):");
  lines.push("- `/` → `pages/index.md`");
  lines.push("- `/foo/bar` → `pages/foo/bar.md`");
  lines.push("- `/foo` → `pages/foo.md` or `pages/foo/index.md`");
  lines.push("");
  lines.push("Common tasks (open these files):");
  lines.push("- Install/update/uninstall: pages/install/index.md, pages/install/updating.md, pages/install/uninstall.md");
  lines.push("- First chat / Control UI: pages/start/getting-started.md, pages/web/control-ui.md, pages/web/dashboard.md");
  lines.push("- Gateway config: pages/gateway/configuration.md, pages/gateway/configuration-reference.md, pages/gateway/configuration-examples.md");
  lines.push(
    "- Security/sandbox: pages/gateway/security/index.md, pages/gateway/sandboxing.md, pages/gateway/sandbox-vs-tool-policy-vs-elevated.md",
  );
  lines.push("- Pairing/access control: pages/channels/pairing.md, pages/channels/*");
  lines.push(
    "- Troubleshooting: pages/gateway/troubleshooting.md, pages/help/troubleshooting.md, pages/channels/troubleshooting.md",
  );
  lines.push("");
  lines.push(`i18n copies included: ${opts.includeI18n ? "yes (--include-i18n)" : "no (default)"}`);
  lines.push("");
  return lines.join("\n");
}

/**
 * @param {{
 *   openclawGitHead: string | null;
 *   openclawGitDescribe: string | null;
 *   includeI18n: boolean;
 *   navTabs: Array<{ tab: string; groups: Array<{ group: string; pages: string[] }> }>;
 *   allPages: string[];
 * }} opts
 */
function renderAtlasFull(opts) {
  const lines = [];
  lines.push("# OpenClaw Capsule Atlas (full)");
  lines.push("");
  lines.push(
    "This folder is for LLM agents. It mirrors OpenClaw docs with layout stripped but content preserved.",
  );
  lines.push("Navigation below is derived from `openclaw/docs/docs.json`.");
  lines.push("");
  if (opts.openclawGitDescribe || opts.openclawGitHead) {
    lines.push("OpenClaw source:");
    if (opts.openclawGitDescribe) lines.push(`- gitDescribe: ${opts.openclawGitDescribe}`);
    if (opts.openclawGitHead) lines.push(`- gitHead: ${opts.openclawGitHead}`);
    lines.push("");
  }
  lines.push("Start here:");
  lines.push("- llms_FULL.txt");
  lines.push("- ATLAS.md (compact map)");
  lines.push("- pages/start/docs-directory.md");
  lines.push("- pages/start/hubs.md");
  lines.push("");
  lines.push("## Navigation (docs.json)");
  lines.push("");

  /** @param {string} slug */
  function slugToPage(slug) {
    const s = String(slug || "").replace(/^\/+/, "").replace(/\.mdx?$/i, "");
    if (!s) return null;
    if (s === "index") return "pages/index.md";
    return `pages/${s}.md`;
  }

  const navSet = new Set();
  for (const tab of opts.navTabs) {
    lines.push(`## ${tab.tab}`);
    lines.push("");
    for (const group of tab.groups) {
      lines.push(`### ${group.group}`);
      for (const slug of group.pages || []) {
        const page = slugToPage(slug);
        if (!page) continue;
        navSet.add(page);
        lines.push(`- ${page}`);
      }
      lines.push("");
    }
  }

  const unlisted = opts.allPages.filter((p) => !navSet.has(p));
  lines.push("## Pages not in docs.json navigation");
  lines.push("");
  if (!unlisted.length) {
    lines.push("- (none)");
  } else {
    lines.push(`- count: ${unlisted.length}`);
    lines.push("- use `manifest.json` or search to locate these pages");
  }
  lines.push("");
  lines.push(`i18n copies included: ${opts.includeI18n ? "yes (--include-i18n)" : "no (default)"}`);
  lines.push("");
  return lines.join("\n");
}

/**
 * @param {Map<string, Set<string>>} index
 * @param {{ title: string; description: string }} opts
 */
function renderIndexMarkdown(index, opts) {
  const lines = [];
  lines.push(`# ${opts.title}`);
  lines.push("");
  lines.push(opts.description.trim());
  lines.push("");
  const keys = [...index.keys()].sort((a, b) => a.localeCompare(b));
  for (const key of keys) {
    const pages = [...(index.get(key) ?? [])].sort((a, b) => a.localeCompare(b));
    lines.push(`- \`${key}\`: ${pages.join(", ")}`);
  }
  lines.push("");
  return lines.join("\n");
}

function parseNameStatus(stdout) {
  /** @type {{ status: string; paths: string[] }[]} */
  const out = [];
  for (const rawLine of stdout.split("\n")) {
    const line = rawLine.trimEnd();
    if (!line) {
      continue;
    }
    const parts = line.split("\t").filter(Boolean);
    const status = parts[0];
    const paths = parts.slice(1);
    if (!status || paths.length === 0) {
      continue;
    }
    out.push({ status, paths });
  }
  return out;
}

function isMarkdownPath(rel) {
  if (rel === "CHANGELOG.md") {
    return true;
  }
  return rel.endsWith(".md") || rel.endsWith(".mdx");
}

function toSourcePath(rel) {
  if (rel === "CHANGELOG.md") {
    return "openclaw/CHANGELOG.md";
  }
  if (rel.startsWith("docs/")) {
    return `openclaw/${rel}`;
  }
  return `openclaw/${rel}`;
}

function sourcePathToPagesRel(sourcePath) {
  if (sourcePath === "openclaw/CHANGELOG.md") {
    return "extra/CHANGELOG.md";
  }
  if (sourcePath.startsWith("openclaw/docs/")) {
    const relFromDocs = sourcePath.slice("openclaw/docs/".length);
    return docsRelToPagesRel(relFromDocs);
  }
  return null;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  const here = path.dirname(fileURLToPath(import.meta.url));
  const toolsRoot = path.resolve(here, "..");
  const workspaceRoot = path.resolve(toolsRoot, "..");

  const openclawRoot = path.resolve(
    toolsRoot,
    args.openclawRoot ? args.openclawRoot : "../openclaw",
  );
  const distRoot = path.resolve(toolsRoot, args.distRoot ? args.distRoot : "../openclaw-docs-capsule");

  const docsRoot = path.join(openclawRoot, "docs");
  const changelogAbs = path.join(openclawRoot, "CHANGELOG.md");
  const docsJsonAbs = path.join(docsRoot, "docs.json");
  const hasChangelog = fs.existsSync(changelogAbs) && fs.statSync(changelogAbs).isFile();

  if (!fs.existsSync(docsRoot) || !fs.statSync(docsRoot).isDirectory()) {
    throw new Error(`Missing docs directory: ${docsRoot}`);
  }

  const skipDirs = args.includeI18n ? new Set() : new Set(["zh-CN", "ja-JP"]);

  const openclawGitHead = safeGit(["rev-parse", "HEAD"], openclawRoot);
  const openclawGitDescribe = safeGit(["describe", "--tags", "--always"], openclawRoot);

  await mkdir(distRoot, { recursive: true });
  await mkdir(path.join(distRoot, "pages"), { recursive: true });
  await mkdir(path.join(distRoot, "ctx"), { recursive: true });
  await mkdir(path.join(distRoot, "extra"), { recursive: true });
  await mkdir(path.join(distRoot, "delta"), { recursive: true });
  await mkdir(path.join(distRoot, "meta"), { recursive: true });
  await mkdir(path.join(distRoot, "meta", "frontmatter"), { recursive: true });

  const manifestAbs = path.join(distRoot, "manifest.json");
  const llmsAbs = path.join(distRoot, "llms.txt");
  const llmsFullAbs = path.join(distRoot, "llms_FULL.txt");
  const atlasAbs = path.join(distRoot, "ATLAS.md");
  const atlasFullAbs = path.join(distRoot, "ATLAS_FULL.md");
  const indexConfigAbs = path.join(distRoot, "INDEX_CONFIG_KEYS.md");
  const indexCliAbs = path.join(distRoot, "INDEX_CLI_COMMANDS.md");
  const pagesMetaAbs = path.join(distRoot, "meta", "pages.json");

  const prevManifest = await readJsonIfExists(manifestAbs);

  const docsAbs = await walkMarkdownFiles(docsRoot, skipDirs);
  const sources = docsAbs.map((abs) => {
    const relFromDocs = normalizeSlashes(path.relative(docsRoot, abs));
    return {
      kind: "docs",
      abs,
      sourcePath: normalizeSlashes(path.join("openclaw", "docs", relFromDocs)),
      relFromDocs,
    };
  });
  if (hasChangelog) {
    sources.push({
      kind: "changelog",
      abs: changelogAbs,
      sourcePath: "openclaw/CHANGELOG.md",
      relFromDocs: null,
    });
  }

  /** @type {Array<{ sourcePath: string; outputPath: string; canonicalUrl?: string; title?: string | null; summary?: string | null; frontmatterPath?: string | null; sourceSha256: string; outputSha256: string; frontmatterSha256?: string | null; sourceBytes: number; outputBytes: number; frontmatterBytes?: number | null }>} */
  const files = [];

  /** @type {Set<string>} */
  const keepPagesRel = new Set();
  /** @type {Set<string>} */
  const keepExtraRel = new Set();
  /** @type {Set<string>} */
  const keepFrontmatterRel = new Set();

  /** @type {Map<string, Set<string>>} */
  const configKeyIndex = new Map();
  /** @type {Map<string, Set<string>>} */
  const cliCommandIndex = new Map();

  let wrotePages = 0;
  let wroteFrontmatter = 0;

  for (const source of sources) {
    const sourceText = await readFile(source.abs, "utf8");
    const sourceSha256 = sha256Utf8(sourceText);
    const sourceBytes = bytesUtf8(sourceText);

    let pagesRel;
    let canonicalUrl;
    let frontmatter = null;
    let frontmatterRel = null;
    let body;
    let title = null;
    let summary = null;

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

    const outputText = renderPageOutput({
      sourcePath: source.sourcePath,
      canonicalUrl,
      frontmatter,
      body,
    });

    const outputSha256 = sha256Utf8(outputText);
    const outputBytes = bytesUtf8(outputText);

    const outputAbs = path.join(distRoot, pagesRel);
    const { changed } = await writeTextIfChanged(outputAbs, outputText);
    if (changed) {
      wrotePages++;
    }

    if (source.kind === "changelog") {
      keepExtraRel.add(normalizeSlashes(path.relative(path.join(distRoot, "extra"), outputAbs)));
    } else {
      keepPagesRel.add(normalizeSlashes(path.relative(path.join(distRoot, "pages"), outputAbs)));
    }

    // Write frontmatter to meta/frontmatter/ as separate YAML file.
    let frontmatterSha256 = null;
    let frontmatterBytes = null;
    if (frontmatter) {
      const inner = pagesRel.startsWith("pages/") ? pagesRel.slice("pages/".length) : pagesRel;
      frontmatterRel = normalizeSlashes(
        path.join("meta", "frontmatter", inner.replace(/\.md$/i, ".yaml")),
      );
      const frontmatterText = frontmatter.trimEnd() + "\n";
      frontmatterSha256 = sha256Utf8(frontmatterText);
      frontmatterBytes = bytesUtf8(frontmatterText);
      const frontmatterAbs = path.join(distRoot, frontmatterRel);
      const { changed: changedFm } = await writeTextIfChanged(frontmatterAbs, frontmatterText);
      if (changedFm) {
        wroteFrontmatter++;
      }
      keepFrontmatterRel.add(
        normalizeSlashes(path.relative(path.join(distRoot, "meta", "frontmatter"), frontmatterAbs)),
      );
    }

    files.push({
      sourcePath: source.sourcePath,
      outputPath: pagesRel,
      canonicalUrl,
      title,
      summary,
      frontmatterPath: frontmatterRel,
      sourceSha256,
      outputSha256,
      frontmatterSha256,
      sourceBytes,
      outputBytes,
      frontmatterBytes,
    });

    for (const key of extractConfigKeys(body)) {
      const set = configKeyIndex.get(key) ?? new Set();
      set.add(pagesRel);
      configKeyIndex.set(key, set);
    }
    for (const cmd of extractCliCommands(body)) {
      const set = cliCommandIndex.get(cmd) ?? new Set();
      set.add(pagesRel);
      cliCommandIndex.set(cmd, set);
    }
  }

  const prunedPages = await pruneExtraFiles(path.join(distRoot, "pages"), keepPagesRel);
  const prunedExtraFiles = await pruneExtraFiles(path.join(distRoot, "extra"), keepExtraRel);
  const prunedFrontmatter = await pruneExtraFiles(
    path.join(distRoot, "meta", "frontmatter"),
    keepFrontmatterRel,
  );
  await pruneEmptyDirs(path.join(distRoot, "meta", "frontmatter")).catch(() => 0);
  const prunedEmptyDirs = await pruneEmptyDirs(path.join(distRoot, "pages")).catch(() => 0);

  const allPages = [...keepPagesRel]
    .map((rel) => normalizeSlashes(path.join("pages", rel)))
    .sort((a, b) => a.localeCompare(b));

  const corePages = pickCorePages(allPages);

  const llmsText = renderLlmsTxt(corePages);
  await writeTextIfChanged(llmsAbs, llmsText);
  const llmsFullText = renderLlmsFullTxt(corePages);
  await writeTextIfChanged(llmsFullAbs, llmsFullText);

  const atlasText = renderAtlas({
    openclawGitHead,
    openclawGitDescribe,
    includeI18n: args.includeI18n,
  });
  await writeTextIfChanged(atlasAbs, atlasText);

  /** @type {any} */
  let docsJson = null;
  if (fs.existsSync(docsJsonAbs)) {
    try {
      docsJson = JSON.parse(await readFile(docsJsonAbs, "utf8"));
    } catch {
      docsJson = null;
    }
  }
  const navTabs =
    docsJson?.navigation?.languages?.find?.((l) => l?.language === "en")?.tabs ??
    docsJson?.navigation?.languages?.[0]?.tabs ??
    [];

  const atlasFullText = renderAtlasFull({
    openclawGitHead,
    openclawGitDescribe,
    includeI18n: args.includeI18n,
    navTabs,
    allPages,
  });
  await writeTextIfChanged(atlasFullAbs, atlasFullText);

  const pagesMeta = {
    openclaw: { gitHead: openclawGitHead, gitDescribe: openclawGitDescribe },
    pages: files
      .map((f) => ({
        outputPath: f.outputPath,
        sourcePath: f.sourcePath,
        canonicalUrl: f.canonicalUrl ?? null,
        title: f.title ?? null,
        summary: f.summary ?? null,
        frontmatterPath: f.frontmatterPath ?? null,
      }))
      .sort((a, b) => a.outputPath.localeCompare(b.outputPath)),
  };
  await writeTextIfChanged(pagesMetaAbs, JSON.stringify(pagesMeta, null, 2) + "\n");

  const configIndexText = renderIndexMarkdown(configKeyIndex, {
    title: "Config key index",
    description:
      "Extracted from backticked dotted tokens in `pages/**` and filtered to common OpenClaw config roots. Open the referenced page for full context.",
  });
  await writeTextIfChanged(indexConfigAbs, configIndexText);

  const cliIndexText = renderIndexMarkdown(cliCommandIndex, {
    title: "CLI command index",
    description:
      "Extracted from lines that start with `openclaw ...` in `pages/**`. Listed by top-level command. Open the referenced page for full context.",
  });
  await writeTextIfChanged(indexCliAbs, cliIndexText);

  const coreParts = await buildBundleParts({
    distRoot,
    prefix: "core",
    pageRelPaths: corePages,
    maxChars: args.maxCharsPerPart,
  });

  const fullParts = await buildBundleParts({
    distRoot,
    prefix: "full",
    pageRelPaths: allPages,
    maxChars: args.maxCharsPerPart,
  });

  const manifest = {
    tool: { name: "openclaw-docs-capsule", version: AI_PACK_VERSION },
    maxCharsPerPart: args.maxCharsPerPart,
    openclaw: {
      gitHead: openclawGitHead,
      gitDescribe: openclawGitDescribe,
    },
    inputs: {
      docsRoot: "openclaw/docs",
      changelog: hasChangelog ? "openclaw/CHANGELOG.md" : null,
      includeI18n: args.includeI18n,
    },
    files: files.sort((a, b) => a.sourcePath.localeCompare(b.sourcePath)),
    ctx: {
      coreParts,
      fullParts,
    },
    meta: {
      pages: "meta/pages.json",
      frontmatterRoot: "meta/frontmatter",
    },
  };

  await writeTextIfChanged(manifestAbs, JSON.stringify(manifest, null, 2) + "\n");

  // Delta (only when OpenClaw git head changed and we can compute a range).
  const prevHead = prevManifest?.openclaw?.gitHead ?? null;
  const nextHead = openclawGitHead ?? null;
  let deltaPath = null;
  /** @type {{ added: string[]; modified: string[]; deleted: string[]; otherChangedPaths: string[] } | null} */
  let changedSources = null;

  if (prevHead && nextHead && prevHead !== nextHead) {
    const stamp = formatDateYYYYMMDD(new Date());
    deltaPath = normalizeSlashes(path.join("delta", `delta-${stamp}.md`));
    const abs = path.join(distRoot, deltaPath);

    let nameStatus = null;
    const nonTextChanges = [];

    try {
      const raw = git(["diff", "--name-status", `${prevHead}..${nextHead}`, "--", "docs", "CHANGELOG.md"], openclawRoot);
      nameStatus = parseNameStatus(raw);
    } catch {
      nameStatus = null;
    }

    /** @type {string[]} */
    const added = [];
    /** @type {string[]} */
    const modified = [];
    /** @type {string[]} */
    const deleted = [];

    if (nameStatus) {
      for (const entry of nameStatus) {
        const status = entry.status;
        const paths = entry.paths;

        // Rename/copy include 2 paths.
        const primary = paths[paths.length - 1];
        if (!primary) {
          continue;
        }
        if (!isMarkdownPath(primary) && primary !== "CHANGELOG.md") {
          nonTextChanges.push(primary);
          continue;
        }

        const sp = toSourcePath(primary);
        if (status.startsWith("A") || status.startsWith("C")) {
          added.push(sp);
        } else if (status.startsWith("D")) {
          deleted.push(sp);
        } else if (status.startsWith("R")) {
          // Treat as delete+add for simplicity.
          const oldPath = paths[0];
          if (oldPath && isMarkdownPath(oldPath)) {
            deleted.push(toSourcePath(oldPath));
          }
          added.push(sp);
        } else {
          modified.push(sp);
        }
      }
    } else {
      // Fallback: hash compare previous manifest entries.
      const prevBySource = new Map();
      for (const entry of prevManifest?.files || []) {
        if (entry?.sourcePath && entry?.sourceSha256) {
          prevBySource.set(String(entry.sourcePath), String(entry.sourceSha256));
        }
      }

      for (const entry of files) {
        const prev = prevBySource.get(entry.sourcePath);
        if (!prev) {
          added.push(entry.sourcePath);
          continue;
        }
        if (prev !== entry.sourceSha256) {
          modified.push(entry.sourcePath);
        }
        prevBySource.delete(entry.sourcePath);
      }

      for (const sourcePath of [...prevBySource.keys()]) {
        deleted.push(sourcePath);
      }
    }

    added.sort((a, b) => a.localeCompare(b));
    modified.sort((a, b) => a.localeCompare(b));
    deleted.sort((a, b) => a.localeCompare(b));

    changedSources = {
      added,
      modified,
      deleted,
      otherChangedPaths: nonTextChanges.map((p) => `openclaw/${p}`),
    };

    const lines = [];
    lines.push(`# OpenClaw Docs LLM Pack Delta (${stamp})`);
    lines.push("");
    lines.push(`OpenClaw: ${prevHead}..${nextHead}`);
    lines.push("");

    if (nameStatus) {
      lines.push("Changed paths (git diff --name-status; markdown only):");
      lines.push("");
      if (!added.length && !modified.length && !deleted.length) {
        lines.push("- (no markdown changes detected)");
      } else {
        for (const p of [...added, ...modified, ...deleted]) {
          lines.push(`- ${p}`);
        }
      }
      if (nonTextChanges.length) {
        lines.push("");
        lines.push("Other changed paths (non-markdown; omitted from pages):");
        for (const p of nonTextChanges) {
          lines.push(`- openclaw/${p}`);
        }
      }
    } else {
      lines.push("Changed sources (hash compare; git diff unavailable):");
      lines.push("");
      for (const p of [...added, ...modified, ...deleted]) {
        lines.push(`- ${p}`);
      }
    }

    const changed = [...added, ...modified].sort((a, b) => a.localeCompare(b));
    for (const sourcePath of changed) {
      const pagesRel = sourcePathToPagesRel(sourcePath);
      if (!pagesRel) {
        continue;
      }
      const pageAbs = path.join(distRoot, pagesRel);
      if (!fs.existsSync(pageAbs)) {
        continue;
      }
      const content = await readFile(pageAbs, "utf8");
      lines.push("");
      lines.push(`## ${sourcePath}`);
      lines.push("");
      lines.push(content.trimEnd());
    }

    for (const sourcePath of deleted) {
      lines.push("");
      lines.push(`## ${sourcePath}`);
      lines.push("");
      lines.push("_DELETED_");
    }

    await writeTextIfChanged(abs, lines.join("\n").trimEnd() + "\n");
  }

  console.log(
    JSON.stringify(
      {
        openclaw: { gitHead: openclawGitHead, gitDescribe: openclawGitDescribe },
        distRoot: normalizeSlashes(path.relative(workspaceRoot, distRoot)) || ".",
        pages: { total: keepPagesRel.size, wrote: wrotePages, pruned: prunedPages, prunedEmptyDirs },
        extra: { total: keepExtraRel.size, pruned: prunedExtraFiles },
        meta: { pages: "meta/pages.json", frontmatter: { wrote: wroteFrontmatter, pruned: prunedFrontmatter } },
        ctx: { coreParts: coreParts.length, fullParts: fullParts.length },
        delta: deltaPath,
        changedSources,
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
