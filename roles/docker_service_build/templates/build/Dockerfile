FROM ubuntu:{{ ubuntu_tag }} AS splunk_hf_base

RUN ln -fs /usr/share/zoneinfo/{{ timezone }} /etc/localtime \
  && groupadd {{ splunk_group }} -g {{ splunk_group_id }} \
  && useradd {{ splunk_user }} -m -d {{ splunk_home }} -g {{ splunk_group }} -u {{ splunk_user_id }} --shell /bin/bash \
  && apt-get update \
  && apt-get install -y --no-install-recommends wget ca-certificates {{ apt_packages|join(' ') }} \
  && apt-get clean

WORKDIR {{ splunk_home }}
USER {{ splunk_user_id }}:{{ splunk_group_id }}

# copy files before downloading, untarring, and accepting the splunk license so user-seed.conf is available
{% for copy_path_name in staging_paths | sort %}
{% if staging_paths[copy_path_name] and 'dest' in staging_paths[copy_path_name] %}
{% set copy_path_config = staging_paths[copy_path_name]%}
COPY {% if 'owner' in copy_path_config %}--chown={{ copy_path_config.owner }}{% if 'group' in copy_path_config %}:{{ copy_path_config.group }}{% endif %} {% endif %}{{ copy_path_name }}/ {{ copy_path_config.dest }}/
{% endif %}
{% endfor %}

# run dummy command and accept license to populate var/ prior to defining the volume
RUN wget -O- "{{ splunk_tgz_url }}" \
  | tar xz -C {{ splunk_home }}/.. \
  && {{ splunk_home }}/bin/splunk version --accept-license

# var/ needs to be a volume to pass file lock test
VOLUME ["{{ splunk_home }}/var"]

ENTRYPOINT {{ splunk_home }}/entrypoint.sh
