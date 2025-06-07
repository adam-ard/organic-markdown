# `CodeBlocks::get_code_block`

This method looks up a named `CodeBlock` within the current `CodeBlocks` instance.

It returns the **first** block that matches the given `name`, or `None` if no match is found.

Used throughout the system to resolve references like `@<name@>` during expansion or execution.

---

### 🔗 `@<codeblocks__get_code_block@>`

```python {name=codeblocks__get_code_block}
def get_code_block(self, name):
    for block in self.code_blocks:
        if block.name == name:
            return block
    return None
```

Simple, linear, and efficient for small to medium projects.
(If performance ever becomes an issue, it could be backed by a dictionary)
