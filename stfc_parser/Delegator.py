from __future__ import annotations

import logging

from stfc_parser.ShipSpecifier import ShipSpecifier
from stfc_parser.core.Combatants import Combatants
from stfc_parser.core.Crew import Crew
import pandas as pd

from stfc_parser.core.Outcome import Outcome
from stfc_parser.core.Ships import Ships

logger = logging.getLogger(__name__)
class Delegator:

    def __init__(self, combat_df: pd.DataFrame) -> None:
        self.combat_df = combat_df
        players_df = combat_df.attrs.get("players_df")
        if not isinstance(players_df, pd.DataFrame):
            logger.warning("SessionInfo missing players_df in combat_df attrs.")
            players_df = pd.DataFrame()
        fleets_df = combat_df.attrs.get("fleets_df")
        if not isinstance(fleets_df, pd.DataFrame):
            logger.warning("SessionInfo missing fleets_df in combat_df attrs.")
            fleets_df = pd.DataFrame()
        self.players_df = players_df
        self.fleets_df = fleets_df
        self.combatants = Combatants(self.players_df, self.combat_df)
        self.crew = Crew(self.players_df, self.combat_df)
        self.ships = Ships(self.combat_df)
        self.outcome = Outcome(self.players_df)
    #
    # From core/Crew
    #
    def get_captain_name(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return the captain officer name(s) for a combatant and ship."""
        return self.crew.get_captain_name(combatant_name, ship_name)

    def get_1st_officer_name(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return the first officer name(s) for a combatant and ship."""
        return self.crew.get_1st_officer_name(combatant_name, ship_name)

    def get_2nd_officer_name(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return the second officer name(s) for a combatant and ship."""
        return self.crew.get_2nd_officer_name(combatant_name, ship_name)

    def get_bridge_crew(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return the bridge crew officer names for a combatant and ship."""
        return self.crew.get_bridge_crew(combatant_name, ship_name)

    def get_below_deck_officers(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return below-deck officer names for a combatant and ship."""
        return self.crew.get_below_deck_officers(combatant_name, ship_name)

    def all_officer_names(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return all officer names activated by a combatant and ship."""
        return self.crew.all_officer_names(combatant_name, ship_name)

    #
    # From core/Combatants
    #
    def combatant_names(self) -> set[str]:
        return self.combatants.combatant_names()

    def alliance_names(self) -> set[str]:
        return self.combatants.alliance_names()


    #
    # From core/Ships
    #
    def get_every_ship(self) -> set[ShipSpecifier]:
        return self.ships.get_every_ship()

    def get_ships(self, combatant_name: str) -> set[str]:
        return self.ships.get_ships(combatant_name)

    #
    # From core/Outcome
    #
    @classmethod
    def normalize_outcome(cls, outcome: object) -> str:
        """Normalize outcome values into uppercase labels."""
        return Outcome.normalize_outcome(outcome)

    @classmethod
    def is_determinate_outcome(cls, outcome: object) -> bool:
        """Return True when the outcome is a known victory/defeat/partial."""
        return Outcome.is_determinate_outcome(outcome)

    @classmethod
    def outcome_label_emoji(cls, outcome: object) -> tuple[str, str] | None:
        """Return the label and emoji for a known outcome."""
        return Outcome.outcome_label_emoji(outcome)

    @classmethod
    def outcome_emoji(cls, outcome: object) -> str:
        """Return the emoji for a known outcome, or the unknown fallback."""
        return Outcome.outcome_emoji(outcome)

    @classmethod
    def infer_player_outcome(cls, npc_outcome: object) -> str | None:
        """Infer a player outcome based on the NPC outcome."""
        return Outcome.infer_player_outcome(npc_outcome)

    def build_outcome_lookup(self) -> dict[tuple[str, str, str], object]:
        return self.outcome.build_outcome_lookup()