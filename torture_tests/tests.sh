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

echo "Running All Torture Tests"

# check that yaml values are coming through
expected_output="~/code"
actual_output=$(omd expand "@<code_dir@>")

compare_strings "$expected_output" "$actual_output"

# check the yaml values do string substitution correctly
expected_output="/home/aard/code/organic-markdown/samples"
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

echo ""
echo "Finished"




