from __future__ import annotations

import logging

import pandas as pd

from stfc_parser.ShipSpecifier import ShipSpecifier
logger = logging.getLogger(__name__)


class Ships:

    def __init__(self, combat_df: pd.DataFrame):
        # self.players_df = players_df
        self.combat_df = combat_df

    def get_every_ship(self) -> set[ShipSpecifier]:
        """Return unique attacker combinations across the combat log."""
        df = self.combat_df
        cols = ["attacker_name", "attacker_alliance", "attacker_ship"]
        missing = [column for column in cols if column not in df.columns]
        if missing:
            logger.warning(
                "Combat df missing attacker columns for ship roster: %s",
                missing,
            )
            return set()

        # Select your columns first
        unique_combos_df = df.loc[:, cols].dropna(how="all")

        # Convert to string without rebuilding the whole DataFrame index/attrs tree
        # Using 'map' or 'applymap' is often safer in experimental Python versions
        unique_combos_df = unique_combos_df.map(lambda x: "" if x is None or pd.isna(x) else str(x))

        # Clean up duplicates
        unique_combos_df = unique_combos_df.drop_duplicates().reset_index(drop=True)

        return {
            ShipSpecifier(
                name=row["attacker_name"],
                alliance=row["attacker_alliance"],
                ship=row["attacker_ship"],
            )
            for row in unique_combos_df.to_dict(orient="records")
        }

    def get_ships(self, combatant_name: str) -> set[str]:
        """Return all ships used by a combatant in attack events."""
        df = self.combat_df
        event_type = df["event_type"].astype(str).str.lower()
        mask = (event_type == "attack") & (df["attacker_name"] == combatant_name)
        return set(df.loc[mask, "attacker_ship"].dropna().astype(str).unique())
