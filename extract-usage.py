#!/usr/bin/env python3
"""
extract-usage.py — Quartermaster usage manifest generator
Reads OpenClaw cron + config, writes usage-manifest.md.
No external dependencies. No LLM.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", HOME / ".openclaw/workspace"))
CRON_JOBS = HOME / ".openclaw/cron/jobs.json"
CRON_RUNS_DIR = HOME / ".openclaw/cron/runs"
OPENCLAW_CONFIG = HOME / ".openclaw/openclaw.json"
OUTPUT = WORKSPACE / "quartermaster/usage-manifest.md"

NOW = time.time()
TODAY = datetime.now().strftime("%Y-%m-%d")


def human_age(ts_ms: int) -> str:
    secs = NOW - (ts_ms / 1000)
    if secs < 3600:
        return f"{int(secs/60)}m ago"
    elif secs < 86400:
        return f"{int(secs/3600)}h ago"
    else:
        return f"{int(secs/86400)}d ago"


def load_json(path: Path) -> dict | list:
    with open(path) as f:
        return json.load(f)


def last_run_info(job_id: str) -> tuple[str, str]:
    """Returns (last_run_human, last_status) from run history."""
    run_file = CRON_RUNS_DIR / f"{job_id}.jsonl"
    if not run_file.exists() or run_file.stat().st_size == 0:
        return "never", "no history"
    lines = run_file.read_text().strip().splitlines()
    if not lines:
        return "never", "no history"
    last = json.loads(lines[-1])
    ts = last.get("ts", 0)
    status = last.get("status") or last.get("action") or "unknown"
    age = human_age(ts) if ts else "unknown"
    return age, status


def status_icon(enabled: bool, last_status: str) -> str:
    if not enabled:
        return "⏸️"
    if last_status == "error":
        return "❌"
    return "✅"


def deep_get(d: dict, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, {})
    return d if d != {} else default


lines = []
lines.append("# Quartermaster Usage Manifest")
lines.append(f"*Auto-generated: {TODAY} — do not edit manually*")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Detected Workloads")
lines.append("")

# ── cron-backed workloads ─────────────────────────────────────────────────────

lines.append("### Cron-Backed Workloads")
lines.append("")

cron_data = load_json(CRON_JOBS) if CRON_JOBS.exists() else {"jobs": []}
jobs = cron_data.get("jobs", [])

if not jobs:
    lines.append("_No cron jobs found._")
    lines.append("")
else:
    for job in jobs:
        job_id = job.get("id", "unknown")
        name = job.get("name", "Unnamed")
        enabled = job.get("enabled", True)
        model = deep_get(job, "payload", "model", default="default")
        schedule = deep_get(job, "schedule", "expr", default="unknown")
        tz = deep_get(job, "schedule", "tz", default="UTC")
        session = job.get("sessionTarget", "unknown")

        last_run, last_status = last_run_info(job_id)
        icon = status_icon(enabled, last_status)

        lines.append(f"**{icon} {name}**")
        lines.append(f"- Source: cron job `{job_id}`")
        lines.append(f"- Model: `{model}`")
        lines.append(f"- Schedule: `{schedule}` ({tz})")
        lines.append(f"- Session: {session}")
        lines.append(f"- Last run: {last_run} — status: {last_status}")
        lines.append(f"- Enabled: {str(enabled).lower()}")
        lines.append("")

# ── config-inferred workloads ─────────────────────────────────────────────────

lines.append("### Config-Inferred Workloads")
lines.append("")

config = load_json(OPENCLAW_CONFIG) if OPENCLAW_CONFIG.exists() else {}

# Heartbeat
hb = deep_get(config, "agents", "defaults", "heartbeat", default=None)
if hb:
    hb_model = hb.get("model", "default")
    hb_every = hb.get("every", "unknown")
    active = hb.get("activeHours", {})
    hb_start = active.get("start", "?")
    hb_end = active.get("end", "?")
    lines.append("**✅ Heartbeat**")
    lines.append("- Source: config (agents.defaults.heartbeat)")
    lines.append(f"- Model: `{hb_model}`")
    lines.append(f"- Frequency: every {hb_every}, active {hb_start}–{hb_end}")
    lines.append("")

# Memory embeddings
mem_search = deep_get(config, "agents", "defaults", "memorySearch", default=None)
if mem_search:
    provider = mem_search.get("provider", "")
    model = mem_search.get("model", "")
    lines.append("**✅ Memory Embeddings (Search)**")
    lines.append("- Source: config (agents.defaults.memorySearch)")
    lines.append(f"- Model: `{provider}/{model}`")
    lines.append("- Trigger: on-demand (every memory_search call)")
    lines.append("")

# Memory flush / compaction
flush_model = deep_get(config, "agents", "defaults", "compaction", "memoryFlush", "model", default=None)
if flush_model:
    lines.append("**✅ Memory Flush (Compaction)**")
    lines.append("- Source: config (agents.defaults.compaction.memoryFlush)")
    lines.append(f"- Model: `{flush_model}`")
    lines.append("- Trigger: compaction events")
    lines.append("")

# Default primary model
primary_model = deep_get(config, "agents", "defaults", "model", "primary", default=None)
if primary_model:
    lines.append("**✅ Main Session (Default)**")
    lines.append("- Source: config (agents.defaults.model.primary)")
    lines.append(f"- Model: `{primary_model}`")
    lines.append("- Trigger: all non-overridden agent turns")
    lines.append("")

# Discord workload
discord_cfg = deep_get(config, "channels", "discord", default=None)
if discord_cfg and discord_cfg.get("enabled"):
    guilds = discord_cfg.get("guilds", {})
    guild_count = len(guilds)
    lines.append("**✅ Discord Responses (Event-Driven)**")
    lines.append("- Source: config (channels.discord)")
    lines.append(f"- Model: main session default (`{primary_model or 'unknown'}`)")
    lines.append(f"- Trigger: inbound Discord messages ({guild_count} guild(s) + DMs)")
    lines.append("- Note: Volume not tracked here — update WORKLOADS.md manually")
    lines.append("")

# ── health signals ────────────────────────────────────────────────────────────

lines.append("---")
lines.append("")
lines.append("## Health Signals")
lines.append("")

health_entries = []
for job in jobs:
    job_id = job.get("id", "")
    name = job.get("name", "Unnamed")
    _, last_status = last_run_info(job_id)
    if last_status == "error":
        run_file = CRON_RUNS_DIR / f"{job_id}.jsonl"
        error_msg = ""
        if run_file.exists():
            raw = run_file.read_text().strip().splitlines()
            if raw:
                last = json.loads(raw[-1])
                error_msg = (last.get("error") or "")[:200]
        health_entries.append(f"- ❌ **{name}**: last run errored — `{error_msg}`")
    elif last_status == "no history":
        health_entries.append(f"- ⚠️ **{name}**: no run history found")

if health_entries:
    lines.extend(health_entries)
else:
    lines.append("_No errors detected._")

lines.append("")
lines.append("---")
lines.append(f"*Generated by extract-usage.py at {TODAY}*")

OUTPUT.write_text("\n".join(lines) + "\n")
print(f"✓ Usage manifest written to {OUTPUT}")
