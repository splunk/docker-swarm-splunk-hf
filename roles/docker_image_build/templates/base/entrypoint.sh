#!/usr/bin/env bash
echo Untarring splunk.tgz \
&& tar xzf {{ splunk_home }}/splunk.tgz -C {{ splunk_home }}/.. \
&& echo Removing splunk.tgz \
&& rm {{ splunk_home }}/splunk.tgz \
&& echo Starting splunk \
&& {{ splunk_home }}/bin/splunk start --nodaemon --accept-license --answer-yes --no-prompt
