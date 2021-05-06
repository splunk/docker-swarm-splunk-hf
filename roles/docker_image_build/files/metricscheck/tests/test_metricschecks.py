"""
MetricsChecks tests
"""

import os
from datetime import datetime
import pytest

from metricscheck.metricschecks import MetricsChecks, UnknownGroupSeriesCheck
from metricscheck.agecheck import AgeCheck


@pytest.fixture(name="log_dir_test_iterators")
def fixture_log_dir_test_iterators():
    """
    :return: Path containing test logs
    """
    test_dirname = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dirname, "logs-test-iterators")


def test_empty_log_dir_filenames():
    """
    Pointing to a directory with no metrics.log files should just yield no filenames
    """
    metrics_checker = MetricsChecks(log_dir="doesnotexist")
    assert len(list(metrics_checker.filenames())) == 0


def test_log_dir_filenames(log_dir_test_iterators):
    """
    Pointing to a directory with metrics.log files should yield proper filenames
    """
    metrics_checker = MetricsChecks(log_dir=log_dir_test_iterators)
    got_file_paths = list(metrics_checker.filenames())
    expected_filenames = ["metrics.log", "metrics.log.1"]
    assert len(got_file_paths) == len(expected_filenames)
    expected_file_paths = [
        os.path.join(log_dir_test_iterators, filename) for filename in expected_filenames
    ]
    assert got_file_paths == expected_file_paths


def test_lines(log_dir_test_iterators):
    """
    The lines() generator should find all lines in metrics.log files in log_dir
    """
    metrics_checker = MetricsChecks(log_dir=log_dir_test_iterators)
    lines = list(metrics_checker.lines())
    assert len(lines) == 5
    assert lines == [
        "metrics.log line 2",
        "metrics.log line 1",
        "metrics.log.1 line 3",
        "metrics.log.1 line 2",
        "metrics.log.1 line 1",
    ]


def test_group_series_generator():
    """
    Test the group_series generator
    """
    metrics_checker = MetricsChecks(
        # not testing files, so log_dir doesn't have to be valid
        "whocares",
        {
            "group": "group1",
            "series": "series1",
            "allowed_age": 600,
        },
        {
            "group": "group2",
            "series": "series2",
            "allowed_age": 600,
        },
    )

    group_series_list = list(metrics_checker.group_series_checks())
    assert len(group_series_list) == 2
    check_0 = group_series_list[0]
    assert (check_0[0], check_0[1]) == ("group1", "series1")
    check_1 = group_series_list[1]
    assert (check_1[0], check_1[1]) == ("group2", "series2")


def test_get_group_series_check():
    """
    Test for exceptions to be raised when asking for a group/series combination that doesn't exist
    """
    metrics_checker = MetricsChecks(
        # not testing files, so log_dir doesn't have to be valid
        "whocares",
        {
            "group": "group_exists",
            "series": "series_exists",
            "allowed_age": 600,
        },
    )

    # should not raise an error
    group_series_check = metrics_checker.group_series_check("group_exists", "series_exists")
    assert isinstance(group_series_check, AgeCheck)

    with pytest.raises(UnknownGroupSeriesCheck, match="Unknown group group_missing"):
        metrics_checker.group_series_check("group_missing", "series_exists")

    with pytest.raises(UnknownGroupSeriesCheck, match="Unknown series series_missing"):
        metrics_checker.group_series_check("group_exists", "series_missing")


# metrics.log files start at 2020-10-24 00:00:00, and have logs at 5 minute intervals
# compare against 2020-10-24 00:10:00
# allowed_age of 150 (2.5 minutes)
@pytest.mark.parametrize("seen_count,expected_age,expected_description,expected_stale", [
    (0, None,           "Insufficient data: No earliest possible time determinable", False),
    (1,  600,                            "Stale, based on last seen time (600/150)",  True),
    (2,  300,                            "Stale, based on last seen time (300/150)",  True),
    (3,    0,                                                   "Not stale (0/150)", False),
])
def test_internal_seen_age(seen_count, expected_age, expected_description, expected_stale):
    """
    Test that expected AgeChecks report staleness from on-disk metrics.log files
    :param seen_count: How many times _internal is reported.  Used to determine log_dir.
    :param expected_age: The age that is expected to be reported for _internal
    :param expected_stale: If _internal is expected to be reported as stale
    """
    test_dirname = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(test_dirname, f"logs-seen-{seen_count}x")
    metrics_checks = MetricsChecks(
        log_dir,
        {
            "group": "per_index_thruput",
            "series": "_internal",
            "allowed_age": 150,
        },
    )

    now = datetime.strptime("2020-10-24 00:10:00 +0000", "%Y-%m-%d %H:%M:%S %z")
    metrics_checks.process()

    internal_check = metrics_checks.group_series_check("per_index_thruput", "_internal")
    assert internal_check.age_at(now) == expected_age
    assert internal_check.status_description_at(now) == expected_description
    assert metrics_checks.any_stale_group_series_at(now) == expected_stale
    assert metrics_checks.group_series_descriptions_at_time(now) == \
           f"per_index_thruput/_internal: {expected_description}"

    stale_group_series = list(metrics_checks.stale_group_series_checks_at(now))
    if expected_stale:
        assert len(stale_group_series) == 1
        group, series, _ = stale_group_series[0]
        assert (group, series) == ("per_index_thruput", "_internal")
    else:
        assert len(stale_group_series) == 0
