import sys
import json
from datetime import datetime, timezone

# this is ugly, but it's:
#    package      module       file                 class
# the upstream package should probably be fixed to be less awful
from metricscheck.metricscheck.metricschecks import MetricsChecks


config_filename = "{{ metrics_healthcheck_config_filename }}"

with open(config_filename) as config_file:
    config = json.load(config_file)

path = config['path']
checks = config['checks']
checks_normalized = [
    {
        "group": check["group"],
        "series": check["series"],
        # inventory config uses allowed_age_seconds to avoid ambiguity
        # but the metricscheck library uses allowed_age, which represents seconds
        "allowed_age": check["allowed_age_seconds"],
    } for check in checks
]

metrics_checks = MetricsChecks(path, *checks_normalized)
metrics_checks.process()

now = datetime.now(timezone.utc)

print(metrics_checks.group_series_descriptions_at_time(now))

if metrics_checks.any_stale_group_series_at(now):
    sys.exit(-1)

sys.exit(0)
