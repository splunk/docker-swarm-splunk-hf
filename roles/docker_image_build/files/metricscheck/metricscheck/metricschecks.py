"""
Components related to MetricsChecks
"""

from glob import glob
from os import path

from file_read_backwards import FileReadBackwards

from .parsedline import ParsedLine
from .agecheck import AgeCheck


class MetricsChecks:
    """
    Class to handle parsing metrics logs and tracking age of groups/series data
    """

    def __init__(self, log_dir, *checks):
        """
        :param log_dir: Directory containing metrics.log files
        """
        self._log_dir = log_dir
        self._checks = {}
        for check in checks:
            group = check["group"]
            series = check["series"]
            allowed_age = check["allowed_age"]

            self._checks.setdefault(group, {})
            self._checks[group][series] = AgeCheck(allowed_age)

    def filenames(self):
        """
        :return: Generator of metrics.log files in log_dir
        """
        logs_glob = path.join(self._log_dir, "metrics.log*")

        for file in sorted(glob(logs_glob)):
            yield file

    def lines(self):
        """
        :return: Generator of metrics.log lines
        """
        for filename in self.filenames():
            with FileReadBackwards(filename, encoding="utf-8") as open_file:
                for line in open_file:
                    yield line

    def parsed_lines(self):
        """
        :return: Generator of ParsedLine objects
        """
        for line in self.lines():
            parsed_line = ParsedLine(line)
            if parsed_line.matches():
                yield parsed_line

    def group_series_check(self, group, series):
        """
        :param group: The group of the AgeCheck
        :param series: The series of the AgeCheck
        :return: The AgeCheck object for the group/series combination
        :raises UnknownGroupSeriesCheck: When group/series isn't associated with a check
        """
        if group not in self._checks:
            raise UnknownGroupSeriesCheck(f"Unknown group {group}")

        if series not in self._checks[group]:
            raise UnknownGroupSeriesCheck(f"Unknown series {series} in group {group}")

        return self._checks[group][series]

    def group_series_checks(self):
        """
        :return: Generator of group, series, checks
        """
        for group_name, group in self._checks.items():
            for series_name, check in group.items():
                yield group_name, series_name, check

    def all_checks_seen(self):
        """
        :return: True if all group/series combinations for this MetricsChecks object have been seen.
        """
        for _, _, check in self.group_series_checks():
            if not check.has_been_seen():
                return False

        return True

    def process(self):
        """
        Process all parsed lines and update AgeCheck objects appropriately
        """
        for parsed_line in self.parsed_lines():
            seen_group = parsed_line.group()
            seen_series = parsed_line.series()
            timestamp = parsed_line.timestamp()

            # update the earliest possible time for *all* AgeCheck objects
            for check_group, check_series, check in self.group_series_checks():
                check_seen = bool((check_group, check_series) == (seen_group, seen_series))
                check.updated_at(timestamp, seen=check_seen)

            if self.all_checks_seen():
                # stop processing lines after all group/series combinations have been seen,
                # because no newer times will be seen for older lines/files
                return

    def stale_group_series_checks_at(self, time):
        """
        :param time: DateTime object to pass to AgeCheck object to assess staleness
        :return: Generator yielding group/series combinations that are stale
        """
        for group, series, check in self.group_series_checks():
            if check.is_stale_at(time):
                yield group, series, check

    def any_stale_group_series_at(self, time):
        """
        :param time: DateTime object to pass to AgeCheck object to assess staleness
        :return: True if any checks stale, otherwise False.
        """
        if len(list(self.stale_group_series_checks_at(time))) > 0:
            return True
        return False

    def group_series_descriptions_at_time(self, time):
        """
        :param time: DateTime object to pass to AgeCheck object to assess staleness
        :return: Concatenated descriptions of all AgeCheck status descriptions
        """
        descriptions = [
            f"{group}/{series}: "
            f"{check.status_description_at(time)}"
            for group, series, check in self.group_series_checks()
        ]

        return "\n".join(descriptions)


class UnknownGroupSeriesCheck(Exception):
    """
    Raised when requesting an unknown group/series combination
    """
