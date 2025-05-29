# CodeBlocks::get_code_block

A function in the [CodeBlocks](class_code_blocks.o.md) class that takes a block name and returns the first block that matches in [self.code_blocks](class_code_blocks.o.md). If no block match the input `name`, then `None` is returned.

```python {name=codeblocks__get_code_block}
def get_code_block(self, name):
    for block in self.code_blocks:
        if block.name == name:
            return block
    return None
```
