#!/bin/bash

OUTPUT_DIR="output"
ANSWER_DIR="answer"

USER_NUMS=$1
START_CASE=$2
END_CASE=$3
SKIP_CASE=$4

if [ -z ${USER_NUMS} ] || [ -z ${START_CASE} ] || [ -z ${END_CASE} ]; then
    echo "Usage: $0 <number of total users> <start testcase> <end testcase>"
    exit 1
fi

DATE_FULL=$(date +%F)
DATE_TODAY=$(date +%m/%d)

for testcase_no in $(seq ${START_CASE} ${END_CASE}); do
    if [[ -n "${SKIP_CASE}" && ${SKIP_CASE} -eq ${testcase_no} ]]; then
        continue
    fi

	TARGET_DIR=${OUTPUT_DIR}/t${testcase_no}

    echo -e "\033[1;34m===== Test case ${testcase_no} =====\033[m"

	number_of_files=$( ls ${TARGET_DIR} | wc -l )
	total_diffs=0

	for user in $(seq 0 $((${USER_NUMS}-1))); do
        sed -i "s_[0-9]\{2\}/[0-9]\{2\}_${DATE_TODAY}_g" ${ANSWER_DIR}/t${testcase_no}/user${user}
        sed -i "s_[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}_${DATE_FULL}_g" ${ANSWER_DIR}/t${testcase_no}/user${user}

        diff_lines=$( diff -wyB --suppress-common-lines ${ANSWER_DIR}/t${testcase_no}/user${user} ${OUTPUT_DIR}/t${testcase_no}/user${user} | wc -l )
        total_diffs=$(( ${total_diffs} + ${diff_lines} ))

		if [ ${diff_lines} -ne 0 ]; then
			echo -e "user${user}: \033[1;31m${diff_lines} different lines!\033[m"

            if [[ ! ${diff_cases} =~ ${testcase_no} ]]; then
                diff_cases="${diff_cases} ${testcase_no}"
            fi
		fi
	done

	if [[ ${number_of_files} -ne ${USER_NUMS} ]]; then
		echo -e "\033[1;31mDifferent number of output!\033[m"
	else
		if [ ${total_diffs} -eq 0 ]; then
			echo -e "\033[1;32mTest passed!\033[m"
            pass_cases="${pass_cases} ${testcase_no}"
		fi
	fi
    echo ""
done

echo -e "\033[1;34m======= Summary =======\033[m"
[ -n "${pass_cases}" ] && echo -e "\033[1;32m[Correct]\033[m:${pass_cases}"
[ -n "${diff_cases}" ] && echo -e "\033[1;31m[Different]\033[m:${diff_cases}"