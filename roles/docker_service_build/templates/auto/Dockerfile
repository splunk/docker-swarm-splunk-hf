FROM ubuntu:{{ ubuntu_tag }} AS splunk_hf_base

RUN ln -fs /usr/share/zoneinfo/{{ timezone }} /etc/localtime \
  && groupadd {{ splunk_group }} -g {{ splunk_group_id }} \
  && useradd {{ splunk_user }} -m -d {{ splunk_home }} -g {{ splunk_group }} -u {{ splunk_user_id }} --shell /bin/bash \
  && apt-get update \
  && apt-get install -y --no-install-recommends wget ca-certificates {{ apt_packages|join(' ') }} \
  && apt-get clean

WORKDIR {{ splunk_home }}
USER {{ splunk_user_id }}:{{ splunk_group_id }}

# copy templated files before downloading, untarring, and accepting the splunk license so user-seed.conf is available
COPY --chown={{ splunk_user_id }}:{{ splunk_group_id }} splunk {{ splunk_home }}/

# run dummy command and accept license to populate var/ prior to defining the volume
RUN wget -O- "{{ splunk_tgz_url }}" \
  | tar xz -C {{ splunk_home }}/.. \
  && {{ splunk_home }}/bin/splunk version --accept-license

# var/ needs to be a volume to pass file lock test
VOLUME ["{{ splunk_home }}/var"]

ENTRYPOINT {{ splunk_home }}/entrypoint.sh
