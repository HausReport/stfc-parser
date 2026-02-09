"""Derived metrics for battle logs."""

from __future__ import annotations

import numpy as np
import pandas as pd

from typing import Iterable

ATTACKER_COLUMN_CANDIDATES = ("attacker_name", "Attacker")
TARGET_COLUMN_CANDIDATES = ("target_name", "Target", "Defender Name")


def resolve_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    """Return the first matching column name from the ordered candidates."""
    return next((candidate for candidate in candidates if candidate in df.columns), None)


def get_series(df: pd.DataFrame, column: str) -> pd.Series:
    """Return a column series or an NA-filled placeholder for missing columns."""
    if column in df.columns:
        return df[column]
    return pd.Series(pd.NA, index=df.index)

def coerce_numeric(series: pd.Series) -> pd.Series:
    """Coerce a series of strings/numbers to numeric values."""
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.strip()
    return pd.to_numeric(cleaned, errors="coerce")

def add_shot_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add shot_index for damage events only (Attack rows with total_normal > 0).
    Non-damage rows get NA.
    """
    updated = df.copy()
    updated.attrs = df.attrs.copy()

    typ = updated["event_type"].astype(str).str.strip().str.lower()
    total_damage = coerce_numeric(get_series(updated, "total_normal"))
    shield_damage = coerce_numeric(get_series(updated, "shield_damage"))
    hull_damage = coerce_numeric(get_series(updated, "hull_damage"))
    pool_positive = (shield_damage > 0) | (hull_damage > 0)

    if "total_normal" in updated.columns:
        total_positive = total_damage > 0
        total_missing = total_damage.isna()
        is_shot = (typ == "attack") & (total_positive | (total_missing & pool_positive))
    else:
        is_shot = (typ == "attack") & pool_positive

    shot_index = pd.Series(pd.NA, index=updated.index, dtype="Int64")
    attacker_column = resolve_column(updated, ATTACKER_COLUMN_CANDIDATES)
    target_column = resolve_column(updated, TARGET_COLUMN_CANDIDATES)
    if attacker_column and target_column:
        shot_counts = (
            updated.loc[is_shot]
            .groupby([attacker_column, target_column], dropna=False)
            .cumcount()
            .add(1)
        )
        shot_index.loc[is_shot] = shot_counts.astype("Int64")
    else:
        shot_index.loc[is_shot] = np.arange(1, int(is_shot.sum()) + 1, dtype=np.int64)

    updated["shot_index"] = shot_index
    return updated
