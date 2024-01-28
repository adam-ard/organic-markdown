import json
import sys
import re
import subprocess
from textwrap import indent

languages = ["python", "bash"]

def strip_emd_ref(text):
    return text[2:-4]

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
        print("Cmd blocks:")
        num = 1
        for block in self.code_blocks:
            if block.is_runnable:
                print(f"    {num}. {block.name}")
                num += 1

        print("\nTangle blocks:")
        num = 1
        for block in self.code_blocks:
            if block.tangle_file is not None:
                print(f"    {num}. {block.name}")
                num += 1

        print("")

    def get_code_block(self, name):
        for block in self.code_blocks:
            if block.name == name:
                return block
        return None

    def add_prefix(self, prefix, code):
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if i > 0:      # line one already has the prefix
                lines[i] = prefix + line
        return '\n'.join(lines)

    def expand_match(self, text, regex):
        pattern = re.compile(regex)
        match = re.search(pattern, text)

        if match is None:
            return text, False

        prefix = text[:match.start()]

        block = self.get_code_block(strip_emd_ref(match.group()))

        if block is None:
            return text, True

        return text[:match.start()] + self.add_prefix(prefix, self.expand(block.code)) + text[match.end():], True

    def expand_line(self, line):
        matched = True
        while(matched):
            line, matched = self.expand_match(line, "<<.*?\(\)>>")
        return line

    def expand(self, text):
        if text is None:
            return ""

        return '\n'.join([self.expand_line(x) for x in text.split('\n')])

    def run(self, name):
        block = self.get_code_block(name)
        if block is not None:
            block.run()

    def tangle(self, name):
        block = self.get_code_block(name)
        if block is not None:
            block.tangle()

    def info(self, name):
        block = self.get_code_block(name)
        if block is not None:
            print(block)

    def tangle_all(self):
        for block in self.code_blocks:
            block.tangle()

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

    def run(self):
        if self.lang == "bash" and self.is_runnable:
            cmd = self.code_blocks.expand(self.code)
            docker_container = self.code_blocks.expand(self.docker_container)
            cwd = self.code_blocks.expand(self.cwd)
            if self.docker_container is None:
                subprocess.call(cmd, shell=True, cwd=cwd)
            else:
                cmd = f'docker exec {docker_container} /bin/bash -c "cd {cwd} && {cmd}"'
                subprocess.call(cmd, shell=True)
        else:
            print(f"Unsupported language: {self.lang}")

    def tangle(self):
        if self.tangle_file is not None:
            tangle_file = self.code_blocks.expand(self.tangle_file)
            code = self.code_blocks.expand(self.code)

            f = open(tangle_file, "w")
            f.write(code)
            f.write("\n")  # put a newline at the end of the file
            f.close()

    def parse(self, the_json):
        self.name = the_json[0][0]
        self.code = the_json[1]
        self.docker_container = None

        for lang in languages:
            if lang in the_json[0][1]:
                self.lang = lang

        if "runnable" in the_json[0][1]:
            self.is_runnable = True

        for attrib in the_json[0][2]:
            if attrib[0] == "dir":
                self.cwd = attrib[1]
            elif attrib[0] == "tangle":
                self.tangle_file = attrib[1]
            elif attrib[0] == "docker":
                self.docker_container = attrib[1]

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

if __name__ == '__main__':

    json_str=""
    for line in sys.stdin:
        json_str+=line

    data = json.loads(json_str)

    code_blocks = CodeBlocks()
    code_blocks.parse(data)

    if len(sys.argv) == 3:
        if sys.argv[1] == "tangle":
            code_blocks.tangle(sys.argv[2])
        elif sys.argv[1] == "run":
            code_blocks.run(sys.argv[2])
        elif sys.argv[1] == "info":
            code_blocks.info(sys.argv[2])
    elif len(sys.argv) == 2:
        if sys.argv[1] == "tangle":
            code_blocks.tangle_all()
        elif sys.argv[1] == "info":
            print(code_blocks)
    else:
        code_blocks.print_summary()
