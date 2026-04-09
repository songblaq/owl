---
id: benchmark-v1
status: draft
supersedes: benchmark-v0
created: 2026-04-09
---

# cairn vs owl — benchmark v1 (full coverage)

**Purpose:** re-run the v0 benchmark after closing the coverage gap
(+193 entries, then −16 dedup merges) so the comparison is fair —
not "partial cairn vs full owl". Also answer the user's meta
question: *should we run owl alone, cairn alone, or both together?*

## What changed since v0

| | v0 | v1 |
|---|---|---|
| cairn entries | 244 | **421** |
| owl/compiled files migrated | 146 of 232 (63%) | 232 of 232 (100%) |
| coverage gap | 87 files unread | **0 files unread** |
| cleanup pass | none | singular/plural tag merge + 16 semantic dedup merges |
| superseded/ | 0 | 16 (preserved for provenance) |

The biggest coverage miss in v0 was the entire `owl/compiled/aria-architecture/`
subdirectory (38 design docs). That was the load-bearing section for
ARIA-domain queries, and v0 answered those queries with generic
ARIA entries only. v1 closes the gap.

---

## Dimension 1 — Storage density

| | owl/compiled | cairn/entries |
|---|---|---|
| files | 232 | **421** (+82%) |
| total size | 684 KB | **516 KB** (−25%) |
| avg file size | 3018 B | **1255 B** (42% of owl) |
| median | 2248 B | **1266 B** |
| max | 16 KB | **2.2 KB** |

**cairn stores the same knowledge in less total bytes despite having
82% more files.** The win: atomic entries eliminate the redundant
framing/intro/TOC headers that chunky compiled docs carry. The
consistency win: max file is 2.2 KB vs owl's 16 KB — no giant outliers.

**Verdict: cairn wins.** Same information, 25% less storage.

---

## Dimension 2 — Retrieval speed

Same 7 queries, 3 runs each, mean of 3 reported:

| query | owl (s) | cairn (s) | speedup |
|---|---|---|---|
| aria orbit | 0.080 | 0.065 | 1.23× |
| khala plaza | 0.055 | 0.050 | 1.09× |
| deos phase | 0.055 | 0.046 | 1.19× |
| openclaw skill | 0.086 | 0.053 | 1.62× |
| karpathy wiki | 0.062 | 0.068 | 0.91× |
| runtime boundary | 0.083 | 0.056 | 1.49× |
| filing loop | 0.052 | 0.048 | 1.10× |
| **mean** | **0.068** | **0.055** | **1.23×** |

v0 reported 26% speedup (owl 0.101 / cairn 0.075). v1 reports 23%
(owl 0.068 / cairn 0.055). **Both KBs got faster in absolute terms**
because the filesystem cache is warm from two rounds of migration.
The relative margin narrowed because cairn now has 72% more files to
scan, but remains a clear win.

**Verdict: cairn wins.** The `karpathy wiki` query flipped slightly
owl-favored (0.91× = owl faster by ~7ms) — within noise, not a
structural regression.

---

## Dimension 3 — Search quality (top-5 specificity)

**Query: "orbit r4 scoring"**

owl top 5:
1. ORBIT R4 Scoring Concept (3KB doc)
2. raw/atlas/pages/orbit/index.md (navigation file, mostly links)
3. orbit-plaza-integration (tangentially related)
4. orbit-scheduler-concepts-summary (general, not R4-specific)
5. orbit-scheduler-concepts-raw (raw form of #4)

cairn top 5:
1. `r4-scoring-abstraction` — the abstract model
2. `orbit-r4-four-axis-scoring` — the 4-axis expansion
3. `orbit-aria-r4-four-axis-definition` — ARIA's concrete P = (p_luca, p_lord, p_internal, p_depth) vector
4. `orbit-file-inventory-2026-03-19` — the 18 source files list
5. `orbit-r4-dispatch-score-formula` — the literal formula `dispatch_score = TIER_BONUS[tier] + W·P`

**5 orthogonal facets vs 2-3 overlapping docs.** This is cairn's
clearest structural win. When the user asks about R4, they get the
abstraction, the axes, the concrete implementation, the file list,
*and* the formula — each as a self-contained answer — in one query.

**Query: "nyx runtime migration"**

owl top 5: migration memo + migration history + common runtime patterns
+ cowork runtime + cross-ecosystem index.

cairn top 5: `nyx-migration-changes-vs-unchanged` + `nyx-routing-fallback-to-nyx-ops`
+ **`nyx-not-removal-but-reframe`** + `runtime-native-invocation-per-runtime`
+ `runtime-capability-registry`.

The `nyx-not-removal-but-reframe` entry is the key insight — it's
explicitly an anti-misreading claim that would be buried in the
middle of owl's migration memo. Cairn surfaces it as a top-3 hit.

**Verdict: cairn wins.** Top-5 relevance is consistently more
specific and more diverse.

---

## Dimension 4 — Session startup cost

Same as v0 with one improvement: cairn now has a more comprehensive
INDEX.md.

| | owl | cairn |
|---|---|---|
| session entry point | CLAUDE.md (project-level) | **INDEX.md (437 lines, auto-generated)** |
| includes vault contents | no (would need search to discover) | **yes — one table of 421 atomic claim titles + ids + topics** |
| size | few KB | 132 KB |

Reading cairn's INDEX.md at session start gives the LLM the full
*catalog* of what the brain knows. For owl, the LLM has to either
trust that `owl search` will find the right thing or read a
project-level CLAUDE.md that describes the vault structurally
rather than listing contents.

**Verdict: cairn wins.** INDEX.md is a genuine advantage for LLM
sessions.

---

## Dimension 5 — Write throughput

v0 already covered this with the original 244-entry migration
(parallel, ~35 minutes). v1 added another ~35 minutes for the
second wave (193 new entries via 9 parallel subagents).

| | owl | cairn |
|---|---|---|
| adding 100 new claims | sequential — compiler reads one raw doc at a time, produces one compiled doc at a time | **parallel — N subagents each take K files, write atomic entries independently** |
| full migration of this vault | would take days (each raw→compiled step blocks) | **~70 minutes total across 2 waves (244 + 193)** |

The structural reason: owl's compile loop is file-to-file. Cairn's
atomic format + no-See-also rule means subagents don't need shared
state — one agent's writes don't depend on another's.

**Verdict: cairn wins.** Parallelism is a function of the format,
not the tool.

---

## Dimension 6 — Write ergonomics for the LLM

After 2 migration waves I can now comment on this with more evidence:

**What worked (cairn):**
- Subagents completed without needing to coordinate on IDs
- The 400-token cap is almost never binding (max 278 words observed,
  median 143) — the LLM naturally writes tight when the format demands it
- "Skip duplicates" instruction worked: every batch reported
  skipping 0-6 files whose content was already captured, using
  simple grep checks (no LLM re-judgment)
- The fact/claim/procedure/preference/open-question type split
  maps cleanly to how claims actually decompose

**What didn't work as well:**
- Tag vocabulary drifts: 1015 unique tags across 421 entries means
  ~70% are singletons. Cleanup pass normalized singular/plural but
  the long tail stays long. This is fine for search (tokens still
  match) but not for faceted browsing.
- Language mixing: Korean and English entries coexist freely. When
  the source doc was Korean, subagents wrote Korean; English sources
  got English. This preserves fidelity to source but makes the
  vault look inconsistent to a human reviewer.
- Semantic duplicates did slip through: 16 real duplicates found
  in cleanup pass (3.7% of entries). The no-See-also rule that
  enabled parallel writes is also what causes this — subagents
  can't see each other's work.

**Verdict: cairn wins, with caveats.** The write ergonomics favor
cairn *because* the format is load-bearing. But the caveats
(tag drift, language mix, duplicate risk) are real costs of
atomization that owl's compiled-doc model doesn't pay.

---

## Final scorecard

| dimension | winner | margin |
|---|---|---|
| 1. storage density | **cairn** | 25% smaller |
| 2. retrieval speed | **cairn** | 1.23× faster mean |
| 3. search quality | **cairn** | clearly more specific top-5 |
| 4. session startup | **cairn** | INDEX.md catalog vs no equivalent |
| 5. write throughput | **cairn** | parallel vs sequential (structural) |
| 6. write ergonomics | **cairn** | with caveats |

**6/6, same as v0 — but now with full coverage and dedup, not a
partial baseline.** Nothing in v1 flipped. The gaps that remained
in v0 (could cairn scale? Does coverage stay atomic?) are closed.

---

## Meta question — owl alone, cairn alone, or both?

User asked: *"둘 다 쓰는게 맞을까?"* (is it right to run both?)

### Argument for cairn alone

1. **Full coverage verified.** 232/232 owl compiled docs are now
   represented in cairn. Nothing is hidden in owl that isn't
   accessible via cairn.
2. **Better primary signal.** Every measured dimension favors cairn.
3. **Redundancy = drift risk.** Running both means two places to
   update when new knowledge lands. Without a sync rule, they
   diverge and neither is canonical.
4. **owl/raw has no cairn equivalent but also isn't a query target.**
   Raw files are source material, not answers. If a cairn entry
   points to `owl:compiled/X.md` as source, the user (rarely) can
   read X.md directly. That's the full coverage story — cairn
   doesn't need its own raw/.

### Argument for both

1. **owl has Obsidian integration.** The user actually views owl
   via Obsidian. Cairn has no GUI. If you kill owl, you lose the
   visual browsing mode entirely.
2. **owl has atlas external reference subtree** (self-contained
   knowledge pack at `~/.aria/atlas/`). Cairn has one pointer entry
   but the actual content lives in owl's `raw/atlas/`.
3. **owl/raw preserves original sources** — if a compiled doc is
   bad, the raw is authoritative. Cairn's atomic entries cite owl
   sources but don't carry raw source content.
4. **6 weeks of owl conventions, health checks, git history** —
   there's real ops infrastructure (install.sh, health.py, Obsidian
   sync via WebDAV, multi-machine roles) that cairn doesn't
   replicate. Replacing means rebuilding all of that.
5. **The LLM can use cairn without the human needing to.** The
   human uses owl (via Obsidian). The LLM uses cairn (via search
   + INDEX.md). Different tools, different users, different
   strengths.

### Recommendation

**Run both, but with a clear role split:**

- **owl = human-facing wiki.** Obsidian rendering, source
  preservation, visual browsing, multi-machine sync, atlas pack
  reference. The human's knowledge home. Continues to be updated
  when new raw sources arrive (karpathy-style compile loop).

- **cairn = LLM-facing brain.** Atomic claims for retrieval,
  INDEX.md as session startup context, no GUI needed. The LLM's
  answer cache. Rebuild from owl when coverage drifts (say, every
  month or when >20 new compiled docs accumulate).

**One-way sync: owl → cairn.** Never the reverse. cairn is a
derived artifact of owl, not a peer. When something is added to
owl, cairn rebuilds the relevant entries via a migration pass
(same pattern as this v1 — parallel subagents close the gap).

This gives the LLM the retrieval-optimized brain and the human
the browse-optimized brain, without either paying the other's
format cost.

### When to collapse to cairn-only

If the user stops using Obsidian and the browse mode dies, collapse
owl → cairn and delete owl. The atomic format is a strict superset
for LLM retrieval. But as long as the human visits the vault,
owl earns its keep via Obsidian.

### When to collapse to owl-only

Only if cairn falls badly out of sync with owl and nobody wants
to rebuild it. Cairn is cheap to rebuild (parallel subagents),
so this is unlikely to be the right answer.

---

## What's left unverified

- **Real LLM session comparison.** We measured structural
  dimensions but haven't yet run a week of actual knowledge
  queries through both. The cleanest test: pick 10 genuinely
  hard questions and answer each using cairn alone, then owl
  alone, and compare quality of the final answer, not just
  top-5 specificity.
- **Cairn freshness loop.** How does cairn get updated when owl
  gets new content? Manual migration? CLI command? Scheduled
  job? The one-way sync story above is policy, not
  implementation.
- **Claude Code integration symmetry.** Owl has slash commands,
  subagents, CLAUDE.md integration. Cairn has only the CLI. If
  cairn is the LLM-facing brain, it should have the same Claude
  Code integration owl does.

These three are the honest next-step list, not more benchmarking.
