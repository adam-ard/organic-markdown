---
includes:
- "constants.md"
- "docker.md"
---

# This is an Electric Markdown file

## Constants

Below are some constants that you should change to match your own
environment

### <<code\_dir>>=
```{name="code_dir"}
~/code
```

### <<project\_name_recurse>>=
```{name="project_name_recurse"}
<<project_name()>>
```

### <<docker\_image_name>>=
```{lang="bash" name="docker_image_name"}
emarkdown-example
```

### <<docker\_container_name>>=
```{lang="bash" name="docker_container_name"}
emarkdown-example1
```

### <<username>>=
```{lang="bash" name="username"}
aard
```

### <<project\_name>>=
```{name="project_name"}
/home/<<username()>>/code/electric-markdown/example
```

### <<copyright\_year>>=
```{name="copyright_year"}
2024
```

## Mkdir
```{name="mkdir" lang="bash" runnable="true"}
mkdir -p <<project_name()>>
```

## Copyright Notice

```{name="copyright-c" lang="C"}
/*
  Copyright <<copyright_year()>> Adam Ard

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

```{name="copyright-dockerfile" lang="Dockerfile"}
#  Copyright <<copyright_year()>> Adam Ard
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

```{name="dockerfile" lang="Dockerfile" tangle=<<project_name()>>/Dockerfile}
<<copyright-dockerfile()>>

FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    TZ=America/Denver \
    apt install -y \
    cmake \
    build-essential

RUN useradd -ms /bin/bash <<username()>>
USER <<username()>>
WORKDIR /home/<<username()>>
```

## Docker Shell

```{name="shell" lang="bash" runnable="true"}
docker exec -it <<docker_container_name()>> /bin/bash
```

## Docker Build

```{name="build_container" lang="bash" runnable="true" dir=<<project_name()>>}
docker build -t <<docker_image_name()>> .
```

## Start Docker Container

```{name="start_container" lang="bash" runnable="true" dir="."}
docker run --rm --name <<docker_container_name()>> -d \
       -v ${PWD}:${PWD} \
       <<docker_image_name()>> \
       tail -f /dev/null
```

## Stop Docker Container

```{name="stop_container" lang="bash" runnable="true"}
docker stop <<docker_container_name()>>
```

## Run something in the container

```{name="in container" lang="bash" runnable="true" docker=<<docker_container_name()>> dir=<<project_name()>>}
hostname
pwd
ls -al <<project_name()>>
```

## Run something outside a container

```{name="out container" lang="bash" runnable="true" dir=<<project_name()>>}
hostname
pwd
ls -al <<project_name()>>
```

## Build

To build this project

```{name="build_project" lang="bash" runnable="true" docker=<<docker_container_name()>> dir=<<project_name()>>}
gcc main.c
```

## Run

Run this project

```{name="run_project" lang="bash" runnable="true" docker=<<docker_container_name()>> dir=<<project_name()>>}
./a.out
```


## Example Functions

Print x, num times
```{name="print_x_num_times" lang="python"}
for i in range(<<num>>):
    print(<<x>>)
```

```{name="test_indent" lang="C"}
printf("testing\n");
printf("testing\n");
printf("testing\n");
```

```{name="test_nesting" lang="C"}
printf("<<testing_nesting_inner()>>-1\n");

printf("<<testing_nesting_inner()>>-2\n");

printf("<<testing_nesting_inner()>>-3\n");

printf("<<testing_nesting_inner()>>-5\n");
```

```{name="testing_nesting_inner" lang="C"}
testing_me
```

```{name="msg2"}
<-end1
<-end2
```

```{name="test_exec" lang="bash" runnable="true" dir="."}
for i in $(seq 1 <<num()>>); do
  echo "<<msg()>> $i <<msg2()>>"
done
```

## Test Main

```{lang="C" tangle=<<project_name()>>/main.c}
<<copyright-c(copyright_year="2014", more="asdf",even_more="qwerty")>>

#include <stdio.h>

void main()
{
    printf("Hello Electric Markdown World\n");
    <<test_nesting()>>
    /*
     *  <<test_nesting()>>
     */
    // <<test_exec(msg="wonderful->", num="15")()>>
}
```
