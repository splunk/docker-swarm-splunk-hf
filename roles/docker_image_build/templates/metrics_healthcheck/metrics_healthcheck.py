import sys
import json
from datetime import datetime, timezone

from metricscheck.metricschecks import MetricsChecks


config_filename = "{{ metrics_healthcheck_config_filename }}"

with open(config_filename) as config_file:
    config = json.load(config_file)

path = config['path']
checks = config['checks']

metrics_checks = MetricsChecks(path, *checks)
metrics_checks.process()

now = datetime.now(timezone.utc)

print(list(metrics_checks.filenames()))
print(metrics_checks.group_series_descriptions_at_time(now))

if metrics_checks.any_stale_group_series_at(now):
    sys.exit(-1)

sys.exit(0)
