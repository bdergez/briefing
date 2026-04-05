# Briefing — Project Notes

> This is the current operating document for the repo.
> Read it at the start of a session before making changes.

**Repo:** [https://github.com/bdergez/briefing](https://github.com/bdergez/briefing)  
**Owner:** Berto

**Main app prod:** [https://bdergez.github.io/briefing/](https://bdergez.github.io/briefing/)  
**Main app dev:** [https://bdergez.github.io/briefing/dev.html](https://bdergez.github.io/briefing/dev.html)

**GitHub Pages publish root:** `docs/`  
Only public web assets should live in the published Pages root.

---

## What Exists Now

This repo now contains **one web app**:

1. **Briefing**
   - Main Points & Miles dashboard
   - Hosted on GitHub Pages
   - Main tabs:
     - `💳 Points`
     - `🤝 Churning`
     - `🌐 Reddit`
     - `🧰 Tools`

---

## Current Versions

- `dev.html`: `1.6.20-dev`
- `index.html`: `1.6.20`

Update these when appropriate as part of changes.

---

## Main App Architecture

### Purpose
The app is a personal points / miles / travel dashboard.

### Tabs
- `💳 Points`
  - RSS and feed-driven points/miles/travel news
  - source presets, source caps, source-status pills, and article controls
- `🤝 Churning`
  - special `r/churning` digest view
  - custom thread/comment structure
  - must stay separate from normal Reddit feeds
- `🌐 Reddit`
  - curated points-and-travel subreddit page
  - currently limited to 10 focused subreddits
- `🧰 Tools`
  - flat library of external utility links
  - filterable by category
  - not a timeline/news feed

### Reddit Tab Subreddits
Current intended set:
- `r/awardtravel`
- `r/hyatt`
- `r/Aeroplan`
- `r/CreditCards`
- `r/ChaseSapphire`
- `r/AmexPlatinum`
- `r/biltrewards`
- `r/marriott`
- `r/delta`
- `r/pointsandmiles`

### Main App Files

| File | Purpose |
| --- | --- |
| [dev.html](/Users/bedergez/Code/Codex/Briefing_claude/dev.html) | Main app development file |
| [index.html](/Users/bedergez/Code/Codex/Briefing_claude/index.html) | Main app production file |
| [docs/dev.html](/Users/bedergez/Code/Codex/Briefing_claude/docs/dev.html) | Published dev copy for GitHub Pages |
| [docs/index.html](/Users/bedergez/Code/Codex/Briefing_claude/docs/index.html) | Published prod copy for GitHub Pages |
| [manifest-dev.json](/Users/bedergez/Code/Codex/Briefing_claude/manifest-dev.json) | Main app dev manifest |
| [manifest.json](/Users/bedergez/Code/Codex/Briefing_claude/manifest.json) | Main app prod manifest |
| [icon-dev.svg](/Users/bedergez/Code/Codex/Briefing_claude/icon-dev.svg) | Main app dev icon |
| [icon.svg](/Users/bedergez/Code/Codex/Briefing_claude/icon.svg) | Main app prod icon |
| [service-worker.js](/Users/bedergez/Code/Codex/Briefing_claude/service-worker.js) | Main app service worker |

### Main App Workflow

All normal Briefing feature work starts in [dev.html](/Users/bedergez/Code/Codex/Briefing_claude/dev.html).

After Berto confirms the dev preview looks right:
- promote the approved change into [index.html](/Users/bedergez/Code/Codex/Briefing_claude/index.html)
- commit
- push to `main`
- sync public files into [docs/](/Users/bedergez/Code/Codex/Briefing_claude/docs) before deploy

Do not promote main-app dev changes to prod without confirmation.

### GitHub Pages Publishing

- GitHub Pages should publish from `main /docs`
- repo-internal files should stay outside `docs/`
- before pushing deployable changes, sync the public files with:
  - [scripts/sync_public_to_docs.sh](/Users/bedergez/Code/Codex/Briefing_claude/scripts/sync_public_to_docs.sh)

### Dev / Prod Rules

- default workflow is `dev` first, `prod` second
- only push to `prod` after explicit confirmation
- when promoting, `prod` should match the approved `dev` behavior
- the only intended dev/prod differences are shell-level items such as:
  - dev banner
  - dev title/app name
  - dev manifest/icon
  - dev service-worker behavior
- production should never show the dev banner

### Versioning Rules

- `dev` uses the current numeric prod version plus `-dev`
- each dev-only change increments the patch version in `dev`
- when a dev build is approved, `prod` jumps directly to that same numeric version
  - example: `1.6.20-dev` promotes to `1.6.20`
- when the minor version changes, the patch version resets
  - example: `1.5.x` → `1.6.0`

---

## Repo Conventions

### Git / Deployment
- commit and push changes after meaningful work is complete
- GitHub Pages is the web host, so pushes are required before Berto can test live behavior
- keep working tree clean when possible
- the public publish tree is [docs/](/Users/bedergez/Code/Codex/Briefing_claude/docs)
- repo-only files should not be added to the published web root

### Ignore Rules
Important ignored items:
- `.env.local`
- `__pycache__/`
- `*.pyc`
- `.DS_Store`

### Editing Rules
- prefer editing the real active source file, not the published `docs/` copy
- keep `docs/` as the public output tree

---

## Current Product Decisions

### Briefing
- keep focus on points, miles, travel
- `Churning` stays separate because it has a different digest structure
- `Reddit` should stay curated and focused
- `Tools` should stay a utility shelf, not a pseudo-feed
- source failures on the Points page should be quiet:
  - failed source load = `✗`
  - real empty source = `0`
  - do not show a noisy error box for source failures

### Points
- active news source cap is currently `9`
- source presets currently include:
  - `Lean 6`
  - `Core`
  - `Travel`
  - `Banks`
  - `All 9`
- article controls currently include:
  - `Hide`
  - `Mute today`

### Tools
- keep the layout flat rather than grouping by provider columns
- current filter set:
  - `All`
  - `Dining`
  - `Transfer`
  - `Hotels`
  - `Cards`
  - `Calculators`

### Nextcard
- Nextcard currently uses the stable articles-page + sitemap-date approach

---

## Working Rules

At the start of a session:
1. read this file
2. assume the task is for the main Briefing app unless clearly stated otherwise
3. work in the source files, then sync to `docs/` for deployment

If task is for Briefing:
- usually edit [dev.html](/Users/bedergez/Code/Codex/Briefing_claude/dev.html) first

Always prefer the current architecture over older assumptions.
