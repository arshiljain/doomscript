"""Game Mechanics, Tilemaps, Dice & Combat Domain Runtime for DoomScript.

Pure Python standard library implementation of tabletop dice rolling,
weighted loot drop tables, 2D tilemaps with A* navigation and Bresenham line-of-sight,
and turn-based RPG combat resolution.
"""

import math
import random
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Set
import heapq
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.runtime import Record


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


# ==============================================================================
# Advanced Game Deepening: Behavior Trees, Steering Behaviors & Tilemap Physics
# ==============================================================================

class NodeStatus:
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"


class BTNode:
    """Base class for behavior tree nodes."""
    def tick(self, blackboard: Dict[str, Any]) -> str:
        raise NotImplementedError


class SequenceNode(BTNode):
    """Executes child nodes in sequence until one fails or returns running."""
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, blackboard: Dict[str, Any]) -> str:
        for child in self.children:
            status = child.tick(blackboard)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS


class SelectorNode(BTNode):
    """Executes child nodes in sequence until one succeeds or returns running."""
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, blackboard: Dict[str, Any]) -> str:
        for child in self.children:
            status = child.tick(blackboard)
            if status != NodeStatus.FAILURE:
                return status
        return NodeStatus.FAILURE


class InverterNode(BTNode):
    """Inverts SUCCESS to FAILURE and FAILURE to SUCCESS."""
    def __init__(self, child: BTNode):
        self.child = child

    def tick(self, blackboard: Dict[str, Any]) -> str:
        st = self.child.tick(blackboard)
        if st == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        elif st == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        return st


class ActionNode(BTNode):
    """Executes a callable taking blackboard."""
    def __init__(self, action_fn: Callable[[Dict[str, Any]], str]):
        self.action_fn = action_fn

    def tick(self, blackboard: Dict[str, Any]) -> str:
        res = self.action_fn(blackboard)
        return str(res) if res in (NodeStatus.SUCCESS, NodeStatus.FAILURE, NodeStatus.RUNNING) else NodeStatus.SUCCESS


class ConditionNode(BTNode):
    """Evaluates a boolean predicate taking blackboard."""
    def __init__(self, condition_fn: Callable[[Dict[str, Any]], bool]):
        self.condition_fn = condition_fn

    def tick(self, blackboard: Dict[str, Any]) -> str:
        return NodeStatus.SUCCESS if self.condition_fn(blackboard) else NodeStatus.FAILURE


class BehaviorTree:
    """Behavior Tree engine with blackboard memory."""
    def __init__(self, root: BTNode, blackboard: Optional[Dict[str, Any]] = None):
        self.root = root
        self.blackboard: Dict[str, Any] = blackboard if blackboard is not None else {}

    def tick(self) -> str:
        return self.root.tick(self.blackboard)


class SteeringBehaviors:
    """Craig Reynolds autonomous agent steering behaviors."""

    @staticmethod
    def _truncate(v: Tuple[float, float], max_val: float) -> Tuple[float, float]:
        mag = math.hypot(v[0], v[1])
        if mag > max_val and mag > 0:
            scale = max_val / mag
            return v[0] * scale, v[1] * scale
        return v

    @classmethod
    def seek(
        cls,
        pos: Tuple[float, float],
        vel: Tuple[float, float],
        target: Tuple[float, float],
        max_speed: float = 4.0,
        max_force: float = 0.2,
    ) -> Tuple[float, float]:
        """Calculates steering force towards target."""
        desired_x = target[0] - pos[0]
        desired_y = target[1] - pos[1]
        dist = math.hypot(desired_x, desired_y)
        if dist < 1e-6:
            return 0.0, 0.0
        desired = (desired_x * (max_speed / dist), desired_y * (max_speed / dist))
        steer = (desired[0] - vel[0], desired[1] - vel[1])
        return cls._truncate(steer, max_force)

    @classmethod
    def flee(
        cls,
        pos: Tuple[float, float],
        vel: Tuple[float, float],
        target: Tuple[float, float],
        max_speed: float = 4.0,
        max_force: float = 0.2,
    ) -> Tuple[float, float]:
        """Calculates steering force away from target."""
        sf = cls.seek(pos, vel, target, max_speed, max_force)
        return -sf[0], -sf[1]

    @classmethod
    def arrive(
        cls,
        pos: Tuple[float, float],
        vel: Tuple[float, float],
        target: Tuple[float, float],
        slowing_radius: float = 10.0,
        max_speed: float = 4.0,
        max_force: float = 0.2,
    ) -> Tuple[float, float]:
        """Arrives smoothly at target slowing down within radius."""
        desired_x = target[0] - pos[0]
        desired_y = target[1] - pos[1]
        dist = math.hypot(desired_x, desired_y)
        if dist < 1e-6:
            return -vel[0], -vel[1]

        target_speed = max_speed * (dist / slowing_radius) if dist < slowing_radius else max_speed
        desired = (desired_x * (target_speed / dist), desired_y * (target_speed / dist))
        steer = (desired[0] - vel[0], desired[1] - vel[1])
        return cls._truncate(steer, max_force)

    @classmethod
    def flock(
        cls,
        agent_pos: Tuple[float, float],
        agent_vel: Tuple[float, float],
        boids: List[Dict[str, Any]],
        neighbor_dist: float = 15.0,
        sep_dist: float = 5.0,
        max_speed: float = 4.0,
        max_force: float = 0.2,
    ) -> Tuple[float, float]:
        """Calculates flocking force (Separation + Alignment + Cohesion)."""
        sep_x, sep_y = 0.0, 0.0
        align_x, align_y = 0.0, 0.0
        coh_x, coh_y = 0.0, 0.0
        n_neighbors = 0
        n_sep = 0

        for b in boids:
            bx, by = b["pos"]
            dx = agent_pos[0] - bx
            dy = agent_pos[1] - by
            d = math.hypot(dx, dy)
            if 0 < d < neighbor_dist:
                n_neighbors += 1
                bvx, bvy = b.get("vel", (0.0, 0.0))
                align_x += bvx
                align_y += bvy
                coh_x += bx
                coh_y += by
                if d < sep_dist:
                    n_sep += 1
                    sep_x += (dx / d) / d
                    sep_y += (dy / d) / d

        force_x, force_y = 0.0, 0.0
        if n_sep > 0:
            force_x += sep_x * 1.5
            force_y += sep_y * 1.5

        if n_neighbors > 0:
            # Alignment
            avg_vx = align_x / n_neighbors
            avg_vy = align_y / n_neighbors
            force_x += (avg_vx - agent_vel[0]) * 1.0
            force_y += (avg_vy - agent_vel[1]) * 1.0

            # Cohesion
            center_x = coh_x / n_neighbors
            center_y = coh_y / n_neighbors
            seek_force = cls.seek(agent_pos, agent_vel, (center_x, center_y), max_speed, max_force)
            force_x += seek_force[0] * 1.0
            force_y += seek_force[1] * 1.0

        return cls._truncate((force_x, force_y), max_force)


class TilemapPhysics:
    """2D grid tilemap collision resolution with slopes and Amanatides-Woo raycasting."""

    @classmethod
    def resolve_box(
        cls,
        box_pos: Tuple[float, float],
        box_size: Tuple[float, float],
        box_vel: Tuple[float, float],
        tilemap: Any,
        tile_size: float = 1.0,
    ) -> Dict[str, Any]:
        """Resolves AABB box collision against solid and slope tiles."""
        x, y = box_pos
        w, h = box_size
        vx, vy = box_vel

        # Move X
        new_x = x + vx
        # Check tiles overlapping in X
        min_tx = int(math.floor(new_x / tile_size))
        max_tx = int(math.floor((new_x + w - 1e-4) / tile_size))
        min_ty = int(math.floor(y / tile_size))
        max_ty = int(math.floor((y + h - 1e-4) / tile_size))

        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                t_val = game_tilemap_get(tilemap, tx, ty)
                if t_val in (1, "solid", "#"):
                    if vx > 0:
                        new_x = tx * tile_size - w
                        vx = 0.0
                    elif vx < 0:
                        new_x = (tx + 1) * tile_size
                        vx = 0.0

        # Move Y
        new_y = y + vy
        min_tx = int(math.floor(new_x / tile_size))
        max_tx = int(math.floor((new_x + w - 1e-4) / tile_size))
        min_ty = int(math.floor(new_y / tile_size))
        max_ty = int(math.floor((new_y + h - 1e-4) / tile_size))

        on_ground = False
        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                t_val = game_tilemap_get(tilemap, tx, ty)
                if t_val in (1, "solid", "#"):
                    if vy > 0:
                        new_y = ty * tile_size - h
                        vy = 0.0
                        on_ground = True
                    elif vy < 0:
                        new_y = (ty + 1) * tile_size
                        vy = 0.0

        return {
            "pos": (round(new_x, 4), round(new_y, 4)),
            "vel": (round(vx, 4), round(vy, 4)),
            "on_ground": on_ground,
        }

    @classmethod
    def raycast_grid(
        cls,
        p0: Tuple[float, float],
        p1: Tuple[float, float],
        tilemap: Any,
        tile_size: float = 1.0,
    ) -> Optional[Dict[str, Any]]:
        """Amanatides-Woo fast voxel grid ray traversal."""
        x0, y0 = p0
        x1, y1 = p1
        dx = x1 - x0
        dy = y1 - y0

        gx = int(math.floor(x0 / tile_size))
        gy = int(math.floor(y0 / tile_size))
        target_gx = int(math.floor(x1 / tile_size))
        target_gy = int(math.floor(y1 / tile_size))

        step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
        step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)

        delta_tx = abs(tile_size / dx) if dx != 0 else float("inf")
        delta_ty = abs(tile_size / dy) if dy != 0 else float("inf")

        if step_x > 0:
            max_tx = ((gx + 1) * tile_size - x0) / dx
        elif step_x < 0:
            max_tx = (gx * tile_size - x0) / dx
        else:
            max_tx = float("inf")

        if step_y > 0:
            max_ty = ((gy + 1) * tile_size - y0) / dy
        elif step_y < 0:
            max_ty = (gy * tile_size - y0) / dy
        else:
            max_ty = float("inf")

        hit_normal = (0, 0)
        while True:
            t_val = game_tilemap_get(tilemap, gx, gy)
            if t_val in (1, "solid", "#"):
                return {
                    "hit_tile": (gx, gy),
                    "normal": hit_normal,
                }

            if gx == target_gx and gy == target_gy:
                break

            if max_tx < max_ty:
                max_tx += delta_tx
                gx += step_x
                hit_normal = (-step_x, 0)
            else:
                max_ty += delta_ty
                gy += step_y
                hit_normal = (0, -step_y)

        return None


def game_create_behavior_tree(root: BTNode, blackboard: Optional[Dict[str, Any]] = None) -> BehaviorTree:
    """Creates a new Behavior Tree."""
    return BehaviorTree(root, blackboard)


def game_steering_seek(pos: Tuple[float, float], vel: Tuple[float, float], target: Tuple[float, float]) -> Tuple[float, float]:
    """Calculates steering force towards target."""
    return SteeringBehaviors.seek(pos, vel, target)


def game_tilemap_resolve(pos: Tuple[float, float], size: Tuple[float, float], vel: Tuple[float, float], tilemap: Any) -> Dict[str, Any]:
    """Resolves AABB box collision against tilemap."""
    return TilemapPhysics.resolve_box(pos, size, vel, tilemap)


# ==============================================================================
# 5. ADVANCED GAME MECHANICS & AI ENGINES
# ==============================================================================

class MinimaxAlphaBetaSearch:
    """Minimax adversarial game tree search with alpha-beta pruning."""

    def __init__(self, max_depth: int = 4):
        self.max_depth = max(1, int(max_depth))
        self.nodes_evaluated = 0

    def search(
        self,
        state: Any,
        depth: Optional[int] = None,
        is_maximizing: bool = True,
        get_moves_fn: Optional[Callable[[Any], List[Any]]] = None,
        apply_move_fn: Optional[Callable[[Any, Any], Any]] = None,
        evaluate_fn: Optional[Callable[[Any], float]] = None,
        is_terminal_fn: Optional[Callable[[Any], bool]] = None,
    ) -> Record:
        """Executes depth-limited alpha-beta minimax search."""
        self.nodes_evaluated = 0
        search_depth = self.max_depth if depth is None else int(depth)

        # Default fallback helpers if working with standard grid/board dictionaries
        if get_moves_fn is None:
            def get_moves_fn(s: Any) -> List[Any]:
                if isinstance(s, dict) and "legal_moves" in s:
                    return list(s["legal_moves"])
                if hasattr(s, "get_legal_moves"):
                    return s.get_legal_moves()
                return []

        if apply_move_fn is None:
            def apply_move_fn(s: Any, m: Any) -> Any:
                if hasattr(s, "make_move"):
                    return s.make_move(m)
                if isinstance(s, dict):
                    nxt = dict(s)
                    nxt["last_move"] = m
                    return nxt
                return s

        if evaluate_fn is None:
            def evaluate_fn(s: Any) -> float:
                if hasattr(s, "evaluate"):
                    return float(s.evaluate())
                if isinstance(s, dict):
                    return float(s.get("score", 0.0))
                return 0.0

        if is_terminal_fn is None:
            def is_terminal_fn(s: Any) -> bool:
                if hasattr(s, "is_terminal"):
                    return bool(s.is_terminal())
                if isinstance(s, dict):
                    return bool(s.get("is_over", False))
                return False

        def _minimax(
            curr_state: Any,
            curr_depth: int,
            alpha: float,
            beta: float,
            maximizing: bool,
        ) -> Tuple[float, Any]:
            self.nodes_evaluated += 1

            if curr_depth == 0 or is_terminal_fn(curr_state):
                return evaluate_fn(curr_state), None

            moves = get_moves_fn(curr_state)
            if not moves:
                return evaluate_fn(curr_state), None

            best_move = moves[0]

            if maximizing:
                max_eval = -float("inf")
                for move in moves:
                    next_state = apply_move_fn(curr_state, move)
                    eval_score, _ = _minimax(next_state, curr_depth - 1, alpha, beta, False)
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_move = move
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break  # Beta cutoff
                return max_eval, best_move
            else:
                min_eval = float("inf")
                for move in moves:
                    next_state = apply_move_fn(curr_state, move)
                    eval_score, _ = _minimax(next_state, curr_depth - 1, alpha, beta, True)
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_move = move
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break  # Alpha cutoff
                return min_eval, best_move

        best_score, best_mv = _minimax(
            state,
            search_depth,
            -float("inf"),
            float("inf"),
            is_maximizing,
        )

        return Record({
            "best_move": best_mv,
            "best_score": round(float(best_score), 4),
            "nodes_evaluated": self.nodes_evaluated,
            "depth_reached": search_depth,
        })


class JumpPointSearchGrid:
    """Jump Point Search (JPS) pathfinder on uniform cost 2D grids (Harabor-Grastien)."""

    def __init__(self, grid: List[List[Any]], obstacle_val: Any = 1):
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0
        self.grid = grid
        self.obstacle_val = obstacle_val

    def is_walkable(self, x: int, y: int) -> bool:
        """Checks if grid cell is inside bounds and not an obstacle."""
        if 0 <= x < self.width and 0 <= y < self.height:
            cell = self.grid[y][x]
            return cell != self.obstacle_val and cell not in ("#", "solid")
        return False

    def _jump(self, x: int, y: int, dx: int, dy: int, goal_x: int, goal_y: int) -> Optional[Tuple[int, int]]:
        """Recursively advances in direction (dx, dy) until a jump point or obstacle is reached."""
        nx = x + dx
        ny = y + dy

        if not self.is_walkable(nx, ny):
            return None

        if nx == goal_x and ny == goal_y:
            return (nx, ny)

        # Diagonal movement
        if dx != 0 and dy != 0:
            # Check forced neighbors for diagonal step
            if (self.is_walkable(nx - dx, ny + dy) and not self.is_walkable(nx - dx, ny)) or \
               (self.is_walkable(nx + dx, ny - dy) and not self.is_walkable(nx, ny - dy)):
                return (nx, ny)

            # Check horizontal and vertical sub-branches
            if self._jump(nx, ny, dx, 0, goal_x, goal_y) is not None or \
               self._jump(nx, ny, 0, dy, goal_x, goal_y) is not None:
                return (nx, ny)
        else:
            # Horizontal movement
            if dx != 0:
                if (self.is_walkable(nx + dx, ny + 1) and not self.is_walkable(nx, ny + 1)) or \
                   (self.is_walkable(nx + dx, ny - 1) and not self.is_walkable(nx, ny - 1)):
                    return (nx, ny)
            # Vertical movement
            else:
                if (self.is_walkable(nx + 1, ny + dy) and not self.is_walkable(nx + 1, ny)) or \
                   (self.is_walkable(nx - 1, ny + dy) and not self.is_walkable(nx - 1, ny)):
                    return (nx, ny)

        return self._jump(nx, ny, dx, dy, goal_x, goal_y)

    def _pruned_neighbors(self, x: int, y: int, px: Optional[int], py: Optional[int]) -> List[Tuple[int, int, int, int]]:
        """Returns directions (dx, dy) allowed by natural and forced neighbor pruning."""
        dirs = []
        if px is None or py is None:
            # Start node: search all 8 directions
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx != 0 or dy != 0:
                        dirs.append((dx, dy))
            return [(x, y, dx, dy) for dx, dy in dirs]

        dx = 1 if x > px else (-1 if x < px else 0)
        dy = 1 if y > py else (-1 if y < py else 0)

        # Diagonal step
        if dx != 0 and dy != 0:
            if self.is_walkable(x, y + dy):
                dirs.append((0, dy))
            if self.is_walkable(x + dx, y):
                dirs.append((dx, 0))
            if self.is_walkable(x + dx, y + dy) and (self.is_walkable(x, y + dy) or self.is_walkable(x + dx, y)):
                dirs.append((dx, dy))
            # Forced neighbors
            if not self.is_walkable(x - dx, y) and self.is_walkable(x, y + dy):
                dirs.append((-dx, dy))
            if not self.is_walkable(x, y - dy) and self.is_walkable(x + dx, y):
                dirs.append((dx, -dy))
        else:
            # Horizontal step
            if dx != 0:
                if self.is_walkable(x + dx, y):
                    dirs.append((dx, 0))
                if not self.is_walkable(x, y + 1) and self.is_walkable(x + dx, y + 1):
                    dirs.append((dx, 1))
                if not self.is_walkable(x, y - 1) and self.is_walkable(x + dx, y - 1):
                    dirs.append((dx, -1))
            # Vertical step
            else:
                if self.is_walkable(x, y + dy):
                    dirs.append((0, dy))
                if not self.is_walkable(x + 1, y) and self.is_walkable(x + 1, y + dy):
                    dirs.append((1, dy))
                if not self.is_walkable(x - 1, y) and self.is_walkable(x - 1, y + dy):
                    dirs.append((-1, dy))

        return [(x, y, d_x, d_y) for d_x, d_y in dirs]

    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
    ) -> Record:
        """Finds path from start to goal coordinates using Jump Point Search."""
        sx, sy = int(start[0]), int(start[1])
        gx, gy = int(goal[0]), int(goal[1])

        if not self.is_walkable(sx, sy) or not self.is_walkable(gx, gy):
            return Record({"found": False, "path": [], "path_length": 0, "total_cost": 0.0, "jump_points": []})

        if sx == gx and sy == gy:
            return Record({"found": True, "path": [(sx, sy)], "path_length": 1, "total_cost": 0.0, "jump_points": [(sx, sy)]})

        def heuristic(x1: int, y1: int, x2: int, y2: int) -> float:
            # Octile distance
            dx = abs(x1 - x2)
            dy = abs(y1 - y2)
            return (dx + dy) + (math.sqrt(2.0) - 2.0) * min(dx, dy)

        # Min-heap: (f_score, counter, (x, y))
        counter = 0
        open_heap = []
        heapq.heappush(open_heap, (heuristic(sx, sy, gx, gy), counter, (sx, sy)))

        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = {(sx, sy): 0.0}
        closed_set: Set[Tuple[int, int]] = set()

        while open_heap:
            _, _, curr = heapq.heappop(open_heap)
            if curr in closed_set:
                continue
            closed_set.add(curr)

            cx, cy = curr
            if cx == gx and cy == gy:
                # Reconstruct jump point path
                jp_path = [curr]
                curr_node = curr
                while curr_node in came_from:
                    curr_node = came_from[curr_node]
                    jp_path.append(curr_node)
                jp_path.reverse()

                # Expand jump points into full discrete grid coordinates
                full_path: List[Tuple[int, int]] = [jp_path[0]]
                for i in range(len(jp_path) - 1):
                    p_a = jp_path[i]
                    p_b = jp_path[i + 1]
                    step_x = 1 if p_b[0] > p_a[0] else (-1 if p_b[0] < p_a[0] else 0)
                    step_y = 1 if p_b[1] > p_a[1] else (-1 if p_b[1] < p_a[1] else 0)
                    walk_x, walk_y = p_a[0], p_a[1]
                    while (walk_x, walk_y) != p_b:
                        walk_x += step_x
                        walk_y += step_y
                        full_path.append((walk_x, walk_y))

                return Record({
                    "found": True,
                    "path": full_path,
                    "path_length": len(full_path),
                    "total_cost": round(g_score[curr], 4),
                    "jump_points": jp_path,
                })

            px, py = came_from.get(curr, (None, None))
            neighbors = self._pruned_neighbors(cx, cy, px, py)

            for x, y, dx, dy in neighbors:
                jump_pt = self._jump(x, y, dx, dy, gx, gy)
                if jump_pt and jump_pt not in closed_set:
                    jx, jy = jump_pt
                    step_dist = math.hypot(jx - cx, jy - cy)
                    tentative_g = g_score[curr] + step_dist

                    if tentative_g < g_score.get(jump_pt, float("inf")):
                        came_from[jump_pt] = curr
                        g_score[jump_pt] = tentative_g
                        f = tentative_g + heuristic(jx, jy, gx, gy)
                        counter += 1
                        heapq.heappush(open_heap, (f, counter, jump_pt))

        return Record({"found": False, "path": [], "path_length": 0, "total_cost": 0.0, "jump_points": []})


class BoidsFlockingEngine:
    """Reynolds 2D flocking steering simulation (Separation, Alignment, Cohesion)."""

    def __init__(
        self,
        width: float = 100.0,
        height: float = 100.0,
        max_speed: float = 2.0,
        max_force: float = 0.05,
    ):
        self.width = float(width)
        self.height = float(height)
        self.max_speed = float(max_speed)
        self.max_force = float(max_force)

    def step(
        self,
        boids: List[Dict[str, Any]],
        dt: float = 1.0,
        sep_radius: float = 5.0,
        ali_radius: float = 15.0,
        coh_radius: float = 15.0,
        w_sep: float = 1.5,
        w_ali: float = 1.0,
        w_coh: float = 1.0,
    ) -> List[Dict[str, Any]]:
        """Simulates one time step for a flock of boids."""
        n = len(boids)
        if n == 0:
            return []

        # Parse boids into working list of floats
        coords = []
        vels = []
        for b in boids:
            if isinstance(b, dict):
                x = float(b.get("x", b.get("pos", (0, 0))[0]))
                y = float(b.get("y", b.get("pos", (0, 0))[1]))
                vx = float(b.get("vx", b.get("vel", (0, 0))[0]))
                vy = float(b.get("vy", b.get("vel", (0, 0))[1]))
            elif isinstance(b, (list, tuple)) and len(b) >= 4:
                x, y, vx, vy = float(b[0]), float(b[1]), float(b[2]), float(b[3])
            else:
                x, y, vx, vy = 0.0, 0.0, 1.0, 0.0
            coords.append([x, y])
            vels.append([vx, vy])

        new_boids = []

        for i in range(n):
            px, py = coords[i]
            vx, vy = vels[i]

            # 1. Separation
            sep_x, sep_y = 0.0, 0.0
            sep_count = 0

            # 2. Alignment
            ali_x, ali_y = 0.0, 0.0
            ali_count = 0

            # 3. Cohesion
            coh_x, coh_y = 0.0, 0.0
            coh_count = 0

            for j in range(n):
                if i == j:
                    continue
                ox, oy = coords[j]
                ovx, ovy = vels[j]

                dx = px - ox
                dy = py - oy
                dist = math.hypot(dx, dy)

                if dist < 1e-6:
                    dist = 1e-6

                if dist < sep_radius:
                    # Repulsion inversely proportional to distance
                    sep_x += (dx / dist) / dist
                    sep_y += (dy / dist) / dist
                    sep_count += 1

                if dist < ali_radius:
                    ali_x += ovx
                    ali_y += ovy
                    ali_count += 1

                if dist < coh_radius:
                    coh_x += ox
                    coh_y += oy
                    coh_count += 1

            fx, fy = 0.0, 0.0

            # Compute steering forces
            if sep_count > 0:
                sep_x /= sep_count
                sep_y /= sep_count
                sm = math.hypot(sep_x, sep_y)
                if sm > 0:
                    sep_x = (sep_x / sm) * self.max_speed - vx
                    sep_y = (sep_y / sm) * self.max_speed - vy
                fx += sep_x * w_sep
                fy += sep_y * w_sep

            if ali_count > 0:
                ali_x /= ali_count
                ali_y /= ali_count
                am = math.hypot(ali_x, ali_y)
                if am > 0:
                    ali_x = (ali_x / am) * self.max_speed - vx
                    ali_y = (ali_y / am) * self.max_speed - vy
                fx += ali_x * w_ali
                fy += ali_y * w_ali

            if coh_count > 0:
                target_x = coh_x / coh_count
                target_y = coh_y / coh_count
                des_x = target_x - px
                des_y = target_y - py
                cm = math.hypot(des_x, des_y)
                if cm > 0:
                    des_x = (des_x / cm) * self.max_speed - vx
                    des_y = (des_y / cm) * self.max_speed - vy
                fx += des_x * w_coh
                fy += des_y * w_coh

            # Clamp steering force to max_force
            f_mag = math.hypot(fx, fy)
            if f_mag > self.max_force:
                fx = (fx / f_mag) * self.max_force
                fy = (fy / f_mag) * self.max_force

            # Integrate velocity & position
            nvx = vx + fx * dt
            nvy = vy + fy * dt

            # Clamp velocity to max_speed
            v_mag = math.hypot(nvx, nvy)
            if v_mag > self.max_speed:
                nvx = (nvx / v_mag) * self.max_speed
                nvy = (nvy / v_mag) * self.max_speed

            npx = (px + nvx * dt) % self.width
            npy = (py + nvy * dt) % self.height

            new_boids.append(Record({
                "x": round(npx, 4),
                "y": round(npy, 4),
                "vx": round(nvx, 4),
                "vy": round(nvy, 4),
                "speed": round(math.hypot(nvx, nvy), 4),
            }))

        return new_boids

    def simulate(
        self,
        boids: List[Dict[str, Any]],
        steps: int = 10,
        dt: float = 1.0,
    ) -> Record:
        """Simulates flock over multiple time steps."""
        curr = list(boids)
        for _ in range(max(1, int(steps))):
            curr = self.step(curr, dt=dt)

        speeds = [float(b.speed) for b in curr]
        avg_speed = sum(speeds) / len(speeds) if speeds else 0.0

        return Record({
            "boids": curr,
            "count": len(curr),
            "steps_completed": int(steps),
            "mean_speed": round(avg_speed, 4),
        })


class MCTSNode:
    """Node in Monte Carlo Tree Search."""

    def __init__(self, state: Any, parent: Optional["MCTSNode"] = None, move: Any = None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children: List["MCTSNode"] = []
        self.visits = 0
        self.wins = 0.0

    def is_fully_expanded(self, legal_moves: List[Any]) -> bool:
        return len(self.children) == len(legal_moves)

    def ucb1(self, exploration_constant: float = 1.414) -> float:
        if self.visits == 0:
            return float("inf")
        exploitation = self.wins / self.visits
        exploration = exploration_constant * math.sqrt(math.log(max(1, self.parent.visits)) / self.visits)
        return exploitation + exploration


class MonteCarloTreeSearchMCTS:
    """Monte Carlo Tree Search (MCTS) with UCT selection policy."""

    def __init__(self, iterations: int = 500, exploration_weight: float = 1.414):
        self.iterations = max(10, int(iterations))
        self.exploration_weight = float(exploration_weight)

    def search(
        self,
        initial_state: Any,
        get_moves_fn: Callable[[Any], List[Any]],
        apply_move_fn: Callable[[Any, Any], Any],
        is_terminal_fn: Callable[[Any], bool],
        evaluate_winner_fn: Callable[[Any], float],
    ) -> Record:
        """Executes MCTS from initial state and selects the most robust action."""
        root = MCTSNode(initial_state)

        for _ in range(self.iterations):
            node = root

            # 1. Selection
            while node.children and not is_terminal_fn(node.state):
                legal_moves = get_moves_fn(node.state)
                if not node.is_fully_expanded(legal_moves):
                    break
                node = max(node.children, key=lambda c: c.ucb1(self.exploration_weight))

            # 2. Expansion
            if not is_terminal_fn(node.state):
                legal_moves = get_moves_fn(node.state)
                expanded_moves = {c.move for c in node.children}
                unexpanded = [m for m in legal_moves if m not in expanded_moves]
                if unexpanded:
                    chosen_move = random.choice(unexpanded)
                    next_state = apply_move_fn(node.state, chosen_move)
                    child = MCTSNode(next_state, parent=node, move=chosen_move)
                    node.children.append(child)
                    node = child

            # 3. Simulation (Rollout)
            rollout_state = node.state
            sim_depth = 0
            while not is_terminal_fn(rollout_state) and sim_depth < 50:
                moves = get_moves_fn(rollout_state)
                if not moves:
                    break
                rollout_state = apply_move_fn(rollout_state, random.choice(moves))
                sim_depth += 1

            reward = evaluate_winner_fn(rollout_state)

            # 4. Backpropagation
            curr: Optional[MCTSNode] = node
            while curr is not None:
                curr.visits += 1
                curr.wins += reward
                curr = curr.parent

        if not root.children:
            moves = get_moves_fn(initial_state)
            best_move = moves[0] if moves else None
            return Record({
                "best_move": best_move,
                "visit_count": 0,
                "win_rate": 0.0,
                "total_simulations": self.iterations,
            })

        best_child = max(root.children, key=lambda c: c.visits)
        win_rate = best_child.wins / max(1, best_child.visits)

        return Record({
            "best_move": best_child.move,
            "visit_count": best_child.visits,
            "win_rate": round(win_rate, 4),
            "total_simulations": self.iterations,
        })


# --- Spoken English Game Mechanics Wrappers ---

def game_minimax_search(
    state: Any,
    depth: int = 3,
    maximizing: bool = True,
) -> Record:
    """Searches optimal adversarial move using Minimax with Alpha-Beta pruning."""
    engine = MinimaxAlphaBetaSearch(max_depth=depth)
    return engine.search(state, depth=depth, is_maximizing=maximizing)


def game_jps_path(
    grid: List[List[Any]],
    start: Any,
    goal: Any,
) -> Record:
    """Finds optimal jump point search path on 2D uniform grid."""
    if isinstance(grid, GameTilemap):
        raw_grid = grid.grid
    else:
        raw_grid = grid
    jps = JumpPointSearchGrid(raw_grid)
    return jps.find_path(start, goal)


def game_simulate_flock(
    boids: List[Any],
    steps: int = 10,
    width: float = 100.0,
    height: float = 100.0,
) -> Record:
    """Runs Craig Reynolds Boids flocking steering behavior simulation."""
    flock_engine = BoidsFlockingEngine(width=width, height=height)
    return flock_engine.simulate(boids, steps=steps)


def game_mcts_search(
    state: Any,
    iterations: int = 100,
) -> Record:
    """Executes Monte Carlo Tree Search to determine the best next move."""
    engine = MonteCarloTreeSearchMCTS(iterations=iterations)

    def get_moves(s: Any) -> List[Any]:
        if isinstance(s, dict) and "moves" in s:
            return list(s["moves"])
        if isinstance(s, dict) and "legal_moves" in s:
            return list(s["legal_moves"])
        return [0, 1]

    def apply_move(s: Any, m: Any) -> Any:
        nxt = dict(s)
        nxt["moves"] = [x for x in nxt.get("moves", []) if x != m]
        nxt["history"] = nxt.get("history", []) + [m]
        return nxt

    def is_term(s: Any) -> bool:
        return len(s.get("moves", [])) == 0

    def eval_fn(s: Any) -> float:
        # Simple heuristic on history
        hist = s.get("history", [])
        return 1.0 if hist and hist[-1] == 1 else 0.0

    return engine.search(
        state,
        get_moves_fn=get_moves,
        apply_move_fn=apply_move,
        is_terminal_fn=is_term,
        evaluate_winner_fn=eval_fn,
    )


# ==============================================================================
# HEXAGONAL GRID COORDINATE SYSTEM (AXIAL & CUBE)
# ==============================================================================

class HexagonalGridCoordinates:
    """Axial (q, r) and Cube (x, y, z) coordinate algebra for hexagonal map boards."""

    DIRECTIONS = [
        (1, 0), (1, -1), (0, -1),
        (-1, 0), (-1, 1), (0, 1),
    ]

    @staticmethod
    def axial_to_cube(q: int, r: int) -> Tuple[int, int, int]:
        x = int(q)
        z = int(r)
        y = -x - z
        return (x, y, z)

    @staticmethod
    def cube_to_axial(x: int, y: int, z: int) -> Tuple[int, int]:
        return (int(x), int(z))

    @classmethod
    def distance(cls, q1: int, r1: int, q2: int, r2: int) -> int:
        """Computes shortest path step distance between two hex cells."""
        x1, y1, z1 = cls.axial_to_cube(q1, r1)
        x2, y2, z2 = cls.axial_to_cube(q2, r2)
        return (abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)) // 2

    @classmethod
    def neighbors(cls, q: int, r: int) -> List[Tuple[int, int]]:
        """Returns the 6 direct adjacent neighbors of a hex coordinate."""
        return [(q + dq, r + dr) for dq, dr in cls.DIRECTIONS]

    @classmethod
    def line_draw(cls, q1: int, r1: int, q2: int, r2: int) -> List[Tuple[int, int]]:
        """Computes straight-line path of hexes connecting two coordinates."""
        n = cls.distance(q1, r1, q2, r2)
        if n == 0:
            return [(q1, r1)]

        x1, y1, z1 = cls.axial_to_cube(q1, r1)
        x2, y2, z2 = cls.axial_to_cube(q2, r2)

        results = []
        for i in range(n + 1):
            t = i / max(1, n)
            # Continuous cube interpolation with nudge to avoid edge ambiguity
            fx = x1 + (x2 - x1) * t + 1e-6
            fy = y1 + (y2 - y1) * t + 1e-6
            fz = z1 + (z2 - z1) * t - 2e-6

            # Cube rounding
            rx = round(fx)
            ry = round(fy)
            rz = round(fz)

            x_diff = abs(rx - fx)
            y_diff = abs(ry - fy)
            z_diff = abs(rz - fz)

            if x_diff > y_diff and x_diff > z_diff:
                rx = -ry - rz
            elif y_diff > z_diff:
                ry = -rx - rz
            else:
                rz = -rx - ry

            results.append(cls.cube_to_axial(rx, ry, rz))

        return results

    @classmethod
    def range_query(cls, center_q: int, center_r: int, radius: int) -> List[Tuple[int, int]]:
        """Returns all hexes within distance radius of center."""
        rad = max(0, int(radius))
        results = []
        for q in range(-rad, rad + 1):
            r1 = max(-rad, -q - rad)
            r2 = min(rad, -q + rad)
            for r in range(r1, r2 + 1):
                results.append((center_q + q, center_r + r))
        return results

    @classmethod
    def ring(cls, center_q: int, center_r: int, radius: int) -> List[Tuple[int, int]]:
        """Returns single border ring of hexes at exact distance radius."""
        rad = int(radius)
        if rad <= 0:
            return [(center_q, center_r)]

        results = []
        # Start at direction 4 multiplied by radius
        cur_q = center_q + cls.DIRECTIONS[4][0] * rad
        cur_r = center_r + cls.DIRECTIONS[4][1] * rad

        for side in range(6):
            dq, dr = cls.DIRECTIONS[side]
            for _ in range(rad):
                results.append((cur_q, cur_r))
                cur_q += dq
                cur_r += dr

        return results


# ==============================================================================
# HIERARCHICAL FINITE STATE MACHINE (HFSM)
# ==============================================================================

class HierarchicalFiniteStateMachineHFSM:
    """Hierarchical Finite State Machine with compound states, parent transitions, and active chain."""

    def __init__(
        self,
        initial_state: str,
        states_def: Dict[str, Dict[str, Any]],
        transitions: List[Dict[str, Any]],
    ):
        self.states_def = states_def
        self.transitions = transitions
        self.current_leaf_state = initial_state
        self.active_chain = self._resolve_active_chain(initial_state)
        self.history_transitions: List[str] = []

    def _resolve_active_chain(self, leaf_state: str) -> List[str]:
        chain = []
        curr: Optional[str] = leaf_state
        visited = set()
        while curr and curr not in visited:
            visited.add(curr)
            chain.append(curr)
            st_info = self.states_def.get(curr, {})
            curr = st_info.get("parent")
        chain.reverse()  # Root -> Leaf
        return chain

    def trigger_event(self, event: str) -> Dict[str, Any]:
        """Evaluates active state hierarchy for transitions matching event."""
        fired_transition = None

        # Check from leaf up to root in active chain
        for active_st in reversed(self.active_chain):
            for t in self.transitions:
                if t.get("from") == active_st and t.get("event") == event:
                    fired_transition = t
                    break
            if fired_transition:
                break

        if not fired_transition:
            return {
                "event": event,
                "transition_fired": False,
                "current_state": self.current_leaf_state,
                "active_chain": list(self.active_chain),
            }

        target_state = fired_transition["to"]
        # If target has initial substate, descend to leaf
        curr_target = target_state
        visited = set()
        while curr_target not in visited:
            visited.add(curr_target)
            sub = self.states_def.get(curr_target, {}).get("initial_substate")
            if sub and sub in self.states_def:
                curr_target = sub
            else:
                break

        prev_leaf = self.current_leaf_state
        self.current_leaf_state = curr_target
        self.active_chain = self._resolve_active_chain(curr_target)
        trans_str = f"{prev_leaf} -> {curr_target} on '{event}'"
        self.history_transitions.append(trans_str)

        return {
            "event": event,
            "transition_fired": True,
            "previous_state": prev_leaf,
            "current_state": self.current_leaf_state,
            "active_chain": list(self.active_chain),
            "transition": trans_str,
        }


def game_hex_distance(q1: int, r1: int, q2: int, r2: int) -> int:
    """Calculates hex board step distance between (q1, r1) and (q2, r2)."""
    return HexagonalGridCoordinates.distance(q1, r1, q2, r2)


def game_hex_line(q1: int, r1: int, q2: int, r2: int) -> List[List[int]]:
    """Calculates straight-line hex coordinates between (q1, r1) and (q2, r2)."""
    return [[p[0], p[1]] for p in HexagonalGridCoordinates.line_draw(q1, r1, q2, r2)]


def game_hex_range(q: int, r: int, radius: int) -> List[List[int]]:
    """Returns list of hex coordinates within distance radius."""
    return [[p[0], p[1]] for p in HexagonalGridCoordinates.range_query(q, r, radius)]


def game_hfsm_create(
    initial_state: str,
    states_def: Dict[str, Any],
    transitions: List[Dict[str, Any]],
) -> Record:
    """Initializes a Hierarchical Finite State Machine instance."""
    hfsm = HierarchicalFiniteStateMachineHFSM(initial_state, states_def, transitions)
    return Record({
        "current_state": hfsm.current_leaf_state,
        "active_chain": hfsm.active_chain,
        "instance": hfsm,
    })


def game_hfsm_trigger(machine_record: Any, event: str) -> Record:
    """Triggers event on HFSM instance and transitions state hierarchy."""
    inst = machine_record.instance if hasattr(machine_record, "instance") else machine_record
    res = inst.trigger_event(event)
    if hasattr(machine_record, "current_state"):
        machine_record["current_state"] = res["current_state"]
        machine_record["active_chain"] = res["active_chain"]
    return Record(res)


