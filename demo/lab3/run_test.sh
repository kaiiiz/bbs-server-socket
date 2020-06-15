#!/bin/bash

OUTPUT_DIR="output"
ANSWER_DIR="answer"
USER_NUM=$1
START_CASE=$2
END_CASE=$3

if [ -z ${USER_NUM} ] || [ -z ${START_CASE} ] || [ -z ${END_CASE} ]; then
  echo "Usage: $0 <number of total users> <start testcase> <end testcase>"
  exit 1
fi

USER_NO=$((${USER_NUM}-1))
DATE_FULL=$(date +%F)
DATE_TODAY=$(date +%m/%d)

for i in $(seq ${START_CASE} ${END_CASE})
do
	TARGET_DIR=${OUTPUT_DIR}/t${i}
	
	echo "Test case ${i}"
    echo "==============="
    
	number_of_files=$(ls ${TARGET_DIR} | wc -l)
	total_errors=0

	for user in $(seq 0 ${USER_NO})
	do
        sed -i "s_[0-9]\{2\}/[0-9]\{2\}_${DATE_TODAY}_g" ${ANSWER_DIR}/t${i}/user${user}
        sed -i "s_[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_${DATE_FULL}_g" ${ANSWER_DIR}/t${i}/user${user}
		errors=$( diff -wyB --suppress-common-lines ${ANSWER_DIR}/t${i}/user${user} ${OUTPUT_DIR}/t${i}/user${user} | wc -l )
		
		total_errors=$(( ${total_errors} + ${errors} ))

		if [ ${errors} -ne 0 ]; then
			echo -e "user${user}: \033[1;31m${errors} different lines!\033[m"
		fi
	done

	if [[ ${number_of_files} -ne ${USER_NUM} ]]; then
		echo -e "\033[1;31mIncorrect number of output!\033[m"
	else
		if [ ${total_errors} -eq 0 ]; then
			echo -e "\033[1;32mTest passed!\033[m"
		fi
	fi
    echo ""
done
