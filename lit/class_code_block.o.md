# Code Block

There are two classes in `omd.py`. `CodeBlock` and `CodeBlocks`. As you might guess, a `CodeBlocks` object represents a list of objects of type `CodeBlock`. `CodeBlock` objects represent parsed information from code blocks in the parsed literate files. Below you can see the basic structure of each class. We will describe specific functions are we progress in the documentation.

### @<classes@>

```python {name=class__codeblock}
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
