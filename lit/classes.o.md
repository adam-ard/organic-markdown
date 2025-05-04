# Classes

Below are the methods for both classes `CodeBlock` and `CodeBlocks`. This file will shrink and eventually disappear as I explain each method individually in the documentation.

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

# TODO: put this in global funcs
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

```

