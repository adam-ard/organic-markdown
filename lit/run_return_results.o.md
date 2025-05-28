# CodeBlock::run_return_results

This method runs the expanded command associated with the CodeBlock's `self.code` field, captures the stdout as a string and returns it. First, the full bash command is retrieved from [self.get_run_command](get_run_cmd.o.md), then it is passed to `subprocess.run` with `shell=True`. Then the last newline is removed (if one exists). This method gets invoked when expanding a reference the the `*` syntax: @<name*@>.

```python {name=codeblock__run_return_results}
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
```
