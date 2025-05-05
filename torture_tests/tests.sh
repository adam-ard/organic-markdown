#!/bin/bash

compare_strings() {
    local expected="$1"
    local actual="$2"

    if [[ "$expected" == "$actual" ]]; then
        printf "."
    else
        echo "Failed! Expected '$expected', Got '$actual'"
    fi
}

# remove output files
rm -rf out

# add back the out dir
mkdir out

# tangle all the files
omd tangle

echo "Running All Torture Tests"

# check that yaml values are coming through
expected_output="~/code"
actual_output=$(omd expand "@<code_dir@>")
compare_strings "$expected_output" "$actual_output"

# check the yaml values do string substitution correctly
expected_output="/home/aard/code/organic-markdown/torture_tests"
actual_output=$(omd expand "@<project_name_recurse@>")
compare_strings "$expected_output" "$actual_output"

# test multiline ref
expected_output="This is 1 thing that I said.
This is another: 2.
And this: 3"
actual_output=$(omd expand "@<multiline-test@>")
compare_strings "$expected_output" "$actual_output"

# test that the fields append when a name is reused
expected_output="2024
hello"
actual_output=$(omd expand "@<copyright_year@>")
compare_strings "$expected_output" "$actual_output"

# make sure that unnamed code src-blocks DON'T append
expected_output="Unnamed 1"
actual_output=$(cat out/unnamed1.txt)
compare_strings "$expected_output" "$actual_output"

expected_output="Unnamed 2"
actual_output=$(cat out/unnamed2.txt)
compare_strings "$expected_output" "$actual_output"

# make sure that we can run python code
expected_output="Here goes nothing testing 1
Here goes nothing testing 2"
actual_output=$(omd expand "@<test_exec_python*@>")
compare_strings "$expected_output" "$actual_output"

echo ""
echo "Finished"




