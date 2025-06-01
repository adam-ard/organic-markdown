# Handle Cmd Tests

This test checks that we are handling the simple cases correctly in the interactive command loop.

### @<handle_cmd_test@>

```python {name=handle_cmd_test}
code_blocks.reset()
cmd="@<cmd@>"
for i in [1]:   # put this inside a for loop so the break and continue commands are valid
    @<handle_cmd@>

@<omd_assert@>

omd_assert(@<parsed@>, code_blocks.parsed)
omd_assert(@<words@>, code_blocks.words)
```

### tangle: tests/handle_cmd.py

```python {tangle=tests/handle_cmd.py}
#!/usr/bin/env python3

class CodeBlocks:
    def __init__(self):
        self.reset()
    def reset(self):
        self.parsed = False
        self. words = []
    def parse(self):
        self.parsed = True
    def handle_cmd(self, words):
        self.words = words

code_blocks = CodeBlocks()

@<handle_cmd_test(cmd=exit
                  parsed=False
                  words=[]
                  fail_msg="didn't run exit")@>

@<handle_cmd_test(cmd=reload
                  parsed=True
                  words=[]
                  fail_msg="did't run reload")@>

@<handle_cmd_test(cmd=diff_command
                  parsed=False
                  words="[\"diff_command\"]"
                  fail_msg="didn't run one word command")@>

@<handle_cmd_test(cmd="diff command"
                  parsed=False
                  words="[\"diff\", \"command\"]"
                  fail_msg="didn't run multi-word command")@>

@<test_passed(name="Handle Cmd")@>
```

# Run Tests

```bash {name=handle_cmd_tests menu=true}
tests/handle_cmd.py
```

[source code](handle_cmd.o.md)
