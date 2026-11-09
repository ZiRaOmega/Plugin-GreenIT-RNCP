from sci import compute


def test_sci_reference():
    r = compute(10, 100, 1000, 100, 1000, 0.5, 10)
    assert r.operational_g == 1000
    assert r.embodied_g == 50
    assert r.sci_g_per_unit == 105
