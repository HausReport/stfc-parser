import logging
from typing import Sequence

import pandas as pd

from stfc_parser.ShipSpecifier import ShipSpecifier

logger = logging.getLogger(__name__)


class FixPlayersDataframe:

    def __init__(self, players_df: pd.DataFrame, combat_df: pd.DataFrame, fleet_df: pd.DataFrame):
        self.players_df = players_df
        self.combat_df = combat_df
        self.fleet_df = fleet_df

    def _fallback_players_df(
        self,  npc_name: str | None
    ) -> pd.DataFrame:
        """Return player rows inferred from combat data when player metadata is missing."""
        required_columns = {
            "attacker_name",
            "attacker_ship",
            "target_name",
            "target_ship",
        }
        if not required_columns.issubset(self.combat_df.columns):
            missing = sorted(required_columns - set(self.combat_df.columns))
            logger.warning(
                "Combat df missing columns for fallback players: %s", missing
            )
            return pd.DataFrame(columns=["Player Name", "Ship Name"])

        frames: list[pd.DataFrame] = []
        for name_col, ship_col in (
            ("attacker_name", "attacker_ship"),
            ("target_name", "target_ship"),
        ):
            subset = (
                self.combat_df.loc[:, [name_col, ship_col]]
                .dropna(how="all")
                .fillna("")
                .astype(str)
                .rename(columns={name_col: "Player Name", ship_col: "Ship Name"})
            )
            frames.append(subset)

        combined = pd.concat(frames, ignore_index=True).drop_duplicates().reset_index(drop=True)
        if npc_name:
            combined = combined[combined["Player Name"].str.strip() != npc_name]
        name_series = combined["Player Name"].fillna("").astype(str).str.strip()
        ship_series = combined["Ship Name"].fillna("").astype(str).str.strip()
        missing_name = (name_series == "") & (ship_series != "")
        if missing_name.any():
            logger.warning(
                "Dropping %s player rows with ship names but no player names.",
                int(missing_name.sum()),
            )
        combined = combined[name_series != ""]
        if combined.empty:
            return pd.DataFrame(columns=["Player Name", "Ship Name"])

        combined = combined.replace({"": pd.NA})
        duplicate_players = combined["Player Name"].duplicated()
        if duplicate_players.any():
            logger.warning(
                "Multiple ships found for players %s; keeping first ship name.",
                ", ".join(combined.loc[duplicate_players, "Player Name"].unique()),
            )

        deduped = (
            combined.groupby("Player Name", sort=False)["Ship Name"]
            .apply(lambda series: series.dropna().iloc[0] if not series.dropna().empty else pd.NA)
            .reset_index()
        )
        return deduped.loc[:, ["Player Name", "Ship Name"]].reset_index(drop=True)

    def _align_players_columns(self, source_df: pd.DataFrame, columns: pd.Index) -> pd.DataFrame:
        """Align inferred player data to the export metadata columns."""
        aligned = {
            column: source_df[column] if column in source_df.columns else pd.NA
            for column in columns
        }
        return pd.DataFrame(aligned)

    def fix(self):
        return self._augment_players_df()

    def _augment_players_df( self) -> pd.DataFrame:
        """Augment player metadata with entries inferred from the combat log."""
        if len(self.players_df) > 1:
            return self.players_df

        npc_name = None
        if not self.players_df.empty:
            npc_name = str(self.players_df.iloc[-1].get("Player Name") or "").strip() or None

        fallback_df = self._fallback_players_df(self.combat_df, npc_name)
        if fallback_df.empty:
            return self.players_df

        aligned_fallback = self._align_players_columns(fallback_df, self.players_df.columns)
        if self.players_df.empty:
            return aligned_fallback

        npc_row = self.players_df.iloc[-1:]
        aligned_fallback = aligned_fallback.dropna(axis="columns", how="all")
        combined = pd.concat([aligned_fallback, npc_row], ignore_index=True)
        return combined.reindex(columns=self.players_df.columns)
