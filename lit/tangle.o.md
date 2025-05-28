# CodeBlock::tangle

This function gets called when a CodeBlock gets tangled (ie. expanded and written to a file). When the `omd tangle` command is run, then all the `CodeBlock` objects in the `CodeBlocks` Object are tangled, that is to say, each `CodeBlock`'s tangle function is called. The tangle function is very straight-forward. The `self.tangle_file` name itself is expanded, then the `self.code` field. Then the file is written (if it has changed). Expanding the `self.tangle_file` field lets you do cool things like this:

``````
```bash {tangle=@<project_name@>.sh}
<cmds>
```
``````

Here is the tangle code:

```python {name=codeblock__tangle}
def tangle(self):
    if self.tangle_file is not None:
        tangle_file = self.code_blocks.expand(self.tangle_file)
        code = self.code_blocks.expand(self.code)

        write_if_different(tangle_file, code)
    return None
```
