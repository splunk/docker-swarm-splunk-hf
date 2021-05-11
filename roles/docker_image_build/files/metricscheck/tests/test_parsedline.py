"""
ParsedLine tests
"""
import pytest

from metricscheck.parsedline import ParsedLine, UnmatchedLine


def test_regex():
    """
    Test ParsedLine's parser against metrics.log sample lines
    :return:
    """
    timestamp_format = "%Y-%m-%d %H:%M:%S %z"

    parser_tests = [
        {
            "line": '10-23-2020 23:24:13.212 +0000 INFO  '
                    'Metrics - group=queue, name=typingqueue, '
                    'max_size_kb=500, current_size_kb=0, current_size=0, '
                    'largest_size=91, smallest_size=0',
            "matches": False,
        },
        {
            "line": '10-23-2020 23:24:13.211 +0000 INFO  '
                    'Metrics - group=per_sourcetype_thruput, series="splunkd_access", '
                    'kbps=0.05406296463256461, eps=0.5207334582833266, kb=1.6611328125, '
                    'ev=16, avg_age=0.0625, max_age=1',
            "matches": True,
            "timestamp": "2020-10-23 23:24:13 +0000",
            "group": "per_sourcetype_thruput",
            "series": "splunkd_access",
        },
    ]

    for test in parser_tests:
        parsed_line = ParsedLine(test["line"])
        assert parsed_line.matches() == test["matches"]

        if test["matches"]:
            assert parsed_line.timestamp().strftime(timestamp_format) == test["timestamp"]
            assert parsed_line.group() == test["group"]
            assert parsed_line.series() == test["series"]
        else:
            with pytest.raises(UnmatchedLine):
                parsed_line.timestamp()
            with pytest.raises(UnmatchedLine):
                parsed_line.group()
            with pytest.raises(UnmatchedLine):
                parsed_line.series()
