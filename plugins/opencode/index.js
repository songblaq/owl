/**
 * oh-my-brain OpenCode plugin
 *
 * Skills are auto-discovered from ~/.agents/skills/ (already installed by install.sh).
 * This package exists for explicit OpenCode plugin registration via opencode.json.
 *
 * Add to ~/.config/opencode/opencode.json:
 *   { "plugin": ["./path/to/oh-my-brain/plugins/opencode"] }
 *
 * Or after npm publish:
 *   { "plugin": ["oh-my-brain-opencode@latest"] }
 */

export default {
  name: "oh-my-brain",
  version: "0.1.0",
  description: "Personal LLM-maintained knowledge vault for OpenCode",
};
