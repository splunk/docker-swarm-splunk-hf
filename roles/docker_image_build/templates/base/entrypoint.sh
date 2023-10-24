#!/usr/bin/env bash
{{ splunk_home }}/bin/splunk migrate migrate-kvstore-36-40
{% if migrate_kvstore is defined %}
{{ splunk_home }}/bin/splunk start --accept-license --answer-yes --no-prompt
{{ splunk_home }}/bin/splunk stop
{{ splunk_home }}/bin/splunk migrate kvstore-storage-engine --target-engine wiredTiger
{% endif %}
{% if upgrade_kvstore is defined %}
{{ splunk_home }}/bin/splunk migrate migrate-kvstore
{% endif %}
{{ splunk_home }}/bin/splunk start --nodaemon --accept-license --answer-yes --no-prompt
