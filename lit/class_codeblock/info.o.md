# Print Info

To make it easy to inspect a `CodeBlock`, we implement Python’s special `__repr__` method. This method is automatically called when you pass an object to the `print()` function, or when inspecting it in a debugger or REPL.

It prints out useful metadata and the expanded code block content in a structured and readable format.

---

### 🔗 `@<codeblock__repr@>`

```python {name=codeblock__repr}
def __repr__(self):
    out = "CodeBlock("
    if self.name is not None:
        out += f"name={self.name}, "
    if self.origin_file is not None:
        out += f"origin={self.origin_file}, "
    if self.docker_container is not None:
        out += f"docker={self.code_blocks.expand(self.docker_container)}, "
    if self.ssh_host is not None:
        out += f"ssh={self.code_blocks.expand(self.ssh_host)}, "
    if self.lang is not None:
        out += f"lang={self.lang}, "
    out += f"dir={self.code_blocks.expand(self.cwd)}, "
    if self.in_menu:
        out += f"menu={self.in_menu}, "
    out += ")\n"
    out += f"{{\n{indent(self.code_blocks.expand(self.code), '    ')}\n}}"
    return out
```

This output includes:

* Basic metadata: name, file of origin, language, working directory
* Execution targets: Docker container or SSH host (if specified)
* Whether it appears in the menu
* The fully expanded code block body

---

### Convenience Method: `info()`

To simplify printing, we add a small `info()` method that just calls `print(self)`. This is a bit more expressive when used in scripts or interactive sessions.

---

### 🔗 `@<codeblock__info@>`

```python {name=codeblock__info}
def info(self):
    print(self)
```
