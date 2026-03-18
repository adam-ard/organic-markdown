# Printing Summary, Help, & IDE Integration

The following functions provide output for `omd status`, `omd --help`, and related tooling. They summarize runnable commands and tangled output files in a clean, human-readable way—or in machine-readable JSON, perfect for editor integration.

The help output is intentionally split into two parts: a static description of the built-in `omd` commands, followed by the dynamic command and file inventory for the current directory. That keeps `omd --help` genuinely useful without duplicating the logic that already powers `omd status`.

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

### `print_help()`

This method prints a concise usage guide for the CLI, including the built-in commands that `omd` understands directly. After that it reuses `print_summary()` so the help output also shows the project-specific commands and output files discovered in the current directory.

```python {name=codeblocks__print_help}
def print_help(self):
    print("Usage:")
    print("  omd                 start interactive mode")
    print("  omd --help          show this help message")
    print("  omd <command>       run a single command and exit")
    print("")
    print("Built-in commands:")
    print("  --help, -h, help    show this help message")
    print("  version             print the omd version")
    print("  status              show project commands and output files")
    print("  cmds                print project commands as JSON")
    print("  files               print project output files")
    print("  tangle              tangle all output files")
    print("  tangle <name>       tangle one named block")
    print("  run <name>          run one named command block")
    print("  info                print info for all code blocks")
    print("  info <name>         print info for one named block")
    print("  origin <name>       print the source file for a named block")
    print("  expand <name>       expand a named block")
    print("  expand-str <ref>    expand a raw reference string")
    print("  import <src> <dest> experimental import support")
    print("  weave <src> <dest>  experimental weave support")
    print("")
    print("Interactive mode commands:")
    print("  exit                leave interactive mode")
    print("  reload              re-parse all .o.md files")
    print("")
    self.print_summary()
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
@<codeblocks__print_help@>
@<codeblocks__print_summary@>
@<codeblocks__print_files@>
@<codeblocks__print_parseable_cmds@>
@<codeblocks__print_cmds@>
```

# Tests

The help output combines static built-in command documentation with the dynamic command and file inventory from the current directory. The test below checks a few stable phrases from each half of the output rather than matching the entire string exactly.

```python {name=print_help_tests menu=true}
@<omd_assert@>
import io
import os
from contextlib import redirect_stdout

class CodeBlock:
    def __init__(self, origin_file, in_menu=False, name=None, tangle_file=None):
        self.origin_file = origin_file
        self.in_menu = in_menu
        self.name = name
        self.tangle_file = tangle_file

class CodeBlocks:
    def __init__(self):
        self.code_blocks = [
            CodeBlock("./proj_cmd.o.md", True, "build-omd"),
            CodeBlock("./lit/run_all_tests.o.md", True, "all_tests"),
            CodeBlock("./lit/code.o.md", False, "omd_file", "lit/omd"),
        ]

    def expand(self, txt):
        return txt

    @<codeblocks__print_help@>
    @<codeblocks__print_summary@>
    @<codeblocks__print_files@>
    @<codeblocks__print_cmds@>

code_blocks = CodeBlocks()
buf = io.StringIO()
with redirect_stdout(buf):
    code_blocks.print_help()

output = buf.getvalue()
omd_assert_regex(r"Usage:\n  omd\s+start interactive mode", output)
omd_assert_regex(r"--help, -h, help\s+show this help message", output)
omd_assert_regex(r"run <name>\s+run one named command block", output)
omd_assert_regex(r"Interactive mode commands:\n  exit\s+leave interactive mode", output)
omd_assert_regex(r"Available commands:\n(?:.*\n)*?\s+build-omd", output)
omd_assert_regex(r"Output files:\n(?:.*\n)*?\s+omd_file", output)

@<test_passed(name="Print Help")@>
```
