#!/bin/bash

SERVER_IP=$1
SERVER_PORT=$2
SESSION="np_demo"
SLEEP_TIME=0.5
if [ -z ${SERVER_IP} ] || [ -z ${SERVER_PORT} ]; then
    echo "Usage: $0 <server ip> <server port>"
    exit 1
fi

if [ -n "`tmux ls | grep ${SESSION}`" ]; then
  tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION
tmux set remain-on-exit on

tmux select-pane -t 0
tmux split-window -v
tmux split-window -h -p 80
tmux split-window -h -p 74
tmux split-window -h -p 65
tmux split-window -h -p 50

tmux select-pane -t 0
tmux split-window -h -p 80
tmux split-window -h -p 74
tmux split-window -h -p 65
tmux split-window -h -p 50

# cat testcase | 
# while IFS= read data 
# do
#     tmux send-keys -t 0 "$data" Enter
#     sleep 1
# done

sleep 2.5
echo "Connection test."
for i in $(seq 0 9)
do
    tmux send-keys -t ${i} "telnet ${SERVER_IP} ${SERVER_PORT}" Enter
    sleep 0.5
done

echo "Registeration test"
for i in $(seq 0 9)
do
    # register successfully
    tmux send-keys -t ${i} "register user${i} user${i}@qwer.zxcv user${i}" Enter
    sleep $SLEEP_TIME
    # show already used
    tmux send-keys -t ${i} "register user${i} user${i}@qwer.zxcv user${i}" Enter
    sleep $SLEEP_TIME
    # command format incorrect
    tmux send-keys -t ${i} "register user${i} user${i}@qwer.zxcv" Enter
    sleep $SLEEP_TIME
    tmux send-keys -t ${i} "login user${i}" Enter 
    sleep $SLEEP_TIME
done

echo "Functions test"
index=0
for tc in qwer asdf zxcv qwer asdf zxcv qwer asdf zxcv bnmm
do
    # types wrong account and password
    tmux send-keys -t ${index} "login ${tc} ${tc}" Enter 
    sleep $SLEEP_TIME
    # show login first
    tmux send-keys -t ${index} "whoami" Enter 
    sleep $SLEEP_TIME
    # show login first
    tmux send-keys -t ${index} "logout" Enter 
    sleep $SLEEP_TIME

    # types correct account and password
    tmux send-keys -t ${index} "login user${index} user${index}" Enter 
    sleep $SLEEP_TIME
    # show logout first
    tmux send-keys -t ${index} "login user${index} user${index}" Enter 
    sleep $SLEEP_TIME
    # show username
    tmux send-keys -t ${index} "whoami" Enter 
    sleep $SLEEP_TIME
    # show bye message
    tmux send-keys -t ${index} "logout" Enter
    sleep $SLEEP_TIME
    let "index++"
done

echo "Switch users."
for i in $(seq 0 9)
do
    let "index=9-i"
    tmux send-keys -t ${index} "login user${i} user${i}" Enter
    sleep $SLEEP_TIME
    tmux send-keys -t ${index} "whoami" Enter 
    sleep $SLEEP_TIME
    tmux send-keys -t ${index} "logout" Enter 
    sleep $SLEEP_TIME
    tmux send-keys -t ${index} "exit" Enter 
    sleep $SLEEP_TIME
done

echo "Show result."
sleep 3
tmux attach-session -t $SESSION

