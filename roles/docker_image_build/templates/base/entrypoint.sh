#!/usr/bin/env bash
{% if migrate_kvstore is defined %}
{{ splunk_home }}/bin/splunk start --accept-license --answer-yes --no-prompt
{{ splunk_home }}/bin/splunk stop
{{ splunk_home }}/bin/splunk migrate kvstore-storage-engine --target-engine wiredTiger
{% endif %}
{{ splunk_home }}/bin/splunk start --nodaemon --accept-license --answer-yes --no-prompt
