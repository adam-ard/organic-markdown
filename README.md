# Organic Markdown

The most natural (and delicious!!) way to program. Organic Mardown
takes advantage of the markdown extensions used by
[pandoc](https://pandoc.org/MANUAL.html) -- specifically yaml blocks
at the top of a file, and attributes for fenced code blocks -- to
create literate, notebook style documents.

## Installation

To install organic mardown, make sure you have the following dependencies installed:

- pandoc must be latest (<= 3.1.12)
- python3
- python3-pytest
- python3-pypandoc

Then run the following to get the latest code:

```bash
https://github.com/adam-ard/organic-markdown.git
```

in the `organic-markdown` directory, run:

```bash
ln -s omd.py omd
```

so that you can run organic markdown (`omd`) without the .py
extention. Finally, add the `organic-markdown` directory to your
PATH variable.

## Getting Started

To create an organic literate file, create an empty file with the
mardown extention - `*.md`. By default, `omd` looks for a file call
`LIT.md` in the current directory, so let's start with that. Create an
empty directory `test` with a single file called `LIT.md`. Put the
following content in the file:

LIT.md
`````markdown
# Simple command

This is a organic markdown test file. To create a notebook style command,
create a code bock with some simple bash code in it:

```bash {name=pwd runnable=true}
pwd
```
`````


In your `LIT.md` file, you have created an executable code block. An
organic markdown code block has a language attribute followed by curly
bracket delimited attributes. Notice that we have given the block a name, and set
its runnable attribute to true.

Now when you run `omd` in the same directory as your `LIT.md` file,
you should see something like this:

```
Commands:
    0. pwd

Files:
```

You have one command available (the `pwd` command you just created)
and no files to be tangled (we'll explain this in a second). To run
your new command, run the following command:

```bash
omd run pwd
```

You should see the output of the `pwd` bash command. To run this
command in another directory, simply add the dir attribute:

`````markdown
```bash {name=pwd runnable=true dir=/var/log}
pwd
```
`````

and run `omd run pwd` again. You should now get `/var/log` as output,
since the bash command was now executed in that directory. Also of
note is that you can run with the number of your command, if you don't
want to type the whole name:

```bash
omd run 0
```

## Files

In addition to notebooks style functionality, organic markdown also
provides more traditional literate programming with weaving and
tangling. For example, you can write (tangle) a file by adding a
`tangle` attribute to a code block:

`````markdown
# An example script file

```bash {name=script_file tangle=test.sh}
#!/bin/bash

echo "This is a bash script"
```
`````

To write the file, run:

```bash
omd tangle script_file
```

A new script called `test.sh` should appear in your directory. You
should also see this file list when you run `omd`.

```bash
Commands:
    0. pwd

Files:
    1. script_file
```

You can also write (tangle) your file by number instead of name by
running `omd tangle 1`. It is not required to give a name as well as a
path to files. If you leave off the name, the listing will show the
target path for the file, in which case you must use the number to
tangle the file.

```bash
Commands:
    0. pwd

Files:
    1. test.sh
```

If you run `omd tangle` with no arguments, `omd` will tangle all files
listed in you markdown file. This makes for a handy command to run
automatically in your editor everytime you save your markdown file. To
create an easy command to test your script add:

`````markdown
# To run your script

```bash {name=script runnable=true}
bash test.sh
```
`````

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
start adding literate references (names surround by `<<` and `>>`)
that `omd` can read and automatically assemble for you while
`tangling`, it becomes much easier to present your code in smaller
chunks alongside the documentation.

Here is a more complete example to demonstrate how `omd` refs work.

`````markdown
# Say Hello

Say Hello is a simple c program that says hello. We start with a
simple main:

```C {tangle=main.c}
#include <stdio.h>

void main()
{
    printf("Hello\n");
}
```

# Build/Run Program

```bash {name=build runnable=true}
gcc main.c
```

```bash {name=app runnable=true}
./a.out
```

`````


Now you can run:

```bash
omd tangle && omd run build && omd run app
```

And you should see the word: `Hello` in your terminal. But now we add
some refs, so that what we show first serves more as a scaffolding
that we can use to add functions to.

`````markdown
# Say Hello

Say Hello is a simple c program that says hello. We start with an **outline**
simple main:

```C {tangle=main.c}
#include <<includes>>

void main()
{
    <<main>>
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

```bash {name=build runnable=true}
gcc main.c
```

```bash {name=app runnable=true}
./a.out
```
`````

In this update example, notice the references that we have add:
`<<includes>>` and `<<main>>`. When `omd` tangles `main.c` it will go
and find any code with those names and insert it into those spots. But
it doesn't just do a simple text substitution. It is smarter than
that. It will look at what comes before and after each reference on
the same line, and will add the before and after each line of the code
being referenced. That is how `#include` will get prefix to all code
tagged as `includes`. That is also how code the come from `<<main>>`
will get indented correctly. To confirm this is the case run:

```bash
omd tangle
```

and inspect the contents of `main.c`. Everything should be in the
right place. Now lets add some more code, and confirm that it goes in
the right places as well. Add the follow section right before the
`Build/Run Program` section:

`````markdown
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
`````

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
code was inserted in the right place! Pretty awesome! But I can't take
credit for the idea, this type of literate programming comes from
[Donald Knuth](http://www.literateprogramming.com/knuthweb.pdf). He is
known to say that literate programming is better than sliced bread --
and I have to agree.



## Advanced Topics
### yaml block (includes and constants)
### executing code block and using the output
### passing arguments to omd refs
### default argument to omd refs
