# `CodeBlocks::handle_cmd`

The `handle_cmd()` method is the central dispatcher for command-line interactions with `omd`. It is used in both **interactive mode** and **scripted mode** (e.g., via `omd run <name>`).

It parses and routes input words (typically from `sys.argv`) to the appropriate method based on how many arguments are provided.

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

These commands are run with just a single word like `status` or `tangle`.

### 🔗 `@<handle_one_word_commands@>`

```python {name=handle_one_word_commands}
if words[0] == "version":
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
elif words[0] == "expand":
    print(self.expand(rest))
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

### 🧪 Related Tests

Run the test suite:

```bash
omd run handle_cmd_tests
```

[Test definition →](handle_cmd_tests.o.md)

---

### 🧵 Internal Refs

* [`run_block_fn`](f_run_block_fn.o.md) — Utility to dispatch methods on specific blocks
* [`import_file`](experimental_features.o.md)
* [`weave_file`](experimental_features.o.md)
