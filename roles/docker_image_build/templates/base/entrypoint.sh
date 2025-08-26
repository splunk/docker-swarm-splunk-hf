#!/usr/bin/env bash
# shellcheck disable=all

# set -e

# performs mongod upgrades and engine migrations as configured
migrate_kvstore() {
    {{ splunk_home }}/bin/splunk migrate migrate-kvstore-36-40

    {% if migrate_kvstore is defined %}
    {{ splunk_home }}/bin/splunk start --accept-license --answer-yes --no-prompt $@
    {{ splunk_home }}/bin/splunk stop
    {{ splunk_home }}/bin/splunk migrate kvstore-storage-engine --target-engine wiredTiger
    {% endif %}

    {% if upgrade_kvstore is defined %}
    {{ splunk_home }}/bin/splunk migrate migrate-kvstore
    {% endif %}
}

# starts Splunk using the CLI
start_splunk() {
    printf "Performing kvstore migration before starting Splunk\n"
    migrate_kvstore

    printf "Starting Splunk with arguments ${*}\n"
    {{ splunk_home }}/bin/splunk start --nodaemon --accept-license --answer-yes --no-prompt $@ &
    splunk_pid=$!
    printf "Splunk is now running with pid ${splunk_pid}\n"
    wait_for_splunk_to_stop
}

# stops Splunk using the CLI
stop_splunk() {
    printf "Stopping Splunk running with pid ${splunk_pid} for graceful shutdown\n"
    {{ splunk_home }}/bin/splunk stop
    if [ -f {{ splunk_home }}/var/run/splunk/conf-mutator.pid ]; then
        printf "Found conf-mutator.pid file containing pid %d after shutdown, removing...\n" "$(cat {{ splunk_home }}/var/run/splunk/conf-mutator.pid)"
        rm -vf {{ splunk_home }}/var/run/splunk/conf-mutator.pid
    fi
}

wait_for_splunk_to_stop() {
    wait -n ${splunk_pid}
    printf "Entrypoint has detected that Splunk is no longer running and is now exiting\n"
}

# log graceful shutdown and call stop_splunk
graceful_shutdown() {
    printf "Received SIGTERM interrupt, now stopping Splunk running with PID ${splunk_pid} for graceful shutdown\n"
    printf "Stopping Splunk running with pid ${splunk_pid} for graceful shutdown\n"
    {{ splunk_home }}/bin/splunk stop
    if [ -f {{ splunk_home }}/var/run/splunk/conf-mutator.pid ]; then
        printf "Found conf-mutator.pid file containing pid %d after shutdown, removing...\n" "$(cat {{ splunk_home }}/var/run/splunk/conf-mutator.pid)"
        rm -vf {{ splunk_home }}/var/run/splunk/conf-mutator.pid
    fi
}

# calls stop_splunk function when SIGINT and SIGTERM are received
# to allow for graceful shutdowns in Docker Swarm
trap graceful_shutdown SIGTERM

# restarts Splunk using the CLI
restart_splunk() {
    stop_splunk
    start_splunk
}

########################
# BEGIN EXECUTION HERE #
########################

case "${1}" in
    "migrate_kvstore")
        migrate_kvstore
    ;;
    "start"|"") # default
        migrate_kvstore
        start_splunk
    ;;
    "stop")
        stop_splunk
    ;;
    "restart")
        restart_splunk
    ;;
esac
