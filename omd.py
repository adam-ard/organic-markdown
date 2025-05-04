#!/usr/bin/env python3

import glob
import json
import sys
import os
import re
import subprocess
from textwrap import indent
from pathlib import Path
import pypandoc
languages = ["bash", "python", "ruby", "haskell", "racket", "perl", "javascript"]
o_sym = "@<"
c_sym = "@>"
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
class CodeBlock:
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
class CodeBlocks:
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

    def run_all_blocks_fn(self, fn):
        for block in self.code_blocks:
            fn(block)

    def handle_cmd(self, words):
        if len(words) == 1:
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

        elif len(words) == 2:
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

        elif len(words) > 2:
            if words[0] == "import":
                import_file(words[1], words[2])
            elif words[0] == "weave":
                self.weave_file(words[1], words[2])
            else:
                print(f"unknown command: {words[0]}")

        else:
            print("missing cmd")
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
    def run_block_fn(self, identifier, fn):
        block = self.get_code_block(identifier)

        if block is None:
            print("Error: No Matching Code Blocks Found.")
            return -1

        return fn(block)

if __name__ == '__main__':
    code_blocks = CodeBlocks()
    code_blocks.parse()

    if len(sys.argv) > 1:
        sys.exit(code_blocks.handle_cmd(sys.argv[1:]))

    else:
        while True:
            cmd = input("> ") # print prompt
            words = cmd.split(" ")

            if words[0] == "exit":
                break

            if words[0] == "reload":
                code_blocks = CodeBlocks()
                code_blocks.parse()
                print("code reloaded")
                continue

            code_blocks.handle_cmd(words)
