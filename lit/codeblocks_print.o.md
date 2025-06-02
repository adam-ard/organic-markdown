# Printing Summary & IDE Integration

The following functions provide output for `omd status` and related tooling. They summarize runnable commands and tangled output files in a clean, human-readable way—or in machine-readable JSON, perfect for editor integration.

---

### `print_summary()`

The main entry point for status output—this method prints available commands and output files:

```python {name=codeblocks__print_summary}
def print_summary(self):
    self.print_cmds()
    print("")
    self.print_files()
```

---

### `print_cmds()`

Prints a list of all code blocks marked with `menu=true`, grouped by the file they came from. This is the output shown under “Available commands” in `omd status`.

```python {name=codeblocks__print_cmds}
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
```

---

### `print_files()`

Prints a list of all code blocks that produce a file via the `tangle` attribute. This section appears under “Output files” in `omd status`.

* If the block has no name, it shows the relative file path.
* If it does have a name, it shows the name instead.

```python {name=codeblocks__print_files}
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
```

---

### `print_parseable_cmds()`

Prints a compact JSON structure of commands grouped by origin file. This is useful for integrating with tools like:

* IDE menus
* LSPs
* External runners / dashboards

```json
[
  {
    "file": "src/foo.o.md",
    "cmds": ["build", "test"]
  },
  ...
]
```

```python {name=codeblocks__print_parseable_cmds}
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
```

### print commands

```python {name=codeblocks__print}
@<codeblocks__print_summary@>
@<codeblocks__print_files@>
@<codeblocks__print_parseable_cmds@>
@<codeblocks__print_cmds@>
```
