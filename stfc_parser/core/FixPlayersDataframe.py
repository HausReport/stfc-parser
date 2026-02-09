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

    def fix(self) -> pd.DataFrame:
        """
        Drop-in replacement for the fix method to handle header recovery,
        outcome propagation, and health reconciliation.
        """

        if len(self.players_df) > 1:
            return self.players_df
        # 1. Identify Participants from shadow data (Attack events)
        # We need the order of appearance to map to Player Fleet 1, 2, 3
        attacks = self.combat_df[self.combat_df['event_type'].str.lower() == 'attack']
        shadow_players = (
            attacks[['attacker_name', 'attacker_alliance', 'attacker_ship']]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # 2. Identify the Enemy (Team 2)
        # Per requirements, Team 2 is the last row of the original players_df or the Enemy Fleet
        npc_row = self.players_df.iloc[-1:] if not self.players_df.empty else pd.DataFrame()
        npc_name = str(npc_row.get("Player Name", pd.Series([""])).iloc[0]).strip()

        # Filter shadow_players to exclude the NPC
        players_only = shadow_players[shadow_players['attacker_name'] != npc_name].reset_index(drop=True)

        # 3. Propagate Outcomes
        # If NPC DEFEAT, Players VICTORY (and vice versa)
        npc_outcome = str(npc_row.get("Outcome", pd.Series(["UNKNOWN"])).iloc[0]).upper()
        inferred_outcome = "DEFEAT" if "VICTORY" in npc_outcome else "VICTORY"

        # 4. Reconstruct the Players Dataframe
        reconstructed_rows = []
        for i, (_, row) in enumerate(players_only.iterrows()):
            new_row = {
                "Player Name": row['attacker_name'],
                "Alliance": row['attacker_alliance'],
                "Ship Name": row['attacker_ship'],
                "Outcome": inferred_outcome,
                "Fleet Type": f"Player Fleet {i + 1}"
            }

            # 5. Calculate Hull Health Remaining (Point 6)
            # Find max health from fleet_df and subtract damage from combat_df
            max_hull = self.fleet_df.loc[self.fleet_df['Fleet Type'] == f"Player Fleet {i + 1}", 'Hull Health'].sum()
            damage_taken = self.combat_df[self.combat_df['target_ship'] == row['attacker_ship']]['hull_damage'].sum()
            new_row["Hull Health Remaining"] = max(0, max_hull - damage_taken)
            new_row["Hull Health"] = max_hull  # Restore max health to the header

            reconstructed_rows.append(new_row)

        # Combine players and the original NPC row
        fallback_df = pd.DataFrame(reconstructed_rows)
        combined = pd.concat([fallback_df, npc_row], ignore_index=True)

        # Align to original column structure (filling missing as pd.NA)
        return self._align_players_columns(combined, self.players_df.columns)


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
