import numpy as np


def test_checked_in_innings_are_converted_from_baseball_notation(pitcher_stats):
    """In `.1`/`.2` baseball notation, the suffix represents outs, not tenths."""
    raw_ip = pitcher_stats["IP"].astype(float)
    whole_innings = np.floor(raw_ip)
    outs = np.rint((raw_ip - whole_innings) * 10)
    expected_decimal = whole_innings + outs / 3

    assert set(outs.unique()) <= {0, 1, 2}
    assert np.allclose(pitcher_stats["IP_decimal"], expected_decimal, atol=0.005)


def test_dataset_contains_both_one_and_two_out_examples(pitcher_stats):
    suffix = np.rint((pitcher_stats["IP"] - np.floor(pitcher_stats["IP"])) * 10)
    assert {1, 2}.issubset(set(suffix))
