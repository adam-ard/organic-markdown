# Organic Markdown

The most natural (and delicious!!) way to program. **Organic Markdown** takes advantage of the Markdown extensions used by [Pandoc](https://pandoc.org/MANUAL.html)—specifically YAML blocks at the top of a file and attributes for fenced code blocks—to create next-gen literate, notebook-style documents. It's strongly influenced by Emacs Org-mode and functional programming.

## Installation

To install Organic Markdown, make sure you have the following dependencies:

* Pandoc (>= 3.1.12)
* Python 3
* pypandoc

Then click on `Releases` to the right of this project page. Choose the version you want (I would recommend the latest). You'll see 3 Assets: `omd`, `Source code (zip)`, `Source code (tar.gz)`. Click on `omd` to download the main script. Put it somewhere in your path. I personally put it in my user's `~/bin` directory. Make it executable:

```
chmod u+x ~/bin/omd
```

You're all set!

## Using OMD

To create an Organic Markdown file, make a new file with the extension `*.o.md`. By default, `omd` reads all `.o.md` files in the current directory (and all subdirectories recursively).

Let's create a simple example. Make a new directory called `test`, and inside it, create a file called `LIT.o.md`:

`LIT.o.md`

``````markdown
# Simple command

This is an Organic Markdown test file. To create a notebook-style command, add a code block with some simple Bash code:

```bash {name=pwd menu=true}
pwd
```
``````

You've just defined an executable code block. An Organic Markdown block starts with a language declaration, followed by curly-brace attributes. Here, you've named the block `pwd` and set `menu=true` to make it show up as a runnable command.

Now run this in the same directory:

```bash
omd status
```

You should see something like:

```
Available commands:
  (use "omd run <cmd>" to execute the command)
    pwd

Output files:
  (use "omd tangle" to generate output files)
```

To execute the command:

```bash
omd run pwd
```

You can also specify the working directory for a code block:

``````markdown
```bash {name=pwd menu=true dir=/var/log}
pwd
```
``````

Then run `omd run pwd` again. This time the output should be `/var/log`.

## Files and Tangling

Organic Markdown also supports more traditional literate programming via **tangling**.

To write a file from a code block, use the `tangle` attribute:

``````markdown
# An example script file

```bash {name=script_file tangle=test.sh}
#!/bin/bash

echo "This is a bash script"
```
``````

Generate the file:

```bash
omd tangle script_file
```

You should now see `test.sh` in your directory. It will also show up in the output of:

```bash
omd status
```

You can tangle all outputs at once:

```bash
omd tangle
```

To test the script, add the following to your file:

``````markdown
# To run your script

```bash {name=script menu=true}
bash test.sh
```
``````

Then run:

```bash
omd run script
```

## Literate References

Literate programming lets you co-locate code and documentation. This keeps your docs more accurate and encourages better habits.

But Organic Markdown goes further: by using **literate references** (`@<name@>`) and **tangling**, you can write small code chunks and stitch them together into clean, readable source files.

### Basic Example

``````markdown
# Say Hello

```C {tangle=main.c}
#include <stdio.h>

void main()
{
    printf("Hello\n");
}
```

# Build/Run

```bash {name=build menu=true}
gcc main.c
```

```bash {name=app menu=true}
./a.out
```
``````

Now run:

```bash
omd tangle && omd run build && omd run app
```

You should see:

```
Hello
```

### Using Literate Refs for Structure

``````markdown
# Say Hello (Ref Version)

```C {tangle=main.c}
#include @<includes@>

void main()
{
    @<main@>
}
```

```C {name=includes}
<stdio.h>
```

```C {name=main}
printf("Hello\n");
```
``````

Tangle the file and inspect `main.c`. It will contain a fully assembled version with proper indentation and substitutions.

Add more blocks:

``````markdown
```C {name=includes}
<time.h>
```

```C {name=main}
time_t t = time(NULL);
struct tm *tm = localtime(&t);
printf("Hello it's %s\n", ctime(&t));
```
``````

Now re-run:

```bash
omd tangle && omd run build && omd run app
```

You should see something like:

```
Hello
Hello it's Mon Mar 18 19:13:51 2024
```

Multiple blocks with the same name will have their contents **appended**.

## Reference Arguments

You can also **parameterize** your refs using arguments:

### `main_template.o.md`

``````markdown
```C {name=main_template}
#include @<includes@>

void main()
{
    @<main@>
}
```
``````

Use it in another file:

``````markdown
```C {tangle=main.c}
@<main_template(includes=@<hello_includes@> main=@<hello_main@>)@>
```

```C {name=hello_includes}
<stdio.h>
```

```C {name=hello_main}
printf("Hello\n");
```
``````

## YAML Header Constants

Use the YAML header to define constants:

``````markdown
---
constants:
  project_name: Hello-Example-Project
  version: 1.23
---

```C {name=hello_main}
printf("@<project_name@>: @<version@>: Hello\n");
```
``````

Escape `@<` if used directly in the YAML header:

```yaml
constants:
  example: \@<ref@>
```

## Default Ref Values

Provide fall-back values in refs using `{}` syntax:

```C {name=hello_main}
printf("@<project_name{undefined}@>: @<version{0.0.0}@>: Hello\n");
```

## Executing Code Blocks and Using Output

Refs can also point to the **output** of executable code blocks. Just add a `*`:

``````markdown
```bash {name=arch menu=true}
echo -n `uname -m`
```

```C {name=hello_main}
printf("Hello from my: @<arch*@>\n");
```
``````

This inserts the runtime result of `arch` into the tangled file.

## More Resources

* [The Joy of Literate Programming](https://rethinkingsoftware.substack.com/p/the-joy-of-literate-programming)
* [Organic Markdown Intro](https://rethinkingsoftware.substack.com/p/organic-markdown-intro)
* [DRY on Steroids](https://rethinkingsoftware.substack.com/p/dry-on-steroids-with-literate-programming)
* [YouTube Tutorials](https://www.youtube.com/@adam-ard/videos)

## Development

For development, there is one additional dependency:

* `black` (for code formatting)

Clone the repository:

```bash
git clone https://github.com/adam-ard/organic-markdown.git
```

then modify the files in the `lit` directory and build new versions of `omd`. Lots of fun!!
