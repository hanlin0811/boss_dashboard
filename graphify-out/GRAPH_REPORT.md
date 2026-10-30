# Graph Report - boss_dashboard  (2026-10-30)

## Corpus Check
- 25 files · ~106,661 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .toml 1)

## Summary
- 250 nodes · 400 edges · 18 communities
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `554a99e5`
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

## God Nodes (most connected - your core abstractions)
1. `render()` - 24 edges
2. `main()` - 10 edges
3. `humanize()` - 9 edges
4. `run()` - 9 edges
5. `ig-dm` - 9 edges
6. `scale()` - 8 edges
7. `check_voice()` - 8 edges
8. `run()` - 8 edges
9. `ig-viral` - 8 edges
10. `words()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `analyse()` --calls--> `re`  [EXTRACTED]
  .claude/skills/ig-caption/caption.py →   _Bridges community 1 → community 2_
- `check_slop()` --calls--> `re`  [EXTRACTED]
  .claude/skills/ig-human/detect.py →   _Bridges community 3 → community 2_
- `main()` --calls--> `run()`  [EXTRACTED]
  .claude/skills/ig-human/detect.py → .claude/skills/ig-human/detect.py  _Bridges community 3 → community 1_
- `words()` --calls--> `re`  [EXTRACTED]
  .claude/skills/ig-reel/hookscore.py →   _Bridges community 4 → community 2_
- `main()` --calls--> `run()`  [EXTRACTED]
  .claude/skills/ig-reel/hookscore.py → .claude/skills/ig-reel/hookscore.py  _Bridges community 4 → community 1_

## Import Cycles
- None detected.

## Communities (18 total, 0 thin omitted)

### Community 0 - "boss_app.py"
Cohesion: 0.07
Nodes (24): _avg_ticket(), _color_chg(), _day_row(), _delta_pct(), find_alerts(), _fmt_chg(), _item_change(), _item_daily_df() (+16 more)

### Community 1 - "json"
Cohesion: 0.11
Nodes (21): analyse(), main(), render(), render_box(), visible_window(), main(), analyse(), main() (+13 more)

### Community 2 - "re"
Cohesion: 0.15
Nodes (13): _cp(), humanize(), load_lexicon(), main(), _match_case(), pass_invisible(), pass_lexical(), pass_typographic() (+5 more)

### Community 3 - "detect.py"
Cohesion: 0.18
Nodes (12): bar(), check_burstiness(), check_fingerprint(), check_slop(), check_specificity(), check_voice(), clamp(), render() (+4 more)

### Community 4 - "hookscore.py"
Cohesion: 0.22
Nodes (11): bar(), check_address(), check_frontload(), check_length(), check_specificity(), check_stakes(), clamp(), render_one() (+3 more)

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

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Are the 3 inferred relationships involving `render()` (e.g. with `_money()` and `_yoy_color()`) actually correct?**
  _`render()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `boss_app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06693877551020408 - nodes in this community are weakly interconnected._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.10960960960960961 - nodes in this community are weakly interconnected._