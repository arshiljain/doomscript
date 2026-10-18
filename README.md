# DoomScript (`.doom`)

> **English-first programming for mortals.**

DoomScript is a modern programming language that reads like conversational English while compiling directly to native Python Abstract Syntax Trees (AST) and standalone native executables. No boilerplate, no cryptic punctuation, and 100% interoperable with the entire Python ecosystem.

---

## What Makes DoomScript Different

### 1. Natural Function Invocations
```doom
to strike target with amount
    decrease target's health by amount

call strike boss with 100
call strike with boss, 100
```

### 2. Conversational Error Handling
Instead of cryptic `try / except Exception:`, write clean English:
```doom
attempt
    fetch json from "https://api.github.com/data" into response
if it fails
    say "Network connection unavailable. Operating offline."
```

### 3. Built-In SQLite Database Engine
Zero SQL strings required. Save and query records natively in English:
```doom
hero = {name: "Doom Slayer", score: 9999, level: 50}
save record hero into database "scores.db" table "hall_of_fame"

load records from database "scores.db" table "hall_of_fame" into leaderboard
say "Total champions recorded: {count of leaderboard}"
```

### 4. Random Rolls & Loot Picking
```doom
roll between 1 and 20 into d20
pick random from ["Super Shotgun", "Plasma Gun", "BFG 9000"] into loot
shuffle deck
```

### 5. English Aggregates & Statistics
```doom
scores = [15, 30, 45, 60]
total = sum of scores
avg = average of scores
top_hit = highest in scores
lowest_hit = lowest in scores
first_val = first item of scores
last_val = last item of scores
```

### 6. HolyC Audio & 2D Graphics Primitives
```doom
beep 520 hz for 0.1 seconds
play sound "shotgun.wav"

open window "Doom Arena" with width 640, height 480
draw rectangle at 20, 20 with width 600, height 440, color "darkred"
draw circle at 320, 240 with radius 40, color "orange"
draw text "BATTLE ARENA" at 320, 60 with size 20, color "white"
refresh screen
clear screen
```

### 7. Post-Condition Sentences
```doom
say "Warning: Low health!" if player's health is under 20
stop if boss's health is 0
```

### 8. Web & APIs in Plain English
```doom
fetch json from "https://api.github.com/users/octocat" into profile
fetch text from "https://example.com" into page_html
download "https://example.com/asset.wad" into file "asset.wad"
```

### 9. Relative Time & Natural Loops
```doom
wait 1.5 seconds

quest_expiry = 3 days from now
past_event = 5 hours ago

repeat while boss's health is over 50
    strike(boss, 25)

repeat until boss's health is 0
    strike(boss, 10)
```

---

## Interactive REPL Shell

Launch an interactive DoomScript shell anytime:
```bash
python -m doomscript.cli repl
```
```text
DOOM> hero = {name: "Slayer", hp: 100}
DOOM> increase hero's hp by 50
DOOM> say hero's hp
150
```

---

## Standalone Binary Compilation (`doom build`)

Compile any `.doom` file into a standalone, single-file native executable (`.exe`) that runs anywhere without Python installed:
```bash
python -m doomscript.cli build examples/dungeon_crawler.doom --output dist/dungeon_crawler.exe
```

---

## Playable Examples

1. **`examples/dungeon_crawler.doom`**: An interactive RPG battle featuring random dice rolls, dynamic monster encounters, audio hits, SQLite leaderboard logging, and aggregate battle statistics.
2. **`examples/epic_quest.doom`**: Multi-pillar demonstration with 2D graphics rendering, post-conditions, audio, and relative time math.
3. **`examples/cyberdemon.doom`**: Fast combat script with string interpolation and possessive mutations.

---

## VS Code Extension

DoomScript includes a full VS Code extension in [`extensions/doomscript-vscode/`](extensions/doomscript-vscode) (already installed in your VS Code!):
- Highlighting for all English verbs, comparisons, possessives, and f-string template interpolation.
