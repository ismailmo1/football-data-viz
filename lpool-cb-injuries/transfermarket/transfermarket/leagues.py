from enum import Enum
from typing import Dict

import pandas as pd
import requests
from transfermarket.utils import headers


class Competition(Enum):
    PREMIER_LEAGUE = "GB1"


def get_prem_club_list(season: str = "2022") -> Dict[str, str]:

    prem_teams_res = requests.get(
        url=f"https://www.transfermarkt.com/premier-league/startseite/"
        f"wettbewerb/GB1?saison_id={season}",
        headers=headers,
    )
    prem_teams_dfs = pd.read_html(prem_teams_res.text, extract_links="all")
    return {
        i[0]: i[1] for i in prem_teams_dfs[1].iloc[:, 1] if i[1] is not None
    }
