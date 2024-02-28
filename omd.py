import json
import sys
import re
import os
import subprocess
from textwrap import indent
from pathlib import Path
import pypandoc

languages = ["bash", "python"]

# returns match (or None if there isn't one) and whether or not it is
#  string replacement or results of a string execution replacement. There is no
#  guarentee that the match will be first in string
def get_match(txt):
    pattern = re.compile(r'<<([^()]*?)\(([^()]*?)\)>>')
    match = re.search(pattern, txt)

    if match is not None:
        return match, False

    pattern = re.compile(r'<<([^()]*?)\(([^()]*?)\)\(\)>>')
    match = re.search(pattern, txt)

    if match is not None:
        return match, True

    return None, False

def add_pre_post(code, prefix, postfix):
    lines = code.split('\n')
    for i, line in enumerate(lines):
        lines[i] = prefix + line + postfix

    return '\n'.join(lines)

def arg_parse(arg_str):
    if arg_str == '':
        return {}

    arg_lst = arg_str.split("\"")

    args = {}
    i = 0
    while arg_lst[i] != "" and i < len(arg_lst):
        args[arg_lst[i].strip().strip("=").strip()] = arg_lst[i+1]
        i += 2

    return args

def insert_blk(txt, blk_txt, start, end):
    lbreak = txt.rfind("\n", 0, start)
    if lbreak == -1:
        lbreak = -1

    rbreak = txt.find("\n", end)
    if rbreak == -1:
        rbreak = len(txt)

    pre_post = add_pre_post(blk_txt, txt[lbreak + 1 : start], txt[end : rbreak])
    return txt[:lbreak + 1] + pre_post + txt[rbreak:]

def parse_runnable_attrib(val):
    if isinstance(val, bool):
        return val

    if isinstance(val, str):
        return val.lower() != "false" and val != "0" and val != ""

    return str(val).lower() != "false" and str(val) != "0" and val is not None

# make a string no longer match (to avoid infinite loop)
def mark_no_match(txt):
    return txt.replace("<<", "<<X").replace(">>","X>>")

# put it back to how it was
def unmark_no_match(txt):
    return txt.replace("<<X", "<<").replace("X>>",">>")

class CodeBlock:
    def __init__(self):
        self.name=None
        self.code=None
        self.lang=None
        self.cwd="."
        self.tangle_file=None
        self.is_runnable = False
        self.code_blocks = None
        self.docker_container=None

    def get_run_cmd(self, args={}):
        if not self.is_runnable:
            return None

        code = self.code_blocks.expand(self.code, args)
        if self.lang == "bash":
            cmd = code
        elif self.lang == "python":
            cmd = f"python3 -c '{code}'"
        else:
            print(f"language {self.lang} is not supported for execution")
            return

        if self.docker_container is not None:
            docker_container = self.code_blocks.expand(self.docker_container, args)
        cwd = self.code_blocks.expand(self.cwd, args)
        cmd_in_dir = f"cd {cwd}\n{cmd}"
        if self.docker_container is None:
            return cmd_in_dir
        else:
            return f'docker exec {docker_container} /bin/bash -c "{cmd_in_dir}"'

    def info(self):
        print(self)

    def run(self):
        cmd = self.get_run_cmd()
        if cmd is None:
            print("Error running command")

        subprocess.call(cmd, shell=True)

    def run_return_results(self, args={}):
        cmd = self.get_run_cmd(args)
        if cmd is None:
            print("Error running command")

        output = subprocess.run(cmd, capture_output=True, shell=True)
        return output.stdout.decode("utf-8")

    def tangle(self):
        if self.tangle_file is not None:
            tangle_file = self.code_blocks.expand(self.tangle_file)
            code = self.code_blocks.expand(self.code)

            f = open(tangle_file, "w")
            f.write(code)
            f.write("\n")  # put a newline at the end of the file
            f.close()

    def parse(self, the_json):
        self.code = the_json[1]

        for attrib in the_json[0][1]:
            if attrib in languages:
                self.lang = attrib

        for attrib in the_json[0][2]:
            if attrib[0] == "runnable":
                self.is_runnable = parse_runnable_attrib(attrib[1])
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
            else:
                print(f"Warning: I don't know what attribute this is {attrib[0]}")

    def __repr__(self):
        out = "CodeBlock("
        if self.name is not None:
            out += f"name={self.name}, "
        if self.docker_container is not None:
            out += f"docker={self.code_blocks.expand(self.docker_container)}, "
        if self.lang is not None:
            out += f"lang={self.lang}, "
        out += f"dir={self.code_blocks.expand(self.cwd)}, "
        if self.is_runnable:
            out += f"runnable={self.is_runnable}, "
        out += ")\n"
        out += f"{{\n{indent(self.code_blocks.expand(self.code), '    ')}\n}}"
        return out

class CodeBlocks:
    def __init__(self, start_file):
        self.code_blocks = []
        self.md_files = [[start_file, False]]

    def add_md_file(self, filename):
        for f in self.md_files:
            if f[0] == filename:
                return

        self.md_files.append([filename, False])

    def get_next_unread(self):
        for f in self.md_files:
            if f[1] == False:
                f[1] = True
                return f[0]

        return None

    def parse(self):
        curr_file = self.get_next_unread()
        if curr_file is None:    # all done reading
            return

        print(f"Parsing File: {curr_file}")
        self.parse_file(curr_file)
        self.parse()   # start over -- because new files might have gone into the list

    def parse_file(self, filename):
        data = json.loads(pypandoc.convert_file(filename, 'json'))

        for section, constants in data['meta'].items():
            if section == "includes":
                for i in constants['c']:
                    self.add_md_file(i['c'][0]['c'])

            if section == "constants":
                for key, val in constants['c'].items():
                    cb = CodeBlock()
                    cb.name = key
                    cb.code = val['c'][0]['c']
                    cb.code_blocks = self
                    self.code_blocks.append(cb)

        for block in data['blocks']:
            if block['t'] == "CodeBlock":
                cb = CodeBlock()
                cb.parse(block['c'])
                cb.code_blocks = self

                # append the code block contents if the name is the same
                if cb.name is not None:
                    blk = self.get_code_block(cb.name)
                    if blk is not None:
                        cb.code = blk.code + "\n" + cb.code
                        self.code_blocks.remove(blk)

                self.code_blocks.append(cb)

    def print_summary(self):
        print("Commands:")
        for num, block in enumerate(self.code_blocks):
            if block.is_runnable:
                print(f"    {num}. {block.name}")

        print("\nFiles:")
        for num, block in enumerate(self.code_blocks):
            if block.tangle_file is not None:
                if block.name is None or block.name == "":
                    expanded_filename = self.expand(block.tangle_file)
                    rel_path = os.path.relpath(expanded_filename)
                    print(f"    {num}. {rel_path}")
                else:
                    print(f"    {num}. {block.name}")

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

    def replace_match(self, txt, match, args):
        def fn(replace_txt):
            return self.expand(insert_blk(txt,
                                          replace_txt,
                                          match.start(),
                                          match.end()),
                               args)
        return fn

    def expand(self, txt, args={}):
        match, exec = get_match(txt)
        if match is None:    # base case, exit point for the recursion
            return unmark_no_match(txt)

        name = match.group(1)
        new_args = arg_parse(match.group(2))
        replace_fn = self.replace_match(txt, match, args | new_args)

        if args is not None and name in args:
            return replace_fn(args[name])

        blk = self.get_code_block(name)
        if blk is None:
            return replace_fn(mark_no_match(match.group(0)))

        if exec:
            return replace_fn(blk.run_return_results(args | new_args))

        return replace_fn(blk.code)

    def run_block_fn(self, identifier, fn):
        block = None
        if identifier.isdigit():
            block = self.code_blocks[int(identifier)]
        else:
            block = self.get_code_block(identifier)

        if block is None:
            print("Error")
            return

        fn(block)

    def run_all_blocks_fn(self, fn):
        for block in self.code_blocks:
            fn(block)

if __name__ == '__main__':
    code_blocks = CodeBlocks("LIT.md")
    code_blocks.parse()

    if len(sys.argv) == 3:
        if sys.argv[1] == "tangle":
            code_blocks.run_block_fn(sys.argv[2], CodeBlock.tangle)
        elif sys.argv[1] == "run":
            code_blocks.run_block_fn(sys.argv[2], CodeBlock.run)
        elif sys.argv[1] == "info":
            code_blocks.run_block_fn(sys.argv[2], CodeBlock.info)

    elif len(sys.argv) == 2:
        if sys.argv[1] == "tangle":
            code_blocks.run_all_blocks_fn(CodeBlock.tangle)
        elif sys.argv[1] == "info":
            code_blocks.run_all_blocks_fn(CodeBlock.info)
    else:
        code_blocks.print_summary()
