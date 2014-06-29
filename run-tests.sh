#!/bin/sh

tests_string=`cat test-schedule.txt`
read -a tests <<< $tests_string

passed_count=0
failed_count=0

for test in "${tests[@]}"
do
    echo "Running '$test' ..."
    source tests/$test.sh > /tmp/hdb-test.out
    eval "echo \"$(< expected/$test.out)\"" > /tmp/hdb-test.expected
    diff_result=$(diff /tmp/hdb-test.out /tmp/hdb-test.expected)
    if [ "$diff_result" == "" ]
    then
        echo "Passed."
        passed_count=$((passed_count+1))
    else
        echo "Failed."
        failed_count=$((failed_count+1))
    fi
done

if [ $failed_count -eq 0 ]
then
    echo "All tests passed successfully!"
else
    echo "$failed_count of $((failed_count+passed_count)) tests failed."
fi
