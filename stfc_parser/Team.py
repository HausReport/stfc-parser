from dataclasses import dataclass

from stfc_parser.ShipSpecifier import ShipSpecifier


@dataclass(frozen=True)
class Team:
    members: list[ShipSpecifier]

    def team_name(self) -> str:
        """
        Logic-based name:
        1. If all members share an alliance, return the Alliance.
        2. If it's a single player, return the Player Name.
        3. Otherwise, return 'Lead Player + X others'.
        """
        alliances = {m.normalized_alliance() for m in self.members if m.alliance}

        if len(alliances) == 1:
            return next(iter(alliances))

        if len(self.members) == 1:
            return self.members[0].format_label(include_alliance=False, include_ship=False)

        if len(self.members) > 1:
            lead = self.members[0].normalized_name()
            return f"{lead} +{len(self.members) - 1} others"

        return "Unknown Team"