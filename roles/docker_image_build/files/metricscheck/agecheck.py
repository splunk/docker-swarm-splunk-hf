"""
Components related to AgeCheck
"""
from enum import Enum


class Status(Enum):
    """
    Represents an AgeCheck status
    """
    INSUFFICIENT_DATA = 1
    STALE_UNSEEN = 2
    STALE_SEEN = 3
    FRESH_UNSEEN = 4
    FRESH_SEEN = 5

    def is_stale(self):
        """
        :return: True if Status represents staleness, otherwise False
        """
        if self not in (
                self.INSUFFICIENT_DATA,
                self.FRESH_UNSEEN,
                self.FRESH_SEEN,
        ):
            return True

        return False

    def description(self):
        """
        :return: Textual description of this status
        """
        status_map = {
            self.INSUFFICIENT_DATA: "Insufficient data: No earliest possible time determinable",
            self.STALE_UNSEEN: "Considered stale, but never seen",
            self.STALE_SEEN: "Stale, based on last seen time",
            self.FRESH_UNSEEN: "Not considered stale, but never seen",
            self.FRESH_SEEN: "Not stale",
        }

        return status_map[self]


class AgeCheck:
    """
    Track age of an object, and determine if it is within an allowable limit
    """

    def __init__(self, allowed_age):
        """
        :param allowed_age: The allowed age, in seconds, before this object is considered stale
        """
        self._allowed_age = allowed_age
        self._earliest_possible_time = None
        self._last_seen = None

    def updated_at(self, time, seen=True):
        """
        :param time: Time that this object was seen.
        :param seen: Update last seen time.  If False, only updates earliest possible time.
        """
        if seen and (not self.has_been_seen() or time > self._last_seen):
            self._last_seen = time

        if not self.has_earliest_possible_time() or (time < self._earliest_possible_time):
            self._earliest_possible_time = time

    def has_been_seen(self):
        """
        :return: True if last seen time is set, otherwise False
        """
        return bool(self._last_seen)

    def has_earliest_possible_time(self):
        """
        :return: True if earliest possible time is set, otherwise False
        """
        return bool(self._earliest_possible_time)

    def status_at(self, time):
        """
        :param time: The time against which to compare this object's last seen time
        :return: Status
        """
        age = self.age_at(time)
        if age is None:
            return Status.INSUFFICIENT_DATA

        if age > self._allowed_age:
            if self.has_been_seen():
                return Status.STALE_SEEN
            return Status.STALE_UNSEEN

        if self.has_been_seen():
            return Status.FRESH_SEEN
        return Status.FRESH_UNSEEN

    def age_at(self, time):
        """
        :param time: The time against which to compare this object's last seen time
        :return: The age, in seconds, of this object at the specified time.  If unable to calculate
        age, due to lack of ever being seen or earliest_possible_time being unset, returns None.
        """
        if not self.has_been_seen():
            # no way to calculate even a guess at age if never seen, and no earliest possible time
            if not self.has_earliest_possible_time():
                return None

            # best case: difference between "now" and earliest_possible_time
            # in reality the age is almost certainly higher than this would yield
            duration_from_start_time = time - self._earliest_possible_time
            return int(duration_from_start_time.total_seconds())

        # specific case: difference between "now" and last seen
        duration_from_last_seen = time - self._last_seen
        return int(duration_from_last_seen.total_seconds())

    def is_stale_at(self, time):
        """
        :param time: The time against which to compare this object's last seen time
        :return: Boolean representing staleness at time
        """
        return self.status_at(time).is_stale()

    def status_description_at(self, time):
        """
        :param time: The time against which to compare this object's last seen time
        :return: Textual description of status at given time
        """
        age = self.age_at(time)
        if age is not None:
            return f"{self.status_at(time).description()} ({age}/{self._allowed_age})"

        return self.status_at(time).description()
