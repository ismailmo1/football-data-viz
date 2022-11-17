def test_get_prem_club_list():

    # HACK pytest discover fails in vscode if we import outside test
    from transfermarket.leagues import get_prem_club_list

    prem_clubs = get_prem_club_list()
    assert prem_clubs is not None
    assert len(prem_clubs) == 20
    assert prem_clubs["Liverpool FC"] == (
        "/fc-liverpool/startseite/verein/31/saison_id/2022"
    )
