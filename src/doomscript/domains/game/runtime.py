"""Game Mechanics, Tilemaps, Dice & Combat Domain Runtime for DoomScript.

Pure Python standard library implementation of tabletop dice rolling,
weighted loot drop tables, 2D tilemaps with A* navigation and Bresenham line-of-sight,
and turn-based RPG combat resolution.
"""

import math
import random
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR


class GameRuntime(DomainRuntime):
    """Runtime coordinator for game mechanics."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class DiceRollResult(int):
    def __new__(cls, val, rolls=None, modifier=0):
        obj = super().__new__(cls, val)
        obj.rolls = rolls or []
        obj.modifier = modifier
        obj.total = val
        return obj

    def __getitem__(self, key):
        if key == "total":
            return self.total
        if key == "rolls":
            return self.rolls
        if key == "modifier":
            return self.modifier
        raise KeyError(key)

    def get(self, key, default=None):
        if key == "total":
            return self.total
        if key == "rolls":
            return self.rolls
        if key == "modifier":
            return self.modifier
        return default


def game_roll_dice(notation: Any) -> Any:
    """Parse and roll standard tabletop dice notation (e.g. '3d6 + 4', '1d20', '2d10 - 2')."""
    s = str(notation).replace(" ", "")
    m = re.match(r"^(\d+)[dD](\d+)(?:([+-])(\d+))?$", s)
    if not m:
        roll = random.randint(1, 6)
        return DiceRollResult(roll, [roll], 0)

    count = int(m.group(1))
    sides = int(m.group(2))
    sign = m.group(3)
    mod_val = int(m.group(4)) if m.group(4) else 0
    mod = mod_val if sign == "+" else (-mod_val if sign == "-" else 0)

    rolls = [random.randint(1, max(1, sides)) for _ in range(max(1, count))]
    total = sum(rolls) + mod
    return DiceRollResult(max(0, total), rolls, mod)


def game_loot_table_pick(loot_table: Any) -> Dict[str, Any]:
    """Select an item from a weighted loot table: list of dicts with 'item' and 'weight'."""
    items = list(loot_table) if isinstance(loot_table, (list, tuple)) else []
    if not items:
        return {"item": "none", "weight": 0}

    weights = []
    for it in items:
        if isinstance(it, dict):
            weights.append(max(0.001, float(it.get("weight", 1.0))))
        else:
            weights.append(1.0)

    chosen = random.choices(items, weights=weights, k=1)[0]
    return chosen if isinstance(chosen, dict) else {"item": chosen}


class GameTilemap:
    """2D grid tilemap representing game terrain, obstacles, and navigation space."""

    def __init__(self, width: int, height: int, default_val: Any = 0):
        self.width = max(1, int(width))
        self.height = max(1, int(height))
        self.grid = [[default_val for _ in range(self.width)] for _ in range(self.height)]

    def set_tile(self, x: int, y: int, val: Any) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = val

    def get_tile(self, x: int, y: int) -> Any:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None


def game_tilemap_create(width: Any, height: Any, default_val: Any = 0) -> GameTilemap:
    """Create a new 2D tilemap with dimensions width x height."""
    return GameTilemap(int(width), int(height), default_val)


def game_tilemap_set(tilemap: Any, x: Any, y: Any, val: Any) -> Any:
    """Set the tile value at coordinates (x, y) in a tilemap."""
    if isinstance(tilemap, GameTilemap):
        tilemap.set_tile(int(x), int(y), val)
    return tilemap


def game_tilemap_get(tilemap: Any, x: Any, y: Any) -> Any:
    """Retrieve the tile value at coordinates (x, y) from a tilemap."""
    if isinstance(tilemap, GameTilemap):
        return tilemap.get_tile(int(x), int(y))
    return None


def game_grid_astar_path(
    tilemap: Any,
    start_pt: Any,
    goal_pt: Any,
    obstacle_val: Any = 1
) -> List[List[int]]:
    """Find shortest obstacle-avoiding 4-way grid path using A* search."""
    if not isinstance(tilemap, GameTilemap):
        return []

    sx, sy = int(start_pt[0]), int(start_pt[1])
    gx, gy = int(goal_pt[0]), int(goal_pt[1])

    if sx == gx and sy == gy:
        return [[sx, sy]]

    def _h(x, y):
        return abs(x - gx) + abs(y - gy)

    open_set: List[Tuple[float, int, int]] = [(_h(sx, sy), sx, sy)]
    g_score: Dict[Tuple[int, int], float] = {(sx, sy): 0.0}
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    visited: Set[Tuple[int, int]] = set()

    while open_set:
        open_set.sort(key=lambda t: t[0])
        _, cx, cy = open_set.pop(0)

        if cx == gx and cy == gy:
            path = []
            curr = (cx, cy)
            while curr in came_from:
                path.append([curr[0], curr[1]])
                curr = came_from[curr]
            path.append([sx, sy])
            return path[::-1]

        visited.add((cx, cy))

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < tilemap.width and 0 <= ny < tilemap.height:
                if tilemap.grid[ny][nx] == obstacle_val:
                    continue
                if (nx, ny) in visited:
                    continue
                tentative_g = g_score[(cx, cy)] + 1.0
                if tentative_g < g_score.get((nx, ny), float("inf")):
                    came_from[(nx, ny)] = (cx, cy)
                    g_score[(nx, ny)] = tentative_g
                    f = tentative_g + _h(nx, ny)
                    open_set.append((f, nx, ny))

    return []


def game_line_of_sight(tilemap: Any, start_pt: Any, goal_pt: Any, obstacle_val: Any = 1) -> bool:
    """Raycast line of sight between two grid coordinates using Bresenham's line algorithm."""
    if not isinstance(tilemap, GameTilemap):
        return False

    x0, y0 = int(start_pt[0]), int(start_pt[1])
    x1, y1 = int(goal_pt[0]), int(goal_pt[1])

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    curr_x, curr_y = x0, y0
    while True:
        if (curr_x, curr_y) != (x0, y0) and (curr_x, curr_y) != (x1, y1):
            if tilemap.get_tile(curr_x, curr_y) == obstacle_val:
                return False

        if curr_x == x1 and curr_y == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            curr_x += sx
        if e2 < dx:
            err += dx
            curr_y += sy

    return True


class GameCombatant:
    """Represents an RPG entity with health, base stats, and active buffs."""

    def __init__(self, name: str, hp: int, attack: int, defense: int):
        self.name = str(name)
        self.hp = int(hp)
        self.max_hp = int(hp)
        self.attack = int(attack)
        self.defense = int(defense)
        self.buffs: List[Dict[str, Any]] = []

    def is_alive(self) -> bool:
        return self.hp > 0


def game_combatant_create(name: Any, hp: Any, attack: Any, defense: Any) -> GameCombatant:
    """Instantiate a new RPG combatant."""
    return GameCombatant(str(name), int(hp), int(attack), int(defense))


def game_resolve_turn(attacker: Any, defender: Any, multiplier: Any = 1.0) -> Dict[str, Any]:
    """Execute a turn-based combat exchange calculating net damage and remaining HP."""
    def get_attr(obj, *keys):
        for k in keys:
            if isinstance(obj, dict) and k in obj:
                return obj[k]
            if hasattr(obj, k):
                return getattr(obj, k)
        return 0

    def set_attr(obj, key, val):
        if isinstance(obj, dict):
            obj[key] = val
        elif hasattr(obj, key):
            setattr(obj, key, val)

    raw_damage = float(get_attr(attacker, "attack", "atk")) * float(multiplier)
    defense = float(get_attr(defender, "defense", "def"))
    damage = max(1, int(raw_damage - defense))
    cur_hp = int(get_attr(defender, "hp", "health"))
    new_hp = max(0, cur_hp - damage)
    set_attr(defender, "hp", new_hp)

    name_atk = get_attr(attacker, "name") or "Attacker"
    name_def = get_attr(defender, "name") or "Defender"

    return {
        "attacker": name_atk,
        "defender": name_def,
        "damage": damage,
        "defender_hp": new_hp,
        "defender_hp_remaining": new_hp,
        "defeated": new_hp <= 0,
    }


def game_apply_buff(combatant: Any, buff_name: Any, duration: Any = 3, magnitude: Any = 0) -> Any:
    """Apply an active status effect/buff to a combatant."""
    if hasattr(combatant, "buffs") and isinstance(combatant.buffs, list):
        combatant.buffs.append({
            "name": str(buff_name),
            "duration": int(duration),
            "magnitude": magnitude
        })
    if str(buff_name).lower() in ("poison", "burn", "bleed") and magnitude:
        cur_hp = combatant.get("hp") if isinstance(combatant, dict) else getattr(combatant, "hp", 0)
        new_hp = max(0, cur_hp - int(magnitude))
        if isinstance(combatant, dict):
            combatant["hp"] = new_hp
        elif hasattr(combatant, "hp"):
            combatant.hp = new_hp
    return combatant


game_apply_status_effect = game_apply_buff
game_create_combatant = game_combatant_create
game_create_tilemap = game_tilemap_create
game_set_tile = game_tilemap_set
game_get_tile = game_tilemap_get


def game_astar_grid(tilemap: Any, *args) -> List[List[int]]:
    if len(args) == 4:
        start_pt = [int(args[0]), int(args[1])]
        goal_pt = [int(args[2]), int(args[3])]
        path = game_grid_astar_path(tilemap, start_pt, goal_pt)
        return [[p[0], p[1]] for p in path]
    elif len(args) >= 2:
        path = game_grid_astar_path(tilemap, args[0], args[1])
        return [[p[0], p[1]] for p in path]
    return []


def game_has_line_of_sight(tilemap: Any, *args) -> bool:
    if len(args) == 4:
        start_pt = [int(args[0]), int(args[1])]
        goal_pt = [int(args[2]), int(args[3])]
        return game_line_of_sight(tilemap, start_pt, goal_pt)
    elif len(args) >= 2:
        return game_line_of_sight(tilemap, args[0], args[1])
    return False


def game_weighted_choice(*args) -> Any:
    if len(args) == 2:
        items = list(args[0])
        weights = list(args[1])
        return random.choices(items, weights=weights, k=1)[0]
    elif len(args) == 1:
        res = game_loot_table_pick(args[0])
        if isinstance(res, dict) and "item" in res:
            return res["item"]
        return res
    return None


def execute_game_ir(spec_id: str) -> Any:
    """Executes a stored Game IR specification."""
    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    spec = reg.get_spec(spec_id)
    if spec is None:
        raise ValueError(f"Unknown game spec: {spec_id}")
    return GameRuntime().execute_ir(spec, {})
