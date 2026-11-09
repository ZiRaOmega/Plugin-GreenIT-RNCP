from ecoindex import compute, grade, quantile, QUANTILES_SIZE


def test_reference_values():
    assert compute(47, 2, 1.37).score == 95
    assert compute(100, 100, 100).score == 72
    assert compute(100, 100, 100).grade == "B"


def test_quantile_official():
    assert quantile(QUANTILES_SIZE, 2500) == 14.086372025739513


def test_grade():
    assert grade(100) == "A"
    assert grade(50.2) == "D"
    assert grade(2) == "G"
