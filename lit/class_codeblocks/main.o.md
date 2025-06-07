# Code Blocks

The `CodeBlocks` class represents a collection of `CodeBlock` objects.

It acts as the main container and controller for code blocks defined in a literate source file. It orchestrates all the block-level behavior in `omd`.

Here’s its structure:

```python {name=class__codeblocks}
class CodeBlocks:
    def __init__(self):
        self.code_blocks = []
    @<codeblocks__parse@>
    @<codeblocks__print@>
    @<codeblocks__expand@>
    @<codeblocks__get_code_block@>
    @<codeblocks__handle_cmd@>
    @<codeblocks__run_all_blocks@>
    @<codeblocks__weave_file@>
    @<codeblocks__run_block_fn@>
```

Each method will be documented in detail in the following files.
