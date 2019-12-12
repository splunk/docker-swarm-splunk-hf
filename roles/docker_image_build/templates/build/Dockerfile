FROM ubuntu:{{ ubuntu_tag }} AS splunk_hf_base

RUN ln -fs /usr/share/zoneinfo/{{ timezone }} /etc/localtime \
  && groupadd {{ splunk_group }} -g {{ splunk_group_id }} \
  && useradd {{ splunk_user }} -m -d {{ splunk_home }} -g {{ splunk_group }} -u {{ splunk_user_id }} --shell /bin/bash \
  && apt-get update \
  && apt-get install -y --no-install-recommends wget ca-certificates {{ apt_packages|join(' ') }} \
  && apt-get clean

# change user prior to untarring splunk
USER {{ splunk_user_id }}:{{ splunk_group_id }}

# fetch and untar splunk tgz as its own layer, so it can be consistent across builds
# done prior to VOLUME definitions.  changes via Dockerfile to VOLUME paths after their creations are discarded.
RUN wget -O- "{{ splunk_tgz_url }}" | tar xz -C {{ splunk_home }}/..

# create VOLUMEs after untarring splunk
{% for volume in volumes %}
{% if volume.mount_type == 'image_volume' %}
USER {{ splunk_user_id }}:{{ splunk_group_id }}
RUN mkdir -p {{ volume.path }}
VOLUME {{ volume.path }}
{% endif %}
{% endfor %}

# perform staged file copies
{% for copy_path_name in staging_paths | sort %}
{% if staging_paths[copy_path_name] and 'dest' in staging_paths[copy_path_name] %}
{% set copy_path_config = staging_paths[copy_path_name]%}
COPY {% if 'owner' in copy_path_config %}--chown={{ copy_path_config.owner }}{% if 'group' in copy_path_config %}:{{ copy_path_config.group }}{% endif %} {% endif %}{{ copy_path_name }}/ {{ copy_path_config.dest }}/
{% endif %}
{% endfor %}

# dump into $SPLUNK_HOME for exec, etc
WORKDIR {{ splunk_home }}

# entrypoint.sh may do run-time configurations prior to starting splunk
ENTRYPOINT {{ splunk_home }}/entrypoint.sh

{% if healthcheck_command is defined %}
HEALTHCHECK --interval={{ healthcheck_interval_seconds }}s CMD {{ healthcheck_command }}
{% endif %}
