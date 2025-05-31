# Classes

Below are the methods for the `CodeBlocks` class

```python {name=CodeBlocks_funcs}
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

    return intersperse(out)

```
