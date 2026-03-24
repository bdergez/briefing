# Points & Miles Dashboard — Project Notes

> This is a living document. Claude should read this at the start of every session
> to restore full context without needing to re-read the entire chat history.

**Live site:** https://bdergez.github.io/briefing/
**Dev preview:** https://bdergez.github.io/briefing/dev.html
**Repo:** https://github.com/bdergez/briefing
**Owner:** Berto (bdergez@gmail.com)

---

## What This App Is

A personal Points & Miles dashboard hosted on GitHub Pages. Three tabs:
1. **News Feed** — RSS articles from 5 travel/credit card blogs, filterable by category
2. **r/churning** — Reddit thread digest with comment previews, grouped by day
3. **Communities** — Hot posts from 13 subreddits across 6 categories

No backend. Everything is fetched client-side from public APIs and RSS feeds.

---

## Files

| File | Purpose |
|------|---------|
| `dev.html` | Active development file. All changes go here first. |
| `index.html` | Production file. Promoted from dev.html when ready. Never edit directly. |
| `manifest.json` | PWA manifest for production |
| `manifest-dev.json` | PWA manifest for dev (separate app icon/name so both can be installed) |
| `service-worker.js` | Production service worker (network-first caching) |
| `icon.svg` | Production app icon |
| `icon-dev.svg` | Dev app icon (different color so you can tell them apart on home screen) |
| `push.sh` | Git commit + push script. Run from your local Mac terminal. |
| `PROJECT.md` | This file. |

---

## Dev → Prod Workflow

**All work happens in `dev.html`.** When changes are confirmed working:

1. Claude promotes dev.html → index.html with these transformations:
   - Remove the yellow `#devBanner` strip (CSS block + HTML element)
   - `[DEV] Points & Miles Dashboard` → `Points & Miles Dashboard` (page title)
   - `P&M DEV` → `P&M` (iOS home screen name)
   - `manifest-dev.json` → `manifest.json`
   - `icon-dev.svg` → `icon.svg` (two occurrences)
   - `1.x.y-dev` → `1.x.y` (VERSION string)
   - Replace SW **unregister** block with SW **register** block

2. You run from your terminal:
```bash
./push.sh 'brief description of changes'
```
GitHub Pages deploys in ~60 seconds.

**Important:** `push.sh` must be run from your local Mac, not from Claude's sandbox — the script `cd`s to `/Users/bedergez/Code/Claude Code/Briefing` which only exists on your machine. Claude can prepare everything but can't push.

**Convention — always end a session with a ready-to-run command:** After every batch of changes Claude will always finish with a copy-pasteable `push.sh` command that includes the version number and a concise commit message summarising what changed. Example:
```bash
./push.sh 'v1.5.26 fix mobile skeleton on show more; fix B-01 category header click; fix B-02 communities reload on refresh'
```
This way you can review the summary, then paste it straight into your terminal without having to compose the message yourself.

**Version numbers:** Claude tracks versions in dev (e.g. `1.5.26-dev`). The last version you actually pushed to production was `v1.5.15`. After that, multiple dev versions were built locally. When you do push, the live site will show whatever version is in index.html.

---

## Code Architecture

### Technology
- Single HTML file (no build tools, no frameworks, no npm)
- Vanilla JavaScript + CSS custom properties for theming
- CSS Grid for layout, `@media (min-width: 641px)` for desktop enhancements
- Hosted on GitHub Pages as a PWA (installable on iPhone home screen)

### Three-Tab Structure
```
<div class="tab-bar">          ← tab buttons
<div id="panel-news">          ← News Feed panel
<div id="panel-reddit">        ← r/churning panel
<div id="panel-communities">   ← Communities panel
```
`switchTab(name)` shows/hides panels and updates active tab button.

### Two-Panel Layout (Desktop Only)
Both r/churning and Communities use the same pattern:
```
[280px left nav panel] [1fr right content panel]
grid-template-columns: 280px 1fr
```
On mobile (≤640px): left panel hidden, single column.

CSS classes shared between both pages for visual consistency:
- `.comm-nav-header` — panel title ("Filter" / "Threads (N)")
- `.comm-nav-item` — any clickable row
- `.comm-nav-cat` — day/category header row (uppercase, smaller text)
- `.comm-nav-sub` — thread/subreddit row (indented)
- `.comm-nav-item.active` — highlighted with accent color + left border

### State Variables
```js
// News Feed
let allArticles = [];           // all fetched RSS articles
let activeCategory = 'all';     // current category filter
let activeSources = new Set();  // which source pills are toggled on

// r/churning
let digestPostsData = [];       // all fetched Reddit posts
let digestCommentsData = {};    // postId → topics[] (cached comment previews)
let selectedPostId = null;      // currently shown single thread (null = show all for day)
let selectedDay = null;         // "YYYY-MM-DD" local day key for right panel

// Communities
let selectedCommCat = null;     // category index (0–5), null = all
let selectedCommSub = null;     // subreddit id string, null = show whole category
```

### Key Functions — r/churning

| Function | What it does |
|----------|-------------|
| `loadRedditDigest()` | Fetches hot.json, filters to 7 local days, sorts by day then comments, stores in `digestPostsData` |
| `renderThreadList(posts)` | Renders left nav panel grouped by local day with day headers and thread items |
| `selectDay(day)` | Shows all threads for a day in right panel; sets `selectedPostId = null` |
| `selectThread(postId, day)` | Shows only one thread in right panel; highlights it in nav |
| `digestPostHTML(p, topics)` | Returns HTML for a single thread card with colored left border |
| `churningThreadColor(post)` | Maps flair/title keywords → consistent color per thread type |
| `simplifyThreadTitle(title)` | Strips date suffixes from thread names (e.g. "Daily Discussion - March 23, 2026" → "Daily Discussion") |
| `localDayKey(utcSeconds)` | Converts UTC timestamp → `"YYYY-MM-DD"` in user's LOCAL timezone |
| `postDayLabel(dayKey)` | Converts `"YYYY-MM-DD"` → "Today" / "Yesterday" / "Mon, Mar 23" |
| `fetchThreadComments(postId, limit)` | Fetches top comments for a thread, 3-strategy proxy fallback |

### Key Functions — Communities

| Function | What it does |
|----------|-------------|
| `loadCommunities()` | Fetches all 13 subreddits in parallel, renders skeleton immediately |
| `renderCommNav()` | Renders left nav with categories and subreddits |
| `renderCommDetail()` | Shows/hides category and subreddit blocks based on selection state |
| `selectCommCat(ci)` | Selects a category, shows all its subs |
| `selectCommSub(subId, ci)` | Selects one subreddit, hides others |

### Key Functions — News Feed

| Function | What it does |
|----------|-------------|
| `loadAll()` | Master refresh: fetches all RSS + Reddit + Communities |
| `fetchSource(source)` | Fetches one RSS feed, parses, updates pills + cards |
| `buildPills()` | Creates/resets source filter pills (reuses existing DOM elements on refresh) |
| `renderCards()` | Filters + renders article cards based on active category/source/search |
| `categorize(title, desc)` | Keyword-matches article into a category |

### CORS / Network Strategy

**Reddit API:** Direct fetch with `credentials:'omit'` (required for iOS WebKit ITP). Fallback chain:
1. Direct: `https://www.reddit.com/r/...`
2. Proxy: `https://api.allorigins.win/get?url=...`
3. Proxy: `https://corsproxy.io/?...`

**RSS feeds:** Always go through proxy (no direct CORS support). Same 3-proxy chain via `fetchWithProxy()`.

**Timeouts:** All fetches use `fetchWithTimeout()` (custom AbortController-based, needed because `AbortSignal.timeout` isn't supported on all mobile browsers).

---

## Design System

### Colors (CSS custom properties)
```css
--bg, --card-bg, --text, --subtext, --border  ← light/dark mode aware
--accent: #4f46e5 (indigo)                    ← primary interactive color
--accent-light: #eef2ff                       ← hover/active backgrounds
--tag-bg: #f1f5f9                             ← pill/badge backgrounds
--header-bg: #1a1a2e                          ← dark navy header
```

### Thread Type Colors (r/churning)
Each thread type gets a consistent left-border color:
- Daily Discussion / Daily Thread → `#4f46e5` indigo
- Newbie / Weekly Question → `#0891b2` teal
- News / Update → `#059669` green
- Off Topic → `#7c3aed` purple
- Frustration → `#dc2626` red
- Manufactured Spending → `#d97706` amber
- Data Point → `#2563eb` blue
- Trip Report / Redemption → `#16a34a` green
- What Card / Card Recommendation → `#db2777` pink
- Targeted Offer → `#ea580c` orange
- Default (unknown) → `#ff4500` Reddit orange

### Subreddit Colors (Communities)
Each subreddit has a hardcoded `color` in the COMMUNITIES config array.
Displayed as a colored left border on subreddit blocks (`.sub-block`).
Same pattern as churning thread colors — no colored dots anywhere.

### Breakpoints
- Mobile: `≤640px` — single column, no left nav, compact header
- Desktop: `≥641px` — two-panel layout, sticky left nav, wider cards

---

## Design Decisions & Conventions

**No colored dots** — both pages use colored left borders on cards instead. Dots were removed for visual consistency.

**No "All Communities"** — Communities page defaults to first category on load. Removed the "All" option to match r/churning's day-based nav style.

**Unified left panels** — both pages use 280px wide left nav with identical CSS classes and visual treatment.

**1-column right panel** — both pages show one column of content (not a 2-column grid). Decided during a layout unification pass.

**Section labels** — both pages show a label above the right panel:
- r/churning: `📅 Today` / `📅 Yesterday` / `📅 Mon, Mar 23`
- Communities: `💳 Points & Travel` / `💰 Finance & FIRE` / etc.

**No post counts in section labels** — removed "Finance & FIRE 12 posts" → just "Finance & FIRE".

**Stickied posts** — kept for r/churning (Daily Discussion is stickied and is the most valuable content), filtered out for Communities (stickied = mod meta posts).

**Day bucketing = local timezone** — always use `localDayKey(utcSeconds)` and `postDayLabel(dayKey)`. Never use `Math.floor(created_utc / 86400)` directly — that's UTC and causes a 1-day shift for US users.

**CSS ordering gotcha** — `.churning-extra { display: none !important }` needs `!important` because `.digest-day-header { display: flex }` is declared after it and would otherwise win.

**Edit tool requires prior read** — Claude's Edit tool will fail if the file hasn't been read in the current session. Always read the relevant section before editing.

---

## Known Issues & Backlog

| ID | Area | Description | Priority | Status |
|----|------|-------------|----------|--------|
| B-01 | Communities | Category headers still have `cursor:pointer` and `onclick="toggleCategory"` even though the collapse toggle is hidden. Clicking accidentally collapses the content with no visual indicator. Fix: remove `onclick` and `cursor:pointer` from `.category-header`. | Medium | Open |
| B-02 | News Feed | Clicking Refresh re-fetches all 13 Communities subreddits and resets nav position. Communities should load once and refresh on its own timer. | Medium | Open |
| B-03 | r/churning Desktop | No obvious way to go back to "all threads for a day" after selecting a single thread — you have to know to click the day header again. | Low | Open |
| B-04 | r/churning Mobile | If user taps "Show less" while background comment fetches are in-flight after "Show more", affected cards get stuck on loading skeleton. | Low | Open |
| B-05 | News Feed | The 🆕 New filter uses `lastVisitTime`. On first visit everything shows as "New" since timestamp defaults to 0. Verify localStorage save/restore is working. | Low | Open |

---

## Recently Fixed

| ID | Area | Description | Fixed In |
|----|------|-------------|----------|
| F-01 | r/churning | Thread dates off by one day (today → yesterday). UTC day bucketing didn't match user's local timezone. Fixed with `localDayKey()` helper throughout. | v1.5.26-dev |
| F-02 | News Feed | Source pills duplicated on every Refresh. `buildPills()` was appending new pills without checking for existing ones. | v1.5.25 |
| F-03 | r/churning Mobile | Hidden day headers visible above "Show more" button due to CSS specificity (display:flex overriding display:none). Fixed with `!important` + restructured DOM order. | v1.5.24-dev |
| F-04 | r/churning Mobile | No comment previews after tapping "Show more". Added background fetches for newly revealed posts. | v1.5.24-dev |
| F-05 | r/churning | Clicking a thread in a different day did nothing. Fixed `selectThread(postId, day)` to switch days first. | v1.5.20-dev |
| F-06 | Communities | Collapse toggle (▼) was confusing after removing "All Communities" mode. Removed with `display:none`. | v1.5.18-dev |
| F-07 | r/churning | Thread type colors added — each thread type gets a consistent colored left border. | v1.5.17-dev |
| F-08 | r/churning | Thread panel redesigned to match Communities nav style with day-group headers. | v1.5.16-dev |
| F-09 | Both pages | Unified left panel width to 280px, removed colored dots, replaced with colored left borders. | v1.5.15 |

---

## Sources & Communities Config

### News Feed Sources
```
Doctor of Credit (DoC)    — #e53e3e red   — doctorofcredit.com/feed/
FrequentMiler (FM)        — #2b6cb0 blue  — frequentmiler.com/feed/
One Mile at a Time (OMAAT)— #6b46c1 purple— onemileatatime.com/feed/
View From The Wing (VFTW) — #2f855a green — viewfromthewing.com/feed/
Miles to Memories (MtM)  — #d97706 amber — milestomemories.com/feed/
```

### Communities
```
💳 Points & Travel:  r/awardtravel, r/CreditCards, r/ChaseSapphire
💰 Finance & FIRE:   r/personalfinance, r/financialindependence, r/Bogleheads, r/investing
🤖 AI & Tech:        r/LocalLLaMA, r/MachineLearning, r/singularity
🏃 Health & Wellness: r/nutrition, r/Supplements
🧘 Lifestyle:        r/productivity, r/minimalism, r/Stoicism
🍕 Food & Local:     r/FoodNYC
```
