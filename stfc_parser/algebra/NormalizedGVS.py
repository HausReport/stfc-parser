from dataclasses import dataclass
import pandas as pd
import numpy as np

@dataclass(frozen=True)
class NormalizedGVS:
    """
    Normalized Graded Vector Space.
    All damage and mitigation quantities are expressed
    as fractions of initial hull health.
    """
    df: pd.DataFrame

    NORM_COLS = [
        'total_normal', 'total_iso',
        'mitigated_normal', 'mitigated_iso', 'mitigated_apex',
        'shield_damage', 'hull_damage',
    ]

    def __post_init__(self):
        self._validate()

    # ---- construction ----
    @classmethod
    def from_non_normalized(cls, nn):
        df = nn.df.copy()

        # --- safeguard ---
        df['initial_hull_health'] = (
            pd.to_numeric(df['initial_hull_health'], errors='coerce')
            .fillna(0.0)
        )

        # --- scalar hull damage fraction ---
        df['damage_pct'] = (
            df['hull_damage'] / df['initial_hull_health']
        ).replace([np.inf, -np.inf], 0).fillna(0)

        # --- linear normalization ---
        for col in cls.NORM_COLS:
            df[f'{col}_norm'] = (
                df[col] / df['initial_hull_health']
            ).replace([np.inf, -np.inf], 0).fillna(0)

        # --- target hull trajectory ---
        df['cumulative_hull_damage_norm'] = (
            df.groupby(
                ['target_name', 'target_ship', 'target_alliance']
            )['hull_damage_norm']
            .cumsum()
        )

        df['current_hull_percentage'] = (
            1.0 - df['cumulative_hull_damage_norm']
        )

        # --- attacker state pullback ---
        df = cls._annotate_attacker_state(df)

        return cls(df)

    # ---- attacker state annotation ----
    @staticmethod
    def _annotate_attacker_state(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df['time_key'] = (
            df['round'] * 1_000_000 +
            df['battle_event'] * 1_000 +
            df['shot_index']
        )

        state_history = df[[
            'time_key',
            'target_name', 'target_ship', 'target_alliance',
            'current_hull_percentage'
        ]].copy()

        state_history.columns = [
            'time_key', 'name', 'ship', 'alliance', 'hp_pct'
        ]

        participants = pd.concat([
            df[['attacker_name', 'attacker_ship', 'attacker_alliance']]
              .rename(columns={'attacker_name':'name',
                               'attacker_ship':'ship',
                               'attacker_alliance':'alliance'}),
            df[['target_name', 'target_ship', 'target_alliance']]
              .rename(columns={'target_name':'name',
                               'target_ship':'ship',
                               'target_alliance':'alliance'}),
        ]).drop_duplicates()

        participants['time_key'] = -1
        participants['hp_pct'] = 1.0

        full_history = (
            pd.concat([participants, state_history])
            .sort_values('time_key')
        )

        df = df.sort_values('time_key')

        df = pd.merge_asof(
            df,
            full_history,
            left_on='time_key',
            right_on='time_key',
            left_by=['attacker_name', 'attacker_ship', 'attacker_alliance'],
            right_by=['name', 'ship', 'alliance'],
            direction='backward',
            allow_exact_matches=False
        )

        df = df.rename(columns={'hp_pct': 'attacker_hull_percentage'})
        df['attacker_hull_percentage'] = df['attacker_hull_percentage'].fillna(1.0)

        return df

    # ---- invariants ----
    def _validate(self):
        if (self.df.filter(like='_norm') < 0).any().any():
            raise ValueError("Negative normalized values detected")