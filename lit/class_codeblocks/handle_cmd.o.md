# `CodeBlocks::handle_cmd`

The `handle_cmd()` method is the central dispatcher for command-line interactions with `omd`. It is used in both **interactive mode** and **scripted mode** (for example, `omd run <name>` or `omd --help`).

It parses and routes input words (typically from `sys.argv`) to the appropriate method based on how many arguments are provided. The one-word command table now includes help aliases so the CLI can advertise its own built-in commands before showing the project-specific command inventory.

---

### 🔗 `@<codeblocks__handle_cmd@>`

```python {name=codeblocks__handle_cmd}
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

---

## 🧩 One-Word Commands

These commands are run with just a single word like `status`, `tangle`, or `--help`.

### 🔗 `@<handle_one_word_commands@>`

```python {name=handle_one_word_commands}
if words[0] in ["--help", "-h", "help"]:
    self.print_help()
elif words[0] == "version":
    print("@<version@>")
elif words[0] == "cmds":
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

#### Command Summary:

* `--help`, `-h`, `help` — Print CLI usage along with discovered project commands and output files
* `cmds` — Print all runnable commands in parseable JSON
* `files` — Print all output files targeted by tangling
* `status` — Print a human-readable summary of both commands and output files
* `tangle` — Tangle all marked blocks in all `.o.md` files
* `info` — Print debug info for all code blocks

---

## 🧩 Two-Word Commands

These commands operate on a single named code block:

### 🔗 `@<handle_two_word_commands@>`

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
elif words[0] == "expand-str":
    print(self.expand(rest))
elif words[0] == "expand":
    print(self.expand(f"{o_sym}{rest}{c_sym}"))
else:
    print(f"unknown command: {' '.join(words)}")
```

#### Command Summary:

* `tangle <name>` — Tangle just the block named `<name>`
* `run <name>` — Run the command defined in block `<name>`
* `info <name>` — Print debug info for block `<name>`
* `origin <name>` — Print the source file that block `<name>` came from
* `expand <name>` — Expand the block and print its fully resolved source

---

## 🧪 Experimental Commands

These multi-word commands are not finalized and are considered experimental:

### 🔗 `@<handle_gt_two_word_commands@>`

```python {name=handle_gt_two_word_commands}
if words[0] == "import":
    import_file(words[1], words[2])
elif words[0] == "weave":
    self.weave_file(words[1], words[2])
else:
    print(f"unknown command: {words[0]}")
```

#### Experimental Features:

* `import <src> <dest>` — [More details here →](experimental_features.o.md)
* `weave <src> <dest>` — [More details here →](experimental_features.o.md)

---

### 🧵 Internal Refs

* [`run_block_fn`](f_run_block_fn.o.md) — Utility to dispatch methods on specific blocks
* [`import_file`](experimental_features.o.md)
* [`weave_file`](experimental_features.o.md)


# Tests

This test suite checks both layers of command handling. The first set of checks covers the small interactive-loop command handler (`exit`, `reload`, and delegation to `CodeBlocks.handle_cmd`). The second set exercises the real `CodeBlocks.handle_cmd()` dispatcher, including the new `--help` aliases.

It uses a lightweight mock `CodeBlocks` object with `reset()`, `parse()`, and `handle_cmd()` methods to keep the tests isolated and fast.

---

### 🔗 `@<handle_cmd_test@>`

```python {name=handle_cmd_test}
code_blocks.reset()
cmd = "@<cmd@>"
for i in [1]:   # put this inside a loop so `break` / `continue` are valid
    @<handle_cmd@>

@<omd_assert@>

omd_assert(@<parsed@>, code_blocks.parsed)
omd_assert(@<words@>, code_blocks.words)
```

---

### 🔧 Test Harness

```python {name=codeblocks__handle_cmd_test}
class CodeBlock:
    def run(self):
        pass

    def tangle(self):
        pass

    def info(self):
        pass

    def origin(self):
        pass

class CodeBlocksDispatcher:
    def __init__(self):
        self.help_calls = 0
        self.summary_calls = 0
        self.run_calls = []

    @<codeblocks__handle_cmd@>

    def print_help(self):
        self.help_calls += 1

    def print_summary(self):
        self.summary_calls += 1

    def print_parseable_cmds(self):
        pass

    def print_files(self):
        pass

    def run_all_blocks_fn(self, fn):
        pass

    def run_block_fn(self, rest, fn):
        self.run_calls.append(rest)

dispatcher = CodeBlocksDispatcher()
dispatcher.handle_cmd(["--help"])
dispatcher.handle_cmd(["-h"])
dispatcher.handle_cmd(["help"])
omd_assert(3, dispatcher.help_calls)

dispatcher.handle_cmd(["status"])
omd_assert(1, dispatcher.summary_calls)

dispatcher.handle_cmd(["run", "build-omd"])
omd_assert("build-omd", dispatcher.run_calls[0])
```

```python {name=handle_cmd_tests menu=true}
@<omd_assert@>

class CodeBlocks:
    def __init__(self):
        self.reset()

    def reset(self):
        self.parsed = False
        self.words = []

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
                  fail_msg="didn't run reload")@>

@<handle_cmd_test(cmd=diff_command
                  parsed=False
                  words="[\"diff_command\"]"
                  fail_msg="didn't run one word command")@>

@<handle_cmd_test(cmd="diff command"
                  parsed=False
                  words="[\"diff\", \"command\"]"
                  fail_msg="didn't run multi-word command")@>

@<codeblocks__handle_cmd_test@>

@<test_passed(name="Handle Cmd")@>
```
