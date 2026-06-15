# `CodeBlock::tangle`

This method is called when a `CodeBlock` is **tangled**—meaning its contents are expanded and written out to a file.

When the user runs:

```bash
omd tangle
```

`omd` walks through all `CodeBlock` objects in the `CodeBlocks` container and calls `tangle()` on each one (if applicable).

---

### Behavior

* First, the `self.tangle_file` value is expanded. This allows references and substitutions in the filename itself.
* Then, the `self.code` content is expanded.
* If the expanded filename includes parent directories, they are created before writing. `exist_ok=True` makes this safe for both existing directories and nested directories that do not exist yet.
* Finally, the output is written to the file—but only if the contents have changed, using `write_if_different()`.

This makes it easy to write dynamic or parameterized file names like:

``````markdown
```bash {tangle=@<project_name@>.sh}
<cmds>
```
``````

When tangled, this will generate a file with the value of `project_name` as its name.

---

### 🔗 `@<codeblock__tangle@>`

```python {name=codeblock__tangle}
def tangle(self):
    if self.tangle_file is not None:
        tangle_file = self.code_blocks.expand(self.tangle_file)
        code = self.code_blocks.expand(self.code)

        target_dir = os.path.dirname(tangle_file)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

        write_if_different(tangle_file, code)
    return None
```

The empty `target_dir` check matters for ordinary filenames such as `script.sh`: passing an empty path to `os.makedirs()` would fail even though no directory needs to be created.

# Tests

These tests exercise the complete tangle write path. The first verifies that missing nested target directories are created. The second protects the ordinary filename case, where the target has no directory component.

```python {name=codeblock__tangle_tests menu=true}
import os
import tempfile

@<write_if_different@>
@<omd_assert@>

class CodeBlocks:
    def expand(self, value):
        return value

class CodeBlock:
    @<codeblock__tangle@>

def tangle(target, code):
    block = CodeBlock()
    block.code_blocks = CodeBlocks()
    block.tangle_file = target
    block.code = code
    block.tangle()

with tempfile.TemporaryDirectory() as tmp:
    target = os.path.join(tmp, "missing", "nested", "output.txt")
    tangle(target, "nested output")

    omd_assert(True, os.path.isdir(os.path.dirname(target)))
    with open(target, "r") as output:
        omd_assert("nested output\n", output.read())

with tempfile.TemporaryDirectory() as tmp:
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp)
        tangle("output.txt", "plain output")
        with open("output.txt", "r") as output:
            omd_assert("plain output\n", output.read())
    finally:
        os.chdir(original_cwd)

@<test_passed(name="CodeBlock.tangle")@>
```
