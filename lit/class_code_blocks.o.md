# Code Blocks

There are two classes in `omd.py`. `CodeBlock` and `CodeBlocks`. As
you might guess, a `CodeBlocks` object represents a list of objects of
type `CodeBlock`. `CodeBlock` objects represent parsed information
from code blocks in the parsed literate files. Below you can see the
basic structure of each class. We will describe specific functions are
we progress in the documentation.

```python {name=classes}
class CodeBlock:
    @<CodeBlock_funcs@>
```

For reference, in a literate source file (has extenstion `.o.md`) code
blocks looks like this. They follow the format used by pandoc: https://pandoc.org/MANUAL.html

``````
```<lang> {name=<name> ...}
source code
```
``````

Below you can see that a `CodeBlocks` class holds a list of `CodeBlock` objects:

```python {name=classes}
class CodeBlocks:
    def __init__(self):
        self.code_blocks = []
    @<CodeBlocks_funcs@>
```
