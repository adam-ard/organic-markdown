# `CodeBlock::run`

This method executes the expanded command associated with a `CodeBlock`.

It works by:

1. Calling [`self.get_run_cmd()`](get_run_cmd.o.md) to build the full shell command (taking into account language, working directory, Docker, or SSH),
2. Passing that command to Python’s `subprocess.call()` with `shell=True`.

This method is triggered when a user runs:

```bash
omd run <name>
```

on the command line.

---

### 🔗 `@<codeblock__run@>`

```python {name=codeblock__run}
def run(self):
    cmd = self.get_run_cmd()
    if cmd is None:
        print("Error running command")
        return

    return subprocess.call(cmd, shell=True)
```

Simple, direct, and effective.
