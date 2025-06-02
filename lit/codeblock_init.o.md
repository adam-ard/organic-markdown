# `CodeBlock::__init__`

The `__init__` method initializes a new `CodeBlock` instance by setting default values for all its attributes.

Each instance variable represents metadata or behavior associated with a single code block parsed from a `.o.md` file.

```python {name=codeblock__init}
def __init__(self):
    self.origin_file = None       # the file this code block was parsed from
    self.name = None              # the name attribute (if present)
    self.code = None              # the contents of the code block
    self.lang = None              # the language of the code block
    self.cwd = "."                # directory in which the block should execute
    self.tangle_file = None       # file path to write the block to (if tangled)
    self.in_menu = False          # whether this block should appear in the omd status menu
    self.code_blocks = None       # reference to the CodeBlocks object containing this block
    self.docker_container = None  # optional Docker container to run the block in
    self.ssh_host = None          # optional SSH host to run the block on
```

