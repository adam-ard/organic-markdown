# `CodeBlock::origin`

Prints the name of the file this code block was originally parsed from.

This is primarily useful for debugging or logging purposes, so you can trace a block back to its source file. Also helpful for code editor integration.

```python {name=codeblock__origin}
def origin(self):
    print(self.origin_file)
```
