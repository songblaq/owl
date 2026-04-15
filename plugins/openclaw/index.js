import { execSync } from "child_process";

/**
 * oh-my-brain OpenClaw plugin
 *
 * Registers omb CLI tools into the OpenClaw runtime.
 * Each tool wraps the corresponding `omb` subcommand.
 *
 * Install:
 *   openclaw plugins install /path/to/oh-my-brain/plugins/openclaw
 */

function runOmb(args) {
  try {
    const result = execSync(`omb ${args}`, {
      encoding: "utf8",
      timeout: 30000,
    });
    return { success: true, output: result.trim() };
  } catch (err) {
    return {
      success: false,
      output: err.stdout?.trim() || "",
      error: err.stderr?.trim() || err.message,
    };
  }
}

export function register(api) {
  // ── omb-search ───────────────────────────────────────────────────────────────
  api.registerTool({
    name: "omb-search",
    label: "OMB: Search knowledge vault",
    description:
      "Search the oh-my-brain knowledge vault using 3-layer search (compiled narratives + atomic entries + graph expansion). Run this before answering knowledge questions.",
    parameters: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query",
        },
        limit: {
          type: "number",
          description: "Max results to return (default 10)",
          default: 10,
        },
      },
      required: ["query"],
    },
    execute: async ({ query, limit = 10 }) => {
      const r = runOmb(`search "${query}" --limit ${limit}`);
      return r.success ? r.output : `Error: ${r.error}\n${r.output}`;
    },
  });

  // ── omb-ingest ───────────────────────────────────────────────────────────────
  api.registerTool({
    name: "omb-ingest",
    label: "OMB: Ingest knowledge",
    description:
      "Add a file or raw text into the oh-my-brain knowledge vault, then rebuild the index.",
    parameters: {
      type: "object",
      properties: {
        file: {
          type: "string",
          description: "Path to file to ingest (mutually exclusive with text)",
        },
        text: {
          type: "string",
          description: "Raw text to ingest (mutually exclusive with file)",
        },
      },
    },
    execute: async ({ file, text }) => {
      if (file) {
        const r = runOmb(`ingest "${file}"`);
        return r.success ? r.output : `Error: ${r.error}`;
      } else if (text) {
        const r = runOmb(`ingest --text "${text.replace(/"/g, '\\"')}"`);
        return r.success ? r.output : `Error: ${r.error}`;
      }
      return "Error: provide either file or text";
    },
  });

  // ── omb-health ───────────────────────────────────────────────────────────────
  api.registerTool({
    name: "omb-health",
    label: "OMB: Vault health check",
    description:
      "Check vault health — source coverage, missing compilations, stale entries. Returns a coverage report.",
    parameters: {
      type: "object",
      properties: {
        json: {
          type: "boolean",
          description: "Return JSON output",
          default: false,
        },
      },
    },
    execute: async ({ json = false }) => {
      const r = runOmb(json ? "health --json" : "health");
      return r.success ? r.output : `Error: ${r.error}`;
    },
  });

  // ── omb-status ───────────────────────────────────────────────────────────────
  api.registerTool({
    name: "omb-status",
    label: "OMB: Vault overview",
    description:
      "Show vault overview — entry count, compiled count, graph size, last updated.",
    parameters: {
      type: "object",
      properties: {},
    },
    execute: async () => {
      const r = runOmb("status");
      return r.success ? r.output : `Error: ${r.error}`;
    },
  });
}
