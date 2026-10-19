"""Game Mechanics Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class GameDomainParser(DomainParser):
    """Parses spoken-English game mechanics, tilemap, and dice statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # roll dice <notation> into <target>
        m_dice = re.match(
            r"^roll\s+dice\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dice:
            notation = m_dice.group(1).strip()
            target = m_dice.group(2).strip()
            return f"set {target} to game_roll_dice({notation})"

        # pick from loot table <tbl> into <target>
        m_loot = re.match(
            r"^pick\s+from\s+loot\s+table\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_loot:
            tbl = m_loot.group(1).strip()
            target = m_loot.group(2).strip()
            return f"set {target} to game_loot_table_pick({tbl})"

        # create tilemap with width <w> and height <h> [and default <d>] into <target>
        m_map = re.match(
            r"^create\s+tilemap\s+with\s+width\s+(.+?)\s+and\s+height\s+(.+?)(?:\s+and\s+default\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_map:
            w = m_map.group(1).strip()
            h = m_map.group(2).strip()
            d = m_map.group(3).strip() if m_map.group(3) else "0"
            target = m_map.group(4).strip()
            return f"set {target} to game_tilemap_create({w}, {h}, {d})"

        # set tile at x <x> and y <y> in <map> to <val>
        m_set = re.match(
            r"^set\s+tile\s+at\s+x\s+(.+?)\s+and\s+y\s+(.+?)\s+in\s+(.+?)\s+to\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_set:
            x = m_set.group(1).strip()
            y = m_set.group(2).strip()
            tmap = m_set.group(3).strip()
            val = m_set.group(4).strip()
            return f"game_tilemap_set({tmap}, {x}, {y}, {val})"

        # get tile at x <x> and y <y> from <map> into <target>
        m_get = re.match(
            r"^get\s+tile\s+at\s+x\s+(.+?)\s+and\s+y\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_get:
            x = m_get.group(1).strip()
            y = m_get.group(2).strip()
            tmap = m_get.group(3).strip()
            target = m_get.group(4).strip()
            return f"set {target} to game_tilemap_get({tmap}, {x}, {y})"

        # find grid path in <map> from <start> to <goal> using a star into <target>
        m_astar = re.match(
            r"^find\s+grid\s+path\s+in\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+using\s+a\s*star\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_astar:
            tmap = m_astar.group(1).strip()
            start_p = m_astar.group(2).strip()
            goal_p = m_astar.group(3).strip()
            target = m_astar.group(4).strip()
            return f"set {target} to game_grid_astar_path({tmap}, {start_p}, {goal_p})"

        # check line of sight in <map> from <start> to <goal> into <target>
        m_los = re.match(
            r"^(?:check\s+)?line\s+of\s+sight\s+in\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_los:
            tmap = m_los.group(1).strip()
            start_p = m_los.group(2).strip()
            goal_p = m_los.group(3).strip()
            target = m_los.group(4).strip()
            return f"set {target} to game_line_of_sight({tmap}, {start_p}, {goal_p})"

        # create combatant <name> with hp <hp> and attack <atk> and defense <def> into <target>
        m_comb = re.match(
            r"^create\s+combatant\s+(.+?)\s+with\s+hp\s+(.+?)\s+and\s+attack\s+(.+?)\s+and\s+defense\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_comb:
            name = m_comb.group(1).strip()
            hp = m_comb.group(2).strip()
            atk = m_comb.group(3).strip()
            df = m_comb.group(4).strip()
            target = m_comb.group(5).strip()
            return f"set {target} to game_combatant_create({name}, {hp}, {atk}, {df})"

        # resolve turn between attacker <att> and defender <def> into <target>
        m_turn = re.match(
            r"^resolve\s+turn\s+between\s+attacker\s+(.+?)\s+and\s+defender\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_turn:
            att = m_turn.group(1).strip()
            defe = m_turn.group(2).strip()
            target = m_turn.group(3).strip()
            return f"set {target} to game_resolve_turn({att}, {defe})"

        # apply buff <buff> with duration <dur> to <combatant> into <target>
        m_buff = re.match(
            r"^apply\s+buff\s+(.+?)\s+with\s+duration\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_buff:
            buff = m_buff.group(1).strip()
            dur = m_buff.group(2).strip()
            c = m_buff.group(3).strip()
            target = m_buff.group(4).strip()
            return f"set {target} to game_apply_buff({c}, {buff}, {dur})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Game domain does not define declarative blocks")
