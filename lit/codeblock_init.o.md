# CodeBlock::__init__

In the __init__ function for the CodeBlock function, instance variables are giving initial values:

```python {name=CodeBlock_funcs}
def __init__(self):
    self.origin_file=None      # the file that this code block was parsed from
    self.name=None             # name attribute
    self.code=None             # the code block content
    self.lang=None             # the language of the code block soure code
    self.cwd="."               # the directory in which the code block should be executed
    self.tangle_file=None      # the path where the block should tangle to
    self.in_menu = False       # whether this block should appear in the omd status menu
    self.code_blocks = None    # reference to the Code Blocks object that contains this code block
    self.docker_container=None # name of the docker container to run this block in
    self.ssh_host=None         # host where to run this block (through ssh)
```
