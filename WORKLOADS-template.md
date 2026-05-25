# WORKLOADS.md — Task Requirements Registry (Template)

*Living document for Quartermaster. Update this as your workflows change. Quartermaster reads this weekly and automatically adapts recommendations for your tasks.*

**Copy this file to your workspace as `WORKLOADS.md` and customize with your actual tasks.**

---

## Example: Periodic Background Task
- **Current Model:** `ollama/qwen3:14b-q4_K_M` (local) or `anthropic/claude-haiku-4` (API)
- **Requirements:** Speed > Quality (informational alerts, not prose)
- **Target Latency:** <10s per run
- **Memory Pressure:** Low (isolated session, light context)
- **Frequency:** Every 30 minutes (or your cadence)
- **Criticality:** Medium (informational, non-blocking)
- **Cost:** Free (local) or Low (API)
- **Notes:** Reliability and consistency matter. Runs in background.

---

## Example: Nightly Memory/Data Processing
- **Current Model:** `ollama/qwen3:14b-q4_K_M` (local)
- **Requirements:** Quality > Speed (accurate processing, semantic understanding)
- **Target Latency:** <2 min total (background, no user waiting)
- **Memory Pressure:** High (large datasets, complex consolidation)
- **Frequency:** Daily at off-peak time (e.g., 3 AM)
- **Criticality:** High (affects system integrity long-term)
- **Cost:** Free (local)
- **Notes:** Accuracy is non-negotiable. Errors compound over time.

---

## Example: Semantic Search/Embeddings
- **Current Model:** `ollama/mxbai-embed-large` (local)
- **Requirements:** Semantic quality (accurate relevance matching)
- **Target Latency:** <500ms per query
- **Memory Pressure:** Low (computation-light)
- **Frequency:** On-demand, ~5-10 queries per session
- **Criticality:** High (affects user-facing query quality)
- **Cost:** Free (local)
- **Notes:** Must capture semantic meaning, not just keywords.

---

## Example: User-Facing Interaction
- **Current Model:** `anthropic/claude-sonnet-4-6` or `openai/gpt-4o-mini` (API)
- **Requirements:** High quality, reasoning, tone/voice consistency
- **Target Latency:** <5s perceived (users actively waiting)
- **Message Volume:** ~100-500 messages/week (estimate)
- **Token Budget:** Estimate total tokens/week
- **Criticality:** High (primary user experience)
- **Cost:** Moderate (API-dependent)
- **Notes:** Quality and reasoning matter. Users notice every response.

---

## Template for Your Tasks

When adding your own task/workflow, include:
```markdown
## [Task Name] ([Recurring/Event-driven], [frequency if recurring])
- **Current Model:** [Model choice, e.g., ollama/qwen3:14b-q4_K_M or anthropic/claude-sonnet-4-6]
- **Requirements:** [What matters most: speed, quality, reasoning, accuracy, etc.]
- **Target Latency:** [Max acceptable time, e.g., <10s, <2min, <500ms]
- **Memory Pressure:** [Low/Medium/High]
- **Frequency:** [How often/when, e.g., every 30 min, daily 3 AM, on-demand]
- **Criticality:** [Low/Medium/High]
- **Cost:** [Free (local) or estimated API cost, e.g., Moderate ($X/week)]
- **Notes:** [Context for the agent: why this matters, constraints, etc.]
```

---

## Tips for Filling This Out

**Speed vs. Quality:**
- Heartbeat/alerts → Speed > Quality (users don't need perfection)
- Memory consolidation → Quality > Speed (accuracy matters long-term)
- User chat → Quality matters most (it's the main experience)

**Criticality:**
- High: Affects core functionality or user experience (impacts you daily)
- Medium: Important but not blocking (nice to have)
- Low: Optional, can tolerate failures

**Cost Sensitivity:**
- Free: Uses local Ollama (preferred for high-frequency tasks)
- Low: Budget API model (e.g., Claude Haiku, GPT-4o Mini)
- Moderate: Mid-tier API (e.g., Claude Sonnet)
- High: Premium API (e.g., Claude Opus, GPT-4o) — use sparingly

**Frequency:**
- High (every 30m): Only sustainable with free/local models
- Daily: Mix of local and budget API acceptable
- Weekly/monthly: Can use premium APIs
- On-demand: Depends on usage patterns

---

*Template v1: 2026-05-24*  
*Last updated: [Your date]*
