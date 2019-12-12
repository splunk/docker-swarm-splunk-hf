import sys
import re
import glob
from datetime import datetime
from dateutil import tz

allowed_age = {{ healthcheck_allowed_age_seconds }}
group = "{{ healthcheck_metrics_group }}"
series = "{{ healthcheck_metrics_series }}"
path = "{{ splunk_home }}/var/log/splunk/metrics.log*"

file_names = glob.glob(path)
if not file_names:
    print("No files match path: {0}".format(path))
    exit(-1)

timestamp_regex = re.compile('^(?P<timestamp>(?P<month>[0-9]{2})-(?P<day>[0-9]{2})-(?P<year>[0-9]{4}) (?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})\.[0-9]{3} (?P<offset_direction>[+-])(?P<offset_hours>[0-9]{2})(?P<offset_minutes>[0-9]{2})) INFO  Metrics - group=(?P<group>[^,]+), series="(?P<series>[^"]+)",')

run_timestamp = datetime.utcnow()
earliest_overall_timestamp = None
latest_group_series_timestamp = None

for file_name in file_names:
    with open(file_name) as log_file:
        for line in log_file:
            match = re.search(timestamp_regex, line)
            if match:
                timestamp_component_names = [ 'year', 'month', 'day', 'hour', 'minute', 'second' ]
                timestamp_components = map(lambda x: int(match.group(x)), timestamp_component_names)

                tz_offset_direction = match.group('offset_direction')
                tz_offset_hours = int(match.group('offset_hours'))
                tz_offset_minutes = int(match.group('offset_minutes'))
                tz_offset_seconds = 0
                if tz_offset_direction == '-':
                    tz_offset_seconds -= tz_offset_hours*3600
                    tz_offset_seconds -= tz_offset_minutes*60
                elif tz_offset_direction == '+':
                    tz_offset_seconds += tz_offset_hours*3600
                    tz_offset_seconds += tz_offset_minutes*60
                else:
                    raise Exception("Lies!")

                timestamp_tz = tz.tzoffset(match.groups('offset'), tz_offset_seconds)

                timestamp = datetime(*timestamp_components, tzinfo=timestamp_tz)

                if earliest_overall_timestamp is None or timestamp < earliest_overall_timestamp:
                    earliest_overall_timestamp = timestamp

                if match.group('group') == group and match.group('series') == series:
                    if latest_group_series_timestamp is None or timestamp > latest_group_series_timestamp:
                        latest_group_series_timestamp = timestamp

run_timestamp_epoch = int(run_timestamp.strftime("%s"))

# have we seen *any* logs?
if earliest_overall_timestamp:
    earliest_overall_timestamp_epoch = int(earliest_overall_timestamp.strftime("%s"))
    # have we seen *enough* logs to actually check?
    earliest_overall_age = run_timestamp_epoch - earliest_overall_timestamp_epoch
    if  earliest_overall_age > allowed_age:
        # have we seen *any* data we care about?
        if latest_group_series_timestamp:
            latest_group_series_timestamp_epoch = int(latest_group_series_timestamp.strftime("%s"))
            latest_group_series_age = run_timestamp_epoch - latest_group_series_timestamp_epoch
            print("{0}/{1} is {2} seconds old".format(group, series, latest_group_series_age))
            # have we seen recent data we care about?
            if latest_group_series_age > allowed_age:
                exit(-1)
            else:
                exit(0)
        else:
            print("{0}/{1} is at least {2} seconds old (no metrics seen for this combination)".format(group, series, earliest_overall_age))
            exit(-1)
    else:
        print("Not bothering to check, we don't have {0} seconds of any group/series metrics logs".format(allowed_age))
        exit(0)
else:
    print("Not bothering to check, we have no metrics logs at all")
    exit(0)
