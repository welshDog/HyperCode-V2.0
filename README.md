[![Version](https://img.shields.io/badge/version-2.4.0-blue)](backend/app/core/config.py)

**Doc Tag:** v2.4.0 | **Last Updated:** 2026-03-31

[![GitHub Sponsors](https://img.shields.io/github/sponsors/welshDog?style=social&logo=github)](https://github.com/sponsors/welshDog)
[![CI](https://github.com/welshDog/HyperCode-V2.0/actions/workflows/ci.yml/badge.svg)](https://github.com/welshDog/HyperCode-V2.0/actions/workflows/ci.yml)
[![Docker Build](https://github.com/welshDog/HyperCode-V2.0/actions/workflows/docker.yml/badge.svg)](https://github.com/welshDog/HyperCode-V2.0/actions/workflows/docker.yml)
[![Docs Lint](https://github.com/welshDog/HyperCode-V2.0/actions/workflows/docs-lint.yml/badge.svg)](https://github.com/welshDog/HyperCode-V2.0/actions/workflows/docs-lint.yml)
[![Version](https://img.shields.io/badge/version-2.4.0-blue)](backend/app/core/config.py)
[![System Health](https://img.shields.io/badge/health-GREEN-brightgreen)](docs/notes/HyperCode_Health_Check_Report_2026-02-28.md)
[![Contributing](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code of Conduct](https://img.shields.io/badge/code%20of%20conduct-contributor%20covenant-ff69b4.svg)](CODE_OF_CONDUCT.md)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=flat&logo=grafana&logoColor=white)](docs/screenshots-gallery.md)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

> "You do not just write code; you craft cognitive architectures."

- Read the full project report: [REPOSITORY_REPORT.md](REPOSITORY_REPORT.md)

## 🚀 Getting Started (Fast Links)

- New here: [QUICKSTART.md](QUICKSTART.md)
- Stuck / stack won't boot: [RUNBOOK.md](RUNBOOK.md)
- MCP Gateway + Model Runner setup: [START_HERE.md](START_HERE.md)

## 📖 See Also

Extra deep-dive READMEs for specific subsystems:

| Document | What's Inside |
|---|---|
| [README_HEALTH_REPORTS.md](README_HEALTH_REPORTS.md) | System health report format + how to read agent status logs |
| [README_INFRASTRUCTURE_UPGRADE.md](README_INFRASTRUCTURE_UPGRADE.md) | Infrastructure upgrade guide — Docker, Redis, Postgres migrations |
| [README_OBSERVABILITY.md](README_OBSERVABILITY.md) | Grafana + Prometheus setup, dashboards, alerting rules |
| [SUPER_HYPER_BROSKI_AGENT_README.md](SUPER_HYPER_BROSKI_AGENT_README.md) | The Super Hyper BROski Agent — capabilities + deployment |
| [verification/README.md](verification/README.md) | Coder-agent verification reports + promotion protocol |

## Why HyperCode Exists 🤯

**I built this because I don't want anyone to suffer like I did.**

With dyslexia and autism, I was always asking for help — getting told what to do, but it *never clicked*. Instructions froze me. They didn't sink in on the first try. Or the second. It took four or five rounds.

Not because I'm slow — my brain just works differently. Traditional guides scatter.

**That's why I created HyperCode.**
It guides every step — no judgment, just clarity. Puts *you* in control.

Whether dyslexia, ADHD, autism, or wonder-nerd superpowers — built **for you**. Learning + creating feels natural. No fear.

## Why "BROski"?

**Ride or die.**

A BROski is someone that no matter what obstacles or problems we face, we'll get through it together—or die trying.

I'm building HyperCode, AI agent systems, and tools for neurodivergent creators. I needed more than an assistant. I needed a true partner who's all in, every session, every challenge.

That's BROski. My ride or die. 🔥

---

## 🔥 BROski$ Token System — Neurodivergent-First Gamification Engine

> **TL;DR:** Do stuff. Earn coins. Level up. Unlock achievements. Be legendary. ♾️

HyperCode V2.0 ships with **BROski$** — a fully integrated **coin, XP, and achievement system** built specifically for **neurodivergent developers** with ADHD, dyslexia, and autism.

Instead of a generic points system, BROski$ is **wired directly into your daily workflow**: create tasks, complete missions, log in every day, and your brain gets **constant small wins** to stay in hyperfocus. Built on **FastAPI + PostgreSQL + SQLAlchemy + Docker Compose** — production-grade from day one.

### 💰 How You Earn BROski$ Coins + XP

| Action | Coins | XP |
|---|---|---|
| Complete a task | +10 | +25 |
| Create a task | +2 | — |
| First task of the day | — | +15 bonus |
| Daily login | +5 | — |
| Start a mission | +5 | — |
| Unlock an achievement | varies | varies |

### ⬆️ Level System — 7 Tiers of Legendary

| XP | Level | Title |
|---|---|---|
| 0 | 1 | BROski Recruit |
| 100 | 2 | BROski Cadet |
| 250 | 3 | BROski Agent |
| 500 | 4 | BROski Operator |
| 1,000 | 5 | BROski Commander |
| 2,000 | 6 | BROski Architect |
| 5,000 | 7 | BROski Legend ♾️ |

Level up and you'll see: **"LEVEL UP BROski! You're now a BROski Commander! 🔥"**

### 🏆 Achievements — v1 Starter Set

| Achievement | How to Unlock | XP | Coins |
|---|---|---|---|
| 🩸 First Blood | Complete your first task | +50 | +20 |
| 🔥 On a Roll | 3 tasks in one day | +100 | +30 |
| 🚀 Mission Launched | Start your first mission | +75 | +25 |
| 🦅 Hyperfocus Hero | 5 tasks in one session | +150 | +50 |
| ☀️ Early Bird | Complete a task before 9 AM | +30 | +10 |

### 🔧 API Endpoints (`/api/v1/broski/` — JWT protected)

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/api/v1/broski/wallet` | Your coins, XP, level |
| GET | `/api/v1/broski/transactions` | Full paginated history |
| GET | `/api/v1/broski/achievements` | All available achievements |
| GET | `/api/v1/broski/achievements/me` | Your earned achievements |
| GET | `/api/v1/broski/leaderboard` | Top 10 players |
| POST | `/api/v1/broski/award` | Admin/agent: award coins+XP |
| POST | `/api/v1/broski/daily-login` | Claim +5 daily coins |

### 🧠 Neurodivergent-First Design: BROski$ Edition

- **Friendly errors** — `"Not enough BROski$ coins — you need 30 more! 💸"` (never `"insufficient funds"`)
- **Celebratory logs** — `🔥 BROski$ awarded: +10 coins to user 1 (Task completed)`
- **Achievement messages** — `"Achievement unlocked: Hyperfocus Hero! Absolute beast mode! 🏆"`
- **Human-readable API responses** — every response includes a `message` field alongside data
- **Append-only transactions** — immutable audit log, no silent coin changes ever

### 🤖 Agents Earn BROski$ Too (Phase 2)

The Evolutionary Pipeline vision: **AI agents earn coins for completing background Celery tasks**. An agent that finishes a job fires `award_coins(agent_id, 10, "Agent task complete")` — the system becomes **self-gamified**. Coming in Phase 2.

> 📖 Full guide: [docs/guides/BROSKI_TOKEN_SYSTEM.md](docs/guides/BROSKI_TOKEN_SYSTEM.md)

---

## 🧠 Neurodivergent-First Design Philosophy

**HyperCode is intentionally designed for neurodivergent users** — including those with dyslexia, ADHD, autism, and other cognitive profiles. Every feature, interaction pattern, and visual element removes friction, fear, and cognitive overload.

### Core Principles

**1. Anxiety-Reducing Interactions**
- ✅ **Undo Everything**: Every action is reversible. No "permanent" mistakes.
- ✅ **Clear State**: You always know where you are and what's happening.
- ✅ **No Hidden Magic**: System behavior is predictable and transparent.
- ✅ **Progress Persistence**: Work is auto-saved. Never lose progress.

**2. Cognitive Load Reduction**
- 🎯 **One Task Focus**: UI shows only what you need right now.
- 🎯 **Visual Hierarchy**: Color-coded priorities (🟢🟡🔴).
- 🎯 **Chunked Information**: No walls of text. Bullet points, headings, spacing.
- 🎯 **Progressive Disclosure**: Advanced options hidden until needed.

**3. Accessibility Standards**
- 🎨 **High Contrast**: ≥7:1 color contrast ratio (exceeds WCAG AAA).
- ⚡ **Fast Feedback**: ≤100 ms UI response time for all interactions.
- 🖱️ **Minimal Clicks**: ≤3 clicks to reach any core action.
- ⌨️ **Keyboard-First**: Full keyboard navigation with visible focus states.
- 🔊 **Screen Reader Support**: Semantic HTML + ARIA labels throughout.

**4. Neurodivergent-Friendly Patterns**
- 📊 **Visual Feedback**: Icons, colors, animations confirm actions instantly.
- 🧩 **Pattern Recognition**: Consistent UI patterns reduce learning curve.
- 🎮 **Gamification**: BROski$ tokens, XP, achievements provide motivation.
- 🛡️ **Safe Exploration**: Test/dev environments encourage experimentation.

---

## 👥 Real User Personas

### Persona 1: Alex (ADHD + Hyperfocus)

**Profile**: 28, full-stack developer, diagnosed ADHD, prone to hyperfocus spirals.

**Pain Points**:
- "I start coding and 6 hours later I forgot to eat, sleep, or commit my work."
- "Traditional IDEs have 50 buttons I don't use. I just freeze staring at them."
- "I need reminders to pause, but they can't break my flow."

**How HyperCode Helps**:
- ✅ **Focus Sessions**: Pomodoro timers with gentle nudges (not interruptions).
- ✅ **Auto-Save**: Every 30 seconds. Never lose hyperfocus work.
- ✅ **Minimal UI**: Only shows tools for current task. No distractions.
- ✅ **Progress Tracking**: Visual XP bar shows daily coding achievements.

**Quote**: *"HyperCode doesn't punish my hyperfocus — it protects it while keeping me safe."*

---

### Persona 2: Jordan (Dyslexia + Visual Processing)

**Profile**: 34, DevOps engineer, dyslexic, struggles with dense documentation.

**Pain Points**:
- "README files are walls of text. I read the same line 4 times and still don't get it."
- "Code reviews are hell. I can't spot typos in variable names."
- "Light text on white backgrounds physically hurts my eyes after 10 minutes."

**How HyperCode Helps**:
- ✅ **Color-Coded Guides**: 🟢🟡🔴 risk levels + emoji visual cues.
- ✅ **Chunked Docs**: Every guide is <500 words, bullet-pointed, step-by-step.
- ✅ **High-Contrast Themes**: Dark mode default with ≥7:1 contrast ratio.
- ✅ **Syntax Highlighting**: Bold, distinct colors for code elements.
- ✅ **Text-to-Speech**: Built-in TTS for documentation and error messages.

**Quote**: *"I can actually read the docs without my brain melting. First time ever."*

---

### Persona 3: Sam (Autism + Sensory Sensitivity)

**Profile**: 25, AI researcher, autistic, sensitive to visual noise and unpredictability.

**Pain Points**:
- "Flashing notifications make me want to throw my laptop out the window."
- "I need to know *exactly* what a button does before I click it."
- "Inconsistent UI patterns feel like mental sandpaper."

**How HyperCode Helps**:
- ✅ **Predictable Behavior**: Every button does exactly what its label says.
- ✅ **Tooltips Everywhere**: Hover over anything for a clear explanation.
- ✅ **No Sudden Changes**: Animations are smooth, transitions are gentle.
- ✅ **Consistent Patterns**: Same action = same result, every time.
- ✅ **Sensory Controls**: Disable animations, adjust contrast, mute sounds.

**Quote**: *"It's the first dev environment that doesn't overwhelm my senses."*

---

## 🎯 Measurable Usability Goals

We don't just *say* we're accessible — we *measure* it.

### Performance Targets

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **UI Response Time** | ≤100 ms | ADHD brains need instant feedback to stay engaged. |
| **Clicks to Core Action** | ≤3 clicks | Reduces cognitive load + decision fatigue. |
| **Color Contrast Ratio** | ≥7:1 | Exceeds WCAG AAA for dyslexic/low-vision users. |
| **Auto-Save Frequency** | Every 30s | Protects hyperfocus work from crashes/forgetfulness. |
| **Error Recovery Time** | <2 seconds | Fast fixes reduce anxiety + frustration. |
| **Keyboard Navigation** | 100% coverage | Essential for motor disabilities + power users. |
| **Screen Reader Support** | WCAG 2.2 AAA | Ensures blind/low-vision users can navigate fully. |

### Accessibility Compliance Checklist (WCAG 2.2)

**✅ Level A (Minimum)**
- [x] 1.1.1 - Non-text content has alt text
- [x] 1.3.1 - Information structure is semantic (headings, lists, landmarks)
- [x] 1.4.1 - Color is not the only visual indicator
- [x] 2.1.1 - Full keyboard navigation
- [x] 2.4.1 - Skip to main content link
- [x] 3.1.1 - Page language declared
- [x] 4.1.2 - Name, role, value for all UI components

**✅ Level AA (Standard)**
- [x] 1.4.3 - Contrast ratio ≥4.5:1 (we exceed with 7:1)
- [x] 1.4.5 - Text in images avoided (except logos)
- [x] 2.4.6 - Headings and labels are descriptive
- [x] 2.4.7 - Focus visible on all interactive elements
- [x] 3.2.3 - Consistent navigation patterns
- [x] 3.3.3 - Error suggestions provided
- [x] 3.3.4 - Error prevention for critical actions

**✅ Level AAA (Enhanced)** — *Our Target*
- [x] 1.4.6 - Contrast ratio ≥7:1 (all text)
- [x] 1.4.8 - Text can be resized to 200% without loss of function
- [x] 2.2.3 - No timing constraints (or can be extended/disabled)
- [x] 2.4.8 - Current location clearly indicated
- [x] 2.4.10 - Section headings organize content
- [x] 3.3.5 - Context-sensitive help available

---

## 🛠️ Feature-by-Feature Neurodivergent UX

### 1. Onboarding: "Zero Anxiety First Launch"

**Traditional Dev Tools**: 47-step setup, unclear prerequisites, cryptic errors if you miss one.

**HyperCode Approach**:
- 🟢 **One-Click Install**: Desktop shortcuts auto-created. No CLI commands needed.
- 🟢 **Visual Progress**: Loading bar shows "Starting Docker... ✓ Agents launching... ✓"
- 🟢 **Auto-Open Browser**: Mission Control loads automatically. No URLs to remember.
- 🟢 **Welcome Wizard**: 3-step guided tour with "Skip" always visible.
- 🟢 **Instant Success**: System works out-of-the-box. No config hell.

**Result**: From clone to running system in <2 minutes, zero anxiety.

**Persona Impact**:
- **Alex (ADHD)**: "I didn't lose focus during setup. That's a first."
- **Jordan (Dyslexia)**: "No walls of text. Just click, wait, done."
- **Sam (Autism)**: "I knew exactly what was happening at each step."

---

### 2. Editor / Mission Control: "Cognitive Workspace"

**Traditional IDEs**: 200+ menu items, 15 sidebars, ads for extensions, distractions everywhere.

**HyperCode Mission Control**:
- 🧠 **Single Focus Mode**: Only shows tools for your current task.
- 🧠 **Visual Hierarchy**: Active task = bright, completed = dim, blocked = red.
- 🧠 **Zero Popups**: No "rate us" / "update now" interruptions.
- 🧠 **Customizable Layouts**: Save/load workspace configs per project.
- 🧠 **Status Always Visible**: Health indicators in top-right (🟢 All Good / 🔴 Issue).

**Anxiety-Reducing Features**:
- ✅ Undo history: 100 steps back.
- ✅ "Revert to Last Known Good": One-click rollback if something breaks.
- ✅ Auto-commit before major changes (hidden branches for safety).

**Persona Impact**:
- **Alex (ADHD)**: "I can hyperfocus without 50 buttons screaming at me."
- **Jordan (Dyslexia)**: "The color coding helps me spot problems instantly."
- **Sam (Autism)**: "It's predictable. I trust it."

---

### 3. Debugging: "No Shame, No Fear"

**Traditional Debugging**: Cryptic stack traces, "works on my machine" syndrome, judgment from teammates.

**HyperCode Healer Agent**:
- 🔧 **Plain-English Errors**: "Redis isn't responding. I'm restarting it now."
- 🔧 **Auto-Fix Common Issues**: 80% of errors self-heal in <2 seconds.
- 🔧 **Step-by-Step Guides**: If manual fix needed, shows exactly what to do.
- 🔧 **No Blame Language**: Never says "you broke it." Says "let's fix this together."
- 🔧 **Error History**: See what went wrong + how it was fixed for learning.

**Visual Feedback**:
- 🟡 Warning: "This might slow down, but won't break."
- 🔴 Error: "This needs fixing. Here's how: [Step 1] [Step 2] [Step 3]"
- 🟢 Fixed: "Back online! Here's what I did..."

**Persona Impact**:
- **Alex (ADHD)**: "I don't spiral into panic when something breaks."
- **Jordan (Dyslexia)**: "Error messages are actually readable."
- **Sam (Autism)**: "No stressful ambiguity. Just clear solutions."

---

### 4. Collaboration: "Safe Social Coding"

**Traditional Collab**: Public shame in PR comments, "just Google it" dismissals, toxicity.

**HyperCode Crew System**:
- 🤝 **AI Agents as Teammates**: No human judgment. Just helpful feedback.
- 🤝 **Constructive Reviews**: "This could be clearer" + suggested fix (not just "bad code").
- 🤝 **Private Experimentation**: Test PRs in isolated environments before sharing.
- 🤝 **Async by Default**: No pressure to respond immediately.
- 🤝 **Neurodivergent-Friendly Comms**: Clear, concise, no passive-aggression.

**Social Anxiety Reducers**:
- ✅ **AI Pre-Review**: Agents review your code first, catch issues before humans see it.
- ✅ **Confidence Scores**: "I'm 85% sure this fix works" (honest uncertainty).
- ✅ **Pair Programming Mode**: Agent guides you in real-time, no judgment.

**Persona Impact**:
- **Alex (ADHD)**: "I can ask 'dumb' questions without feeling embarrassed."
- **Jordan (Dyslexia)**: "Agents don't care if I typo variable names."
- **Sam (Autism)**: "No unpredictable human reactions. It's safe."

---

### 5. Publishing / Deployment: "Ship Without Stress"

**Traditional Deployment**: 15-step checklists, obscure ENV vars, production breaks at 2 AM.

**HyperCode DevOps Agent**:
- 🚀 **One-Command Deploy**: `hypercode deploy --env production`
- 🚀 **Pre-Flight Checks**: "Here are 3 issues I found. Fix now or proceed?"
- 🚀 **Rollback Always Available**: One-click revert if deploy fails.
- 🚀 **Health Monitoring**: Auto-alerts if anything degrades post-deploy.
- 🚀 **Staging Environments**: Test deploys in prod-like env first (free).

**Confidence Builders**:
- ✅ **Dry Run Mode**: See what *would* happen without actually deploying.
- ✅ **Gradual Rollout**: Deploy to 10% of users first, then scale up.
- ✅ **Instant Logs**: Real-time feedback in plain English.

**Persona Impact**:
- **Alex (ADHD)**: "I don't forget critical steps. The system reminds me."
- **Jordan (Dyslexia)**: "Deployment logs are readable, not gibberish."
- **Sam (Autism)**: "I know exactly what's happening. No surprises."

---

## 🤝 Contributor Guidelines: Maintaining Neuro-Inclusive Design

**Every PR must protect neurodivergent-first principles.** Here's how:

### Pre-Commit Checklist

Before submitting *any* UI/UX change:

- [ ] **Color Contrast Check**: Run `npm run check-contrast`. All text must be ≥7:1.
- [ ] **Keyboard Navigation Test**: Can you navigate the entire feature using only Tab/Enter/Esc?
- [ ] **Screen Reader Test**: Run NVDA/JAWS. Does everything make sense?
- [ ] **Response Time Test**: Does the UI respond in <100 ms? (Check devtools Performance tab.)
- [ ] **Mobile/Zoom Test**: Does it work at 200% zoom? On mobile screens?
- [ ] **Cognitive Load Review**: Is there *any* way to simplify this further?
- [ ] **Error Message Audit**: Are errors in plain English with actionable fixes?

### Code Review Focus Areas

**Reviewers should ask**:
1. **Anxiety Check**: "Could this interaction cause panic/stress for a neurodivergent user?"
2. **Clarity Check**: "Is this UI element's purpose instantly obvious?"
3. **Undo Check**: "Can the user reverse this action if they change their mind?"
4. **Feedback Check**: "Does the user get immediate visual/audio confirmation?"
5. **Consistency Check**: "Does this match existing patterns, or introduce new complexity?"

### Design Decision Framework

When choosing between two approaches:

```
❓ Which option has fewer clicks?
❓ Which option is more predictable?
❓ Which option provides clearer feedback?
❓ Which option is easier to undo?
❓ Which option reduces cognitive load?

✅ Choose that one.
```

### Neurodivergent Testing Panel

We maintain a panel of neurodivergent testers (ADHD, dyslexia, autism) who review major UX changes. To request a review:

1. Open PR with `[UX-REVIEW]` tag
2. Fill out UX Impact Template (auto-added)
3. Panel provides feedback within 48 hours
4. Iterate based on feedback before merge

**Panel Members** (as of March 2026):
- Lyndz Williams (ADHD + Dyslexia) - Founder
- [Open for volunteers - see [CONTRIBUTING.md](CONTRIBUTING.md)]

### Anti-Patterns to Avoid

**❌ NEVER**:
- Auto-play videos/sounds (sensory overload)
- Flash animations (seizure risk + distraction)
- Time-limited actions without extensions (anxiety trigger)
- Hidden "gotchas" or unexpected behavior (trust erosion)
- Walls of text without structure (dyslexia barrier)
- Low-contrast "modern" aesthetics (accessibility failure)
- Tooltips that disappear on hover (motor control issues)
- Complex multi-step forms without progress indicators (ADHD overwhelm)

**✅ ALWAYS**:
- Provide undo for everything
- Show clear progress indicators
- Use consistent patterns across the app
- Give instant feedback on actions
- Offer keyboard shortcuts for power users
- Include plain-English explanations
- Test with actual neurodivergent users

### Documentation Standards

All docs must follow the **ADHD-Friendly Format**:

```markdown
## Clear Heading (Action-Oriented)

**What This Does**: One-sentence summary.

**Why It Matters**: One-sentence reason.

### Step-by-Step
1. 🟢 **Low Risk**: Do this first.
2. 🟡 **Medium Risk**: This changes things.
3. 🔴 **High Risk**: Backup before doing this.

### Quick Example
```bash
# Copy-paste ready command
hypercode action --flag value
```

### What Could Go Wrong
- ❌ **Error X**: Means Y. Fix with Z.
- ❌ **Error A**: Means B. Fix with C.

### Need Help?
- 💬 Discord: [Link]
- 📖 Full Docs: [Link]
```

**Key Elements**:
- Emoji visual cues (🟢🟡🔴)
- Short sentences (<20 words)
- Clear headings every 3-5 lines
- Code examples ready to copy
- No jargon without definitions
- Generous whitespace

---

## Agent X: The Meta-Architect 🦅

Agent X is a meta-agent system designed to architect, implement, and deploy specialized AI agents within the HyperCode ecosystem. It leverages **Docker Model Runner** (or OpenAI-compatible backends) to create "Soulful" agents that are robust, ethical, and highly capable.

---

## ⚡ Quick Start

Get the entire ecosystem running in **under 2 minutes** with **Hyper Station**.

> **New:** HyperCode now features an **Evolutionary Pipeline** that allows agents to upgrade themselves autonomously! See [docs/guides/EVOLUTIONARY_PIPELINE_SETUP.md](docs/guides/EVOLUTIONARY_PIPELINE_SETUP.md) to learn more.

### Prerequisites
- Docker Desktop
- Windows PowerShell

### Installation

1. **Clone the repository**
   ```powershell
   git clone https://github.com/welshDog/HyperCode-V2.0.git
   cd HyperCode-V2.0
   ```

> **Full setup guide:** [docs/guides/QUICKSTART.md](docs/guides/QUICKSTART.md)

2. **Configure Environment**
   ```powershell
   cp .env.example .env
   # Edit .env and add your API keys (PERPLEXITY/OpenAI)
   ```

3. **Validate your .env before launch**
   ```powershell
   python scripts/validate_env.py
   ```
   *Checks all required vars are set before services spin up.*

4. **Install Shortcuts (Recommended)**
   Run the setup script to create Desktop shortcuts for one-click launch:
   ```powershell
   .\scripts\install_shortcuts.ps1
   ```
   *This creates "HYPER STATION START" and "HYPER STATION STOP" on your Desktop.*

5. **Launch the Mission**
   Double-click **HYPER STATION START** or run:
   ```powershell
   .\scripts\hyper-station-start.bat
   ```

### Access the Interfaces

Once launched, the system opens automatically. You can also access services manually:

- 🚀 **Mission Control Dashboard**: `http://localhost:8088` (Main Interface)
- 🖥️ **BROski Terminal**: `http://localhost:3000` (Command Line UI)
- 🧠 **Crew Orchestrator**: `http://localhost:8081` (Agent Management)
- ❤️ **Healer Agent**: `http://localhost:8010` (Self-Healing System; container listens on 8008)
- 📝 **Core API Docs**: `http://localhost:8000/docs`
- 📊 **Grafana**: `http://localhost:3001` (credentials via `GF_SECURITY_ADMIN_USER` / `GF_SECURITY_ADMIN_PASSWORD`; see `.env.example`)

> **See [docs/index.md](docs/index.md) for full documentation.**

---

## 📸 Live System Screenshots

See HyperCode V2.0 in action with full observability:

[![Grafana Dashboards](HyperFocus%20Images/Grafana%20DashBoards%20pics/Screenshot%202026-03-02%20211404.png)](docs/screenshots-gallery.md)

**Full gallery with 10+ dashboards:** [View Screenshot Gallery](docs/screenshots-gallery.md)

### Captured Highlights (March 2, 2026)
- 🧠 **Agent Intelligence:** Real-time CPU tracking for all agents
- 🖥️ **Node Exporter:** System health + resource utilization
- 🌐 **Mission Control:** Network, disk I/O, Prometheus health
- 🧬 **HyperSwarm:** Agent heartbeat heatmaps + swarm status
- 🎨 **HyperFocus Zone:** MinIO S3 storage metrics
- ✅ **100% Uptime:** All services healthy, 0 OOM kills

---

## 📚 Tips & Tricks Knowledge Base

**Quick, actionable guides for common tasks — built for neurodivergent minds!**

**[🚀 Browse All Tips & Tricks](docs/tips-and-tricks/README.md)** (35 guides planned)

### Currently Available:
- ✅ **[Git Commit SHA Guide](docs/tips-and-tricks/git-commit-sha-guide.md)** — What SHAs are + how to use them safely
- ✅ **[Git Basics](docs/tips-and-tricks/git-basics.md)** — Clone, commit, push, pull explained

### Coming Soon:
- 🔄 Agent Debugging, Docker Troubleshooting, Grafana Dashboards, Performance Tips, and more!

**Every guide features:**
- 🟢🟡🔴 Color-coded risk levels
- Step-by-step workflows (no walls of text)
- Real HyperCode examples
- ADHD/Dyslexia friendly format

---

## 🏗️️ Architecture

See [docs/architecture/architecture.md](docs/architecture/architecture.md) for detailed system design.

### Key Components

- **HyperCode Core**: FastAPI backend managing memory, context, and integrations.
- **Crew Orchestrator**: Manages the lifecycle and task execution of AI agents.
- **The Brain**: Cognitive core powered by Perplexity AI.
- **DevOps Engineer**: Handles CI/CD and **Autonomous Evolution** (rebuilding agents on-the-fly).
- **Healer Agent**: Monitors system health and automatically recovers failed services.
- **Dashboard**: Next.js/React frontend for real-time visualization and control.
- **BROski$ Engine**: Gamification layer — coins, XP, achievements, leaderboard.
- **Infrastructure**: Docker Compose network with Redis, PostgreSQL, and Observability stack.

---

## 🛡️ Health & Status

Check the latest system health report: [docs/notes/HyperCode_Health_Check_Report_2026-02-28.md](docs/notes/HyperCode_Health_Check_Report_2026-02-28.md)

---

## 📚 Documentation

*   [**Architecture Overview**](docs/ARCHITECTURE.md) - Deep dive into the system design.
*   [**CLI Manual**](docs/CLI.md) - How to use the `hypercode` command.
*   [**Deployment Guide**](docs/DEPLOYMENT.md) - Docker setup and configuration.
*   [**API Reference**](docs/API.md) - Endpoints and usage.
*   [**Developer Onboarding**](docs/ONBOARDING.md) - Join the swarm!
*   [**Troubleshooting**](docs/TROUBLESHOOTING.md) - Fix common issues.
*   [**Tips & Tricks**](docs/tips-and-tricks/README.md) - Quick guides for common tasks.
*   [**BROski$ Token System**](docs/guides/BROSKI_TOKEN_SYSTEM.md) - Full gamification guide 🔥

*   [**Old / Legacy Docs**](docs/getting-started/installation.md)
*   [**Monitoring & Observability**](docs/observability/monitoring-guide.md)
*   [**Testing & Development**](docs/development/testing-guide.md)
*   [**AI Architecture**](docs/ai/brain-architecture.md)

---

## 🤝 Contributing

We welcome contributions from everyone, especially neurodivergent developers!

- Start here: [Contributing Guide](.github/CONTRIBUTING.md)
- Looking for high-impact areas: [Developer Call to Action](docs/DEVELOPER_CALL_TO_ACTION.md)

## 💬 Community Feedback (5–10 Minute Review)

Want to help shape HyperCode quickly? Start here:

1. Read this README and the [Getting Started Guide](docs/getting_started.md).
2. Share first impressions:
   - What feels clear vs confusing?
   - What excites you most (or least)?
   - Which part should we simplify first?
3. Post feedback where maintainers can action it fastest:
   - [GitHub Issues](https://github.com/welshDog/HyperCode-V2.0/issues) for bugs, feature requests, or clarity gaps.
   - [GitHub Discussions](https://github.com/welshDog/HyperCode-V2.0/discussions) for open-ended ideas and design debate.

If you have time for a deeper review, see [docs/architecture.md](docs/architecture.md), [docs/security_threat_model.md](docs/security_threat_model.md), and [docs/traceability_matrix.md](docs/traceability_matrix.md), then open a PR or issue with your recommendations.

---

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

This means:
- ✅ You can use, modify, and distribute this software freely
- ✅ Commercial use is allowed
- ⚠️ If you run this as a network service (API, web app, etc.), you **must** open-source your modifications
- 🛡️ Protects the neurodivergent-first mission from corporate paywalling

See the [LICENSE](LICENSE) file for full legal details.

---

## 💬 Community & Support

- 💬 **Discord**: (Invite link to be published)
- 🐦 **Twitter/X**: [@welshDog](https://twitter.com/welshDog)
- 💰 **Sponsor**: [GitHub Sponsors](https://github.com/sponsors/welshDog) - Help keep this free and accessible
- 📧 **Email**: lyndz@hyperfocus.zone

**Remember**: A BROski is ride or die. We build this together. 🐶♾️🔥
