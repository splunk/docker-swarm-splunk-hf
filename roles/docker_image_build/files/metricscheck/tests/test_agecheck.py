"""
AgeCheck tests
"""

from datetime import datetime, timedelta

import pytest

from metricscheck.agecheck import AgeCheck


@pytest.fixture(name="now")
def fixture_now():
    """
    :return: Datetime object for "now"
    """
    return datetime.now()


@pytest.fixture(name="one_day_ago")
def fixture_one_day_ago(now):
    """
    :param now: Datetime object for "now"
    :return: Datetime object one day older than "now"
    """
    return now - timedelta(days=1)


@pytest.fixture(name="two_days_ago")
def fixture_two_days_ago(now):
    """
    :param now: Datetime object for "now"
    :return: Datetime object two days older than "now"
    """
    return now - timedelta(days=2)

@pytest.fixture(name="three_days_ago")
def fixture_three_days_ago(now):
    """
    :param now: Datetime object for "now"
    :return: Datetime object three days older than "now"
    """
    return now - timedelta(days=3)


@pytest.fixture(name="age_check_one_day")
def fixture_age_check_one_day():
    """
    :return: AgeCheck object with an allowed age of one day (86400 seconds)
    """
    return AgeCheck(allowed_age=86400)


def test_unset_last_seen_age_at(age_check_one_day, now, one_day_ago, two_days_ago):
    """
    age_at(now) for never-updated should be three days (difference between start_time and now)
    """
    assert age_check_one_day.age_at(now) is None
    assert not age_check_one_day.has_been_seen()
    assert not age_check_one_day.has_earliest_possible_time()
    age_check_one_day.updated_at(two_days_ago, seen=False)
    assert age_check_one_day.age_at(now) == 86400*2
    assert not age_check_one_day.has_been_seen()
    age_check_one_day.updated_at(one_day_ago)
    assert age_check_one_day.age_at(now) == 86400
    assert age_check_one_day.has_been_seen()


def test_last_seen_age_at_one_day_ago(age_check_one_day, now, one_day_ago):
    """
    age_at(now) for updated_at(one_day_ago) should be one day, and should not be stale
    """
    age_check_one_day.updated_at(one_day_ago)
    assert age_check_one_day.age_at(now) == 86400
    assert not age_check_one_day.is_stale_at(now)


def test_last_seen_age_at_two_days_ago(age_check_one_day, now, two_days_ago):
    """
    age_at(now) for updated_at(two_days_ago) should be two days, and should be stale
    """
    age_check_one_day.updated_at(two_days_ago)
    assert age_check_one_day.age_at(now) == 86400*2
    assert age_check_one_day.is_stale_at(now)


def test_updated_at_keeps_latest(age_check_one_day, now, one_day_ago, two_days_ago):
    """
    age_at should reflect the most recent updated_at time, even if an older one is applied after
    """
    age_check_one_day.updated_at(one_day_ago)
    age_check_one_day.updated_at(two_days_ago)
    assert age_check_one_day.age_at(now) == 86400
