import { createHash } from "node:crypto";

export const AI_PACK_VERSION = 1;
export const DEFAULT_MAX_CHARS_PER_PART = 80_000;

export const SUPPORTED_MDX_TAGS = new Set([
  "Columns",
  "CardGroup",
  "Card",
  "Check",
  "Steps",
  "Step",
  "Tabs",
  "Tab",
  "AccordionGroup",
  "Accordion",
  "Frame",
  "Note",
  "Tip",
  "Warning",
  "Info",
  "Tooltip",
]);

export const CORE_PAGE_ORDER = [
  "pages/index.md",
  "pages/start/getting-started.md",
  "pages/start/quickstart.md",
  "pages/start/setup.md",
  "pages/start/wizard.md",
  "pages/start/hubs.md",
  "pages/gateway/index.md",
  "pages/gateway/configuration.md",
  "pages/gateway/configuration-reference.md",
  "pages/gateway/troubleshooting.md",
  "pages/channels/index.md",
  "pages/channels/pairing.md",
  "pages/channels/troubleshooting.md",
  "pages/channels/whatsapp.md",
  "pages/channels/telegram.md",
  "pages/channels/discord.md",
  "pages/channels/slack.md",
  "pages/channels/imessage.md",
  "pages/tools/index.md",
  "pages/tools/slash-commands.md",
  "pages/tools/exec.md",
  "pages/tools/exec-approvals.md",
  "pages/tools/skills.md",
];

export const CONFIG_KEY_ROOTS = new Set([
  "agents",
  "channels",
  "gateway",
  "tools",
  "hooks",
  "plugins",
  "cron",
  "logging",
  "models",
  "memory",
  "sessions",
  "messages",
  "sandbox",
  "web",
  "nodes",
  "providers",
]);

/** @param {string} p */
export function normalizeSlashes(p) {
  return p.replace(/\\/g, "/");
}

/** @param {Date} date */
export function formatDateYYYYMMDD(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** @param {string} text */
export function sha256Utf8(text) {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

/** @param {string} text */
export function bytesUtf8(text) {
  return Buffer.byteLength(text, "utf8");
}

/**
 * Extracts YAML frontmatter if present.
 * @param {string} text
 * @returns {{ frontmatter: string | null; body: string }}
 */
export function extractFrontmatter(text) {
  if (!text.startsWith("---")) {
    return { frontmatter: null, body: text };
  }
  const match = text.match(/^---\s*\r?\n([\s\S]*?)\r?\n---\s*\r?\n?/);
  if (!match) {
    return { frontmatter: null, body: text };
  }
  return {
    frontmatter: match[1].trimEnd(),
    body: text.slice(match[0].length),
  };
}

/**
 * @param {string | undefined} attrText
 * @returns {Record<string, string>}
 */
export function parseAttributes(attrText) {
  /** @type {Record<string, string>} */
  const attrs = {};
  if (!attrText) {
    return attrs;
  }

  const regex = /([A-Za-z0-9_-]+)\s*=\s*"([^"]*)"/g;
  let match;
  while ((match = regex.exec(attrText))) {
    const [, key, value] = match;
    attrs[key] = value;
  }
  return attrs;
}

/** @param {string[]} lines */
function trimBlankLines(lines) {
  let start = 0;
  while (start < lines.length && !lines[start].trim()) {
    start++;
  }
  let end = lines.length;
  while (end > start && !lines[end - 1].trim()) {
    end--;
  }
  return lines.slice(start, end);
}

/**
 * Prefix lines as a blockquote, preserving blank lines.
 * @param {string[]} lines
 */
function blockquote(lines) {
  return lines.map((line) => (line.trim() ? `> ${line}` : ">"));
}

/**
 * @param {string} label
 * @param {string[]} bodyLines
 */
function renderCallout(label, bodyLines) {
  const body = trimBlankLines(bodyLines);
  if (body.length === 0) {
    return [`> ${label}:`];
  }
  if (body.length === 1) {
    return [`> ${label}: ${body[0].trimEnd()}`];
  }
  return [`> ${label}:`, ...blockquote(body)];
}

/** @param {string[]} lines */
function indent(lines, prefix) {
  return lines.map((line) => (line.length ? `${prefix}${line}` : line));
}

/**
 * Best-effort canonical URL mapping for docs pages.
 * @param {string} relFromDocs
 */
export function canonicalUrlForDocsPath(relFromDocs) {
  const slug = normalizeSlashes(relFromDocs).replace(/\.(md|mdx)$/i, "");
  if (slug === "index") {
    return "https://hermes-agent.nousresearch.com/docs/";
  }
  if (slug.endsWith("/index")) {
    const base = slug.slice(0, -"/index".length);
    return `https://hermes-agent.nousresearch.com/docs/${base}`;
  }
  return `https://hermes-agent.nousresearch.com/docs/${slug}`;
}

/**
 * Maps a docs-relative path (like "channels/discord.md") to a pages-relative path
 * (like "pages/channels/discord.md"). Always emits ".md".
 * @param {string} relFromDocs
 */
export function docsRelToPagesRel(relFromDocs) {
  const normalized = normalizeSlashes(relFromDocs);
  const withoutExt = normalized.replace(/\.(md|mdx)$/i, "");
  return `pages/${withoutExt}.md`;
}

/**
 * Render a "pages/**" or "extra/**" file as body-only output.
 * Provenance/frontmatter is stored separately in meta/.
 * @param {{ sourcePath: string; canonicalUrl?: string; frontmatter?: string | null; body: string }} opts
 */
export function renderPageOutput(opts) {
  return opts.body.replace(/\r\n/g, "\n").trimEnd() + "\n";
}

/**
 * Convert a single-line HTML <img ... /> tag to Markdown.
 * Returns null if it doesn't look like an <img> tag we can safely convert.
 * @param {string} line
 */
function convertImgTag(line) {
  const trimmed = line.trim();
  if (!/^<img\b/i.test(trimmed)) {
    return null;
  }
  if (!/\/?>\s*$/.test(trimmed)) {
    return null;
  }
  if (!/^<img\b[^>]*\/?>\s*$/i.test(trimmed)) {
    return null;
  }
  const attrs = parseAttributes(trimmed);
  const src = attrs.src?.trim();
  if (!src) {
    return null;
  }
  const alt = attrs.alt ?? "";
  return `![${alt}](${src})`;
}

/**
 * Replace inline `<Tooltip ...>...</Tooltip>` with plain text.
 * @param {string} line
 */
function replaceInlineTooltips(line) {
  return line.replace(/<Tooltip(\s+[^>]*)?>(.*?)<\/Tooltip>/g, (_full, attrText, inner) => {
    const attrs = parseAttributes(attrText);
    const tip = attrs.tip?.trim();
    const headline = attrs.headline?.trim();
    const prefix = headline ? `${headline}: ` : "";
    if (!tip) {
      return inner;
    }
    return `${inner} (${prefix}${tip})`;
  });
}

/**
 * Convert common Mintlify/MDX layout components to plain Markdown.
 * Does not summarize; it only changes structure/markup.
 * @param {string} input
 */
export function transformMintlifyMdx(input) {
  const text = input.replace(/\r\n/g, "\n");
  const lines = text.split("\n");

  /** @type {string[]} */
  const out = [];

  /**
   * @typedef {{ tag: string; attrs: Record<string, string>; out: string[]; meta?: Record<string, unknown>; openLine: string }} Node
   */

  /** @type {Node[]} */
  const stack = [];

  /** @param {string[]} emitted */
  function emit(emitted) {
    if (!emitted.length) {
      return;
    }
    if (stack.length > 0) {
      stack[stack.length - 1].out.push(...emitted);
    } else {
      out.push(...emitted);
    }
  }

  /** @param {Node} node */
  function convertNode(node) {
    const body = trimBlankLines(node.out);

    if (
      node.tag === "Columns" ||
      node.tag === "CardGroup" ||
      node.tag === "AccordionGroup" ||
      node.tag === "Tabs"
    ) {
      return [...body, ""];
    }

    if (node.tag === "Card") {
      const title = node.attrs.title?.trim() || "Card";
      const href = node.attrs.href?.trim();
      const desc = body.join(" ").replace(/\s+/g, " ").trim();
      if (href) {
        return [`- [${title}](${href})${desc ? `: ${desc}` : ""}`];
      }
      return [`- ${title}${desc ? `: ${desc}` : ""}`];
    }

    if (node.tag === "Check") {
      return [...renderCallout("Check", body), ""];
    }

    if (node.tag === "Note" || node.tag === "Tip" || node.tag === "Warning" || node.tag === "Info") {
      return [...renderCallout(node.tag, body), ""];
    }

    if (node.tag === "Accordion") {
      const title = node.attrs.title?.trim() || "Details";
      return [`### Details: ${title}`, "", ...body, ""];
    }

    if (node.tag === "Frame") {
      const caption = node.attrs.caption?.trim();
      if (caption) {
        return [`Caption: ${caption}`, "", ...body, ""];
      }
      return [...body, ""];
    }

    if (node.tag === "Tooltip") {
      const tip = node.attrs.tip?.trim();
      const headline = node.attrs.headline?.trim();
      const prefix = headline ? `${headline}: ` : "";
      const inner = body.join(" ").replace(/\s+/g, " ").trim();
      if (!tip) {
        return [inner];
      }
      return [`${inner} (${prefix}${tip})`];
    }

    if (node.tag === "Tab") {
      const title = node.attrs.title?.trim() || "Option";
      return [`### Option: ${title}`, "", ...body, ""];
    }

    if (node.tag === "Step") {
      const title = node.attrs.title?.trim() || "Step";
      const parent = stack[stack.length - 1];
      if (parent?.tag === "Steps") {
        const current = Number(parent.meta?.stepIndex ?? 0) + 1;
        parent.meta = { ...(parent.meta || {}), stepIndex: current };
        const indentedBody = indent(body, "  ");
        return [`${current}. ${title}`, ...indentedBody, ""];
      }
      return [`### Step: ${title}`, "", ...body, ""];
    }

    if (node.tag === "Steps") {
      return [...body, ""];
    }

    return [node.openLine, ...node.out];
  }

  /**
   * @param {string} line
   */
  function fenceMarker(line) {
    const match = line.match(/^\s*(```+|~~~+)/);
    return match ? match[1] : null;
  }

  let fence = null;
  /** @type {{ lines: string[] } | null} */
  let pendingImg = null;

  for (const originalLine of lines) {
    const marker = fenceMarker(originalLine);
    if (marker) {
      if (!fence) {
        fence = marker;
      } else if (originalLine.trim().startsWith(fence)) {
        fence = null;
      }
      emit([originalLine]);
      continue;
    }

    if (fence) {
      emit([originalLine]);
      continue;
    }

    if (pendingImg) {
      pendingImg.lines.push(originalLine);
      if (originalLine.includes(">")) {
        const joined = pendingImg.lines.map((l) => l.trim()).join(" ");
        const converted = convertImgTag(joined);
        if (converted) {
          emit([converted]);
        } else {
          emit(pendingImg.lines);
        }
        pendingImg = null;
      }
      continue;
    }

    const line = replaceInlineTooltips(originalLine);
    const trimmed = line.trim();

    if (/^<img\b/i.test(trimmed) && !trimmed.includes(">")) {
      pendingImg = { lines: [trimmed] };
      continue;
    }

    const convertedImg = convertImgTag(trimmed);
    if (convertedImg) {
      emit([convertedImg]);
      continue;
    }

    const inline = trimmed.match(/^<([A-Za-z]+)(\s+[^>]*)?>(.*?)<\/\1>\s*$/);
    if (inline && SUPPORTED_MDX_TAGS.has(inline[1])) {
      const tag = inline[1];
      const attrs = parseAttributes(inline[2]);
      const inner = inline[3];

      if (tag === "Note" || tag === "Tip" || tag === "Warning" || tag === "Info") {
        emit([...renderCallout(tag, [inner]), ""]);
        continue;
      }
      if (tag === "Check") {
        emit([...renderCallout("Check", [inner]), ""]);
        continue;
      }
      if (tag === "Card") {
        const title = attrs.title?.trim() || "Card";
        const href = attrs.href?.trim();
        const desc = inner.trim();
        emit([
          href ? `- [${title}](${href})${desc ? `: ${desc}` : ""}` : `- ${title}${desc ? `: ${desc}` : ""}`,
        ]);
        continue;
      }
      if (tag === "Tooltip") {
        const tip = attrs.tip?.trim();
        const headline = attrs.headline?.trim();
        const prefix = headline ? `${headline}: ` : "";
        emit([tip ? `${inner} (${prefix}${tip})` : inner]);
        continue;
      }
    }

    const open = trimmed.match(/^<([A-Za-z]+)(\s+[^>]*)?>\s*$/);
    if (open && SUPPORTED_MDX_TAGS.has(open[1])) {
      const tag = open[1];
      const attrs = parseAttributes(open[2]);
      /** @type {Node} */
      const node = { tag, attrs, out: [], meta: undefined, openLine: line };
      if (tag === "Steps") {
        node.meta = { stepIndex: 0 };
      }
      stack.push(node);
      continue;
    }

    const close = trimmed.match(/^<\/([A-Za-z]+)>\s*$/);
    if (close && SUPPORTED_MDX_TAGS.has(close[1])) {
      const tag = close[1];
      const node = stack.pop();
      if (!node || node.tag !== tag) {
        // Best-effort: keep the raw closing tag if the nesting is unexpected.
        emit([line]);
        continue;
      }
      emit(convertNode(node));
      continue;
    }

    emit([line]);
  }

  // Best-effort flush: never drop content if tags were unbalanced.
  while (stack.length > 0) {
    const node = stack.shift();
    if (!node) {
      break;
    }
    out.push(node.openLine, ...node.out);
  }

  return out.join("\n").replace(/\n{3,}/g, "\n\n").trimEnd() + "\n";
}

/**
 * @param {string[]} allPages
 */
export function pickCorePages(allPages) {
  const set = new Set(allPages);
  return CORE_PAGE_ORDER.filter((p) => set.has(p));
}

/**
 * @param {string} value
 */
export function yamlUnquote(value) {
  const trimmed = String(value ?? "").trim();
  if (
    (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

/**
 * Extract a simple YAML scalar (single-line) from frontmatter text.
 * @param {string | null} frontmatter
 * @param {string} key
 */
export function extractYamlScalar(frontmatter, key) {
  if (!frontmatter) {
    return null;
  }
  const regex = new RegExp(`^${key}:\\s*(.+)\\s*$`, "m");
  const match = frontmatter.match(regex);
  if (!match) {
    return null;
  }
  return yamlUnquote(match[1]);
}

/**
 * Extract backticked dotted tokens like `channels.whatsapp.allowFrom`.
 * @param {string} text
 */
export function extractBacktickedDottedTokens(text) {
  const out = new Set();
  const regex = /`([a-z][a-z0-9_-]*(?:\.[a-z0-9_-]+)+)`/g;
  let match;
  while ((match = regex.exec(text))) {
    out.add(match[1]);
  }
  return [...out];
}

/**
 * Extract dotted "config-like" keys from text, limited to known top-level roots.
 * @param {string} text
 */
export function extractConfigKeys(text) {
  return extractBacktickedDottedTokens(text).filter((token) => CONFIG_KEY_ROOTS.has(token.split(".")[0]));
}

/**
 * Extract top-level Hermes CLI commands from lines like: `hermes gateway ...`
 * @param {string} text
 */
export function extractCliCommands(text) {
  const out = new Set();
  const lines = String(text ?? "").replace(/\r\n/g, "\n").split("\n");
  for (const line of lines) {
    const trimmed = line.trimStart();
    if (!trimmed.startsWith("hermes ")) {
      continue;
    }
    const parts = trimmed.split(/\s+/);
    const cmd = parts[1];
    if (!cmd) {
      continue;
    }
    // Skip "hermes@latest"-like strings that may appear in npm commands.
    if (cmd.includes("@")) {
      continue;
    }
    out.add(cmd);
  }
  return [...out];
}
