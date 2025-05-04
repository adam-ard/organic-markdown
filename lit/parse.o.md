# Parse Code

To parse literate code files (files that end in `o.md`), we create a `CodeBlocks` object and call the `parse` function.

OMD parses all `o.md` files in the current directory. It looks for OMD files recursively in any subfolders as well.

```python {name=parse}
code_blocks = CodeBlocks()
code_blocks.parse()
```

[Run Command And Exit](command_mode.o.md)
