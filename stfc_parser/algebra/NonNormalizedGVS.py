from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class NonNormalizedGVS:
    """
    Non-normalized Graded Vector Space of combat damage events.

    Each row is an atomic attack event (shot-level), graded by round,
    carrying raw offensive flux, defensive response, and target capacity.
    """
    df: pd.DataFrame

    # ---- canonical column groups ----
    IDENTITY_COLS = [
        'round', 'battle_event', 'shot_index', 'event_type',
        'attacker_name', 'attacker_ship', 'attacker_alliance',
        'target_name', 'target_ship', 'target_alliance',
    ]

    OFFENSIVE_COLS = [
        'is_crit', 'total_normal', 'total_iso',
    ]

    DEFENSIVE_COLS = [
        'mitigated_normal', 'mitigated_iso', 'mitigated_apex',
        'shield_damage', 'hull_damage',
    ]

    PARAMETER_COLS = [
        'initial_hull_health',
    ]

    # ---- lifecycle ----
    def __post_init__(self):
        self._validate()

    # ---- construction ----
    @classmethod
    def from_parser_outputs(
        cls,
        combat_df: pd.DataFrame,
        players_df: pd.DataFrame,
        fleets_df: pd.DataFrame | None = None,
    ) -> "NonNormalizedGVS":
        """
        Construct the NonNormalizedGVS from TJ parser outputs.
        fleets_df is accepted for symmetry/future use but unused here.
        """

        # --- select attack events ---
        target_columns = (
            cls.IDENTITY_COLS
            + cls.OFFENSIVE_COLS
            + cls.DEFENSIVE_COLS
        )

        df = combat_df[combat_df['event_type'] == 'Attack'][target_columns].copy()
        df = df.reset_index(drop=True)

        # --- normalize join keys ---
        def normalize_columns_to_str(df, cols):
            df = df.copy()
            for c in cols:
                df[c] = (
                    df[c]
                    .astype(str)
                    .str.strip()
                    .replace(['nan', 'None', '<NA>', ''], '')
                )
            return df

        df = normalize_columns_to_str(
            df,
            ['attacker_name', 'attacker_ship', 'attacker_alliance',
             'target_name', 'target_ship', 'target_alliance']
        )

        hull_lookup = players_df[
            ['Player Name', 'Ship Name', 'Alliance', 'Hull Health']
        ].copy()

        hull_lookup['Hull Health'] = pd.to_numeric(
            hull_lookup['Hull Health'], errors='coerce'
        )

        hull_lookup = normalize_columns_to_str(
            hull_lookup,
            ['Player Name', 'Ship Name', 'Alliance']
        )

        # --- pull target capacity into event space ---
        df = df.merge(
            hull_lookup,
            left_on=['target_name', 'target_ship', 'target_alliance'],
            right_on=['Player Name', 'Ship Name', 'Alliance'],
            how='left'
        )

        df = df.rename(columns={'Hull Health': 'initial_hull_health'})
        df = df.drop(columns=['Player Name', 'Ship Name', 'Alliance'], errors='ignore')

        df['initial_hull_health'] = (
            pd.to_numeric(df['initial_hull_health'], errors='coerce')
            .fillna(0.0)
        )

        return cls(df)

    # ---- invariants ----
    def _validate(self):
        required = (
            set(self.IDENTITY_COLS)
            | set(self.OFFENSIVE_COLS)
            | set(self.DEFENSIVE_COLS)
            | set(self.PARAMETER_COLS)
        )

        missing = required - set(self.df.columns)
        if missing:
            raise ValueError(f"NonNormalizedGVS missing columns: {missing}")

        if (self.df['initial_hull_health'] < 0).any():
            raise ValueError("Negative initial_hull_health detected")

    # ---- immutability helpers ----
    def copy(self) -> "NonNormalizedGVS":
        return NonNormalizedGVS(self.df.copy())

    def with_df(self, df: pd.DataFrame) -> "NonNormalizedGVS":
        return NonNormalizedGVS(df)

    # ---- semantic projections ----
    @property
    def identity(self) -> pd.DataFrame:
        return self.df[self.IDENTITY_COLS]

    @property
    def offensive_flux(self) -> pd.DataFrame:
        return self.df[self.OFFENSIVE_COLS]

    @property
    def defensive_response(self) -> pd.DataFrame:
        return self.df[self.DEFENSIVE_COLS]

    def by_round(self, k: int) -> "NonNormalizedGVS":
        return NonNormalizedGVS(self.df[self.df['round'] == k].copy())

    def for_target(self, target_name: str) -> "NonNormalizedGVS":
        return NonNormalizedGVS(
            self.df[self.df['target_name'] == target_name].copy()
        )