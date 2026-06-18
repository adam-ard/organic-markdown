# `CodeBlock::run_omd`

An `omd` code block is a batch of ordinary Organic Markdown commands, one command per line. For example:

````markdown
```omd {name=all menu=true}
tangle
run build
run tests
run app
```
````

Running `omd run all` reaches this method through `CodeBlock.run()`. The block body is expanded once, then each nonblank line is split into command words and sent to `CodeBlocks.handle_cmd()`. Crucially, the method reuses `self.code_blocks`, the collection created by the single project parse at process startup; it never constructs or parses another collection.

The batch has the same short-circuit behavior as the shell command chain it replaces. A command that returns `None` or `0` is successful. The first other return value stops the batch and is returned to the outer command invocation. Blank lines are ignored so commands can be grouped for readability.

```python {name=codeblock__run_omd}
def run_omd(self):
    code = self.code_blocks.expand(self.code)

    for line in code.splitlines():
        words = line.split()
        if not words:
            continue

        result = self.code_blocks.handle_cmd(words)
        if result not in [None, 0]:
            return result

    return 0
```

# Tests

The test double records expansion and dispatch without parsing files or launching subprocesses. It verifies ordered execution, blank-line handling, expansion before dispatch, successful completion, and failure short-circuiting.

```python {name=codeblock__run_omd_tests menu=true}
@<omd_assert@>

class CodeBlocks:
    def __init__(self, results):
        self.results = results
        self.expansions = []
        self.commands = []

    def expand(self, code):
        self.expansions.append(code)
        return code.replace("BUILD_COMMAND", "run build")

    def handle_cmd(self, words):
        self.commands.append(words)
        return self.results.get(" ".join(words))

class CodeBlock:
    @<codeblock__run_omd@>

successful_blocks = CodeBlocks({})
successful = CodeBlock()
successful.code_blocks = successful_blocks
successful.code = "tangle\n\nBUILD_COMMAND\nrun tests"

omd_assert(0, successful.run_omd())
omd_assert([successful.code], successful_blocks.expansions)
omd_assert(
    [["tangle"], ["run", "build"], ["run", "tests"]],
    successful_blocks.commands,
)

failing_blocks = CodeBlocks({"run tests": 3})
failing = CodeBlock()
failing.code_blocks = failing_blocks
failing.code = "run build\nrun tests\nrun app"

omd_assert(3, failing.run_omd())
omd_assert(
    [["run", "build"], ["run", "tests"]],
    failing_blocks.commands,
)

@<test_passed(name="CodeBlock.run_omd")@>
```
