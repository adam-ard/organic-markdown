# Parse Code

To parse literate code files (files that end in `o.md`), we create a
`CodeBlocks` object and call the `parse` function.

OMD parses all `o.md` files in the current directory. It looks for OMD files
recursively in any subfolders as well.

```python {name=parse}
code_blocks = CodeBlocks()
code_blocks.parse()
```

# Command Mode

Command mode is straight forward. We take all arguments to the script
except the first one (which will be the name of the script itself) and
pass them to the `handle_cmd` function on the `code_blocks` object. We
exit the program with the exit code returned from the `handle_cmd`
function.

```python {name=cmd_exit}
sys.exit(code_blocks.handle_cmd(sys.argv[1:]))
```

# Interactive Mode

Interactive mode is an infinite loop. After printing a command prompt
it reads input from the user. After splitting the input into a list
based on characters separated by whitespace, it check the first word
for a couple simple matches. If the word is `exit`, we break out of
the loop and exit the program. If the word is `reload`, we parse the
literate files again and continue. Otherwise, we pass the command to
`handle_cmd` function to execute a single command. After which we loop
back and print another command prompt, and wait for the next command.

```python {name=interactive_mode}
while True:
    cmd = input("> ") # print prompt
    @<handle_cmd@>
```

```python {name=handle_cmd}
words = cmd.split(" ")

if words[0] == "exit":
    break

if words[0] == "reload":
    code_blocks = CodeBlocks()
    code_blocks.parse()
    print("code reloaded")
    continue

code_blocks.handle_cmd(words)
```

# CodeBlocks::handle_cmd function

The `handle_cmd` methods is used in both interactive mode and command
mode. It is a member of the `CodeBlocks` class explained below. It
dispatches different commands to different methods on the class:

```python {name=CodeBlocks_funcs}
def handle_cmd(self, words):
    if len(words) == 1:
        @<handle_one_word_commands@>

    elif len(words) == 2:
        @<handle_two_word_commands@>

    elif len(words) > 2:
        @<handle_gt_two_word_commands@>

    else:
        print("missing cmd")
```

The following one word commands are dispatched to cooresponding
methods in the source block below.

1. cmds - print all available cmds found in literate source files
1. files - print filenames of files that `omd tangle` will output
1. status - print a more human readable listing of cmds and files from `omd cmds` and `omd files`
1. tangle - emit all files marked for tangling in literate source files
1. info - print information for all src blocks in literate source files

```python {name=handle_one_word_commands}
if words[0] == "cmds":
    self.print_parseable_cmds()
elif words[0] == "files":
    self.print_files()
elif words[0] == "status":
    self.print_summary()
elif words[0] == "tangle":
    self.run_all_blocks_fn(CodeBlock.tangle)
elif words[0] == "info":
    self.run_all_blocks_fn(CodeBlock.info)
else:
    print(f"unknown command: {words[0]}")
```

The following two word commands are dispatched to cooresponding
methods in the source block below.

1. tangle <name> - tangle only the file describe by the block: <name>
1. run <name> - execute the block: <name>, and print the output to stdout
1. info <name> - print information for a specific source block
1. origin <name> - print the name of the literate source file where the block <name> is defined
1. expand <name> - expand all refs in source block: <name>, and print to stdout

```python {name=handle_two_word_commands}
rest = " ".join(words[1:])

if words[0] == "tangle":
    return self.run_block_fn(rest, CodeBlock.tangle)
elif words[0] == "run":
    return self.run_block_fn(rest, CodeBlock.run)
elif words[0] == "info":
    return self.run_block_fn(rest, CodeBlock.info)
elif words[0] == "origin":
    return self.run_block_fn(rest, CodeBlock.origin)
elif words[0] == "expand":
    print(self.expand(rest))
else:
    print(f"unknown command: {' '.join(words)}")
```

Finally all commands that have greater than two words. I won't explain
these commands in detail since they are experimental.

```python {name=handle_gt_two_word_commands}
if words[0] == "import":
    import_file(words[1], words[2])
elif words[0] == "weave":
    self.weave_file(words[1], words[2])
else:
    print(f"unknown command: {words[0]}")
```

# Code Blocks

There are two classes in `omd.py`. `CodeBlock` and `CodeBlocks`. As
you might guess, a `CodeBlocks` object represents a list of objects of
type `CodeBlock`. `CodeBlock` objects represent parsed information
from code blocks in the parsed literate files. Below you can see the
basic structure of each class. We will describe specific functions are
we progress in the documentation.

```python {name=classes}
class CodeBlock:
    @<CodeBlock_funcs@>
```

For reference, in a literate source file (has extenstion `.o.md`) code
blocks looks like this. They follow the format used by pandoc: https://pandoc.org/MANUAL.html

``````
```<lang> {name=<name> ...}
source code
```
``````

Below you can see that a `CodeBlocks` class holds a list of `CodeBlock` objects:

```python {name=classes}
class CodeBlocks:
    def __init__(self):
        self.code_blocks = []
    @<CodeBlocks_funcs@>
```

# Experimental Features

Below are some experimental features that are in development. They are
not ready to be used. I am using them to help me develop a good work
flow around importing source files into literate source files and
generating polished documentation files with lots of bells and
whistles (internal linking, expansion of refs, etc..)

```python {name=CodeBlocks_funcs}
def weave_file(self, filename, dest):
    with open(filename, 'r') as f:
        content = f.read()

    # Split by triple backticks to find code and non-code sections
    parts = re.split(r'(```.*?```)', content, flags=re.DOTALL)
    weaved_content = []

    for part in parts:
        if part.startswith("```"):
            # Code section - keep as-is
            weaved_content.append(part)
        else:
            # Non-code section
            expanded_part = self.expand(part)
            weaved_content.append(expanded_part)

    # Write the weaved output to a new Markdown file
    weaved_filename = f"{dest}/{filename}"
    with open(weaved_filename, 'w') as f:
        f.write("".join(weaved_content))
    print(f"Weaved file created: {weaved_filename}")
```

```python {name=funcs}
def import_file(lang, file_path):
    print(f"importing {file_path}")

    # Get the absolute path of the file and the current directory
    abs_file_path = os.path.abspath(file_path)
    current_directory = os.path.abspath(os.getcwd())

    # Check if the file path is a descendant of the current directory
    if not abs_file_path.startswith(current_directory):
        raise ValueError("The file path must be a descendant of the current directory.")

    # Ensure the file exists
    if not os.path.isfile(abs_file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Extract the filename and create the new filename with ".o.md" extension
    original_filename = os.path.basename(file_path)
    new_filename = f"{original_filename}.o.md"
    new_file_path = os.path.join(current_directory, new_filename)

    # Read the content of the original file
    with open(abs_file_path, 'r') as original_file:
        content = original_file.read()

    # Modify the content by adding triple backticks and the {name=<path>} tag
    modified_content = f"```{lang} {{tangle={abs_file_path}}}\n{content}```\n"

    # Write the modified content to the new file in the current directory
    with open(new_file_path, 'w') as new_file:
        new_file.write(modified_content)
```

# Tests

## Run all tests

```bash {name=all_tests menu=true}
tests/main_code.py
tests/handle_cmd.py
```

## Command Tests Info
Each test is a single python file. They use the literate references to
import code NOT the import statement. This makes is easy to mock
anything you would like. Below are a couple functions that are helpful
to use in tests. They are also used through literate reference instead
of import. I could do this with an import if I wanted to though.

```python {name=test_failed}
print("@<name@> FAILED: @<msg@>")
exit(1)
```

```python {name=test_passed}
print("PASSED: @<name@>!!")
exit(0)
```

## Main Code
Simple test that check that the right mode is executed at the right
time: command mode when there are more than one argument, and
interactive mode otherwise. Also assures that the program exits with
an error code if it fails.

```python {tangle=tests/main_code.py}
#!/usr/bin/env python3

class sys:
  argv = ["script_name"]

interactive_mode_ran = False;
@<main_code(parse="pass" cmd_exit="pass" interactive_mode="interactive_mode_ran=True")@>

if not interactive_mode_ran:
    @<test_failed(name="Main Code" msg="command mode not invoked")@>

sys.argv.append("extra")
sys.argv.append("args")
@<main_code(parse="pass" cmd_exit="interactive_mode_ran=False" interactive_mode="pass")@>

if interactive_mode_ran:
    @<test_failed(name="Main Code" msg="interactive mode not invoked")@>

@<test_passed(name="Main Code")@>
```

## Handle Cmd

This test checks that we are handling the simple cases correctly in
the interactive command loop.

```python {name=handle_cmd_test}
code_blocks.reset()
cmd="@<cmd@>"
for i in [1]:   # put this inside a for loop so the break and continue commands are valid
    @<handle_cmd@>

if code_blocks.parsed != @<parsed@> or code_blocks.words != @<words@>:
    @<test_failed(name="Handle Cmd" msg="@<fail_msg@>")@>
```

```python {tangle=tests/handle_cmd.py}
#!/usr/bin/env python3

class CodeBlocks:
    def __init__(self):
        self.reset()
    def reset(self):
        self.parsed = False
        self. words = []
    def parse(self):
        self.parsed = True
    def handle_cmd(self, words):
        self.words = words

code_blocks = CodeBlocks()

@<handle_cmd_test(cmd=exit
                  parsed=False
                  words=[]
                  fail_msg="didn't run exit")@>

@<handle_cmd_test(cmd=reload
                  parsed=True
                  words=[]
                  fail_msg="did't run reload")@>

@<handle_cmd_test(cmd=diff_command
                  parsed=False
                  words="[\"diff_command\"]"
                  fail_msg="didn't run one word command")@>

@<handle_cmd_test(cmd="diff command"
                  parsed=False
                  words="[\"diff\", \"command\"]"
                  fail_msg="didn't run multi-word command")@>

@<test_passed(name="Handle Cmd")@>
```
