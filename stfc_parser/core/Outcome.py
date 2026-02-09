from __future__ import annotations

import logging
import pandas as pd

from stfc_parser.ShipSpecifier import ShipSpecifier

logger = logging.getLogger(__name__)

OUTCOME_ICONS = {
    "VICTORY": ("Victory", "🏆"),
    "DEFEAT": ("Defeat", "💀"),
    "PARTIAL VICTORY": ("Partial Victory", "⚖️"),
    "PARTIAL": ("Partial Victory", "⚖️"),
}
OUTCOME_SYNONYMS = {
    "WIN": "VICTORY",
    "WON": "VICTORY",
    "LOSS": "DEFEAT",
    "LOST": "DEFEAT",
    "DEFEATED": "DEFEAT",
    "PARTIAL VICTORY": "PARTIAL",
}
UNKNOWN_OUTCOMES = {"UNKNOWN", "UNSURE", "N/A", "NA", "?", ""}

class Outcome:
    def __init__(self, players_df: pd.DataFrame, combat_df: pd.DataFrame):
        self.players_df = players_df
        self.combat_df = combat_df

    def build_outcome_lookup(self) -> dict[tuple[str, str, str], object]:
        """Return a lookup of normalized ship specs to Outcome values."""
        if not isinstance(self.players_df, pd.DataFrame) or self.players_df.empty:
            logger.warning("Outcome lookup skipped: players_df missing or empty.")
            return {}
        if "Outcome" not in self.players_df.columns:
            logger.warning("Outcome lookup skipped: 'Outcome' column missing.")
            return {}
        outcome_lookup: dict[tuple[str, str, str], object] = {}
        attacker_alliances = self._attacker_alliance_lookup()
        npc_row = self.players_df.iloc[-1]
        npc_name = self.normalize_text(npc_row.get("Player Name"))
        npc_outcome = npc_row.get("Outcome")
        normalized_npc_outcome = self.normalize_outcome(npc_outcome)
        inferred_player_outcome = self.infer_player_outcome(normalized_npc_outcome)
        if npc_name and not normalized_npc_outcome:
            logger.warning("NPC outcome missing for %s in players_df.", npc_name)
        #
        # Test 1 - look to see if this combatant has a victory/defeat entry
        #
        for _, row in self.players_df.iterrows():
            name = self.normalize_text(row.get("Player Name"))
            ship = self.normalize_text(row.get("Ship Name"))
            alliance = self._resolve_player_alliance(row)
            if not any([name, ship, alliance]):
                continue
            key = self.normalize_spec_key(name, alliance, ship)
            normalized_outcome = self.normalize_outcome(row.get("Outcome"))
            if not self.is_determinate_outcome(normalized_outcome):
                continue
            if key not in outcome_lookup:
                outcome_lookup[key] = row.get("Outcome")
            if not alliance:
                for inferred_alliance in attacker_alliances.get((name, ship), set()):
                    derived_key = self.normalize_spec_key(name, inferred_alliance, ship)
                    if derived_key not in outcome_lookup:
                        outcome_lookup[derived_key] = row.get("Outcome")
        #
        # Test 2 - the NPC should ALWAYS be in this players_df and should always have an outcome
        #
        if npc_name and normalized_npc_outcome:
            for _, row in self.players_df.iterrows():
                name = self.normalize_text(row.get("Player Name"))
                ship = self.normalize_text(row.get("Ship Name"))
                alliance = self._resolve_player_alliance(row)
                if not any([name, ship, alliance]):
                    continue
                key = self.normalize_spec_key(name, alliance, ship)
                if key in outcome_lookup:
                    continue
                if name == npc_name:
                    outcome_lookup[key] = normalized_npc_outcome
                elif inferred_player_outcome:
                    outcome_lookup[key] = inferred_player_outcome
                if not alliance:
                    for inferred_alliance in attacker_alliances.get((name, ship), set()):
                        derived_key = self.normalize_spec_key(name, inferred_alliance, ship)
                        if derived_key in outcome_lookup:
                            continue
                        if name == npc_name:
                            outcome_lookup[derived_key] = normalized_npc_outcome
                        elif inferred_player_outcome:
                            outcome_lookup[derived_key] = inferred_player_outcome
        #
        # Test 3 - The battle_df should have a row with Type="Combatant Destroyed" and Attacker Name==the loser's name

        #
        return outcome_lookup

    def _attacker_alliance_lookup(self) -> dict[tuple[str, str], set[str]]:
        """Return attacker alliance values keyed by (name, ship)."""
        df = self.combat_df
        required_columns = {"attacker_name", "attacker_ship", "attacker_alliance"}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            logger.warning("Combat df missing attacker columns for alliances: %s", sorted(missing))
            return {}

        # Select and copy the data
        subset = df.loc[:, ["attacker_name", "attacker_ship", "attacker_alliance"]].copy()

        # 1. Convert everything to a stripped string, handling NaNs manually
        # This avoids the internal .astype() 'concat' bug
        subset = subset.map(lambda x: str(x).strip() if pd.notna(x) else "")

        # 2. Filter out the empty strings
        subset = subset[
            (subset["attacker_name"] != "")
            & (subset["attacker_ship"] != "")
            & (subset["attacker_alliance"] != "")
            ]
        grouped = (
            subset.groupby(["attacker_name", "attacker_ship"])["attacker_alliance"]
            .agg(lambda values: set(values))
            .to_dict()
        )
        return {key: set(values) for key, values in grouped.items()}

    @classmethod
    def normalize_spec_key(
        cls,
        name: object,
        alliance: object,
        ship: object,
    ) -> tuple[str, str, str]:
        """Normalize a (name, alliance, ship) tuple for stable lookups."""
        return ShipSpecifier.normalize_key(name, alliance, ship)


    @staticmethod
    def normalize_text(value: object) -> str:
        """Normalize values into trimmed strings, mapping nulls to empty."""
        return ShipSpecifier.normalize_text(value)

    def _resolve_player_alliance(self, row: pd.Series) -> str:
        """Return the alliance field from the players section when available."""
        for column in ("Alliance", "Player Alliance"):
            if column in row.index:
                alliance = self.normalize_text(row.get(column))
                if alliance:
                    return alliance
        return ""


    @classmethod
    def normalize_outcome(cls, outcome: object) -> str:
        """Normalize outcome values into uppercase labels."""
        if pd.isna(outcome) or outcome is None:
            return ""
        normalized = str(outcome).strip().upper().replace("_", " ")
        normalized = OUTCOME_SYNONYMS.get(normalized, normalized)
        if normalized in UNKNOWN_OUTCOMES:
            return ""
        return normalized

    @classmethod
    def is_determinate_outcome(cls, outcome: object) -> bool:
        """Return True when the outcome is a known victory/defeat/partial."""
        normalized = cls.normalize_outcome(outcome)
        return normalized in OUTCOME_ICONS

    @classmethod
    def outcome_label_emoji(cls, outcome: object) -> tuple[str, str] | None:
        """Return the label and emoji for a known outcome."""
        normalized = cls.normalize_outcome(outcome)
        if not normalized:
            return None
        return OUTCOME_ICONS.get(normalized)

    @classmethod
    def outcome_emoji(cls, outcome: object) -> str:
        """Return the emoji for a known outcome, or the unknown fallback."""
        label_emoji = cls.outcome_label_emoji(outcome)
        if label_emoji:
            return label_emoji[1]
        return "❔"

    @classmethod
    def infer_player_outcome(cls, npc_outcome: object) -> str | None:
        """Infer a player outcome based on the NPC outcome."""
        normalized = cls.normalize_outcome(npc_outcome)
        if not normalized:
            return None
        if normalized == "VICTORY":
            return "DEFEAT"
        if normalized == "DEFEAT":
            return "VICTORY"
        if normalized in {"PARTIAL", "PARTIAL VICTORY"}:
            return "PARTIAL"
        return None

