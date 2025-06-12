Use these so that the opening and closing ref symbols don't get expanded

```bash {name=o}
@<
```

```bash {name=c}
@>
```

```bash {name=OMD_UT}
../lit/omd
```

```bash {name=CMP_IF}
if [[ "$expected" == "$actual" ]]; then
    printf "."
else
    echo "Failed! Expected '$expected', Got '$actual'"
fi
```

```bash {name=CMP}
expected="@<exp@>"
actual="@<got@>"

@<CMP_IF@>
```

```bash {name=CMP_CMD}
expected="@<exp@>"
actual="$(@<got@>)"

@<CMP_IF@>
```

```bash {name=CMP_OMD_CMD}
expected="@<exp@>"
actual="$(@<OMD_UT@> @<got@>)"

@<CMP_IF@>
```

```bash {name=CMP_EXPAND}
expected="@<exp@>"
actual="$(@<OMD_UT@> expand "@<o@>@<got@>@<c@>")"

@<CMP_IF@>
```

```bash {name=status-expected}
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
```

```bash {name=file-test-expected}
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
```

```bash {name=e2e-tests dir=e2e-tests menu=true}
# remove output files
rm -rf out

# add back the out dir
mkdir out

# tangle all the files
@<OMD_UT@> tangle

echo "Running All E2E Tests"

# check that yaml values are coming through
@<CMP_EXPAND(exp=~/code got=code_dir)@>

# check a different calling convention
@<CMP_EXPAND(exp=~/code got=code_dir())@>

# check the yaml values do string substitution correctly
@<CMP_EXPAND(exp=/home/aard/code/organic-markdown/e2e-tests got=project_name_recurse)@>

# test multiline ref
expected_output="This is 1 thing that I said.
This is another: 2.
And this: 3"
@<CMP_EXPAND(exp="$expected_output" got=multiline-test)@>

expected_output="This is 11 thing that I said.
This is another: 22.
And this: 33"
@<CMP_EXPAND(exp="$expected_output" got="multiline-ref(one=11 two=22 three=33)")@>

# test that the fields append when a name is reused
expected_output="2024
hello"
@<CMP_EXPAND(exp="$expected_output" got=copyright_year)@>

# make sure that unnamed code src-blocks DON'T append
@<CMP_CMD(exp="Unnamed 1" got="cat out/unnamed1.txt")@>
@<CMP_CMD(exp="Unnamed 2" got="cat out/unnamed2.txt")@>

expected_output="Here goes nothing testing 1
Here goes nothing testing 2"
@<CMP_EXPAND(exp="$expected_output" got="test_exec_python*")@>

# file test
@<file-test-expected@>
@<CMP_CMD(exp="$expected_output" got="cat out/main.c")@>

# make sure that we still traverse into subfolders
@<CMP_EXPAND(exp="~/code-1" got="code_dir_1")@>
@<CMP_EXPAND(exp="~/code-2" got="code_dir_2")@>
@<CMP_EXPAND(exp="~/code-3" got="code_dir_3")@>
@<CMP_EXPAND(exp="~/code-4" got="code_dir_4")@>

# test python, ruby, haskell, racket, perl, javascript
@<CMP_EXPAND(exp="python: The sum of squares of even numbers from 1 to 10 is: 220" got="python_example*")@>
@<CMP_EXPAND(exp="ruby: The sum of squares of even numbers from 1 to 10 is: 220" got="ruby_example*")@>
@<CMP_EXPAND(exp="haskell: The sum of squares of even numbers from 1 to 10 is: 220" got="haskell_example*")@>
@<CMP_EXPAND(exp="racket: The sum of squares of even numbers from 1 to 10 is: 220" got="racket_example*")@>
@<CMP_EXPAND(exp="perl: The sum of squares of even numbers from 1 to 10 is: 220" got="perl_example*")@>
@<CMP_EXPAND(exp="javascript: The sum of squares of even numbers from 1 to 10 is: 220" got="javascript_example*")@>

# test argument overrides
@<CMP_EXPAND(exp="This is my message: Be happy!" got="my_msg")@>
@<CMP_EXPAND(exp="This is my message: Dude!" got="my_msg(the_msg=Dude!)")@>

expected_output="hello \"world\""
actual_output=$(@<OMD_UT@> expand "@<o@>ssh-test*@<c@>")
actual_output="$(echo "$actual_output" | sed 's/[[:space:]]*$//')"
@<CMP(exp="$expected_output" got="$actual_output")@>

@<status-expected@>
@<CMP_OMD_CMD(exp="$expected_output" got="status")@>

echo ""
echo "Finished"
```
