FROM ubuntu:19.04 AS sas_docker_base

RUN ln -fs /usr/share/zoneinfo/{{ timezone }} /etc/localtime \
  && groupadd {{ splunk_group }} -g {{ splunk_group_id }} \
  && useradd {{ splunk_user }} -m -d {{ splunk_home }} -g {{ splunk_group }} -u {{ splunk_user_id }} --shell /bin/bash \
  && apt-get update \
  && apt-get install -y --no-install-recommends wget ca-certificates {{ apt_packages|join(' ') }}

WORKDIR {{ splunk_home }}
USER {{ splunk_user_id }}:{{ splunk_group_id }}
RUN wget -O- "{{ splunk_tgz_url }}" | tar xz -C {{ splunk_home }}/..

COPY --chown={{ splunk_user_id }}:{{ splunk_group_id }} copy {{ splunk_home }}/

ENTRYPOINT {{ splunk_home }}/entrypoint.sh
