import pandas as pd


class Combatants:

    def __init__(self, players_df: pd.DataFrame, combat_df: pd.DataFrame):
        self.players_df = players_df
        self.combat_df = combat_df

    def combatant_names(self) -> set[str]:
        """Return the union of player and attacker names."""
        df = self.players_df
        combatants = set(df["Player Name"].dropna().astype(str).unique())
        df = self.combat_df
        combatants.update(set(df["attacker_name"].dropna().astype(str).unique()))
        return combatants

    def alliance_names(self) -> set[str]:
        """Return all attacker alliance names in the combat log."""
        df = self.combat_df
        return set(df["attacker_alliance"].dropna().astype(str).unique())