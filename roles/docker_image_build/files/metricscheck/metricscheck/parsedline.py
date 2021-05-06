"""
Components related to ParsedLine class
"""
from datetime import datetime
import re


class ParsedLine:
    """
    Class used to parse metrics.log lines
    """
    _match_regex = re.compile('''
        ^
        (?P<timestamp>
            (?P<month>[0-9]{2})-(?P<day>[0-9]{2})-(?P<year>[0-9]{4})
            \\s
            (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})\\.(?P<milliseconds>[0-9]{3})
            \\s
            (?P<offset_direction>[+-])(?P<offset_hours>[0-9]{2})(?P<offset_minutes>[0-9]{2})
        )
        \\s
        INFO
        \\s\\s
        Metrics
        \\s
        -
        \\s
        group=(?P<group>[^,]+),
        \\s
        series="(?P<series>[^"]+)",
    ''', re.VERBOSE)

    def __init__(self, line):
        self._line = line
        self._match = None
        self._timestamp = None
        self._group = None
        self._series = None

        self._parse()

    def _parse(self):
        """
        Apply the regex to the objects line
        """
        self._match = re.search(self._match_regex, self._line)
        if self._match:
            self._timestamp = self._parse_timestamp()
            self._group = self._match["group"]
            self._series = self._match["series"]

    def matches(self):
        """
        :return: True if the regex matched, otherwise False
        """
        if self._match:
            return True

        return False

    def _parse_timestamp(self):
        """
        :return: Parsed Datetime object for the timestamp in matched line
        """

        return datetime.strptime(self._match["timestamp"], "%m-%d-%Y %H:%M:%S.%f %z")

    def assert_matches(self):
        """
        :raise: UnmatchedLine unless line matches regex
        """
        if not self.matches():
            raise UnmatchedLine

    def timestamp(self):
        """
        :return: Datetime object for the timestamp in matched line
        """
        self.assert_matches()

        return self._timestamp

    def group(self):
        """
        :return: The group from the matched line
        """
        self.assert_matches()

        return self._group

    def series(self):
        """
        :return: The series from the matched line
        """
        self.assert_matches()

        return self._series


class UnmatchedLine(Exception):
    """
    Exception raised when an operation requiring a matched line was attempted against
    an object with an unmatched line
    """
