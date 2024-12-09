---
constants:
  code_dir: ~/code
  project_name_recurse: \@<project_name()@>
  docker_image_name: omarkdown-example
  docker_container_name: omarkdown-example1
  username: aard
  project_name: /home/@<username@>/code/organic-markdown/samples
  copyright_year: 2024
  multi_word: 'one two three four               five'
---

# This is an Organic Markdown file for the project: @<username@>

``` {name=multiline-ref}
This is @<one@> thing that I said.
This is another: @<two@>.
And this: @<three@>
```

``` {name=multiline-test}
@<multiline-ref(one=1
                two=2
                three=3)@>
```

## Mkdir
```{name="mkdir" lang="bash" menu="true"}
mkdir -p @<project_name@>
```

## Failed bash command
```{name="failed" lang="bash" menu="true"}
ls asdfasdfasdf
```

## Successful bash command
```{name="success" lang="bash" menu="true"}
ls LIT.md
```

## Append
``` {name="copyright_year"}
hello
```

```{name=msg1}
this is great
```

```bash {name=four menu=true dir="."}
echo @<msg1@>
```

## Copyright Notice

```{name="copyright-c" lang="C"}
/*
  Copyright @<copyright_year@> Adam Ard

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
```

```Dockerfile {name="copyright-dockerfile"}
#  Copyright @<copyright_year@> Adam Ard
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
```

## Dockerfile

```Dockerfile {tangle=@<project_name@>/Dockerfile}
@<copyright-dockerfile@>

FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    TZ=America/Denver \
    apt install -y \
    cmake \
    build-essential

RUN useradd -ms /bin/bash @<username@>
USER @<username@>
WORKDIR /home/@<username@>
```

## Docker Shell

```{name="shell" lang="bash" menu="true"}
docker exec -it @<docker_container_name@> /bin/bash
```

## Docker Build

```{name="build_container" lang="bash" menu="true" dir=@<project_name@>}
docker build -t @<docker_image_name@> .
```

## Start Docker Container

```{name="start_container" lang="bash" menu="true" dir="."}
docker run --rm --name @<docker_container_name@> -d \
       -v ${PWD}:${PWD} \
       @<docker_image_name@> \
       tail -f /dev/null
```

## Stop Docker Container

```{name="stop_container" lang="bash" menu="true"}
docker stop @<docker_container_name@>
```

## Run something in the container

```bash {name="in container" menu=true}
@<docker(txt=@<dir(txt=@<lang.bash(txt=@<in_cont@>)@> cwd=@<project_name@>)@> cont=@<docker_container_name@>)@>
```

^ This works the same as this (except above does line pre-post fixing):

```bash {name="in_cont" dir=@<project_name@> docker=@<docker_container_name@> menu=true}
hostname
pwd
ls -al @<project_name@>
```

## Run something outside a container

```bash {name="out container" menu="true" dir=@<project_name@>}
hostname
pwd
ls -al @<project_name@>
```

## Run something with a name with spaces in it
```{name="call_spaces"}
@<out container*@>
```

## Build

To build this project

```{name="build_project" lang="bash" menu="true" docker=@<docker_container_name@> dir=@<project_name@>}
gcc main.c
```

## Run

Run this project

```{name="run_project" lang="bash" menu="true" docker=@<docker_container_name@> dir=@<project_name@>}
./a.out
```


## Python Code

```{name="python_example" lang="python" menu="true"}
result = sum(x**2 for x in range(1, 11) if x % 2 == 0); print(f"python: The sum of squares of even numbers from 1 to 10 is: {result}")
```

## Ruby Code

```{name="ruby_example" lang="ruby" menu="true"}
result = (1..10).select(&:even?).map { |x| x**2 }.sum; puts "ruby: The sum of squares of even numbers from 1 to 10 is: #{result}"
```

## Haskell Code

```{name="haskell_example" lang="haskell" menu="true"}
let result = sum [x^2 | x <- [1..10], even x] in putStrLn $ "haskell: The sum of squares of even numbers from 1 to 10 is: " ++ show result
```

## racket Code

```racket {name="racket_example" lang="racket" menu="true"}
(displayln (string-append "racket: The sum of squares of even numbers from 1 to 10 is: " (number->string (apply + (map (lambda (x) (* x x)) (filter even? (range 1 11)))))))
```

## perl Code

```racket {name="perl_example" lang="perl" menu="true"}
$result = 0; $result += $_ ** 2 for grep { $_ % 2 == 0 } 1..10; say "perl: The sum of squares of even numbers from 1 to 10 is: $result";
```

## javascript Code

```racket {name="javascript_example" lang="javascript" menu="true"}
const result = [...Array(11).keys()].slice(1).filter(x => x % 2 === 0).map(x => x ** 2).reduce((a, b) => a + b, 0); console.log(`javascript: The sum of squares of even numbers from 1 to 10 is: ${result}`);
```


## Example Functions

Print x, num times
```{name="print_x_num_times" lang="python"}
for i in range(@<num@>):
    print(@<x@>)
```

```{name="test_indent" lang="C"}
printf("testing\n");
printf("testing\n");
printf("testing\n");
```

```{name="test_nesting" lang="C"}
printf("@<testing_nesting_inner@>-1\n");

printf("@<testing_nesting_inner@>-2\n");

printf("@<testing_nesting_inner@>-3\n");

printf("@<testing_nesting_inner@>-5\n");
```

```{name="testing_nesting_inner" lang="C"}
testing_me
```

```{name="msg"}
begin->
```

```{name="msg2"}
<-end1
<-end2
```

```{name="test_exec" lang="bash" menu="true" dir="."}
for i in $(seq 1 @<num@>); do
  echo "@<msg@> $i @<msg2@>"
done
```

```python {name="test_exec_python" lang="python" menu="true" dir="."}
testing="testing"
print(f"Here goes nothing {testing} 1")
print(f"Here goes nothing {testing} 2")
```

```{name="includes"}
<stdio.h>
```

```{name="includes"}
<stdlib.h>
```

```{name="includes"}
<string.h>
```

## Test Main

```C {tangle=@<project_name@>/main.c}
@<copyright-c(copyright_year="2014", more="asdf",even_more="qwerty")@>

#include @<includes@>

void main()
{
    printf("Hello Organic Markdown World\n");
    @<test_nesting@>
    /*
     *  @<test_nesting@>
     */
    // @<test_exec*(msg="wonderful->", num="15")@>
}
```
