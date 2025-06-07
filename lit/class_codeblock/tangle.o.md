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

        write_if_different(tangle_file, code)
    return None
```

Short, efficient, and extremely powerful when combined with literate references.
