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
{% for template_path in template_paths %}
{% if 'dest' in template_path and template_path.condition %}
COPY {% if 'owner' in template_path %}--chown={{ template_path.owner }}{% if 'group' in template_path %}:{{ template_path.group }}{% endif %} {% endif %}{{ template_path.name }} {{ template_path.dest }}/
{% endif %}
{% endfor %}

# run dummy command and accept license to populate var/ prior to defining the volume
RUN wget -O- "{{ splunk_tgz_url }}" \
  | tar xz -C {{ splunk_home }}/.. \
  && {{ splunk_home }}/bin/splunk version --accept-license

# var/ needs to be a volume to pass file lock test
VOLUME ["{{ splunk_home }}/var"]

ENTRYPOINT {{ splunk_home }}/entrypoint.sh
