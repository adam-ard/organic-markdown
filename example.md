# This is an Electric Markdown file

## Constants {#my_consts .one .two three=four five=six}

Below are some constants that you should change to match your own
environment

### <<code\_dir>>=
```{#code_dir}
~/code
```

### <<project\_name_recurse>>=
```{#project_name_recurse}
<<project_name()>>
```

### <<docker\_image_name>>=
```{.bash #docker_image_name}
emarkdown-example
```

### <<docker\_container_name>>=
```{.bash #docker_container_name}
emarkdown-example1
```

### <<username>>=
```{.bash #username}
aard
```

### <<project\_name>>=
```{#project_name}
/home/<<username()>>/code/electric-markdown/example
```

### <<copyright\_year>>=
```{#copyright_year}
2024
```

## Mkdir
```{#mkdir .bash .runnable}
mkdir -p <<project_name()>>
```

## Copyright Notice

```{#copyright-c .c}
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

```{#copyright-dockerfile .Dockerfile}
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

```{#dockerfile .Dockerfile tangle=<<project_name()>>/Dockerfile}
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

```{#shell .bash .runnable}
docker exec -it <<docker_container_name()>> /bin/bash
```

## Docker Build

```{#build_container .bash .runnable dir=<<project_name()>>}
docker build -t <<docker_image_name()>> .
```

## Start Docker Container

```{#start_container .bash .runnable dir="."}
docker run --rm --name <<docker_container_name()>> -d \
       -v ${PWD}:${PWD} \
       <<docker_image_name()>> \
       tail -f /dev/null
```

## Stop Docker Container

```{#stop_container .bash .runnable}
docker stop <<docker_container_name()>>
```

## Run something in the container

```{#in_container .bash .runnable docker=<<docker_container_name()>> dir=<<project_name()>>}
hostname
pwd
ls -al <<project_name()>>
```

## Run something outside a container

```{#out_container .bash .runnable dir=<<project_name()>>}
hostname
pwd
ls -al <<project_name()>>
```

## Build

To build this project

```{#build_project .bash .runnable docker=<<docker_container_name()>> dir=<<project_name()>>}
gcc main.c
```

## Run

Run this project

```{#run_project .bash .runnable docker=<<docker_container_name()>> dir=<<project_name()>>}
./a.out
```


## Example Functions

Print x, num times
```{#print_x_num_times .python results=stdout}
for i in range(<<num>>):
    print(<<x>>)
```

```{#test_indent .C}
printf("testing\n");
printf("testing\n");
printf("testing\n");
```

```{#test_nesting .C}
printf("<<testing_nesting_inner()>>-1\n");
printf("<<testing_nesting_inner()>>-2\n");
printf("<<testing_nesting_inner()>>-3\n");
printf("<<testing_nesting_inner()>>-5\n");
```

```{#testing_nesting_inner .C}
testing_me
```

## Test Main

```{.C tangle=<<project_name()>>/main.c}
<<copyright-c(copyright_year="2014")>>

#include <stdio.h>

void main()
{
    printf("Hello Electric Markdown World\n");
    <<test_nesting()>>
}
```
