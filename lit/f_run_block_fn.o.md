# CodeBlocks::run_block_fn

In the [CodeBlocks](class_code_blocks.o.md) class, is a useful function called `run_block_fn` which takes an identifier and a pointer to a function. If the identifier is a digit, it is treated as an index into the list of blocks that the `CodeBlocks` holds as data. The function will call the function `fn` on the `CodeBlock` located at index `identifier`. Otherwise, it is assumed that the identifier represents the name of a `CodeBlock` and the function will search for the `CodeBlock` with a matching name, and execute `fn` with the matching block as its argument.

This function get used a lot in the [CodeBlocks::handle_cmd](handle_cmd.o.md) function of the program.

```python {name=CodeBlocks_funcs}
def run_block_fn(self, identifier, fn):
    block = self.get_code_block(identifier)

    if block is None:
        print("Error: No Matching Code Blocks Found.")
        return -1

    return fn(block)
```
