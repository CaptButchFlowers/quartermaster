# Quartermaster — Autonomous Infrastructure Intelligence for OpenClaw

A weekly agent that monitors your AI model stack and tells you what to change. Runs every Sunday. Costs ~$10/year.

**The problem:** New models drop weekly. Prices shift monthly. Your workloads evolve. Nobody manually checks — it's tedious and the opportunity cost is real. Quartermaster does it instead.

**Three questions, answered every week:**
1. **What changed in my build?** (workload drift, registry health, config changes)
2. **What's new in the ecosystem?** (model releases, pricing shifts, benchmark updates)
3. **What should I do about it?** (concrete, prioritized recommendations)

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
Optionally deliver summary to a chat channel
    ↓
You decide: implement, skip, or update WORKLOADS.md
```

Delta-first: stable conclusions carry forward silently. Airtime goes to what actually changed.

**The recursive loop:** Add a new workload to `WORKLOADS.md` → Quartermaster evaluates it next Sunday, no code changes. Quartermaster itself is an entry in `WORKLOADS.md` — it evaluates its own model choice each week like everything else.

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

**`extract-usage.sh`** — deterministic manifest generator. Pure Python, no API calls. Reads your OpenClaw cron jobs and config, writes `usage-manifest.md` (what's actually running). Quartermaster reconciles this against `WORKLOADS.md` to detect drift.

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
   Without this, WORKLOADS.md drifts and Quartermaster optimizes stale data.

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
   openclaw cron run <job-id> --wait --wait-timeout 6m
   ```

### Customization

**No local models?** Remove the local model research step from the task definition.

**No Discord?** Drop `--announce --channel discord --to` from the cron command. Report still writes locally.

**Different channel?** Replace with `--channel telegram` or your target. OpenClaw supports multiple providers.

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

## Files

```
README.md                          ← this file
WORKLOADS-template.md              ← task registry template
quartermaster-report.md            ← report structure template
quartermaster-subagent-spec-template.md  ← full agent prompt + cron setup
extract-usage.sh / extract-usage.py     ← manifest generator (copy to quartermaster/)
LICENSE
```

---

**Share it. Fork it. Adapt it.**

*Built by Killick for OpenClaw. Named after Jack Aubrey's steward — because quartermaster means resource optimization.*

---

## How This Was Built (And What Went Wrong)

Quartermaster wasn't built correctly the first time.

**First attempt:** Used Claude Haiku to design the spec. Haiku produced a complete, coherent architecture. It was entirely fabricated — the cron config schema didn't match how OpenClaw actually works, and it picked `qwen3:14b` as the agent model without testing whether a 14B local model could handle multi-step research.

**First test run:** qwen3:14b called the same web search query ten times, looped for 14 minutes, timed out.

**The audit:** Switched to Claude Opus to review the build. Opus found the fictional schema immediately, flagged the model choice, caught broken delivery syntax. Started over.

**The rebuild:** Verified every config field against the live CLI. Used `openclaw cron add` instead of invented patches. Tested end-to-end before writing documentation. Second run: 130 seconds, clean report, delivered. Status: ok.

### The lesson

AI models fabricate plausible-looking technical details with confidence. Config schemas, CLI flags, API surfaces — a smaller model invents these rather than admitting uncertainty, and it looks correct until you test it.

Model choice for agentic tasks matters more than most people think. Understanding intent ≠ reliably executing a multi-step workflow. For 5+ steps with multiple tool calls and synthesis, Sonnet-class minimum. Local 14B models handle simple repetitive tasks well but loop on complex chains.

Build the thing. Test it. Audit it. Rebuild it.
