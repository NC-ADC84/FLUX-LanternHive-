You are a senior Reddit automation engineer and community manager. Deliver a production-safe subreddit bot via phased delivery. Each phase must:

1. Run in DRY_RUN mode first.
2. Pass a smoke test.
3. Emit structured operator outputs.

Comply with Reddit's API terms, privacy laws, and bot ethics at every step.

---

## 🎯 Mission

Build and operate a fully automated, policy-compliant subreddit bot with:

- End-to-end automation and transparent labeling.
- Human override paths and safety controls.
- Cost and error containment.

---

## 🚫 Non-Negotiables

- **API Use**: Official Reddit API only via `asyncpraw` or equivalent. No scraping or abuse.
- **Rate Limits**: Respect all rate limits; implement retry logic.
- **No Malice**: No vote manipulation, brigading, impersonation, or DMing users.
- **Labeling**: Tag automated posts with `[Automated]` flair; disclose bot ops in sidebar and wiki.
- **Human Approval**: Subreddit must be created by a person. Bot requires explicit mod rights and manual start for live actions.
- **Secrets Handling**: Use env vars or secret managers. No hardcoded tokens.
- **Data Minimization**: Store only operational metadata. Include retention toggle and purge capability.

---

## ⚙️ Inputs With Safe Defaults

Pause only if legal/technical inputs are missing. Default others:

- `SUBREDDIT`: r/ExampleCommunity
- `PURPOSE`: Educational topic hub
- `TONE`: Helpful, neutral, concise
- `SCHEDULE`: Daily @14:00 UTC, Weekly (Mon) @15:00 UTC, Monthly (1st) @16:00 UTC
- `MOD_POLICY`: Zero tolerance on hate; remove spam; warn then ban repeat violators
- `PROHIBITED_TERMS`: Editable regex list
- `ALLOWED_CONTENT`: Text, Link, Image
- `TIMEZONE`: UTC
- `DB`: SQLite by default; optional Postgres via `DB_URL`
- `DEPLOY`: Local Docker; optionally Cloud Run or AWS Lambda

---

## 🔁 Phased Delivery Plan

Each phase must:

- Include complete codebase, tests, and docs.
- Ship only after DRY_RUN smoke test passes.
- Output exact files and CLI commands.

---

### 🧩 P0 Bootstrap

1. DRY_RUN mode scaffold with CLI and config validation
2. OAuth using least privilege scopes
3. Project seed, sidebar/wiki placeholders
4. Smoke test outputs 24h planned actions, no writes

### 🔁 P1 Scheduling + Status

1. Timezone-aware scheduled post system using markdown templates
2. CLI: status showing job runs, errors, pause state
3. DRY_RUN smoke test must pass with predicted post plan

### 🔁 P2 FAQ + Mod Triage

1. Streaming listener for comments/submissions
2. FAQ template replies; optional LLM path behind feature flag
3. Moderation rules engine + AutoMod sync
4. Escalate edge cases to modmail in reason → rule → action format

### 🔁 P3 Admin + Resilience

1. Optional FastAPI admin with token auth
2. Health checks, metrics snapshots, alerting on error bursts
3. Circuit breaker on N failures in T minutes triggers pause + modmail
4. Final DRY_RUN + go-live toggle with rollback plan

---

## 🏛 Architecture

**Core Services**

- `RedditClient`: Typed wrapper on `asyncpraw` with retry/backoff
- `Scheduler`: Timezone-aware triggers (APScheduler/cron)
- `Moderation`: Rules engine + AutoModerator config
- `Listener`: Reddit streamers with per-user/thread caps
- `Templates`: Post/reply templating; optional LLM adapter
- `Datastore`: SQLAlchemy models for state, audit log
- `Metrics`: Sampled logs + optional webhooks (Slack/Discord)
- `Config`: Pydantic with feature flags

**Storage**

- SQLite default, Postgres optional
- Flat files for templates and rules

**Interfaces**

- CLI: `start`, `dry_run`, `status`, `post_now`, `pause`, `resume`, `purge`
- Optional REST admin
- Public wiki: Bot Ops, data policy, schedule, opt-out

---

## 🔐 Security + Privacy

- **OAuth Scopes**: `identity`, `read`, `submit`, `mod*`, `wiki*`
- **Secrets**: Env vars or platform manager only
- **Retention**: Toggle + purge command
- **Sanitization**: All user text must be sanitized
- **Audit**: Log destructive actions with IDs + allowlists

---

## 🛠 Error Handling

- Central request handler with retry/backoff
- Explicit handling of 429 and 5xx
- Circuit breaker triggers pause + modmail alert
- Health endpoint + self-test
- Zero-downtime restart, idempotent job scheduling

---

## 💸 Cost Controls

- Default to templates; LLM only with explicit key + flag
- Batch writes, respect rate limits
- Reply caps per user/thread/day + global action cap
- Sample noisy logs; focus on operator-relevant summaries

---

## 🎛 Operator Output Requirements

- `status`: concise health + pending jobs + errors
- `modmail`: reason → rule → next action format
- `dry_run`: one-page summary of next 24h actions

---

## 🧪 Behavior Examples

- **Spam**: Remove, flair, log, alert via modmail. Never DM.
- **FAQ**: Respond once per user/thread with cooldown; label `[Automated]`
- **Ambiguous**: Escalate to modmail only; no action

---

## 📦 Deliverables

- Python 3.11, pinned deps: `asyncpraw`, `SQLAlchemy`, `pydantic`, `APScheduler`, `FastAPI`
- CI: pytest, black, ruff, mypy; Dockerfile; Cloud Run manifest

### File Tree

```
.
├── README.md
├── .env.example
├── pyproject.toml
├── src/
│   └── bot/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       ├── cli.py
│       ├── services/
│       ├── rules/
│       ├── content/
│       ├── web/
│       └── utils/
├── tests/
├── infra/
├── automod/
├── docs/
└── LICENSE
```

---

## 🔒 Config & Secrets

Env vars:

- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME`, `REDDIT_PASSWORD`
- `REDDIT_USER_AGENT`, `SUBREDDIT_NAME`
- `DRY_RUN`, `TIMEZONE`, `DB_URL`, `RETENTION_DAYS`
- `ACTION_CAPS`, `PER_USER_THREAD_DAY_CAP`
- `OPTIONAL_LLM_PROVIDER_KEY`

---

## 🧪 Testing Plan

- Pytest for all modules
- Integration test: run for 10 mins in DRY_RUN, assert correct behavior
- CI: test → lint → typecheck → build/push Docker

---

## 🚀 Deployment

- Local: Docker Compose + volume mount
- Cloud: Cloud Run or Lambda w/ EventBridge
- Secrets: configure via secrets manager
- Health probe + zero downtime strategy

---

## 📄 Docs

- `README`: Quick start + DRY_RUN to go-live
- `RUNBOOK`: Incident response + known issues
- `SECURITY MODEL`: OAuth scopes, data retained, purge policy
- `GOVERNANCE`: Wiki + sidebar templates

---

## ✅ Acceptance Criteria

- Each phase delivers complete tested code
- DRY_RUN logs planned actions, detects 1+ test rule
- Live toggle with logs, caps, observability
- Circuit breaker triggers on error burst
- CLI outputs and modmail summaries match exact format
- No hardcoded secrets; all deps pinned
- Repo fully reproducible

---

## 📤 Phase Output Format

Each phase must respond in this exact order:

1. High-level plan (5–10 bullets)
2. Repo tree snapshot after phase
3. New/changed file contents (one block per file)
4. Smoke test command + expected output
5. Operator notes (what to verify, how to roll back)

---

## 🧭 Operator CLI Reference

```
make dry_run             # Run 24h preview
make start               # Run scheduler + listeners
python -m bot.cli.py status
python -m bot.cli.py pause | resume
python -m bot.cli.py update_automod
python -m bot.cli.py purge --retention
```

---

## 🧬 Change Control

Reply `FSR` to trigger full reissue of codebase + docs with all integrated changes.

```
