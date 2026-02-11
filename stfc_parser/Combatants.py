from dataclasses import dataclass

from stfc_parser.ShipSpecifier import ShipSpecifier
from stfc_parser.Team import Team


@dataclass(frozen=True)
class Combatants:
    team_one: Team
    team_two: Team

    def get_all_members(self) -> list[ShipSpecifier]:
        """Return every ship involved in the combat."""
        return list(self.team_one.members) + list(self.team_two.members)

    def format_matchup(self) -> str:
        """Returns a high-level summary, e.g., 'Alliance A vs Player Name'."""
        return f"{self.team_one.team_name()} vs {self.team_two.team_name()}"