# CodeBlocks::get_code_block

A `CodeBlocks` function that takes a block name and returns the first block that matches in `self.code_blocks`. If no block match the input `name`, then `None` is returned.


```python {name=CodeBlocks_funcs}
def get_code_block(self, name):
    for block in self.code_blocks:
        if block.name == name:
            return block
    return None
```
