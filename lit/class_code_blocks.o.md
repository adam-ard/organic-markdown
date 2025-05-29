# Code Blocks

There are two classes in `omd.py`. `CodeBlock` and `CodeBlocks`. As you might guess, a `CodeBlocks` object represents a list of objects of type `CodeBlock`. `CodeBlock` objects represent parsed information from code blocks in the parsed literate files. Below you can see the basic structure of each class. We will describe specific functions are we progress in the documentation.

### @<classes@>

```python {name=classes}
class CodeBlock:
    @<codeblock__origin@>
    @<codeblock__repr@>
    @<codeblock__info@>
    @<codeblock__get_run_cmd@>
    @<codeblock__run@>
    @<codeblock__run_return_results@>
    @<codeblock__tangle@>
    @<codeblock__parse@>
    @<codeblock__init@>
```

For reference, in a literate source file (has extenstion `.o.md`) code blocks looks like this. They follow the format used by pandoc: https://pandoc.org/MANUAL.html

``````
```<lang> {name=<name> ...}
source code
```
``````

Below you can see that a `CodeBlocks` class holds a list of `CodeBlock` objects:

### @<classes@>

```python {name=classes}
class CodeBlocks:
    def __init__(self):
        self.code_blocks = []
    @<CodeBlocks_funcs@>
    
    @<codeblocks__get_code_block@>
    @<codeblocks__handle_cmd@>
    @<codeblocks__run_all_blocks@>
    @<codeblocks__weave_file@>
    @<codeblocks__run_block_fn@>
```
