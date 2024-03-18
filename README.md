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

`````markdown
This is a organic markdown test. To create a notebook style command,
create a code bock with some simple bash code in it:

```bash {name="pwd"}
pwd
```
`````





