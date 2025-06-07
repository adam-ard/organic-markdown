# Code Blocks run_all_blocks_fn

A simple function that runs a function on each CodeBlock. The `fn` arg must be a member of the `CodeBlock` class
and only take on argument.

```python {name=codeblocks__run_all_blocks}
def run_all_blocks_fn(self, fn):
    for block in self.code_blocks:
        fn(block)
```
