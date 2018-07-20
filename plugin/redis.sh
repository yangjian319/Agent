#!/bin/bash
# scan redis info
# Version 1.2
# Last change: jonnysun 2015-8-24
# Last change: jonnysun 2015-10-30 fix get memory bug.
# Last change: jonnysun 2015-11-16 set nc sleep to 1s.

FILE_REDIS_PORT=`mktemp -t REDIS_PORT.XXXXXXXXXXX`
FILE_REDIS_INFO=`mktemp -t REDIS_INFO.XXXXXXXXXXX`
PID="0"
ALL_IP=`ifconfig | grep "inet addr:" | grep "Bcast" | awk '{print $2}' | awk -F":" '{print $2}'`
IP="0.0.0.0"

LISTEN_IP="0.0.0.0"
LISTEN_PORT="6379"
ROLE="master"
PEER="null"
PEER_PORT="null"
VERSION="0"
MAX_MEM="0"
REDIS_MODE="0"
CONFIG_FILE="0"
BIN_FILE="0"

netstat -nltp | grep "redis-serve" | awk '{print $4,$7}' \
    | grep -Eo "[.0-9]+:[0-9]+ [0-9]+" | tr ':' ' ' > ${FILE_REDIS_PORT}

cat ${FILE_REDIS_PORT} | while read LISTEN_IP LISTEN_PORT PID;
do
    (printf "info\r\n";sleep 1)  | nc ${LISTEN_IP} ${LISTEN_PORT} > ${FILE_REDIS_INFO}
    if [ ! -s ${FILE_REDIS_INFO} ]; then
        continue;
    fi

    ROLE=`grep "role:" ${FILE_REDIS_INFO} | awk -F: '{print $2}' | tr -d ' \r\n'`
    if [ "${ROLE}"x == "master"x ]; then
        PEER="null"
        PEER_PORT="null"
    else
        PEER=`grep "master_host:" ${FILE_REDIS_INFO} | awk -F: '{print $2}' | tr -d ' \r\n'`
        PEER_PORT=`grep "master_port:" ${FILE_REDIS_INFO} | awk -F: '{print $2}' | tr -d ' \r\n'`
    fi
    VERSION=`grep "redis_version:" ${FILE_REDIS_INFO} | awk -F: '{print $2}' | tr -d ' \r\n'`
    REDIS_MODE=`grep "redis_mode:" ${FILE_REDIS_INFO} | awk -F: '{print $2}' | tr -d ' \r\n'`
    CONFIG_FILE=`grep "config_file:" ${FILE_REDIS_INFO} | awk -F: '{print $2}' | tr -d ' \r\n'`

    # can't read from info
    MAX_MEM=`(printf "config get maxmemory\r\n";sleep 1)  | nc ${LISTEN_IP} ${LISTEN_PORT} | tail -1 | grep -Eo "[0-9]+"  | tr -d ' \r\n'`
    if [[ -z ${MAX_MEM} ]]; then
        MAX_MEM=0
    fi
    BIN_FILE=`readlink /proc/${PID}/exe | tr -d ' \r\n'`

    # if 0.0.0.0 expand
    if [ "${LISTEN_IP}"x == "0.0.0.0"x ];then
        for IP in ${ALL_IP}
        do
            echo "${IP}||${LISTEN_PORT}||${ROLE}||${PEER}||${PEER_PORT}||${VERSION}||${MAX_MEM}||${REDIS_MODE}||${CONFIG_FILE}||${BIN_FILE}"
        done
    else
        echo "${LISTEN_IP}||${LISTEN_PORT}||${ROLE}||${PEER}||${PEER_PORT}||${VERSION}||${MAX_MEM}||${REDIS_MODE}||${CONFIG_FILE}||${BIN_FILE}"
    fi
done

rm -f ${FILE_REDIS_PORT}
rm -f ${FILE_REDIS_INFO}

