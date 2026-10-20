import pytest

from M2.retry_budget import budget


@pytest.mark.parametrize("setup", [0, 120, 215, 900, 1260])
def test_setup_compute_exit_package_upload_fit_six_hours(setup):
    result = budget(1000, 1000 + setup)
    assert result["compute_seconds"] + setup + result["total_reserve_seconds"] == 21600
    assert result["total_reserve_seconds"] == 330
    assert result["termination_reserve_seconds"] >= 40
    assert result["scientific_budget"] == 20


def test_no_compute_when_setup_exhausts_safe_window():
    with pytest.raises(ValueError, match="Insufficient"):
        budget(0, 21600 - 330)


def test_compute_gets_measured_extra_fifteen_and_half_minutes():
    assert budget(0, 215)["compute_seconds"] == 20125 + 930
