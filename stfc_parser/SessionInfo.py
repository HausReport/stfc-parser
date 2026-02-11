from __future__ import annotations

import logging
from typing import Sequence

import pandas as pd

from stfc_parser.Delegator import Delegator
from stfc_parser.ShipSpecifier import ShipSpecifier
from stfc_parser.core.FilterCombatDataframeByCombatant import FilterCombatDataframeByCombatant
from stfc_parser.teams import get_teams_from_players_df, get_combatants_from_df

logger = logging.getLogger(__name__)

class SessionInfo(Delegator):
    """Expose filtered views and helpers for combat session data."""

    def get_combatants(self):
        return get_combatants_from_df(self.players_df)

    def get_teams(self):
        return get_teams_from_players_df(self.players_df)

    def get_combat_df_filtered_by_attackers(
        self,
        specs: Sequence[ShipSpecifier],
    ) -> pd.DataFrame:
        """Return combat rows for any of the provided attacker specs."""
        return FilterCombatDataframeByCombatant._get_combat_df_filtered_by_specs(self.combat_df, specs, "attacker")

    def get_combat_df_filtered_by_targets(
        self,
        specs: Sequence[ShipSpecifier],
    ) -> pd.DataFrame:
        """Return combat rows for any of the provided target specs."""
        return FilterCombatDataframeByCombatant._get_combat_df_filtered_by_specs(self.combat_df, specs, "target")
