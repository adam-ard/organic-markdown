#!/bin/bash

OMD_UNDER_TEST="../lit/omd"

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
${OMD_UNDER_TEST} tangle

echo "Running All E2E Tests"

# check that yaml values are coming through
expected_output="~/code"
actual_output=$(${OMD_UNDER_TEST} expand "@<code_dir@>")
compare_strings "$expected_output" "$actual_output"

# check a different calling convention
expected_output="~/code"
actual_output=$(${OMD_UNDER_TEST} expand "@<code_dir()@>")
compare_strings "$expected_output" "$actual_output"

# check the yaml values do string substitution correctly
expected_output="/home/aard/code/organic-markdown/e2e-tests"
actual_output=$(${OMD_UNDER_TEST} expand "@<project_name_recurse@>")
compare_strings "$expected_output" "$actual_output"

# test multiline ref
expected_output="This is 1 thing that I said.
This is another: 2.
And this: 3"
actual_output=$(${OMD_UNDER_TEST} expand "@<multiline-test@>")
compare_strings "$expected_output" "$actual_output"

expected_output="This is 11 thing that I said.
This is another: 22.
And this: 33"
actual_output=$(${OMD_UNDER_TEST} expand "@<multiline-ref(one=11 two=22 three=33)@>")
compare_strings "$expected_output" "$actual_output"

# test that the fields append when a name is reused
expected_output="2024
hello"
actual_output=$(${OMD_UNDER_TEST} expand "@<copyright_year@>")
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
actual_output=$(${OMD_UNDER_TEST} expand "@<test_exec_python*@>")
compare_strings "$expected_output" "$actual_output"

# file test
expected_output=$(cat <<'EOF'
/*
  Copyright 2014 Adam Ard

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void main()
{
    printf("Hello Organic Markdown World\n");
    printf("testing_me-1\n");
    
    printf("testing_me-2\n");
    
    printf("testing_me-3\n");
    
    printf("testing_me-5\n");
    /*
     *  printf("testing_me-1\n");
     *  
     *  printf("testing_me-2\n");
     *  
     *  printf("testing_me-3\n");
     *  
     *  printf("testing_me-5\n");
     */
    // wonderful-> 1 <-end1
    // wonderful-> 1 <-end2
    // wonderful-> 2 <-end1
    // wonderful-> 2 <-end2
    // wonderful-> 3 <-end1
    // wonderful-> 3 <-end2
    // wonderful-> 4 <-end1
    // wonderful-> 4 <-end2
    // wonderful-> 5 <-end1
    // wonderful-> 5 <-end2
    // wonderful-> 6 <-end1
    // wonderful-> 6 <-end2
    // wonderful-> 7 <-end1
    // wonderful-> 7 <-end2
    // wonderful-> 8 <-end1
    // wonderful-> 8 <-end2
    // wonderful-> 9 <-end1
    // wonderful-> 9 <-end2
    // wonderful-> 10 <-end1
    // wonderful-> 10 <-end2
    // wonderful-> 11 <-end1
    // wonderful-> 11 <-end2
    // wonderful-> 12 <-end1
    // wonderful-> 12 <-end2
    // wonderful-> 13 <-end1
    // wonderful-> 13 <-end2
    // wonderful-> 14 <-end1
    // wonderful-> 14 <-end2
    // wonderful-> 15 <-end1
    // wonderful-> 15 <-end2
}
EOF
)
actual_output=$(cat out/main.c)
compare_strings "$expected_output" "$actual_output"

# make sure that we still traverse into subfolders
expected_output="~/code-1"
actual_output=$(${OMD_UNDER_TEST} expand "@<code_dir_1@>")
compare_strings "$expected_output" "$actual_output"

expected_output="~/code-2"
actual_output=$(${OMD_UNDER_TEST} expand "@<code_dir_2@>")
compare_strings "$expected_output" "$actual_output"

expected_output="~/code-3"
actual_output=$(${OMD_UNDER_TEST} expand "@<code_dir_3@>")
compare_strings "$expected_output" "$actual_output"

expected_output="~/code-4"
actual_output=$(${OMD_UNDER_TEST} expand "@<code_dir_4@>")
compare_strings "$expected_output" "$actual_output"

# test python example
expected_output="python: The sum of squares of even numbers from 1 to 10 is: 220"
actual_output=$(${OMD_UNDER_TEST} expand "@<python_example*@>")
compare_strings "$expected_output" "$actual_output"

# test ruby example
expected_output="ruby: The sum of squares of even numbers from 1 to 10 is: 220"
actual_output=$(${OMD_UNDER_TEST} expand "@<ruby_example*@>")
compare_strings "$expected_output" "$actual_output"

# test haskell example
expected_output="haskell: The sum of squares of even numbers from 1 to 10 is: 220"
actual_output=$(${OMD_UNDER_TEST} expand "@<haskell_example*@>")
compare_strings "$expected_output" "$actual_output"

# test racket example
expected_output="racket: The sum of squares of even numbers from 1 to 10 is: 220"
actual_output=$(${OMD_UNDER_TEST} expand "@<racket_example*@>")
compare_strings "$expected_output" "$actual_output"

# test perl example
expected_output="perl: The sum of squares of even numbers from 1 to 10 is: 220"
actual_output=$(${OMD_UNDER_TEST} expand "@<perl_example*@>")
compare_strings "$expected_output" "$actual_output"

# test javascript example
expected_output="javascript: The sum of squares of even numbers from 1 to 10 is: 220"
actual_output=$(${OMD_UNDER_TEST} expand "@<javascript_example*@>")
compare_strings "$expected_output" "$actual_output"

# test argument overrides
expected_output="This is my message: Be happy!"
actual_output=$(${OMD_UNDER_TEST} expand "@<my_msg@>")
compare_strings "$expected_output" "$actual_output"

expected_output="This is my message: Dude!"
actual_output=$(${OMD_UNDER_TEST} expand "@<my_msg(the_msg=Dude!)@>")
compare_strings "$expected_output" "$actual_output"

expected_output="hello \"world\""
actual_output=$(${OMD_UNDER_TEST} expand "@<ssh-test*@>")
actual_output="$(echo "$actual_output" | sed 's/[[:space:]]*$//')"

compare_strings "$expected_output" "$actual_output"

expected_output=$(cat <<'EOF'
Available commands:
  (use "omd run <cmd>" to execute the command)
        ./main.o.md:
            mkdir
            failed
            success
            four
            shell
            build_container
            start_container
            stop_container
            in container
            in_cont
            out container
            build_project
            run_project
            python_example
            ruby_example
            haskell_example
            racket_example
            perl_example
            javascript_example
            test_exec
            test_exec_python

Output files:
  (use "omd tangle" to generate output files)
        out/Dockerfile
        out/main.c
        out/unnamed1.txt
        out/unnamed2.txt
EOF
)
actual_output=$(${OMD_UNDER_TEST} status)

compare_strings "$expected_output" "$actual_output"

echo ""
echo "Finished"




