"""Pandera schema for player metadata dataframes."""

from __future__ import annotations

from typing import ClassVar
import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series

COLUMN_ORDER: ClassVar[list[str]] = [
    "Player Name", "Player Level", "Outcome", "Ship Name",
    "Ship Level", "Ship Strength", "Ship XP",
    "Officer One", "Officer Two", "Officer Three",
    "Hull Health", "Hull Health Remaining",
    "Shield Health", "Shield Health Remaining",
    "Location", "Timestamp", "Alliance"
]


class PlayersSchema(pa.DataFrameModel):
    """Schema definition for player metadata rows with full export coverage."""

    # Identity and Meta
    player_name: Series[str] = pa.Field(alias="Player Name", nullable=True)
    player_level: Series[float] = pa.Field(alias="Player Level", nullable=True)
    outcome: Series[str] = pa.Field(alias="Outcome", nullable=True)
    alliance: Series[str] = pa.Field(alias="Alliance", nullable=True)

    # Ship Identity and Strength
    ship_name: Series[str] = pa.Field(alias="Ship Name", nullable=True)
    ship_level: Series[float] = pa.Field(alias="Ship Level", nullable=True)
    ship_strength: Series[float] = pa.Field(alias="Ship Strength", nullable=True)
    ship_xp: Series[float] = pa.Field(alias="Ship XP", nullable=True)

    # Bridge Crew
    officer_one: Series[str] = pa.Field(alias="Officer One", nullable=True)
    officer_two: Series[str] = pa.Field(alias="Officer Two", nullable=True)
    officer_three: Series[str] = pa.Field(alias="Officer Three", nullable=True)

    # Health Reconciliation (Crucial for applied algebra)
    hull_health: Series[float] = pa.Field(alias="Hull Health", nullable=True)
    hull_health_remaining: Series[float] = pa.Field(alias="Hull Health Remaining", nullable=True)
    shield_health: Series[float] = pa.Field(alias="Shield Health", nullable=True)
    shield_health_remaining: Series[float] = pa.Field(alias="Shield Health Remaining", nullable=True)

    # Context
    location: Series[str] = pa.Field(alias="Location", nullable=True)
    timestamp: Series[str] = pa.Field(alias="Timestamp", nullable=True)

    class Config:
        """Enable dtype coercion while allowing extra columns (like 'Player Alliance')."""
        coerce = True
        strict = False