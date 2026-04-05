# Briefing / Homes — Project Notes

> This is the current operating document for the repo.
> Read it at the start of a session before making changes.

**Repo:** [https://github.com/bdergez/briefing](https://github.com/bdergez/briefing)  
**Owner:** Berto

**Main app prod:** [https://bdergez.github.io/briefing/](https://bdergez.github.io/briefing/)  
**Main app dev:** [https://bdergez.github.io/briefing/dev.html](https://bdergez.github.io/briefing/dev.html)

**Homes app prod:** [https://bdergez.github.io/briefing/homes/](https://bdergez.github.io/briefing/homes/)  
**Legacy Homes URL:** [https://bdergez.github.io/briefing/homes.html](https://bdergez.github.io/briefing/homes.html)  
This legacy URL should remain as a redirect to `/homes/`.

**GitHub Pages publish root:** `docs/`  
Only public web assets should live in the published Pages root.

---

## What Exists Now

This repo now contains **two related but separate web apps**:

1. **Briefing**
   - Main Points & Miles dashboard
   - Hosted on GitHub Pages
   - Main tabs:
     - `💳 Points`
     - `🤝 Churning`
     - `🌐 Reddit`
     - `🧰 Tools`

2. **Homes Dash**
   - Separate standalone housing/listings app
   - Lives under `/homes/`
   - No longer part of the main app tab flow

The old “Homes inside Briefing” setup is no longer the intended architecture.

---

## Current Versions

- `dev.html`: `1.6.20-dev`
- `index.html`: `1.6.20`
- `homes/index.html`: `homes-1.1.1`

Update these when appropriate as part of changes.

---

## Main App Architecture

### Purpose
The main app is a personal points / miles / travel dashboard.

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
  - example: `1.6.14-dev` promotes to `1.6.14`
- when the minor version changes, the patch version resets
  - example: `1.5.x` → `1.6.0`

---

## Homes App Architecture

### Purpose
Homes Dash is a separate housing/listings watchlist app.

### Important Product Rules
- Homes is **standalone**
- Homes is **not** part of the main app navigation anymore
- Homes changes can go directly to production unless Berto asks for a separate dev path
- only **real listing data** should be shown
- currently live imported markets are:
  - `Miami Area`
  - `Miami Beach`
- other configured markets can exist as optional locations, but should show empty state unless real data exists

### Homes Files

| File | Purpose |
| --- | --- |
| [homes/index.html](/Users/bedergez/Code/Codex/Briefing_claude/homes/index.html) | Standalone Homes app |
| [docs/homes/index.html](/Users/bedergez/Code/Codex/Briefing_claude/docs/homes/index.html) | Published Homes app copy |
| [homes/manifest.json](/Users/bedergez/Code/Codex/Briefing_claude/homes/manifest.json) | Homes app manifest |
| [homes/service-worker.js](/Users/bedergez/Code/Codex/Briefing_claude/homes/service-worker.js) | Homes app service worker |
| [homes/icon.svg](/Users/bedergez/Code/Codex/Briefing_claude/homes/icon.svg) | Homes app icon |
| [homes/data/house-markets.json](/Users/bedergez/Code/Codex/Briefing_claude/homes/data/house-markets.json) | Homes market metadata / defaults |
| [homes.html](/Users/bedergez/Code/Codex/Briefing_claude/homes.html) | Redirect stub to `/homes/` |

### Homes State

The standalone Homes app has its own localStorage keys:
- `homesDashTheme`
- `homesDashLastVisit`
- `homesDashDisabledListings`
- `homesDashCustomListings`

These should stay separate from the main app.

### Homes Data Flow

The browser does **not** call RentCast directly.

Current flow:

1. Browser opens [homes/index.html](/Users/bedergez/Code/Codex/Briefing_claude/homes/index.html)
2. Homes app fetches markets + listing cards from **Supabase**
3. Listings render from Supabase data
4. RentCast is only used by the **local importer script**

That means page refreshes do **not** consume RentCast API quota.

### Homes Backend / Data

- Backend/data host: **Supabase**
- Upstream source for imported live listings: **RentCast**
- Current importer script:
  - [scripts/import_rentcast_miami.py](/Users/bedergez/Code/Codex/Briefing_claude/scripts/import_rentcast_miami.py)

### Supabase

Current important tables/views:
- `markets`
- `listings`
- `listing_markets`
- `listing_cards`

Frontend read path:
- uses Supabase **publishable** key

Importer write path:
- uses Supabase **secret/service** credential stored locally only

### Homes Market / Source Rules

- default active markets should currently be Miami-focused
- Boston and Stamford are optional, not default
- live imports should be conservative because RentCast quota is limited

### Homes Link Rules

For listing actions:
- prefer Zillow-style direct/search link behavior
- use Google fallback if needed
- do not show fake provider links

---

## Secrets / Security

Never commit secrets.

### Local Secret File
Use:
- [`.env.local`](/Users/bedergez/Code/Codex/Briefing_claude/.env.local)

It is ignored by Git and should stay that way.

Expected keys:
- `RENTCAST_API_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

### Allowed in Frontend
These are acceptable in frontend code:
- Supabase publishable key

### Not Allowed in Frontend
Do not expose:
- Supabase secret/service key
- RentCast API key

### Git
- remote should stay clean
- do **not** embed GitHub tokens in `.git/config`

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
- prefer editing the real active file for the target app
- do not leave fake fallback content live when the product expects real data
- keep Homes and Briefing decoupled

---

## Current Product Decisions

### Briefing
- keep focus on points, miles, travel
- `Churning` stays separate because it has a different digest structure
- `Reddit` should stay curated and focused
- `Tools` should stay a utility shelf, not a pseudo-feed
- source failures on the Points page should be quiet:
  - failed source load = `X`
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

### Homes
- separate product surface
- honest empty states are better than fake listings
- only real imported listing data should appear
- current live emphasis is Miami + Miami Beach

### Nextcard
- in main dev app, Nextcard currently uses the sitemap parser
- title-only cards are preferred over fake slug-based previews

---

## Known Issues / Follow-Up

### Main App
- Nextcard preview quality is limited because sitemap mode is the stable option

### Homes App
- [homes/index.html](/Users/bedergez/Code/Codex/Briefing_claude/homes/index.html) is much cleaner now, but may still contain some old helper code that can be pruned later
- importer automation is intentionally conservative because of RentCast quota limits

---

## Working Rules For Claude

At the start of a session:
1. read this file
2. identify whether the task is for:
   - main Briefing app
   - standalone Homes app
3. work in the correct file set

If task is for Briefing:
- usually edit [dev.html](/Users/bedergez/Code/Codex/Briefing_claude/dev.html) first

If task is for Homes:
- edit [homes/index.html](/Users/bedergez/Code/Codex/Briefing_claude/homes/index.html) directly unless told otherwise

Always prefer the current architecture over older integrated assumptions.
