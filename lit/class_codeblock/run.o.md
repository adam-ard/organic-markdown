# `CodeBlock::run`

This method executes the command associated with a `CodeBlock`. Ordinary language blocks are expanded into a temporary executable file as before. The specialized `omd` language is handled separately by [`run_omd()`](run_omd.o.md), because its contents are OMD commands that must be dispatched against the already-parsed `CodeBlocks` collection rather than passed to an external interpreter.

It works by:

1. Delegating `omd` blocks to `run_omd()`, or
2. Calling [`self.get_run_cmd()`](get_run_cmd.o.md) to build the full shell command (taking into account language, working directory, Docker, or SSH), then passing that command to Python’s `subprocess.call()` with `shell=True`.

This method is triggered when a user runs:

```bash
omd run <name>
```

on the command line.

---

### 🔗 `@<codeblock__run@>`

```python {name=codeblock__run}
def run(self):
    if self.lang == "omd":
        return self.run_omd()

    cmd = self.get_run_cmd()
    if cmd is None:
        print("Error running command")
        return

    return subprocess.call(cmd, shell=True)
```

The language check belongs here, before `get_run_cmd()`, so `omd` remains a control language rather than an external executable language.

# Tests

This focused test verifies that an `omd` block is delegated to the in-process batch runner and that ordinary languages retain the external-command path.

```python {name=codeblock__run_tests menu=true}
@<omd_assert@>

class CodeBlock:
    @<codeblock__run@>

    def __init__(self, lang):
        self.lang = lang
        self.batch_calls = 0

    def run_omd(self):
        self.batch_calls += 1
        return 7

    def get_run_cmd(self):
        return None

batch = CodeBlock("omd")
omd_assert(7, batch.run())
omd_assert(1, batch.batch_calls)

ordinary = CodeBlock("bash")
omd_assert(None, ordinary.run())
omd_assert(0, ordinary.batch_calls)

@<test_passed(name="CodeBlock.run")@>
```
