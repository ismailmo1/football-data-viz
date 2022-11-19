import datetime


def test_get_players():
    from transfermarket.teams import get_players

    team_url = "/fc-liverpool/startseite/verein/31/saison_id/2022"
    players = get_players(team_url)
    assert players is not None
    assert len(players) == 27
    assert players["Mohamed Salah"] == "/mohamed-salah/profil/spieler/148455"


def test_get_player_list_by_position():
    from transfermarket.teams import get_player_list_by_position

    chelsea_url = "/fc-chelsea/startseite/verein/631/saison_id/2022"
    players_by_pos = get_player_list_by_position(chelsea_url)

    assert players_by_pos is not None
    assert len(players_by_pos) == 10
    assert len(players_by_pos["Defensive Midfield"]) == 3

    left_back_names = [i[0] for i in players_by_pos["Left-Back"]]
    assert "Marc Cucurella" in left_back_names


def test_get_team_fixtures():
    from transfermarket.leagues import Competition
    from transfermarket.teams import get_team_fixtures

    westham_url = "/west-ham-united/startseite/verein/379/saison_id/2022"
    fixtures = get_team_fixtures(
        westham_url, "2021", Competition.PREMIER_LEAGUE
    )

    assert fixtures is not None
    assert len(fixtures) == 38
    assert (
        fixtures.loc[
            datetime.datetime(2021, 12, 26), "Matchday"
        ]  # type:ignore
        == "19"
    )
    assert (
        fixtures.loc[datetime.datetime(2021, 9, 25), "Result"]  # type:ignore
        == "1:2"
    )
    assert (
        "Everton"
        in fixtures.loc[
            datetime.datetime(2022, 4, 3),  # type:ignore
            "Away team.1",
        ]
    )
