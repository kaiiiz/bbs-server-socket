#!/bin/bash

SESSION="IntroNP4Demo"

SHORT_SLEEP_TIME=1.5
LONG_SLEEP_TIME=2.5

TESTCASE_DIR="testcase"
OUTPUT_DIR="output"
USER_NUMS=4

START_CASE=1
END_CASE=3
SKIP_CASE=

INPUT_CMD=${@:1}

if [ -d ${OUTPUT_DIR} ]; then
    rm -rf ${OUTPUT_DIR}
fi

mkdir ${OUTPUT_DIR}

if [ "`tmux ls | grep ${SESSION}`" ]; then
    tmux kill-session -t ${SESSION}
fi

tmux new-session -d -s ${SESSION} -n demo_testcase1
tmux set remain-on-exit on

test_list=("basic function test" "simple subscription test" "final test")

for testcase_no in $(seq ${START_CASE} ${END_CASE}); do
    if [[ -n "${SKIP_CASE}" && ${SKIP_CASE} -eq ${testcase_no} ]]; then
        continue
    fi

    echo -e "\033[1;34m======= Running ${test_list[$((${testcase_no}-1))]}  =======\033[m"
    tmux split-window -h
    tmux split-window -h
    tmux split-window -h
    tmux select-layout tiled

    mkdir ${OUTPUT_DIR}/t${testcase_no}
	TARGET_DIR=${OUTPUT_DIR}/t${testcase_no}

    for user_no in $(seq 0 $((${USER_NUMS}-1))); do
		sleep ${SHORT_SLEEP_TIME}
        tmux send-keys -t ${user_no} "${INPUT_CMD} | tee ${TARGET_DIR}/user${user_no}" Enter
	done

    while IFS= read -r line; do
        echo ${line}
        user_no=$(echo ${line} | cut -d ':' -f1 | tr -d '\n')
		command=$(echo ${line} | cut -d':' -f2)
		tmux send-keys -t ${user_no} "${command}" Enter

		if [[ ${command} =~ register|create-post|read|delete-post|update-post|comment ]]; then
			sleep ${LONG_SLEEP_TIME}
		else
			sleep ${SHORT_SLEEP_TIME}
		fi
    done < ${TESTCASE_DIR}/t${testcase_no}
    sleep ${SHORT_SLEEP_TIME}

    tmux new-window -n demo_testcase$((${testcase_no}+1))
    echo -e "\033[1;34m======= Finish test case $((${testcase_no})) =======\033\n[m"
done

tmux rename-window test_results
sleep ${SHORT_SLEEP_TIME}
tmux send-keys -t 0 "./run_test.sh ${USER_NUMS} ${START_CASE} ${END_CASE} ${SKIP_CASE}" Enter
tmux -2 attach-session -t ${SESSION}