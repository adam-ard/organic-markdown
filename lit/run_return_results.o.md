# `CodeBlock::run_return_results`

This method runs the expanded command associated with the block’s `self.code` and returns its output as a string.

Unlike `run()`, which simply executes the command and streams its output to the terminal, this method **captures the result** for further processing. It’s used when referencing a block with the `*` syntax, like:

```markdown
@<name*@>
```

Here’s how it works:

1. It retrieves the fully expanded shell command from [`self.get_run_cmd(args)`](get_run_cmd.o.md),
2. Executes the command using `subprocess.run()` with `capture_output=True`,
3. Decodes the output to UTF-8,
4. Removes one trailing newline (if present),
5. Returns the result as a string.

---

### 🔗 `@<codeblock__run_return_results@>`

```python {name=codeblock__run_return_results}
def run_return_results(self, args={}):
    cmd = self.get_run_cmd(args)
    if cmd is None:
        print("Error running command")
        return

    output = subprocess.run(cmd, capture_output=True, shell=True)
    out_decode = output.stdout.decode("utf-8")

    # remove at most one newline, if it exists at the end of the output
    if len(out_decode) > 0 and out_decode[-1] == "\n":
        out_decode = out_decode[:-1]

    return out_decode
```

This method gives `omd` its dynamic capabilities—allowing code block outputs to be embedded directly in other files or strings.
