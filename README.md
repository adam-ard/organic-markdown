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
This is a organic markdown test file. To create a notebook style command,
create a code bock with some simple bash code in it:

```bash {name=pwd runnable=true}
pwd
```
`````


In your `LIT.md` file, you have created an executable code block. A
organic markdown code block has a language attribute followed by curly
bracket delimited attributes. Notice that we have given the block a name, and set
its runnable attribute to true.

Now when you run `omd` in the same directory as your `LIT.md` file:

```bash
omd
```

You should see something like this:

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

and run `omd run pwd` again. You should now get /var/log as output,
since the bash command was executed in that directory. Also of note is
that you can run with the number of your command, if you don't
want to type the whole name:

```bash
omd run 0
```
