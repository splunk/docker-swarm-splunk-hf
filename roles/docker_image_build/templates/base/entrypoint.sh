#!/usr/bin/env bash
/bin/rm -f {{ splunk_home }}/var/lib/splunk/kvstore/mongo/mongod.lock
{{ splunk_home }}/bin/splunk start --nodaemon --accept-license --answer-yes --no-prompt
