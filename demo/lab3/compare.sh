#!/bin/bash

OUTPUT_DIR="output"
ANSWER_DIR="answer"
TEST_CASE_NUM=$1
USER_ID=$2

if [ -z ${TEST_CASE_NUM} ] || [ -z ${USER_ID} ]; then
  echo "Usage: $0 <testcase number> <user number>"
  exit 1
fi

vimdiff -c "set diffopt+=iwhite" -c "map <F1> :qa<CR>" ${OUTPUT_DIR}/t${TEST_CASE_NUM}/user${USER_ID} \
${ANSWER_DIR}/t${TEST_CASE_NUM}/user${USER_ID}