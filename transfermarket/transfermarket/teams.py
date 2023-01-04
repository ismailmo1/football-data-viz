from typing import Dict, List, Literal, Optional, Tuple

import bs4
import pandas as pd
import requests

from transfermarket.leagues import Competition
from transfermarket.utils import headers


def get_players(team_url: str) -> Dict[str, str]:
    """
    get profile links of players at team_name
    returns {'player_name':'player_url'}
    """

    team_res = requests.get(
        url="https://www.transfermarkt.com" + team_url, headers=headers
    )
    soup = bs4.BeautifulSoup(team_res.text, features="lxml")
    players = {
        link
        for link in soup.select("tr .posrela a")
        if link.get("title") == link.contents[0]
    }
    return {str(player.contents[0]): str(player["href"]) for player in players}


def get_player_list_by_position(
    team_url: str,
) -> Dict[str, List[Tuple[str, str, str]]]:
    """
    if team_url doesn't have "saison" parameter, the current season's players
    will be returned.
    get profile links of players at team_name grouped by position
    returns {'player_name':'player_url'}
    """

    team_res = requests.get(
        url="https://www.transfermarkt.com" + team_url, headers=headers
    )
    soup = bs4.BeautifulSoup(team_res.text)
    player_elements = soup.select(":nth-child(2 of tr .posrela tr td) a")[::2]
    positions = [
        el.text for el in soup.select(":nth-child(2 of tr .posrela tr)")
    ]
    player_names = [player.contents[0] for player in player_elements]
    player_links = [player["href"] for player in player_elements]
    zipped_player_link_pos = list(zip(player_names, player_links, positions))
    positions = {pos[2] for pos in zipped_player_link_pos}
    player_by_position = {}

    for position in positions:
        player_by_position[position] = [
            player
            for player in zipped_player_link_pos
            if player[2] == position
        ]

    return player_by_position


def get_team_fixtures(
    team_url: str, year: str, competition: Optional[Competition] = None
):

    fixture_url = team_url.replace("startseite", "spielplandatum")
    fixture_url = (
        fixture_url.split("saison_id")[0] + f"/plus/1?saison_id={year}"
    )
    if competition:
        fixture_url += f"&wettbewerb_id={competition.value}"

    fix_res = requests.get(
        "https://www.transfermarkt.com" + fixture_url, headers=headers
    )
    fix_df = pd.read_html(fix_res.text)
    match_fix = fix_df[1]
    match_fix["Date"] = pd.to_datetime(
        match_fix["Date"].apply(lambda x: str(x).split(". ")[-1]),
        errors="coerce",
        dayfirst=True,
    )
    match_fix = match_fix.dropna(subset=["Date"]).reset_index(drop=True)
    match_fix.set_index("Date", inplace=True)
    match_fix.dropna(how="all", axis=1, inplace=True)

    def get_result_outcome(
        row: pd.Series,
    ) -> Literal["W"] | Literal["L"] | Literal["D"] | None:
        is_home_team = "liverpool" in str(row["Home team.1"]).lower()
        result = str(row["Result"]).split(" ")[0]
        try:
            home_goals = int(str(result).split(":")[0])
            away_goals = int(str(result).split(":")[1])
        except ValueError:
            return None
        if home_goals == away_goals:
            return "D"
        if is_home_team:
            if home_goals > away_goals:
                return "W"
            return "L"
        if not is_home_team:
            if home_goals < away_goals:
                return "W"
            return "L"
        return None

    # drop matches where we have no result
    match_fix["Win"] = match_fix.apply(
        get_result_outcome, axis=1  # type:ignore
    )  # type:ignore
    match_fix.dropna(subset=["Win"], inplace=True)
    return match_fix
