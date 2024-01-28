# This is an Electric Markdown file

## Constants {#my_consts .one .two three=four five=six}

Below are some constants that you should change to match your own
environment

### <<code\_dir>>=
```{#code_dir}
~/code
```

### <<project\_name>>=
```{#project_name}
example
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

### <<docker\_container_user>>=
```{.bash #docker_container_user}
build_user
```

## Mkdir
```{#mkdir .bash .runnable}
mkdir -p <<project_name()>>
```

## Dockerfile

```{#dockerfile .Dockerfile tangle="<<project_name()>>/Dockerfile"}
FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    TZ=America/Denver \
    apt install -y \
    cmake \
    build-essential

RUN useradd -ms /bin/bash build_user
USER build_user
WORKDIR /home/build_user
```

## Docker Build

```{#build_container .bash .runnable dir="<<project_name()>>"}
docker build -t <<docker_image_name()>> .
```

## Start Docker Container

```{#start_container .bash .runnable dir="."}
docker run --rm --name <<docker_container_name()>> -d \
       -v ./<<project_name()>>:/home/<<docker_container_user()>>/<<project_name()>> \
       <<docker_image_name()>> \
       tail -f /dev/null
```

## Stop Docker Container

```{#stop_container .bash .runnable}
docker stop <<docker_container_name()>>
```

## Run something in the container

```{#in_container .bash .runnable docker=<<docker_container_name()>> dir="<<project_name()>>"}
pwd
ls -al <<project_name()>>
```

## Run something outside a container

```{#out_container .bash .runnable dir="<<project_name()>>"}
pwd
ls -al <<project_name()>>
```

## Build

To build this project

```{#build_project .bash .runnable docker=<<docker_container_name()>> dir="<<project_name()>>"}
gcc main.c
```

## Run

Run this project

```{#run_project .bash .runnable docker=<<docker_container_name()>> dir="<<project_name()>>"}
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
printf("<<testing_nesting_inner()>>\n");
printf("<<testing_nesting_inner()>>\n");
printf("<<testing_nesting_inner()>>\n");
```

```{#testing_nesting_inner .C}
testing_me
```

## Test Main

```{#test_main .C tangle="<<project_name()>>/main.c"}
#include <stdio.h>

void main()
{
    printf("Hello Electric Markdown World\n");
    <<test_nesting()>>
}
```
