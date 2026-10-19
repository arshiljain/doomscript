"""Game Mechanics, Tilemaps, Dice & Combat Domain Pack for DoomScript.

Enables native spoken-English tabletop dice rolling, weighted loot drop tables,
2D tilemaps with A* navigation & line of sight, and turn-based combat via 'use game'.
"""

from typing import List, Optional
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.game.runtime import (
    GameRuntime,
    GameTilemap,
    GameCombatant,
    game_roll_dice,
    game_loot_table_pick,
    game_tilemap_create,
    game_tilemap_set,
    game_tilemap_get,
    game_grid_astar_path,
    game_line_of_sight,
    game_combatant_create,
    game_resolve_turn,
    game_apply_buff,
)
from doomscript.domains.game.parser import GameDomainParser
from doomscript.domains.game.exporter import GameASTExporter


class GameDomain(DomainContract):
    """Domain contract for Game Mechanics & Tilemaps."""

    name = "game"
    aliases = ["gamedev", "rpg"]
    description = "Tabletop dice, 2D tilemaps, A* grid navigation, and RPG combat"
    parser = GameDomainParser()
    runtime = GameRuntime()
    exporter = GameASTExporter()
    capabilities = ["dice", "tilemaps", "astar", "combat", "raycasting"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="roll dice {notation:expr} into {target:ident}",
            description="Rolls standard tabletop dice notation (e.g. '3d6 + 4')",
        ),
        VerbSpec(
            pattern="pick from loot table {tbl:expr} into {target:ident}",
            description="Weighted random selection from loot drops",
        ),
        VerbSpec(
            pattern="create tilemap with width {w:expr} and height {h:expr} into {target:ident}",
            description="Instantiates a 2D grid tilemap",
        ),
        VerbSpec(
            pattern="find grid path in {map:expr} from {start:expr} to {goal:expr} using a star into {target:ident}",
            description="A* pathfinding on 2D tilemap obstacle grid",
        ),
        VerbSpec(
            pattern="create combatant {name:expr} with hp {hp:expr} and attack {atk:expr} and defense {def:expr} into {target:ident}",
            description="Creates an RPG combatant entity",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("roll dice ")
            or s.startswith("pick from loot table ")
            or s.startswith("create tilemap with width ")
            or s.startswith("set tile at x ")
            or s.startswith("get tile at x ")
            or s.startswith("find grid path in ")
            or s.startswith("line of sight in ")
            or s.startswith("check line of sight in ")
            or s.startswith("create combatant ")
            or s.startswith("resolve turn between ")
            or s.startswith("apply buff ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


GAME_DOMAIN = GameDomain()
get_domain_registry().register(GAME_DOMAIN)

__all__ = [
    "GameDomain",
    "GAME_DOMAIN",
    "GameRuntime",
    "GameTilemap",
    "GameCombatant",
    "GameDomainParser",
    "GameASTExporter",
    "game_roll_dice",
    "game_loot_table_pick",
    "game_tilemap_create",
    "game_tilemap_set",
    "game_tilemap_get",
    "game_grid_astar_path",
    "game_line_of_sight",
    "game_combatant_create",
    "game_resolve_turn",
    "game_apply_buff",
]
