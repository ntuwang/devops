#!/usr/bin/env bash

APP=devops
PORT=8000

WORKSPACE=$(cd $(dirname $0)/; pwd)
cd ${WORKSPACE}

logdir="logs"
mkdir -p ${logdir}

pidfile=${logdir}/${APP}.pid
logfile=${logdir}/${APP}.log

function requirement() {
    source ./venv/bin/activate
    python3 -m pip install -r ./requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
}

function init() {
    echo "Initing Devops"
    echo "----------------"
    python3 -m pip install --user virtualenv -i https://mirrors.aliyun.com/pypi/simple/
    if [[ ! -d "venv" ]]; then
        python3 -m virtualenv --system-site-packages venv
    fi

    requirement
    if [[ $? == 0 ]]; then
        echo "************************************************"
        echo -e "\033[42;37m >>>>>> Initing Devops SUCESS <<<<<< \033[0m"
        echo "************************************************"
    else
        echo "************************************************"
        echo -e "\033[41;37m >>>>>> Initing Devops ERROR <<<<<< \033[0m"
        echo "************************************************"
    fi
}

function check_pid() {
    if [[ -f ${pidfile} ]]; then
        pid=$(cat ${pidfile})
        if [[ -n ${pid} ]]; then
            running=$(ps -p ${pid}|grep -v "PID TTY" |wc -l)
            return ${running}
        fi
    fi
    return 0
}

function start() {
    echo -e "\033[42;37m  ----->> Starting Devops <<------ \033[0m"
    source ./venv/bin/activate
    check_pid
    running=$?
    if [[ ${running} -gt 0 ]]; then
        echo -n "${APP} now is rcunning already, pid="
        cat ${pidfile}
        return 1
    fi
    gunicorn -w 2 -b 127.0.0.1:${PORT} ${APP}.wsgi:application -D --pid ${pidfile} --capture-output --log-level debug --log-file=${logfile} 2>&1
    sleep 1
    echo -n "${APP} started..., pid="
    cat ${pidfile}
}

function stop() {
    pid=$(cat ${pidfile})
    kill ${pid}
    echo "${APP} quit ..."
}

function restart() {
    stop
    sleep 2
    start
}

function status() {
    check_pid
    running=$?
    if [ ${running} -gt 0 ];then
        echo -n "${APP} now is running, pid="
        cat ${pidfile}
    else
        echo "${APP} is stoped ..."
    fi
}

function reload() {
    python manage.py collectstatic --noinput
}

case "$1" in
    init )
        init
        ;;
    start )
        start
        ;;
    stop )
        stop
        ;;
    status )
        status
        ;;
    restart )
        restart
        ;;
    reload )
        reload
        ;;
    * )
        echo "************************************************"
        echo "Usage: sh admin {init|start|stop|restart|status|reload}"
        echo "************************************************"
        ;;
esac