def test_get_player_availability():
    from transfermarket.leagues import Competition
    from transfermarket.players import get_player_availability

    player_url = "https://www.transfermarkt.com/antony/profil/spieler/602105/"
    comp = Competition.PREMIER_LEAGUE
    season = "2022"

    avail_data = get_player_availability(player_url, comp, season, "Matchday")

    assert avail_data is not None
    assert avail_data.loc["antony", 10] == 4
    assert avail_data.loc["antony", 5] == 1
    assert avail_data.loc["antony", 14] == 0
