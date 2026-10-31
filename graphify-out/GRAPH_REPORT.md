# Graph Report - boss_dashboard  (2026-10-31)

## Corpus Check
- 61 files · ~464,816 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: .css 3, (none) 2, .toml 1)

## Summary
- 825 nodes · 1295 edges · 62 communities (60 shown, 2 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 38 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8ba242d0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- boss_app.py
- json
- re
- detect.py
- hookscore.py
- ig-dm
- ig-viral
- ig-caption
- ig-comment
- ig-human
- ig-reel
- ig-reply
- ig-audit
- ig-carousel
- ig-plan
- ig-repurpose
- ig-story
- ig-profile
- assets.mjs
- scenes.mjs
- draw.mjs
- inspect.mjs
- 6. Recipes
- charts.js
- app-draw.mjs
- Imagery
- The run
- The study
- Layout
- Colour
- Scroll scenes
- argparse
- App screens
- Tells — the dated registry
- Type
- beats.py
- Stage
- 7. Tables and lists
- Words
- 2. The run for an app screen
- Critique — judging the render
- tasteskill v2 (`design-taste-frontend`)
- app.json
- 9. Type and colour
- kinds
- 3. The shell
- 4. The canvas and the page title
- 6. Charts
- builder
- commerce
- community
- creator
- devtools
- finance
- markets
- report
- smb-admin
- support
- wallet
- workspace
- 8. Forms and settings

## God Nodes (most connected - your core abstractions)
1. `getOne()` - 31 edges
2. `render()` - 24 edges
3. `search()` - 22 edges
4. `getVideo()` - 19 edges
5. `6. Recipes` - 19 edges
6. `App screens` - 16 edges
7. `The study` - 15 edges
8. `kinds` - 14 edges
9. `Imagery` - 14 edges
10. `line()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `6.4 Marks` --references--> `short()`  [INFERRED]
  .claude/skills/design-taste-frontend/references/app-screens.md → .claude/skills/design-taste-frontend/scripts/assets.mjs
- `7. Signature moves` --references--> `scale()`  [INFERRED]
  .claude/skills/design-taste-frontend/references/motion.md → .claude/skills/ig-human/detect.py
- `run()` --calls--> `sleep()`  [EXTRACTED]
  .claude/skills/design-taste-frontend/scripts/scenes.mjs → .claude/skills/design-taste-frontend/scripts/lib/cdp.mjs

## Import Cycles
- None detected.

## Communities (62 total, 2 thin omitted)

### Community 0 - "boss_app.py"
Cohesion: 0.07
Nodes (24): _avg_ticket(), _color_chg(), _day_row(), _delta_pct(), find_alerts(), _fmt_chg(), _item_change(), _item_daily_df() (+16 more)

### Community 1 - "json"
Cohesion: 0.21
Nodes (10): load_lexicon(), main(), render_report(), analyse(), classify(), load_formulas(), main(), read_rows() (+2 more)

### Community 2 - "re"
Cohesion: 0.18
Nodes (10): _cp(), humanize(), _match_case(), pass_invisible(), pass_lexical(), pass_typographic(), protect_urls(), restore_capitals() (+2 more)

### Community 3 - "detect.py"
Cohesion: 0.18
Nodes (13): bar(), check_burstiness(), check_fingerprint(), check_slop(), check_specificity(), check_voice(), clamp(), main() (+5 more)

### Community 4 - "hookscore.py"
Cohesion: 0.22
Nodes (12): bar(), check_address(), check_frontload(), check_length(), check_specificity(), check_stakes(), clamp(), main() (+4 more)

### Community 5 - "ig-dm"
Cohesion: 0.20
Nodes (9): Before writing, get the specifics, Follow-ups, ig-dm, Never, Output, The collab pitch, The first message to someone warm, The keyword delivery (+1 more)

### Community 6 - "ig-viral"
Cohesion: 0.22
Nodes (8): ig-viral, Output, Step 1: pick the accounts, Step 2: go and look, Step 3: rank it, Step 4: say what it means, carefully, Step 5: turn it into something to shoot, The one idea that makes this worth doing

### Community 7 - "ig-caption"
Cohesion: 0.25
Nodes (7): First, decide which job this caption has, Hashtags, honestly, ig-caption, Rules, Search terms matter more than hashtags now, The loop, The shape

### Community 8 - "ig-comment"
Cohesion: 0.25
Nodes (7): Batch mode, ig-comment, Input, Never, Output, Rules, The nine comment types

### Community 9 - "ig-human"
Cohesion: 0.25
Nodes (7): ig-human, Order of operations, Say this honestly, The five checks, What does NOT get fixed automatically, What gets fixed automatically, Why this matters more on Instagram than it looks

### Community 10 - "ig-reel"
Cohesion: 0.25
Nodes (7): Before you write, Example, ig-reel, On-screen text is a separate script, Rules that make the difference, The loop, The shape

### Community 11 - "ig-reply"
Cohesion: 0.25
Nodes (7): How to reply, ig-reply, Input, Keyword comments, Output, The move most people miss, Triage first

### Community 12 - "ig-audit"
Cohesion: 0.29
Nodes (6): ig-audit, Input, Output, The distinction that saves people months, Then find the pattern, What to actually measure

### Community 13 - "ig-carousel"
Cohesion: 0.29
Nodes (6): Building the files, ig-carousel, Output, Slide copy rules, Structure, When to use it instead of a Reel

### Community 14 - "ig-plan"
Cohesion: 0.29
Nodes (6): ig-plan, Input, Output, The engagement round, which is not optional, What to post, When to post

### Community 15 - "ig-repurpose"
Cohesion: 0.29
Nodes (6): Extract, do not summarise, ig-repurpose, Input, Output, Then build the week, Then pick the format per extract

### Community 16 - "ig-story"
Cohesion: 0.29
Nodes (6): ig-story, Output, Rules, The daily shape, The DM funnel, done honestly, The stickers, and what each is actually for

### Community 17 - "ig-profile"
Cohesion: 0.33
Nodes (5): ig-profile, Input, Output, Score it, Then rewrite, in this order

### Community 18 - "assets.mjs"
Cohesion: 0.07
Nodes (85): AIC_FIELDS, AIC_HEADERS, applyThumb(), ARCHIVE_LICENCE, args, argv, base(), clock() (+77 more)

### Community 19 - "scenes.mjs"
Cohesion: 0.06
Nodes (28): alive(), Browser, findChrome(), Page, sleep(), sweepProfiles(), APP_LEVEL, appMode (+20 more)

### Community 20 - "draw.mjs"
Cohesion: 0.10
Nodes (41): adjustments(), argv, assetQueries(), ASSETS_PATH, briefStop(), briefWords(), deal(), dealHero() (+33 more)

### Community 21 - "inspect.mjs"
Cohesion: 0.07
Nodes (29): allow, appMode, args, asJson, dealtFonts, fails, film, HEIGHT (+21 more)

### Community 22 - "6. Recipes"
Cohesion: 0.06
Nodes (31): 10. Rules for motion, 1. The budget, 2. What strong pages do with motion, 3. Four questions before any animation, 4. Tokens, 5. Scroll behaviours, ranked, 6. Recipes, 7. Signature moves (+23 more)

### Community 23 - "charts.js"
Cohesion: 0.21
Nodes (24): axes(), bars(), dayHeads(), diverging(), frame(), hits(), kindStyle(), lane() (+16 more)

### Community 24 - "app-draw.mjs"
Cohesion: 0.11
Nodes (22): argv, deal(), dealScreen(), dealShell(), dealStyle(), fontLink(), HERE, kebab() (+14 more)

### Community 25 - "Imagery"
Cohesion: 0.09
Nodes (22): 10. Markup and credits, 11. Video, 12. Where pictures and footage go, 1. What the study measured, 2. Decide what imagery exists, 3. Real pictures from the open collections, 4. The dealt photographs, 5. Cropping and placing (+14 more)

### Community 26 - "The run"
Cohesion: 0.11
Nodes (17): 10. Report, 1. Read the brief and the project, 2. Write the argument, 3. Draw the direction, 4. Find the idea, 5. Write the words, 6. Build it, still, 7. Gate (+9 more)

### Community 27 - "The study"
Cohesion: 0.12
Nodes (15): 10. The 25 highest-scored sites and their ideas, 11. How the skill was tested, 12. The October 2026 study: 100 Sites of the Day, 13. The app-screen study, 1. Method and its limits, 2. Scores, 3. Where the idea comes from, 4. Headlines (+7 more)

### Community 28 - "Layout"
Cohesion: 0.15
Nodes (12): 10. How pages fail, 1. What strong pages do, 2. Margins and the grid, 3. Where text sits, 4. Empty space, 5. The frame: margins, balance and titles, 6. Sections: carry the idea, vary the arrangement, 7. Navigation (+4 more)

### Community 29 - "Colour"
Cohesion: 0.17
Nodes (11): 1. What the study measured, 2. The roles, 3. Proportion, 4. Surfaces without lines or shadows, 5. Colour fields, 6. Dark pages, 7. Colour and photographs, 8. Contrast (+3 more)

### Community 30 - "Scroll scenes"
Cohesion: 0.17
Nodes (11): 1. What a scene is, 2. Putting a scene on a page, 3. Filling it, 4. Fitting it to the page, 5. The phone, reduced motion, no script, 6. Checking it, 7. Rules for scenes, 8. When no scene in the library fits (+3 more)

### Community 31 - "argparse"
Cohesion: 0.29
Nodes (5): analyse(), main(), render(), render_box(), visible_window()

### Community 32 - "App screens"
Cohesion: 0.18
Nodes (10): 10. Density, 11. Empty, zero, loading and error states, 12. The phone, 13. House rules for app screens, 14. Tells of generated dashboards, 1. When this applies, 5. KPIs, App screens (+2 more)

### Community 33 - "Tells — the dated registry"
Cohesion: 0.18
Nodes (10): 1. First wave (2023–2024), 2. Second wave (2025), 3. Third wave (2025–2026): the "fix" that became the look, 4. Gallery fashion, banned as house style, 5. Structural tells, 6. Copy tells, 7. Motion tells, 8. Why removal is not enough (+2 more)

### Community 34 - "Type"
Cohesion: 0.18
Nodes (10): 1. What the study measured, 2. The scale: few sizes, far apart, 3. Setting display type, 4. Setting text, 5. Loading the fonts properly, 6. One family or two, 7. Details that separate set type from typed text, 8. Mistakes the inspector cannot see (+2 more)

### Community 35 - "beats.py"
Cohesion: 0.31
Nodes (7): analyse(), main(), pretty(), render(), split_beats(), tc(), words()

### Community 37 - "7. Tables and lists"
Cohesion: 0.20
Nodes (10): 7.1 Rows, 7.2 Header, 7.3 Dividers, 7.4 Figures and alignment, 7.5 Ink inside rows, 7.6 Status pills, 7.7 Media, 7.8 Actions and paging (+2 more)

### Community 38 - "Words"
Cohesion: 0.20
Nodes (9): 1. Write the argument first, 2. The two-line headline, 3. Headline shapes that work, 4. Supporting line, body, buttons, 5. Proof without inventing it, 6. Things that read as generated, 7. Micro-typography, Contents (+1 more)

### Community 39 - "2. The run for an app screen"
Cohesion: 0.22
Nodes (9): 2.1 Inventory the data and the jobs, 2.2 Name the screen's one question, 2.3 Choose a style, 2.4 Build the shell, 2.5 Put in the data, 2.6 Build the states, 2.7 The check, 2.8 Report (+1 more)

### Community 40 - "Critique — judging the render"
Cohesion: 0.22
Nodes (8): 1. How to look, 2. The score, 3. Caps, 4. Writing the critique, 5. What to fix first, 6. When to stop, Contents, Critique — judging the render

### Community 41 - "tasteskill v2 (`design-taste-frontend`)"
Cohesion: 0.29
Nodes (6): Contents, How it works, Install, Notes, Requirements, tasteskill v2 (`design-taste-frontend`)

### Community 42 - "app.json"
Cohesion: 0.33
Nodes (5): about, patterns, shells, styles, version

### Community 43 - "9. Type and colour"
Cohesion: 0.33
Nodes (6): 9.1 Type, 9.2 Colour on light screens, 9.3 Colour on dark screens, 9.4 Surfaces, radius, icons, spacing, 9.5 Default tokens, 9. Type and colour

### Community 44 - "kinds"
Cohesion: 0.40
Nodes (5): note, screens, styles, kinds, analytics

### Community 45 - "3. The shell"
Cohesion: 0.40
Nodes (5): 3.1 Five archetypes, 3.2 Sidebar, 3.3 Top bar, 3.4 Right rail and pinned columns, 3. The shell

### Community 46 - "4. The canvas and the page title"
Cohesion: 0.40
Nodes (5): 4.1 Width and gutters, 4.2 One left edge, one right edge, 4.3 The title, 4.4 Tabs, filters and the date range, 4. The canvas and the page title

### Community 47 - "6. Charts"
Cohesion: 0.40
Nodes (5): 6.1 Which chart for which question, 6.2 One question, one series, 6.3 Axes and gridlines, 6.4 Marks, 6. Charts

### Community 48 - "builder"
Cohesion: 0.50
Nodes (4): note, screens, styles, builder

### Community 49 - "commerce"
Cohesion: 0.50
Nodes (4): note, screens, styles, commerce

### Community 50 - "community"
Cohesion: 0.50
Nodes (4): note, screens, styles, community

### Community 51 - "creator"
Cohesion: 0.50
Nodes (4): note, screens, styles, creator

### Community 52 - "devtools"
Cohesion: 0.50
Nodes (4): note, screens, styles, devtools

### Community 53 - "finance"
Cohesion: 0.50
Nodes (4): note, screens, styles, finance

### Community 54 - "markets"
Cohesion: 0.50
Nodes (4): markets, note, screens, styles

### Community 55 - "report"
Cohesion: 0.50
Nodes (4): report, note, screens, styles

### Community 56 - "smb-admin"
Cohesion: 0.50
Nodes (4): smb-admin, note, screens, styles

### Community 57 - "support"
Cohesion: 0.50
Nodes (4): support, note, screens, styles

### Community 58 - "wallet"
Cohesion: 0.50
Nodes (4): wallet, note, screens, styles

### Community 59 - "workspace"
Cohesion: 0.50
Nodes (4): workspace, note, screens, styles

### Community 60 - "8. Forms and settings"
Cohesion: 0.50
Nodes (4): 8.1 Fields, 8.2 Settings layout, 8.3 Buttons, 8. Forms and settings

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `short()` connect `assets.mjs` to `6. Charts`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `render()` (e.g. with `_money()` and `_yoy_color()`) actually correct?**
  _`render()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `boss_app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06693877551020408 - nodes in this community are weakly interconnected._
- **Why does `App screens` connect `App screens` to `7. Tables and lists`, `2. The run for an app screen`, `9. Type and colour`, `3. The shell`, `4. The canvas and the page title`, `6. Charts`, `8. Forms and settings`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `search()` (e.g. with `searchAic()` and `searchArchive()`) actually correct?**
  _`search()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `assets.mjs` be split into smaller, more focused modules?**
  _Cohesion score 0.06648426812585499 - nodes in this community are weakly interconnected._
- **Why does `6.4 Marks` connect `6. Charts` to `assets.mjs`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._