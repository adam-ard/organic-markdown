# Organic Markdown

The most natural (and delicious!!) way to program. Organic Mardown
takes advantage of the markdown extensions used by
[pandoc](https://pandoc.org/MANUAL.html) -- specifically yaml blocks
at the top of a file, and attributes for fenced code blocks -- to
create next-gen literate, notebook style documents, strongly
influenced by emacs org-mode and functional programming.

## Installation

To install organic mardown, make sure you have the following dependencies:

- pandoc (>= 3.1.12)
- python3
- python3-pytest
- python3-pypandoc
- black (pip install black)

Run the following to get the latest code:

```bash
https://github.com/adam-ard/organic-markdown.git
```

and then add the `organic-markdown` directory to your PATH variable.

## Getting Started

To create an organic literate file, create an empty file with the
mardown extention - `*.o.md`. By default, `omd` reads all files that
have a `.o.md` extension in the current directory (and any
subdirectories recursively). Let's create an empty directory `test`
with a single file called `LIT.o.md` and put the following contents in
it:

LIT.o.md
``````markdown
# Simple command

This is a organic markdown test file. To create a notebook style command,
create a code bock with some simple bash code in it:

```bash {name=pwd menu=true}
pwd
```
``````


In your `LIT.o.md` file, you have created an executable code block. An
organic markdown code block has a language attribute followed by curly
bracket delimited attributes. Notice that we have given the block a name, and set
its menu attribute to true.

Now when you run `omd status` in the same directory as your `LIT.o.md` file,
you should see something like this:

```
Available commands:
  (use "omd run <cmd>" to execute the command)
    pwd

Output files:
  (use "omd tangle" to generate output files)
```

You have one command available (the `pwd` command you just created)
and no files to be tangled (we'll explain this in a second). To run
your new command, run the following command:

```bash
omd run pwd
```

You should see the output of the `pwd` bash command. To run this
command in another directory, simply add the dir attribute:

``````markdown
```bash {name=pwd menu=true dir=/var/log}
pwd
```
``````

and run `omd run pwd` again. You should now get `/var/log` as output,
since the bash command was now executed in that directory. 

## Files

In addition to notebooks style functionality, organic markdown also
provides more traditional literate programming with weaving and
tangling. For example, you can write (tangle) a file by adding a
`tangle` attribute to a code block:

``````markdown
# An example script file

```bash {name=script_file tangle=test.sh}
#!/bin/bash

echo "This is a bash script"
```
``````

To write the file, run:

```bash
omd tangle script_file
```

A new script called `test.sh` should appear in your directory. You
should also see this file listed when you run `omd status`.

```bash
Available commands:
  (use "omd run <cmd>" to execute the command)
    pwd

Output files:
  (use "omd tangle" to generate output files)
    script_file
```

If you run `omd tangle` with no arguments, `omd` will tangle all files
listed in your markdown file. This makes for a handy command to run
automatically in your editor everytime you save a markdown file. To
create a command to test your script add:

``````markdown
# To run your script

```bash {name=script menu=true}
bash test.sh
```
``````

Then you can run:

```bash
omd run script
```


## Literate references

One of the benifits of literate programming is that you can keep your
documentation located right next your code. You are more likely to to
write documentation this way. Additionally, the documentation is more
likely to stay updated and in sync with your actual code. But this
isn't the only reason that literate programming is helpful. Once you
start adding literate references (names surround by `@<` and `@>`)
that `omd` can read and automatically assemble for you while
`tangling`, it becomes much easier to present your code in smaller
chunks alongside the documentation.

Here is a more complete example to demonstrate how `omd` refs work.

``````markdown
# Say Hello

Say Hello is a simple c program that says hello. First we start with a
simple main:

```C {tangle=main.c}
#include <stdio.h>

void main()
{
    printf("Hello\n");
}
```

# Build/Run Program

```bash {name=build menu=true}
gcc main.c
```

```bash {name=app menu=true}
./a.out
```

``````


Now you can run:

```bash
omd tangle && omd run build && omd run app
```

And you should see the word: `Hello` in your terminal. Now we'll add
some refs to make a simple outline or scaffolding for our main file:

``````markdown
# Say Hello

Say Hello is a simple c program that says hello. We start with an **outline**
simple main:

```C {tangle=main.c}
#include @<includes@>

void main()
{
    @<main@>
}
```

# Code for saying hello

In order to print we need to add the `stdio` include:

```C {name="includes"}
<stdio.h>
```

Following is code to say hello:

```C {name="main"}
printf("Hello\n");
```

# Build/Run Program

```bash {name=build menu=true}
gcc main.c
```

```bash {name=app menu=true}
./a.out
```
``````

In this version we have add two references: `@<includes@>` and
`@<main@>`. When `omd` tangles `main.c` it will go and find any code
with those names and insert it into those spots. But it doesn't just
do a simple text substitution. It is smarter than that. It will look
at what comes before and after each reference on the same line, and
will add it before and after each line of the code being
referenced. That is how `#include` will get prefixed to all code
tagged as `includes`. That is also how code coming from `@<main@>`
will get indented correctly. To confirm this is the case run:

```bash
omd tangle
```

and inspect the contents of `main.c`. Everything should be in the
right place. Now lets add some more code, and confirm that it goes in
the right places as well. Add the follow section right before the
`Build/Run Program` section:

``````markdown
# Code for saying hello, a second way

In order to get the time, we need to include:

```C {name="includes"}
<time.h>
```

Following is code to say hello with the date:

```C {name="main"}
time_t t = time(NULL);
struct tm *tm = localtime(&t);

printf("Hello it's %s\n", ctime(&t));
```
``````

now run:

```bash
omd tangle && omd run build && omd run app
```

you should see something like this:

```
Hello
Hello it's Mon Mar 18 19:13:51 2024
```

If you inspect `main.c`, you'll see that the new include and new main
code was inserted in the right place as well. This is because when you
reference something with the same name a second time, the text is
appended to the previous text. Pretty awesome! [Donald
Knuth](http://www.literateprogramming.com/knuthweb.pdf) really knew
what he was doing when he designed literate programming. He is known
to say that literate programming is better than sliced bread -- and I
have to agree.

# Reference Arguments

Expanding on Donald Knuth's idea, and to make it a little easier to
reuse code blocks, in organic markdown you can pass arguments to
literate refs. For example, say you would like to reuse the scaffolding
you built above for any source files with main in it, you can pull this
code block (and some explanation) into it's own file, and call it
`main_template.o.md`:

``````markdown
# A template for main

A reusable template for any file that has a main in it:

```C {name="main_template"}
#include @<includes@>

void main()
{
    @<main@>
}
```
``````

Then you can use the template in another file in the same directory,
like this:

``````markdown
# Say Hello

'Say Hello' is a simple c program that says hello. Here is our simple main:

```C {tangle=main.c}
@<main_template(includes=@<hello_includes@>
                main=@<hello_main@>)@>
```

# Code for saying hello

In order to print we need to add the `stdio` include:

```C {name="hello_includes"}
<stdio.h>
```

Following is code to say hello:

```C {name="hello_main"}
printf("Hello\n");
```
``````

You can easily imagine doing this for a header files, and non-main
source files as well. This makes creating new files -- that all stay
very uniform with each other and that can be modified in one place and
reflected everywhere -- very quick and easy.

# Yaml Header Constants

Another thing you can do is use a yaml header block to define
constants for short snippets that don't have any attributes except a
name. This makes your files more concise. For example, you may want to
reference a project name or version in your source code:

``````markdown
---
constants:
  project_name: Hello-Example-Project
  version: 1.23
---

# Say Hello

Say Hello is a simple c program that says hello. Here is our simple main:

```C {tangle=main.c}
@<main_template(includes=@<hello_includes@>
                main=@<hello_main@>)@>
```

# Code for saying hello

In order to print we need to add the `stdio` include:

```C {name="hello_includes"}
<stdio.h>
```

Following is code to say hello:

```C {name="hello_main"}
printf("@<project_name@>: @<version@>: Hello\n");
```
``````

## Note:

If you use the `@<name@>` notation in the yaml block at the top of the file, you must prefix the first `@<` with a escape `\` char, like this:

```
constants:
  testing: \@<testing@>
```

yaml doesn't like the `@` being the first char in the value field.


# defaults

Each literate ref can also have a default value in case that
particular ref is not define anywhere. Say we never set the version or
project_name. We can specify a default placeholder:

``````markdown
# Say Hello

Say Hello is a simple c program that says hello. Here is our simple main:

```C {tangle=main.c}
@<main_template(includes=@<hello_includes@>
                main=@<hello_main@>)@>
```


# Code for saying hello

In order to print we need to add the `stdio` include:

```C {name="hello_includes"}
<stdio.h>
```

Following is code to say hello:

```C {name="hello_main"}
printf("@<project_name{undefined}@>: @<version{0.0.0}@>: Hello\n");
```
``````

Then when you run, you should get this output:

```bash
undefined: 0.0.0: Hello
```

# executing code block and using the output

The final tweak that organic markdown makes to the literate reference
syntax is to allow you to use the results of executing a code
snippet. This gives you the power of any language (currently only
python and bash are supported but more are comming soon) to automate
your literate programming. Let say you would like to print the
architecture of the machine that you are building your app on. You can
do this:

``````markdown
```bash {name=arch menu=true}
echo -n `uname -m`   # use echo -n to strip off the newline for the substition
```

Following is code to say hello:

```C {name="hello_main"}
printf("Hello from my: @<arch*@>\n");
```
``````

Adding a '*' to any ref name means: substitute the results of running
this code block. When I run this on my machine, I get this output:

```bash
Hello from my: x86_64
```

Note: We use `echo -n` with `uname` so that we can strip off the newline
character, because if we have multi-line input from a literate ref, we
have special string substitution behavior (explained above) that isn't
what we want here.

# more resources / tutorials

- https://rethinkingsoftware.substack.com/p/the-joy-of-literate-programming
- https://rethinkingsoftware.substack.com/p/organic-markdown-intro
- https://rethinkingsoftware.substack.com/p/dry-on-steroids-with-literate-programming
- https://www.youtube.com/@adam-ard/videos
