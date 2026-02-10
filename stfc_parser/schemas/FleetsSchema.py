"""Pandera schema for fleet metadata dataframes."""

from typing import ClassVar
import pandas as pd
import pandera as pa
from pandera.typing import Series

COLUMN_ORDER: ClassVar[list[str]] = [
    "Fleet Type", "Attack", "Defense", "Health",
    "Ship Ability", "Captain Maneuver",
    "Officer One Ability", "Officer Two Ability", "Officer Three Ability",
    "Officer Attack Bonus", "Damage Per Round", "Armour Pierce",
    "Shield Pierce", "Accuracy", "Critical Chance", "Critical Damage",
    "Officer Defense Bonus", "Armour", "Shield Deflection", "Dodge",
    "Officer Health Bonus", "Shield Health", "Hull Health",
    "Impulse Speed", "Warp Range", "Warp Speed",
    "Cargo Capacity", "Protected Cargo", "Mining Bonus",
    "Debuff applied", "Buff applied"
]

class FleetsSchema(pa.DataFrameModel):
    """Schema definition for fleet metadata rows with full game-stat coverage."""

    # Identity and Core Stats
    fleet_type: Series[str] = pa.Field(alias="Fleet Type", nullable=True)
    attack: Series[float] = pa.Field(alias="Attack", nullable=True)
    defense: Series[float] = pa.Field(alias="Defense", nullable=True)
    health: Series[float] = pa.Field(alias="Health", nullable=True)

    # Abilities and Maneuvers
    ship_ability: Series[str] = pa.Field(alias="Ship Ability", nullable=True)
    captain_maneuver: Series[str] = pa.Field(alias="Captain Maneuver", nullable=True)
    officer_1_ability: Series[str] = pa.Field(alias="Officer One Ability", nullable=True)
    officer_2_ability: Series[str] = pa.Field(alias="Officer Two Ability", nullable=True)
    officer_3_ability: Series[str] = pa.Field(alias="Officer Three Ability", nullable=True)

    # Offense Specifics
    officer_attack_bonus: Series[float] = pa.Field(alias="Officer Attack Bonus", nullable=True)
    damage_per_round: Series[float] = pa.Field(alias="Damage Per Round", nullable=True)
    armour_pierce: Series[float] = pa.Field(alias="Armour Pierce", nullable=True)
    shield_pierce: Series[float] = pa.Field(alias="Shield Pierce", nullable=True)
    accuracy: Series[float] = pa.Field(alias="Accuracy", nullable=True)
    critical_chance: Series[float] = pa.Field(alias="Critical Chance", nullable=True)
    critical_damage: Series[float] = pa.Field(alias="Critical Damage", nullable=True)

    # Defense Specifics
    officer_defense_bonus: Series[float] = pa.Field(alias="Officer Defense Bonus", nullable=True)
    armour: Series[float] = pa.Field(alias="Armour", nullable=True)
    shield_deflection: Series[float] = pa.Field(alias="Shield Deflection", nullable=True)
    dodge: Series[float] = pa.Field(alias="Dodge", nullable=True)

    # Health and Scaling
    officer_health_bonus: Series[float] = pa.Field(alias="Officer Health Bonus", nullable=True)
    shield_health: Series[float] = pa.Field(alias="Shield Health", nullable=True)
    hull_health: Series[float] = pa.Field(alias="Hull Health", nullable=True)

    # Navigation and Cargo
    impulse_speed: Series[float] = pa.Field(alias="Impulse Speed", nullable=True)
    warp_range: Series[float] = pa.Field(alias="Warp Range", nullable=True)
    warp_speed: Series[float] = pa.Field(alias="Warp Speed", nullable=True)
    cargo_capacity: Series[float] = pa.Field(alias="Cargo Capacity", nullable=True)
    protected_cargo: Series[float] = pa.Field(alias="Protected Cargo", nullable=True)
    mining_bonus: Series[float] = pa.Field(alias="Mining Bonus", nullable=True)

    # Status Flags
    # Since inputs are "YES"/"NO", ensure your pre-processor converts them to bools
    # so pd.BooleanDtype (nullable boolean) can take over.
    debuff_applied: Series[pd.BooleanDtype] = pa.Field(alias="Debuff applied", nullable=True)
    buff_applied: Series[pd.BooleanDtype] = pa.Field(alias="Buff applied", nullable=True)

    class Config:
        """Enable dtype coercion while allowing extra columns."""
        coerce = True
        strict = False