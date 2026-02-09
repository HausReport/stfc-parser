import logging
from typing import Sequence

import pandas as pd

from stfc_parser.ShipSpecifier import ShipSpecifier

logger = logging.getLogger(__name__)

class FilterCombatDataframeByCombatant:

    @classmethod
    def _get_combat_df_filtered_by_specs(
        cls,
        combat_df: pd.DataFrame,
        specs: Sequence[ShipSpecifier],
        role: str,
    ) -> pd.DataFrame:
        """Return combat rows for any provided ship specs for a given role."""
        if not specs:
            return combat_df
        df = combat_df
        required_columns = (
            f"{role}_name",
            f"{role}_alliance",
            f"{role}_ship",
        )
        for column in required_columns:
            if column not in df.columns:
                logger.warning(
                    "Combat df missing %s column; cannot filter by %s.",
                    column,
                    role,
                )
                return df.iloc[0:0]

        mask = pd.Series(False, index=df.index)
        for spec in specs:
            spec_mask = pd.Series(True, index=df.index)
            if spec.name:
                spec_mask &= df[f"{role}_name"] == spec.name
            if spec.alliance:
                spec_mask &= df[f"{role}_alliance"] == spec.alliance
            if spec.ship:
                spec_mask &= df[f"{role}_ship"] == spec.ship
            mask |= spec_mask

        return df.loc[mask]