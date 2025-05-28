# Print Info

In order to print information from a CodeBlock, I implimented the python `__repr__` function which gets called when you pass an object to the `print` function.

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

As a convience, I created a function called `info` on the CodeBlock class that simply calls print for the object:

```python {name=codeblock__info}
def info(self):
    print(self)
```
