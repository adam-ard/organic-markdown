import json
import sys
import re
import os
import subprocess
from textwrap import indent

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

    arg_lst = arg_str.split(",")
    arg_lst_lst = [x.split("=") for x in arg_lst]

    args = {}
    for a in arg_lst_lst:
        args[a[0].strip()] = a[1].strip().strip('"')

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

        if self.lang == "bash":
            cmd = self.code_blocks.expand(self.code, args)
            if self.docker_container is not None:
                docker_container = self.code_blocks.expand(self.docker_container, args)
            cwd = self.code_blocks.expand(self.cwd, args)
            cmd_in_dir = f"cd {cwd}\n{cmd}"
            if self.docker_container is None:
                return cmd_in_dir
            else:
                return f'docker exec {docker_container} /bin/bash -c "{cmd_in_dir}"'
        else:
            print(f"language {self.lang} is not supported for execution")

    def info(self):
        print(self.__repr__())

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

    # this function returns a bash command to be executed by calling bash script
    #   it allows for interactive things like "docker exec -it" to work
    def irun(self):
        cmd = self.get_run_cmd()
        if cmd is None:
            print("echo Error running command")

        print(cmd)

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
    def __init__(self):
        self.code_blocks = []

    def __repr__(self):
        out = "\nDebug Info:\n"
        for block in self.code_blocks:
            out += indent(block.__repr__(), '    ')
            out += "\n"
        return out

    def parse(self, data):
        for block in data['blocks']:
            if block['t'] == "CodeBlock":
                cb = CodeBlock()
                cb.parse(block['c'])
                cb.code_blocks = self
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

    def expand(self, txt, args={}):
        match, exec = get_match(txt)
        if match is None:    # base case, exit point for the recursion
            return txt.replace("<<X", "<<").replace("X>>",">>")

        name = match.group(1)
        new_args = arg_parse(match.group(2))
        if args is not None and name in args:
            return self.expand(insert_blk(txt, args[name], match.start(), match.end()),
                               args | new_args)

        blk = self.get_code_block(name)
        if blk is None:
            non_match_name = match.group(0).replace("<<", "<<X").replace(">>","X>>")   # make it no longer match (to avoid infinite loop)
            return self.expand(insert_blk(txt, non_match_name, match.start(), match.end()),
                               args | new_args)

        if exec:
            return self.expand(insert_blk(txt, blk.run_return_results(args | new_args), match.start(), match.end()),
                               args | new_args)
        else:
            return self.expand(insert_blk(txt, blk.code, match.start(), match.end()),
                               args | new_args)

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

    json_str=""
    for line in sys.stdin:
        json_str+=line

    data = json.loads(json_str)

    code_blocks = CodeBlocks()
    code_blocks.parse(data)

    # eventually we can probably make this call be default, and remove non-interactive run
    #   for now it is nice to have both for debugging
    if len(sys.argv) == 4 and sys.argv[1] == "-i" and sys.argv[2] == "run":
        code_blocks.run_block_fn(sys.argv[3], CodeBlock.irun)

    elif len(sys.argv) == 3:
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
