from stfc_parser.ShipSpecifier import ShipSpecifier
import pandas as pd

def get_teams_from_players_df(players_df: pd.DataFrame):
    """
    Given players_df, returns two sets: Team1 and Team2.
    Team2 will always have a single element, the last row of players_df.
    Team1 will be the rest of the rows.

    Args:
        players_df (pd.DataFrame): DataFrame containing player information.

    Returns:
        tuple[set[ShipSpecifier], set[ShipSpecifier]]: A tuple containing Team1 and Team2 sets.
    """
    if players_df.empty:
        return set(), set()

    # Create a local copy of players_df and normalize its 'Alliance' column
    # to match the normalization applied to derived3.
    normalized_players_df = players_df.copy()
    normalized_players_df['Alliance'] = normalized_players_df['Alliance'].astype(str).str.strip()
    normalized_players_df['Alliance'] = normalized_players_df['Alliance'].replace(['nan', 'None', '<NA>', ''], '')


    # Team2 is the last row
    last_row = normalized_players_df.iloc[-1]
    team2_specifier = ShipSpecifier(
        name=last_row.get('Player Name'),
        alliance=last_row.get('Alliance'),
        ship=last_row.get('Ship Name')
    )
    team2_set: set[ShipSpecifier] = {team2_specifier}

    # Team1 is the rest of the rows
    team1_set = set()
    if len(normalized_players_df) > 1:
        other_rows = normalized_players_df.iloc[:-1]
        for _, row in other_rows.iterrows():
            team1_specifier = ShipSpecifier(
                name=row.get('Player Name'),
                alliance=row.get('Alliance'),
                ship=row.get('Ship Name')
            )
            team1_set.add(team1_specifier)

    return team1_set, team2_set