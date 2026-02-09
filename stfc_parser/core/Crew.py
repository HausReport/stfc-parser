import pandas as pd


class Crew:

    def __init__(self, players_df: pd.DataFrame, combat_df: pd.DataFrame):
        self.players_df = players_df
        self.combat_df = combat_df

    def get_captain_name(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return the captain officer name(s) for a combatant and ship."""
        df = self.players_df
        mask = (df["Ship Name"] == ship_name) & (df["Player Name"] == combatant_name)
        return set(df.loc[mask, "Officer One"].dropna().astype(str).unique())

    def get_1st_officer_name(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return the first officer name(s) for a combatant and ship."""
        df = self.players_df
        mask = (df["Ship Name"] == ship_name) & (df["Player Name"] == combatant_name)
        return set(df.loc[mask, "Officer Two"].dropna().astype(str).unique())

    def get_2nd_officer_name(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return the second officer name(s) for a combatant and ship."""
        df = self.players_df
        mask = (df["Ship Name"] == ship_name) & (df["Player Name"] == combatant_name)
        return set(df.loc[mask, "Officer Three"].dropna().astype(str).unique())

    def get_bridge_crew(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return the bridge crew officer names for a combatant and ship."""
        bridge_crew: set[str] = set()
        bridge_crew.update(self.get_captain_name(combatant_name, ship_name))
        bridge_crew.update(self.get_1st_officer_name(combatant_name, ship_name))
        bridge_crew.update(self.get_2nd_officer_name(combatant_name, ship_name))
        return bridge_crew

    def get_below_deck_officers(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return below-deck officer names for a combatant and ship."""
        all_officers = self.all_officer_names(combatant_name, ship_name)
        bridge_crew = self.get_bridge_crew(combatant_name, ship_name)
        return all_officers - bridge_crew

    def all_officer_names(self, combatant_name: str, ship_name: str) -> set[str]:
        """Return all officer names activated by a combatant and ship."""
        df = self.combat_df
        event_type = df["event_type"].astype(str).str.lower()
        mask = (
            (event_type == "officer")
            & (df["attacker_ship"] == ship_name)
            & (df["attacker_name"] == combatant_name)
        )
        return set(df.loc[mask, "ability_owner_name"].dropna().astype(str).unique())

