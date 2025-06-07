# Code Block

There are two main classes in `omd`: `CodeBlock` and `CodeBlocks`.

As you might guess, a `CodeBlocks` object represents a list of `CodeBlock` objects. Each `CodeBlock` instance holds the parsed information from a single code block in a literate source file.

Below is the structure of the `CodeBlock` class. We'll go into more detail on each method as we progress through the documentation.

---

### 🔗 `@<classes@>`

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

---

For reference, in a literate source file (with the `.o.md` extension), code blocks follow the [Pandoc fenced code block](https://pandoc.org/MANUAL.html#fenced-code-blocks) format, like so:

````
```<lang> {name=<name> ...}
source code
```
````

This format allows metadata like `name`, `tangle` to be embedded directly in the code block header.
