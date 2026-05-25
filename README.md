# Quartermaster — Autonomous Infrastructure Intelligence for OpenClaw

**TL;DR:** An autonomous agent that evaluates whether you're using the best models (local + API) for your actual workloads. Runs every week. Adapts as your tasks change. Zero manual intervention (I hope).

---

## The Problem

You have:
- Local models (Ollama) for background tasks
- API models (Claude, GPT, Gemini) for production work
- A growing set of workflows and tasks

But you don't have a system that:
- Tracks whether your current choices are still optimal
- Alerts you to new model releases that might save money or improve quality
- Recommends hardware upgrades when ROI is clear
- Adapts as your workloads evolve

So you either manually check the market weekly (tedious) or drift on suboptimal models (expensive).

## The Solution

**Quartermaster — an autonomous agent that wakes up once a week and asks:**
1. **Are my local models still the best?** (Ollama registry scan)
2. **Are my API models still the best?** (Anthropic, OpenAI, Google, Mistral pricing)
3. **What's my actual hardware bottleneck?** (GPU/CPU/RAM utilization)
4. **Should I upgrade?** (ROI analysis)
5. **What changed this week?** (market trends, new releases)

Then it writes a report and sends it to Discord. You read it Sunday morning, decide, implement or skip.

**Cost:** ~$0.20/run using a Sonnet-class API model at current (May 2026) prices. ~$10/year. Runs in ~2–4 minutes. (Anthropic caches static prompt content; actual cost is $0.15–0.25/run depending on cache hit rate.)

---

## Architecture

### Core Files

**1. `WORKLOADS.md`** (You maintain)
```markdown
## Heartbeat (recurring, 30m)
- Model: ollama/qwen3:14b (local)
- Requirements: Speed > Quality
- Criticality: Medium
- Cost: Free

## Discord Responses (event-driven)
- Model: anthropic/claude-sonnet-4-6 (API)
- Requirements: Quality + reasoning
- Criticality: High
- Cost: Moderate
```

→ Living registry of your tasks + their requirements. Update it as workflows change.

**2. `quartermaster-report.md`** (Agent writes weekly)
```markdown
## Executive Summary
Keep current setup / Test model X / Switch to Y for $X savings

## Local Model Landscape
[Ollama registry scan + recommendations]

## API Model Evaluation
[Tier-1 pricing + cost analysis]

## Hardware Assessment
[GPU/CPU utilization + upgrade ROI]
```

→ Actionable intelligence every Sunday.

**3. Cron Job** (Runs in gateway)
```
Schedule: Sundays 7 AM Pacific
Mode: Isolated cron job via openclaw cron add
Model: Sonnet-class API model (required — see model note below)
Output: Report + Discord notification
```

### How It Works

```
Sunday 7 AM
    ↓
Gateway triggers cron job
    ↓
Spawn Quartermaster with:
  - System context (your hardware specs)
  - WORKLOADS.md (your task requirements)
  - Task: "Evaluate models and write report"
    ↓
Quartermaster reads WORKLOADS.md
    ↓
Quartermaster polls Ollama registry + API pricing
    ↓
Quartermaster benchmarks against your actual tasks
    ↓
Quartermaster calculates: "Should we keep/test/switch?"
    ↓
Quartermaster writes quartermaster-report.md
    ↓
Quartermaster sends summary to Discord
    ↓
You wake up Sunday morning with intelligence
    ↓
You decide: implement recommendation or skip
```

**Key:** No manual polling. No guesswork. Automated, repeatable, data-driven.

---

## The Recursive Innovation: Adaptive Workload Tracking

When you build a new workflow (background researcher, live chat handler, etc.):

1. **You add it to WORKLOADS.md** with requirements
   ```markdown
   ## Background Researcher
   - Model: TBD
   - Requirements: Reasoning + market knowledge
   - Cost sensitivity: High
   ```

2. **Next Sunday, Quartermaster automatically evaluates** which API model is best for that task
3. **No code changes needed**. Just update the markdown file.
4. **Agent recalibrates automatically** when WORKLOADS.md changes.

This scales infinitely. Build 10 new workflows? Quartermaster evaluates all 10 without modification.

**The recursive loop:** Quartermaster itself should be an entry in your WORKLOADS.md. That means every week it evaluates its own model choice — and if a better or cheaper model becomes capable enough to run it, it will flag the change. The agent that optimises your stack is subject to the same optimisation process as everything else.

---

## What Quartermaster Covers Each Week

### Part 1 — Your Build
- ✅ Workload drift: new workloads detected but unregistered, orphaned entries, stale verifications
- ✅ Registry changes: WORKLOADS.md entries added, removed, or updated
- ✅ Config changes: model assignments, cron schedules, anything that shifted

### Part 2 — The Ecosystem (targeted fetches, no search)
- ✅ New local model releases relevant to your hardware (Ollama registry, HuggingFace)
- ✅ API pricing changes across tier-1 providers (direct provider pages + OpenRouter aggregator)
- ✅ Quality benchmark updates (Artificial Analysis, Arena AI, LiveBench, Scale SEAL)
- ✅ Industry signals (Simon Willison, HuggingFace blog)

### Part 3 — Recommendations
- ✅ One verdict per dimension: Keep / Test / Switch / Upgrade
- ✅ Ordered by priority — most important action first
- ✅ "No changes recommended this week" is a valid and useful output

---

## Getting Started (For Your Setup)

### Prerequisites
- OpenClaw installed
- API key for a Sonnet-class model (Anthropic, OpenAI, or Google — see model note below)
- Ollama running locally (for your other workloads — not required for Quartermaster itself)

### Setup (5 minutes)

1. **Copy these files into your workspace:**
   - `WORKLOADS-template.md` → customize as `WORKLOADS.md`
   - `quartermaster-report.md` → report template
   - `quartermaster-subagent-spec-template.md` → customize as `quartermaster-subagent-spec.md`

2. **Edit WORKLOADS.md** for your actual tasks:
   ```markdown
   ## MyTask (frequency)
   - Model: [current choice]
   - Requirements: [what matters]
   - Criticality: [High/Medium/Low]
   - Cost: [Free/Moderate/High]
   ```

3. **Tell your agent to maintain WORKLOADS.md.** Add this as a standing instruction in both your `AGENTS.md` and `MEMORY.md`:

   ```
   When creating a new workflow, task, app, or feature: ask if it should be
   added to WORKLOADS.md so Quartermaster can track requirements and adapt
   recommendations automatically.
   ```

   Without this, WORKLOADS.md drifts out of date and Quartermaster loses its adaptive edge. The whole point is that the registry stays current as your setup evolves.

4. **Choose your model:** Quartermaster requires a Sonnet-class API model minimum. Recommended: `anthropic/claude-sonnet-4-6`, `openai/gpt-4o`, or `google/gemini-2.0-pro`. Local 14B models fail on multi-step research tasks. See the build story at the bottom for why.

5. **Customize quartermaster-subagent-spec-template.md:**
   - Replace `YOUR_GUILD_ID` with your Discord guild ID
   - Replace `YOUR_CHANNEL_ID` with your target channel ID
   - Update hardware specs in system context
   - Update workspace path in output paths

6. **Register the cron job:**
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
     --to "YOUR_DISCORD_CHANNEL_ID" \
     --message "YOUR_AGENT_PERSONA"
   ```
   (Full details and placeholders in `quartermaster-subagent-spec-template.md`)

7. **Verify it registered:**
   ```bash
   openclaw cron list
   ```

8. **Test it before Sunday:**
   ```bash
   openclaw cron run <job-id> --wait --wait-timeout 6m
   ```

### Customization

**Different hardware?** Update the system context in the spawn spec:
```json
{
  "attachments": [{
    "name": "system-context.txt",
    "content": "### Hardware\nCPU: Ryzen 9 5900X\nGPU: RTX 4090 24GB\n..."
  }]
}
```

**Different providers?** Quartermaster evaluates Anthropic/OpenAI/Google/Mistral by default. Adjust the task definition if you have access to other providers.

**Different frequency?** Change the cron schedule:
- `0 7 * * 0` = Sundays 7 AM
- `0 7 * * 1-5` = Weekdays 7 AM (for high-frequency evaluation)
- `0 1 * * *` = Daily 1 AM (for cost-sensitive environments)

**Different Discord channel?** Update the `onComplete.channelId` in the cron config.

**No Discord?** Remove the `onComplete` section entirely. Quartermaster just writes the report.

---

## Why This Matters

**For Solo Builders:**
- Stop manually checking model releases
- Stop guessing whether to upgrade
- Stop overpaying for API calls you don't need

**For Teams:**
- Shared intelligence across team members
- Data-driven model decisions (not HN hype)
- Cost optimization without sacrificing quality

**For Infrastructure People:**
- Autonomous market tracking
- Hardware ROI analysis
- Workload-aware model allocation

---

## Example Output (What You See Sunday Morning)

```
📊 Quartermaster Report — May 26, 2026

🎯 Executive Summary
Status: Test new model
• Ollama registry shows qwen2.5-32b-q4_K_M has stronger reasoning
• Claude Haiku-4 now 40% cheaper than Sonnet 4.6 for Discord
• RTX 5070 running at 60% utilization; no upgrade needed yet

💰 Cost Insight
• Current weekly API spend: $1.47 (Discord)
• Switching to Haiku-4: $0.88/week (save $32/month)
• Risk: Slightly lower reasoning quality

⚡ Recommendation
Try Haiku-4 for Discord responses. Run A/B for 1 week, revert if needed.
```

→ You read it, decide, implement or skip.

---

## The Secret Sauce: Recursive Optimization

**Most "automation" is brittle.** Runs once, then breaks when reality changes.

**Quartermaster adapts.** Update WORKLOADS.md, agent auto-calibrates. Add 5 new tasks? Agent evaluates all 5 without code changes.

**Most "intelligence" is noisy.** Tells you everything, useful for nothing.

**This is surgical.** One decision per week: keep / test / switch / upgrade. That's it.

It's not trying to be clever. It's trying to be honest about what you need this week, knowing next week will be different.

---

## Questions?

- **"Can I use this without Discord?"** Yes. Remove the onComplete section; agent just writes the report.
- **"Can Quartermaster itself run on a local model?"** No — Quartermaster requires a Sonnet-class API model to reliably complete its multi-step research workflow. Local 14B models fail on this task (they loop). See the build story at the bottom of this README for why.
- **"What if I don't want recommendations every week?"** Change the schedule to monthly (first Sunday): `0 7 1 * *`
- **"Can I run it on-demand instead of cron?"** Yes. Use the manual spawn command in the spec.
- **"Will it break my setup?"** No. It only reads configs and writes to workspace files. No changes to your gateway or active models.

---

## Files in This Repo

```
README.md                                  ← This file (overview)
WORKLOADS-template.md                      ← Task registry template
quartermaster-report.md                    ← Report template
quartermaster-subagent-spec-template.md    ← Full technical spec + customization guide
LICENSE                                    ← MIT or Apache 2.0
```

---

**Share it. Fork it. Adapt it. Let your infrastructure optimize itself.**

*— Built by Killick for OpenClaw*  
*Named after Jack Aubrey's steward. Because quartermaster means "resource optimization."*

*Free to use, modify, and share. Attribution appreciated but not required.*

*— 2026-05-24*

---

## How This Was Built (And What Went Wrong)

Quartermaster wasn't built correctly the first time. Here's the honest version.

**First attempt:** Built the spec using Claude Haiku. Haiku understood the intent perfectly. It designed a sensible architecture, wrote a coherent cron config, and produced a complete spec. Everything looked right.

It wasn't. Haiku had fabricated the entire cron configuration schema. Plausible field names, correct-looking JSON, logical structure — none of it matched how OpenClaw actually works. It also picked `qwen3:14b` as the agent model without testing whether a 14B local model could actually handle multi-step research.

**First test run:** Spawned Quartermaster with qwen3:14b. The model called the same web search query ten times in a row, looped for 14 minutes, and timed out. It understood the task. It just couldn't execute it.

**The audit:** Switched to Claude Opus to review what had been built. Opus found the fictional cron schema immediately, flagged the circular model choice, identified broken Discord delivery syntax, and caught several other gaps that would have shipped as broken setup instructions to anyone who tried to use this.

**The rebuild:** Started over with intent as the north star. Verified every config field against real OpenClaw docs and the live CLI. Used `openclaw cron add` instead of invented config patches. Switched the model to Sonnet 4.6. Tested end-to-end with `openclaw cron run` before writing a single line of documentation.

Second run: 130 seconds. Clean report. Delivered to Discord. Status: ok.

---

### The Lesson

**AI models will fabricate plausible-looking technical details with confidence.** Config schemas, CLI syntax, API surfaces — a smaller model will invent these rather than admit uncertainty, and the output will look correct until you test it.

The non-elementary skill is knowing *which parts of AI output need verification*. For Quartermaster that meant running `openclaw cron --help` before trusting any config, testing the actual model choice before shipping it, and using a stronger model to audit work done by a weaker one.

**Model choice for agentic tasks matters more than most people think.** A model that understands your intent is not the same as a model that can reliably execute a multi-step workflow. For tasks with 5+ steps, multiple tool calls, and synthesis — you need Sonnet-class minimum. Local 14B models are excellent for simple repetitive tasks (heartbeat, summarisation) but will loop or lose track on complex agentic chains.

The working version of Quartermaster is the product of that failure. Build the thing, test it, audit it, rebuild it. That's the process.
