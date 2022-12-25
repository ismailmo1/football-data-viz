from typing import Literal

import numpy as np
import pandas as pd
import requests
from transfermarket.utils import headers


def get_match_data(player_url: str, season: str):
    # TODO: add separate parsing logic for competition filters
    player_url = player_url + f"/plus/1?saison={season}"
    # get name out of url

    # stats for injuries are on different page to profile
    player_url = player_url.replace("profil", "leistungsdatendetails")

    tm_res = requests.get(url=player_url, headers=headers)

    dfs = pd.read_html(tm_res.text)
    match_dfs = []
    for idx, df in enumerate(dfs):
        if "Matchday" in df.columns:
            match_dfs.append(df)
    try:
        all_matches = pd.concat(match_dfs)
    except ValueError:
        print(f"no match data found for {player_url}")
        return
    # remove footer row
    all_matches = all_matches.loc[
        all_matches.iloc[:, 0].apply(
            lambda x: "Squad" not in str(x)
        )  # type:ignore
    ]
    all_matches["Date"] = pd.to_datetime(all_matches["Date"], errors="coerce")

    # last column is minutes played
    all_matches["min_played"] = all_matches.iloc[:, 16].fillna(0)
    # check if player used as sub
    all_matches["subbed_off"] = all_matches.iloc[:, 15]
    all_matches["subbed_on"] = all_matches.iloc[:, 14]

    all_matches = all_matches.loc[
        :,
        [
            "Date",
            "Matchday",
            "Home team.1",
            "Away team.1",
            "Result",
            "min_played",
            "subbed_on",
            "subbed_off",
        ],
    ]

    return all_matches


def get_minutes_played(match_data: pd.DataFrame):
    def get_min_played(min_played: str):
        minutes_split = str(min_played).split("'")
        if len(minutes_split) < 2:
            return 0
        else:
            return int(minutes_split[0])

    match_data["min_played"] = match_data["min_played"].apply(get_min_played)

    return match_data


def calculate_player_availability(
    player_name: str,
    minutes_played: pd.DataFrame,
    columns: Literal["Matchday"] | Literal["Date"] = "Date",
    add_match_result: bool = False,
):
    def get_availability(row: pd.Series):
        if row["Result"] == "-:-":
            return None
        if row["min_played"] > 0:
            if row["subbed_on"] is np.nan:
                return "Played (starter)"
            return "Played (sub)"
        if row["subbed_on"] == "on the bench":
            return "Bench"
        if row["subbed_on"] == "Not in squad":
            return "Not in squad"
        if "suspension" in str(row["subbed_on"]).lower():
            return "Suspended"

        return "Injured"

    # create categories based on subbed on/off, minutes played
    minutes_played["availability"] = minutes_played.apply(
        get_availability, axis=1  # type:ignore
    )

    availability_levels = {
        "Injured": 0,
        "Not in squad": 1,
        "Bench": 2,
        "Played (sub)": 3,
        "Played (starter)": 4,
    }
    minutes_played["availability_level"] = minutes_played["availability"].map(
        availability_levels
    )

    if add_match_result:
        availability_df = minutes_played.loc[
            :,
            [
                columns,
                "availability_level",
                "Home team.1",
                "Away team.1",
                "Result",
            ],
        ]
    else:
        availability_df = minutes_played.loc[
            :, [columns, "availability_level"]
        ]
    if columns == "Date":
        availability_df["Date"] = availability_df["Date"].apply(
            lambda x: x.date()
        )
    else:
        availability_df["Matchday"] = pd.to_numeric(
            availability_df["Matchday"]
        )
    availability_df.sort_values(columns, inplace=True)
    availability_df = availability_df.set_index(columns).transpose()
    availability_df.rename(
        {"availability_level": player_name}, axis=0, inplace=True
    )

    return availability_df


def get_player_availability(
    player_url: str,
    season: str,
):
    player_name = player_url.split("https://www.transfermarkt.com/")[1].split(
        "/"
    )[0]
    match_data = get_match_data(player_url, season)
    if not match_data:
        return
    minutes_played = get_minutes_played(match_data)
    player_availability = calculate_player_availability(
        player_name, minutes_played
    )

    return player_availability
