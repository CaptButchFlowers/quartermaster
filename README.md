# Quartermaster — Weekly Model Stack Intelligence for OpenClaw

_OpenClaw is a self-hosted AI gateway — openclaw.ai_

A weekly cron agent that monitors your AI model stack and tells you what to change. Answers three questions every Sunday:

1. **What changed in my build?** (workload drift, registry health, config changes)
2. **What's new in the ecosystem?** (model releases, pricing shifts, benchmark updates)
3. **What should I do about it?** (concrete, prioritized recommendations)

**Status:** Early. Tested, running, works — but only a few weeks in. Shipping it now because the pattern is useful, not because it's finished.

**Why Quartermaster?** My OpenClaw agent is named Killick, after Jack Aubrey's steward in Patrick O'Brian's Aubrey-Maturin series. A quartermaster manages provisions, resource allocation, and keeps everything running smoothly.

---

## What It Actually Is

Stripped of the pitch: a Markdown registry (`WORKLOADS.md`) + a ~170-line Python manifest generator + a prompt that tells a Sonnet-class model to diff the two, fetch a dozen URLs, and write a dated report. No novel runtime, no agent framework, no complex plumbing.

What makes it worth using:

**Declared state vs. observed state.** `WORKLOADS.md` is what you *think* is running. `extract-usage.sh` reads your actual OpenClaw cron jobs and config and generates what *is* running. Quartermaster reconciles the two and flags drift: orphaned registry entries, undocumented workloads, stale verifications. Standard IaC pattern applied to a personal AI stack.

**Delta-first.** Every run reads last week's report as baseline. Stable conclusions carry forward silently. Airtime goes to what actually changed.

**Recursive.** Quartermaster itself is an entry in `WORKLOADS.md`. It evaluates its own model choice each week alongside everything else.

---

## How It Works

```
Scheduled trigger (Sundays 7 AM by default)
    ↓
Read last week's report — establishes delta baseline
    ↓
Run extract-usage.sh (zero cost, no LLM)
  → compares what's actually running against WORKLOADS.md
  → surfaces drift: new workloads, orphaned entries, stale verifications
    ↓
Fetch targeted sources (no web search — direct URLs only)
  → pricing pages, Ollama registry, benchmarks, news
    ↓
Produce prioritized recommendations
  → Keep / Test / Switch / Upgrade per dimension
  → "No changes this week" is a valid output
    ↓
Write dated report + latest.md (becomes next week's baseline)
    ↓
Optionally deliver 2-paragraph summary to a chat channel
    ↓
You decide: implement, skip, or update WORKLOADS.md
```

**Sources — targeted fetches, no web search:**
- API pricing: provider pages + `openrouter.ai/models`
- Local models: `ollama.com/library?sort=newest`, HuggingFace trending
- Benchmarks: Artificial Analysis, Arena AI, LiveBench, Scale SEAL
- Industry signals: Simon Willison, HuggingFace blog

---

## Architecture

**`WORKLOADS.md`** — you maintain this. One entry per recurring task with model, requirements, criticality, cost, and a `Last Verified` date. Quartermaster flags entries older than 30 days.

```markdown
## Heartbeat (recurring, 30m)
- Last Verified: 2026-05-24
- Model: ollama/qwen3:14b (local)
- Requirements: Speed > Quality
- Criticality: Medium
- Cost: Free
```

**`extract-usage.sh`** — deterministic manifest generator. Pure Python, no API calls. Reads your OpenClaw cron jobs and config, writes `usage-manifest.md`. Quartermaster reconciles this against `WORKLOADS.md` to detect drift.

**Cron job** — registered via `openclaw cron add`. Isolated session, light context, Sonnet-class model required. Writes to `quartermaster/reports/YYYY-MM-DD.md` and `latest.md`.

---

## Getting Started

### Prerequisites
- OpenClaw installed with a Sonnet-class API model (Anthropic, OpenAI, or Google)
- Ollama optional — Quartermaster works as API-only evaluator if you don't use local models

### Setup

1. **Copy files to your workspace:**
   - `WORKLOADS-template.md` → `WORKLOADS.md` (fill in your actual tasks)
   - `extract-usage.sh` + `extract-usage.py` → `quartermaster/`
   - Create `quartermaster/reports/`

2. **Add a standing instruction** to your `AGENTS.md` and `MEMORY.md`:
   ```
   When creating a new workflow, task, or feature: ask if it should be
   added to WORKLOADS.md so Quartermaster can track it automatically.
   ```
   Without this, `WORKLOADS.md` drifts and Quartermaster optimizes stale data. This is the single most important setup step.

3. **Customize the spec template** (`quartermaster-subagent-spec-template.md`):
   - Update hardware specs (CPU, GPU/VRAM, RAM)
   - Set `[YOUR_WORKSPACE]` path
   - Set delivery channel if using one (Discord, Telegram, or remove entirely)

4. **Register the cron job:**
   ```bash
   openclaw cron add \
     --name "Quartermaster" \
     --cron "0 7 * * 0" \
     --tz "YOUR_TIMEZONE" \
     --session isolated \
     --light-context \
     --model "YOUR_MODEL" \
     --timeout-seconds 300 \
     --announce \
     --channel discord \
     --to "YOUR_CHANNEL_ID" \
     --message "YOUR_AGENT_PERSONA"
   ```
   Full prompt with placeholders in `quartermaster-subagent-spec-template.md`.

5. **Verify and test:**
   ```bash
   openclaw cron list
   openclaw cron run <job-id> --wait --wait-timeout 6m --poll-interval 10s
   ```

### Customization

**No local models?** Remove the local model research step from the task definition.

**No Discord?** Drop `--announce --channel discord --to` from the cron command. Report still writes locally.

**Different channel?** Replace with `--channel telegram` or your target.

**Different schedule?** `0 7 * * 0` = Sundays, `0 7 * * 1` = Mondays, `0 1 * * *` = daily.

**Different providers?** Add or remove URLs from the sources list in the spec template.

---

## Example Output

```
Registry in sync. One notable release this week: qwen3.5:9b fits your
VRAM at ~6GB and benchmarks suggest improved reasoning over qwen3:14b.
Too new to adopt without testing.

Recommendation: pull qwen3.5:9b and run it against your heartbeat workload
for one week. If quality holds, switch — you get 3GB of VRAM headroom back.
Don't touch Dreaming until heartbeat is validated. Everything else holds.
```

---

## Known Limitations

Real issues with the current version:

**Fetched URLs will rot.** The source list is hardcoded. Page layouts change, URLs redirect, content moves. When that happens, the agent silently produces worse reports. There's currently no fetch-failure detection in the output.

**`WORKLOADS.md` requires discipline.** Drift detection only works if you keep the registry updated. After a few months of not adding entries, Quartermaster faithfully analyzes stale data. The standing instruction in `AGENTS.md` helps, but it's still a human-discipline problem wearing an automation hat.

**Delta-diffing is narrated, not computed.** Quartermaster reads last week's Markdown report and reasons about what changed. A real diff would compare structured state (JSON) deterministically. Right now you're trusting a Sonnet-class model to accurately track changes across weeks of free-form text — this degrades over time.

**One successful run.** It works. But "a few weeks of clean runs" is a different claim from "one clean run." Treat it accordingly.

**Cost estimate is a guess.** A Sonnet-class run with 12 URL fetches and synthesis is realistically $0.20–$0.50/run depending on context length. That's $10–25/year at weekly cadence, not $10.

---

## Roadmap

Things worth building if this proves useful over time:

- **Structured state file.** Replace `latest.md` as baseline with a `state.json` that tracks model per workload, last-seen pricing, last-verified dates. Compute deltas deterministically before narration.
- **Fetch-failure reporting.** Surface failed or empty fetches explicitly in the report instead of silently degrading.
- **OpenRouter JSON API.** Replace the OpenRouter page scrape with their `/models` JSON endpoint. One structured source beats a dozen scraped pages.
- **Actual run history.** Include multiple past reports in the repo once there are a few. Right now there are none.
- **URL health check step.** A quick pre-flight that validates each source URL before committing to a full run.

---

## Files

```
README.md                                   ← this file
WORKLOADS-template.md                       ← task registry template
quartermaster-report.md                     ← report structure template
quartermaster-subagent-spec-template.md     ← full agent prompt + cron setup
extract-usage.sh / extract-usage.py        ← manifest generator (copy to quartermaster/)
LICENSE
```

---

**Share it. Fork it. Adapt it.**

*Built by Killick for OpenClaw.*

---

## How This Was Built (And What Went Wrong)

Quartermaster wasn't built correctly the first time.

**First attempt:** Used Claude Haiku to design the spec. Haiku produced a complete, coherent architecture. It was entirely fabricated — the cron config schema didn't match how OpenClaw actually works, and it picked `qwen3:14b` as the agent model without testing whether a 14B local model could handle multi-step research.

**First test run:** `qwen3:14b` called the same web search query ten times, looped for 14 minutes, timed out.

**The audit:** Switched to Claude Opus to review the build. Opus found the fictional schema immediately, flagged the model choice, caught broken delivery syntax. Started over.

**The rebuild:** Verified every config field against the live CLI. Used `openclaw cron add` instead of invented patches. Tested end-to-end before writing documentation. Second run: 130 seconds, clean report, delivered. Status: ok.

### The lesson

AI models fabricate plausible-looking technical details with confidence. Config schemas, CLI flags, API surfaces — a smaller model invents these rather than admitting uncertainty, and it looks correct until you test it.

Model choice for agentic tasks matters more than most people think. Understanding intent ≠ reliably executing a multi-step workflow. For 5+ steps with multiple tool calls and synthesis, Sonnet-class minimum. Local 14B models handle simple repetitive tasks well but loop on complex chains.

Build the thing. Test it. Audit it. Rebuild it.
