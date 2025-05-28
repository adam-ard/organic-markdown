# CodeBlock::run

This method runs the expanded command associated with the CodeBlock's `self.code` field. First, the full bash command is retrieved from [self.get_run_command](get_run_cmd.o.md), then it is passed to `subprocess.call` with `shell=True`. Short and sweet. This method gets invoke when someone runs the `omd run <name>` command-line.

```python {name=codeblock__run}
def run(self):
    cmd = self.get_run_cmd()
    if cmd is None:
        print("Error running command")
        return

    return subprocess.call(cmd, shell=True)
```
