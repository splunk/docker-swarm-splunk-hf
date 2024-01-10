FROM ubuntu:{{ ubuntu_tag }} AS splunk_hf_base

{% if docker_labels is defined %}
{% for label in docker_labels %}
LABEL "{{ label.name }}"="{{ label.value }}"
{% endfor %}
{% endif %}

RUN ln -fs /usr/share/zoneinfo/{{ timezone }} /etc/localtime \
  && groupadd {{ splunk_group }} -g {{ splunk_group_id }} \
  && useradd {{ splunk_user }} -m -d {{ splunk_home }} -g {{ splunk_group }} -u {{ splunk_user_id }} --shell /bin/bash \
  && apt-get update \
  && apt-get install -y --no-install-recommends wget ca-certificates {{ apt_packages|join(' ') }} \
  && apt-get clean

# Add tini as an init to fix signal forwarding when using a bash script as the entrypoint
ENV TINI_VERSION {{ tini_version }}
ADD https://github.com/krallin/tini/releases/download/${{ tini_version }}/tini /tini
RUN chmod +x /tini

{% if install_splunk %}
# change user prior to untarring splunk
USER {{ splunk_user_id }}:{{ splunk_group_id }}

# fetch and untar splunk tgz as its own layer, so it can be consistent across builds
# done prior to VOLUME definitions.  changes via Dockerfile to VOLUME paths after their creations are discarded.
RUN wget -O- "{{ splunk_tgz_url }}" | tar xz -C {{ splunk_home }}/..
{% endif %}

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

{% if run_commands %}
# configurable RUN commands are called after file copies so they can use the copied files
{% for run_command in run_commands %}
{% if 'user' in run_command %}
USER {{ run_command.user }}{% if 'group' in run_command  %}:{{ run_command.group }}{% endif %}

{% endif %}
{% if run_command.command is string %}
RUN {{ run_command.command }}
{% else %}
RUN {{ run_command.command | join (' && ') }}
{% endif %}
{% endfor %}
{% endif %}

# run as splunk user on start
USER {{ entrypoint_user }}

# dump into $SPLUNK_HOME for exec, etc
WORKDIR {{ splunk_home }}

# btool check needs to succeed before moving on
{% if install_splunk and btool_check %}
RUN {{ splunk_home }}/bin/splunk btool check
{% endif %}

# entrypoint.sh may do run-time configurations prior to starting splunk
ENTRYPOINT [ "/tini", "--", {{ entrypoint | tojson | join(', ') }} ]

{% if healthcheck_command %}
HEALTHCHECK \
    --interval={{ healthcheck_interval_seconds }}s \
    --timeout={{ healthcheck_timeout_seconds }}s \
    --start-period={{ healthcheck_start_period_seconds }}s \
    --retries={{ healthcheck_retries }} \
    CMD {{ healthcheck_command }}
{% endif %}
