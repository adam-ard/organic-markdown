---
constants:
  open_sym: \@<
  close_sym: \@>
---

# Organic Markdown Source

In the spirit of eating your own dog food, below is the `omd.py`
source code in literate form. How is this done? You ask. How can you
write a literate programming tool in the literate style of the tool
itself? Isn't there a chicken and egg problem here? Let me explain.

I first wrote `omd.py`, all in one big file, not in any literate
style. After playing with it and tweaking it, it finally became stable
enough that I decided to try to do a more disciplined job of
documenting and testing it. What better way to do that then with
literate programming?! So I have been using that little, brute-force,
bootstrapping python script to re-impliment OMD in an OMD
style. Eventually, when the source I emit from these literate files is
as stable as the first bootstrap script, I'll remove the bootstrap
script (`omd.py`) from the repo. Then OMD will be implimented in OMD.

As I go through this process, all I really need to do at first is diff
the output of these OMD files with the `omd.py` bootstrapping
script. If they are the same, then I am golden. This will get me
pretty far. Eventually though, I will want to start emitting python
that isn't identical to the bootstrapping script. By that time, I hope to
have enough good documentation and testing in place, that I can
confirm its validity that way. Fingers-crossed.

# The Code

This is the code file. Yes, it is all in one file. But that is OK!
Because we are using literate programming, the code that gets created
is more like compiled code. You are going to look at it (or even check
it into git). It is a different way of thinking for sure, but it's
really nice once you get the hang of it.

```python {tangle=next_omd.py}
#!/usr/bin/env python3

@<imports@>
@<globals@>
@<funcs@>
@<classes@>

@<main@>
```

# Imports

All the modules that must be imported are include here:

```python {name=imports}
import glob
import json
import sys
import os
import re
import subprocess
from textwrap import indent
from pathlib import Path
import pypandoc
```

# Globals

All the global data definitions:

```python {name=globals}
languages = ["bash", "python", "ruby", "haskell", "racket", "perl", "javascript"]
o_sym = "@<open_sym@>"
c_sym = "@<close_sym@>"
```

# Functions

All the function definitions:

```python {name=funcs}
# do this so that the timestamp doesn't change on all files, even when they don't change
#   make assumes that it needs to rebuild when that happens
def write_if_different(file_path, new_content):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            current_content = file.read()

        if current_content.rstrip('\n') == new_content:
            return

    with open(file_path, 'w') as file:
        file.write(new_content)
        file.write("\n")  # put a newline at the end of the file
        file.close()

def split_lines_line_cont_char(txt):
    new_lines = [""]
    lines = txt.split('\n')

    j = 0
    for i, line in enumerate(lines):
        if len(line) > 0 and line[-1:] == "\\":
            new_lines[j] += line[:-1]
        else:
            new_lines[j] += line
            if i < len(lines) - 1:  # don't add if it is the last one
                new_lines.append("")
                j+=1

    return new_lines

def split_lines(txt):
    new_lines = []

    ref_num = 0
    length = len(txt)
    i = 0
    start = 0
    while i < length:
        if txt[i] == "\n" and ref_num == 0:   # need a newline
            new_lines.append(txt[start:i])
            start=i+1
        if txt[i : i + 2] == o_sym:
            ref_num += 1
            i += len(o_sym) - 1
        if txt[i : i + 2] == c_sym:
            ref_num -= 1
            i += len(c_sym) - 1
        i += 1

    new_lines.append(txt[start:i])
    return new_lines

# returns match (or None if there isn't one) and whether or not it is
#  string replacement or results of a string execution replacement. It
#  will return matches in a left to right order
def get_match(txt):
    cur = 0
    while cur < len(txt):
        res, cur = get_match_inner(txt, cur)
        if res is not None:
            return res
    return None

def get_match_inner(txt, cur):
    open_count = 0
    start = -1

    while cur < len(txt):
        if cur + len(o_sym) <= len(txt) and txt[cur : cur + len(o_sym)] == o_sym:
            if start == -1:
                start = cur
            open_count += 1
            cur += len(o_sym) - 1

        elif cur + len(c_sym) <= len(txt) and txt[cur:cur+len(c_sym)] == c_sym:
            if start != -1:
                open_count -= 1
            cur += len(c_sym) - 1

        if open_count < 1 and start != -1:
            match = parse_match(txt[start + len(o_sym) : cur - 1])
            if match is None:
                print(f"content internal to {o_sym} and {c_sym} is invalid: {txt[start:cur + len(c_sym) - 1]}")
                return None, start + len(o_sym)
            return match | {"full": txt[start:cur + len(c_sym) - 1],
                            "start": start,
                            "end": cur + len(c_sym) - 1}, start + len(o_sym)
        cur += 1

    if start == -1:
        return None, len(txt)

    return None, start + len(o_sym)

def parse_name(txt):
    o_txt = txt
    name = ""
    while len(txt) > 0:
        if len(txt) > 1 and txt[0] == "\\" and txt[1] in ['(', '{']:
            name += txt[:2]
            txt = txt[2:]
            continue

        if txt[0] in ['(', '{']:
            break

        name += txt[0]
        txt = txt[1:]
    return name, txt

def parse_exec(txt):
    if len(txt) == 0:
        print(f'name has zero length')
        return "", False, False

    if txt[-1:] == "*":
        if len(txt) == 1:
            print(f'name has zero length')
            return "", False, False

        return txt[:-1], True, True

    return txt, False, True

def parse_args_str(txt):
    args = ""
    if len(txt) == 0:
        return args, txt

    if txt[0] == '{':
        return args, txt

    if txt[0] != '(':
        print(f'Bad char: {txt[0]} while parsing args from: "{txt}"')
        return None, txt

    txt = txt[1:]    # eat the opening paren
    open_count = 1
    while len(txt) > 0:
        if txt[0] == '(':
            open_count += 1
        elif txt[0] == ')':
            open_count -= 1

        if open_count < 1:
            return args, txt[1:]

        args += txt[0]
        txt = txt[1:]

    return None, False

def parse_default(txt):
    if len(txt) == 0:
        return "", txt

    if txt[0] != "{":
        print(f'Bad char: {txt[0]} while parsing default from: "{txt}"')
        return None, txt

    open_count = 1
    default = ""
    o_txt = txt
    txt = txt[1:]
    while len(txt) > 0:
        if txt[0] == '{':
            open_count += 1
        elif txt[0] == '}':
            open_count -= 1

        if open_count < 1:
            return default, txt[1:]

        default += txt[0]
        txt = txt[1:]

    print(f'End of string before getting a "}}" char: "{o_txt}"')
    return None, txt

def parse_match(txt):
    o_txt = txt
    name, txt = parse_name(txt)
    if name is None:
        print(f'Error parsing name from: "{o_txt}"')
        return None

    name, exec, success = parse_exec(name)
    if success == False:
        print(f'Error parsing exec from: "{name}"')
        return None

    args, txt = parse_args_str(txt)
    if args == None:
        print(f'Error parsing args from: "{o_txt}"')
        return None

    default, txt = parse_default(txt)
    if default == None:
        print(f'Error parsing default from: "{o_txt}"')
        return None

    return {"name": name,
            "exec": exec,
            "args": args,
            "default": default.strip('"')}

def eat_ws(txt):
    return txt.lstrip()

def eat_eq(txt):
    if len(txt) == 0:
        return None

    if txt[0] == "=":
        return txt[1:]
    return None

def parse_arg_name(txt):
    if txt == "" or txt[0].isspace():
        return None, txt

    name = ""
    while len(txt) > 0:
        if txt[0].isspace() or txt[0] == "=":
            return name, txt

        name += txt[0]
        txt = txt[1:]

    return name, txt

def parse_arg_value(txt):
    if txt == "" or txt[0].isspace():
        return None, txt

    value = ""
    quoted = False
    in_ref = 0

    if txt[0] == '"':
        quoted = True
        txt = txt[1:]

    while len(txt) > 0:
        if len(txt) > 1 and txt[0] == "\\" and txt[1] in [o_sym[0], c_sym[0], '"']:
            value += txt[1:2]
            txt = txt[2:]

        if len(txt) >= len(o_sym) and txt[:len(o_sym)] == o_sym:
            in_ref += 1
            value += o_sym
            txt = txt[len(o_sym):]
            continue

        if len(txt) >= len(c_sym) and txt[:len(c_sym)] == c_sym:
            in_ref -= 1
            value += c_sym
            txt = txt[len(c_sym):]
            continue

        if not quoted and in_ref < 1 and txt[0].isspace():
            return value, txt

        if quoted and in_ref < 1 and txt[0] == '"':
            return value, txt[1:]

        value += txt[0]
        txt = txt[1:]

    return value, txt

def parse_arg_name_value(txt):
    txt = eat_ws(txt)
    if txt == "":
        return "", "", ""

    name, txt = parse_arg_name(txt)
    if name == None:
        return None, None, ""

    txt = eat_ws(txt)
    txt = eat_eq(txt)
    if txt == None:
        return None, None, ""

    txt = eat_ws(txt)
    value, txt = parse_arg_value(txt)
    if value == None:
        return None, None, ""

    return name, value, txt

# TODO return None for errors
def parse_args(txt):
    args = {}
    while len(txt) > 0:
        name, value, txt = parse_arg_name_value(txt)
        if name == None:
            return {}   # TODO switch this to error
        if name == "":
            return args
        args[name] = value
    return args

def parse_menu_attrib(val):
    if isinstance(val, bool):
        return val

    if isinstance(val, str):
        return val.lower() != "false" and val != "0" and val != ""

    return str(val).lower() != "false" and str(val) != "0" and val is not None
```

# Classes

Below are the classes `CodeBlock` and `CodeBlocks`:

```python {name=CodeBlock_funcs}
def __init__(self):
    self.origin_file=None
    self.name=None
    self.code=None
    self.lang=None
    self.cwd="."
    self.tangle_file=None
    self.in_menu = False
    self.code_blocks = None
    self.docker_container=None
    self.ssh_host=None

def origin(self):
    print(self.origin_file)

def get_run_cmd(self, args={}):
    code = self.code_blocks.expand(self.code, args)
    if self.lang == "bash":
        cmd = code
    elif self.lang == "python":
        cmd = f"python3 -c '{code}'"
    elif self.lang == "ruby":
        cmd = f"ruby -e '{code}'"
    elif self.lang == "haskell":
        cmd = f"ghci -e '{code}'"
    elif self.lang == "racket":
        cmd = f"racket -e '{code}'"
    elif self.lang == "perl":
        cmd = f"perl -E '{code}'"
    elif self.lang == "javascript":
        cmd = f"node -e '{code}'"
    else:
        print(f"language {self.lang} is not supported for execution")
        return

    if self.docker_container is not None:
        docker_container = self.code_blocks.expand(self.docker_container, args)
    if self.ssh_host is not None:
        ssh_host = self.code_blocks.expand(self.ssh_host, args)
    cwd = self.code_blocks.expand(self.cwd, args)
    cmd_in_dir = f"cd {cwd}\n{cmd}"
    if self.docker_container is not None:
        return f'docker exec {self.docker_container} \'/bin/bash -c "{cmd_in_dir}"\''
    elif self.ssh_host is not None:
        return f'ssh {ssh_host} \'/bin/bash -c "{cmd_in_dir}"\''
    else:
        return cmd_in_dir

def info(self):
    print(self)
    return None

def run(self):
    cmd = self.get_run_cmd()
    if cmd is None:
        print("Error running command")
        return

    return subprocess.call(cmd, shell=True)

def run_return_results(self, args={}):
    cmd = self.get_run_cmd(args)
    if cmd is None:
        print("Error running command")
        return

    output = subprocess.run(cmd, capture_output=True, shell=True)
    out_decode = output.stdout.decode("utf-8")

    # remove at most one newline, it one exists at the end of the output
    if len(out_decode) > 0 and out_decode[-1] == "\n":
        out_decode = out_decode[:-1]

    return out_decode


def tangle(self):
    if self.tangle_file is not None:
        tangle_file = self.code_blocks.expand(self.tangle_file)
        code = self.code_blocks.expand(self.code)

        write_if_different(tangle_file, code)
    return None

def parse(self, the_json):
    self.code = the_json[1]
    if self.code is not None and len(self.code) > 0:
        self.code = self.code.replace(o_sym + "br" + c_sym, "\n")

    for attrib in the_json[0][1]:
        if attrib in languages:
            self.lang = attrib

    for attrib in the_json[0][2]:
        if attrib[0] == "menu":
            self.in_menu = parse_menu_attrib(attrib[1])
        elif attrib[0] == "lang":
            self.lang = attrib[1]
        elif attrib[0] == "name":
            self.name = attrib[1]
        elif attrib[0] == "dir":
            self.cwd = attrib[1]
        elif attrib[0] == "tangle":
            self.tangle_file = attrib[1]
        elif attrib[0] == "docker":
            self.docker_container = attrib[1]
        elif attrib[0] == "ssh":
            self.ssh_host = attrib[1]
        else:
            print(f"Warning: I don't know what attribute this is {attrib[0]}")

def __repr__(self):
    out = "CodeBlock("
    if self.name is not None:
        out += f"name={self.name}, "
    if self.origin_file is not None:
        out += f"origin={self.origin_file}, "
    if self.docker_container is not None:
        out += f"docker={self.code_blocks.expand(self.docker_container)}, "
    if self.ssh_host is not None:
        out += f"ssh={self.code_blocks.expand(self.ssh_host)}, "
    if self.lang is not None:
        out += f"lang={self.lang}, "
    out += f"dir={self.code_blocks.expand(self.cwd)}, "
    if self.in_menu:
        out += f"menu={self.in_menu}, "
    out += ")\n"
    out += f"{{\n{indent(self.code_blocks.expand(self.code), '    ')}\n}}"
    return out
```

```python {name=CodeBlocks_funcs}
def __init__(self):
    self.code_blocks = []

def parse(self):
    # read all file in the curren directory (recursively) with .o.md extenstion
    for root, dirs, files in os.walk("."):
        for cur_file in files:
            cur_full_file = f"{root}/{cur_file}"
            if cur_full_file.endswith(".o.md"):
                self.parse_file(cur_full_file)

def parse_file(self, filename):
    data = json.loads(pypandoc.convert_file(filename, 'json', format="md"))
    self.parse_json(data, filename)

def add_code_block(self, code_block):
    if code_block.name is not None:
        blk = self.get_code_block(code_block.name)
        if blk is not None:
            code_block.code = blk.code + "\n" + code_block.code
            self.code_blocks.remove(blk)

    self.code_blocks.append(code_block)

def parse_json(self, data, origin_file):
    for section, constants in data['meta'].items():
        if section == "constants":
            for key, val in constants['c'].items():
                str = ""
                for i in val['c']:
                    if i['t'] == "Str":
                        str += i['c']
                    if i['t'] == "Space":
                        str += " "

                cb = CodeBlock()
                cb.origin_file = origin_file
                cb.name = key
                cb.code = str
                cb.code_blocks = self

                # append the code block contents if the name is the same
                # Note: the yaml parser only uses the last value for any given name, so you utilize more than
                # one entry with the same name.
                self.add_code_block(cb)

    for block in data['blocks']:
        if block['t'] == "CodeBlock":
            cb = CodeBlock()
            cb.origin_file = origin_file
            cb.parse(block['c'])
            cb.code_blocks = self

            # append the code block contents if the name is the same
            self.add_code_block(cb)

def print_summary(self):
    self.print_cmds()
    print("")
    self.print_files()

def print_files(self):
    print("Output files:")
    print(f'  (use "omd tangle" to generate output files)')
    for num, block in enumerate(self.code_blocks):
        if block.tangle_file is not None:
            if block.name is None or block.name == "":
                expanded_filename = self.expand(block.tangle_file)
                rel_path = os.path.relpath(expanded_filename)
                print(f"        {rel_path}")
            else:
                print(f"        {block.name}")

def print_parseable_cmds(self):
    origin_file_dict = {}
    for num, block in enumerate(self.code_blocks):
        if block.origin_file not in origin_file_dict:
            origin_file_dict[block.origin_file] = []
        if block.in_menu:
            origin_file_dict[block.origin_file].append(block.name)

    print("[")
    first = True  # Track if this is the first JSON object
    for key, cmd_list in origin_file_dict.items():
        if not cmd_list:
            continue
        if not first:  # Print a comma before the next JSON object
            print(",")
        first = False  # Subsequent iterations are no longer the first
        print(f'  {{"file": "{key}", "cmds": [', end="")

        first_2 = True
        for name in cmd_list:
            if not first_2:  # Print a comma before the next JSON object
                print(",", end="")
            first_2 = False
            print(f'"{name}"', end="")
        print(']}', end="")
    print("\n]")

def print_cmds(self):
    print("Available commands:")
    print(f'  (use "omd run <cmd>" to execute the command)')
    origin_file_dict = {}
    for num, block in enumerate(self.code_blocks):
        if block.origin_file not in origin_file_dict:
            origin_file_dict[block.origin_file] = []
        if block.in_menu:
            origin_file_dict[block.origin_file].append(block.name)

    for (key, cmd_list) in origin_file_dict.items():
        if cmd_list == []:
            continue
        print(f"        {key}:")
        for name in cmd_list:
            print(f"            {name}")

def get_code_block(self, name):
    for block in self.code_blocks:
        if block.name == name:
            return block
    return None

def get_code_block_by_code(self, code):
    for block in self.code_blocks:
        if block.code == code:
            return block
    return None

def get_max_lines(self, sections):
    max = 0
    for s in sections:
        num_lines = s.split("\n")
        if len(num_lines) > max:
            max = len(num_lines)
    return max

def intersperse(self, sections):
    out = []
    max_lines = self.get_max_lines(sections)
    for i in range(max_lines):
        line = ""
        for s in sections:
            lines = s.split('\n')
            if i < len(lines):
                line += lines[i]
            else:
                line += lines[-1]   # just repeat the last entry until we need something more
        out.append(line)
    return "\n".join(out)

def expand(self, txt, args={}):
    return "\n".join(
        [self.expand_line(x, args) for x in split_lines(txt)]
    )

def expand_line(self, txt, args={}):
    out = []
    while True:
        match = get_match(txt)
        if match is None:
            out.append(txt)
            break

        out.append(txt[:match["start"]])

        name = match["name"]
        new_args = parse_args(match["args"])
        blk = self.get_code_block(name)

        # if there is an argument passed in with that name, replace with that.
        if args is not None and name in args:
            out.append(self.expand(args[name], args | new_args))
        elif blk is None:
            out.append(self.expand(match["default"], args | new_args))   # if block doesn't exist, use default
        # replace ref with the result of running the command
        elif match["exec"]:
            out.append(self.expand(blk.run_return_results(args | new_args), args | new_args))
        else:
            out.append(self.expand(blk.code, args | new_args))
        txt = txt[match["end"]:]

    return self.intersperse(out)

def import_file(self, lang, file_path):
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

def run_block_fn(self, identifier, fn):
    block = None
    if identifier.isdigit():
        block = self.code_blocks[int(identifier)]
    else:
        block = self.get_code_block(identifier)

    if block is None:
        print("Error")
        return

    return fn(block)

def run_all_blocks_fn(self, fn):
    for block in self.code_blocks:
        fn(block)

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

# Main

Any good program starts with main. This one is no exception. Python
sets a global variable called `__name__` to the value `__main__` if
you happen to be calling it as a program. This helps you distiguish
from when the file is being used as a library that has been import (in
which case you would not want to run any "main" code, because you have
a main already in the program the is importing you as a
library).

```python {name=main}
if __name__ == '__main__':
    @<main_code@>
```

# Main Code

The `main_code` section is where our program gets going. Two modes are
available: interactive and command. In interactive mode all the
literate code is parsed and then you get dropped into a repl, where
you can ask questions. Command mode parses the code, runs a single
command, and then exits. Usually command mode is sufficient, because
the parsing is fast, but if you had a lot of code, it might be nice to
parse it once and run several commands in a row without having to pay the
price of parsing over and over.

The way the code determines which mode to invoke is by the number of
command-line arguments. If there are zero args, then OMD invokes
interactive mode. Otherwise, it executes a single command in command mode.

```python {name=main_code}
@<parse@>

if len(sys.argv) > 1:
    @<cmd_exit@>

else:
    @<interactive_mode@>
```

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
1.

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
    self.import_file(words[1], words[2])
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

```python {name=classes}
class CodeBlocks:
    @<CodeBlocks_funcs@>
```

For reference, in a literate source file (has extenstion `.o.md`) code
blocks looks like this. They follow the format used by pandoc: https://pandoc.org/MANUAL.html

``````
```<lang> {name=<name> ...}
source code
```
``````

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
