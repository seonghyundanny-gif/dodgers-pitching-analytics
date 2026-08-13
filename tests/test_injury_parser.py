from scripts.collect.collect_injuries import parse_il_stints


def _transaction(date, description):
    return {"date": date, "description": description}


def test_parser_pairs_placement_and_activation_and_honors_retroactive_date():
    transactions = [
        _transaction(
            "2025-04-10",
            "Los Angeles Dodgers placed RHP Example Pitcher on the 15-day injured list "
            "retroactive to April 8, 2025.",
        ),
        _transaction(
            "2025-04-24",
            "Los Angeles Dodgers activated RHP Example Pitcher from the 15-day injured list.",
        ),
    ]

    assert parse_il_stints(transactions, "2025-09-28") == [
        {
            "name": "Example Pitcher",
            "start_date": "2025-04-08",
            "end_date": "2025-04-24",
            "right_censored": False,
        }
    ]


def test_parser_right_censors_an_open_stint_at_season_end():
    transactions = [
        _transaction(
            "2025-08-01",
            "Los Angeles Dodgers placed LHP Open Stint on the 15-day injured list.",
        )
    ]

    assert parse_il_stints(transactions, "2025-09-28") == [
        {
            "name": "Open Stint",
            "start_date": "2025-08-01",
            "end_date": "2025-09-28",
            "right_censored": True,
        }
    ]


def test_parser_does_not_overwrite_a_duplicate_open_placement():
    transactions = [
        _transaction(
            "2025-05-01",
            "Los Angeles Dodgers placed RHP Duplicate Case on the injured list.",
        ),
        _transaction(
            "2025-05-03",
            "Los Angeles Dodgers placed RHP Duplicate Case on the injured list.",
        ),
        _transaction(
            "2025-05-20",
            "Los Angeles Dodgers activated RHP Duplicate Case from the injured list.",
        ),
    ]

    stint = parse_il_stints(transactions, "2025-09-28")[0]
    assert stint["start_date"] == "2025-05-01"
    assert stint["end_date"] == "2025-05-20"
