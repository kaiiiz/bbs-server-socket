#!/bin/bash

SESSION="nphw3demo"
SHORT_SLEEP_TIME=1.5
LONG_SLEEP_TIME=2.5
TESTCASE_DIR="testcase"
OUTPUT_DIR="output"
USER_NUM=4
START_CASE=1
END_CASE=5
RUN_CMD=${@:1}

if [ -n "`tmux ls | grep ${SESSION}`" ]; then
  tmux kill-session -t ${SESSION}
fi

if [ -d ${OUTPUT_DIR} ]; then
  rm -rf ${OUTPUT_DIR}
fi

mkdir ${OUTPUT_DIR}

tmux new-session -d -s ${SESSION}
tmux set remain-on-exit on
tmux select-pane -t 0
tmux split-window -v -p 10
tmux select-pane -t 0
tmux split-window -h -p 75
tmux split-window -h -p 65
tmux split-window -h -p 50

sleep 1.5

USER_ID=$((${USER_NUM}-1))

test_map=("Registration function test." "Log in and Board related function test." "Create post function test."\
 "Delete and update post function test." "Mail related function test.")

echo "Start testing..."

for i in $(seq ${START_CASE} ${END_CASE})
do
	mkdir ${OUTPUT_DIR}/t${i}
	TARGET_DIR=${OUTPUT_DIR}/t${i}
	
	echo ${test_map[$((i-1))]}

	for user in $(seq 0 ${USER_ID})
	do
		tmux send-keys -t ${user} "${RUN_CMD} | tee ${TARGET_DIR}/user${user}" Enter
		sleep ${SHORT_SLEEP_TIME}
	done

	while IFS= read -r line
	do
		index=$(echo ${line} | cut -d ':' -f1 | tr -d '\n')

		command=$(echo ${line} | cut -d':' -f2)
		tmux send-keys -t ${index} "${command}" Enter

		if [[ ${command} =~ register|create-post|read|delete-post|update-post|comment|mail ]]; then
			sleep ${LONG_SLEEP_TIME}
		else
			sleep ${SHORT_SLEEP_TIME}
		fi
	done < ${TESTCASE_DIR}/t${i}
	sleep 1.5
done

tmux send-keys -t ${USER_NUM} "./run_test.sh ${USER_NUM} ${START_CASE} ${END_CASE}" Enter

tmux attach-session -t ${SESSION}

