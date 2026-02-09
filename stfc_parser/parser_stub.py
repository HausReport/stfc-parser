"""Battle log parser stub."""

from __future__ import annotations

import logging

import pandas as pd

from stfc_parser.BattleSectionParser import BattleSectionParser
from stfc_parser.FleetSectionParser import FleetSectionParser
from stfc_parser.LootSectionParser import LootSectionParser
from stfc_parser.PlayerSectionParser import PlayerSectionParser

logger = logging.getLogger(__name__)


def parse_battle_log(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """
    Should return a pandas DataFrame with at least:
      - 'mitigated_apex'
      - 'total_normal'
    """
    del filename
    df, raw_df, sections = BattleSectionParser(file_bytes).parse_with_sections()
    psp = PlayerSectionParser(sections.get("players"), df)
    validated_players_df = psp.parse()
    validated_fleets_df = FleetSectionParser(sections.get("fleets")).parse()
    validated_loot_df = LootSectionParser(sections.get("rewards")).parse()
    validated_players_df = psp.repair(validated_players_df, df, validated_fleets_df)
    df.attrs.update(
        {
            "players_df": validated_players_df,
            "fleets_df": validated_fleets_df,
            "loot_df": validated_loot_df,
            "raw_combat_df": raw_df,
        }
    )
    return df
