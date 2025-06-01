# Tests for CodeBlock::get_run_cmd

Here are a few tests to confirm that the get_run_cmd functionality is working correctly:


```python {tangle=tests/get_run_cmd.py}
#!/usr/bin/env python3

@<omd_assert@>

def escape_code(code):
    return code

class CodeBlocksFake:
    def expand(self, code, args):
        return code

class CodeBlockFake:
    def __init__(self, lang, code, docker_container, ssh_host, cwd):
        self.code = code
        self.lang = lang
        self.code_blocks = CodeBlocksFake()
        self.docker_container = docker_container
        self.ssh_host = ssh_host
        self.cwd = cwd
    @<codeblock__get_run_cmd@>

cb = CodeBlockFake("bash", "<cmd>", None, None, "/the/path")
cmd = cb.get_run_cmd()
expected = """cd /the/path
<cmd>"""

omd_assert(expected, cmd)

cb = CodeBlockFake("bash", "<cmd>", "my_docker", None, "/the/path")
cmd = cb.get_run_cmd()
expected = """docker exec -it my_docker 'cd /the/path
<cmd>'"""

omd_assert(expected, cmd)

cb = CodeBlockFake("perl", "<cmd>", None, None, "/the/path")
cmd = cb.get_run_cmd()
expected = """cd /the/path
perl -E '<cmd>'"""

omd_assert(expected, cmd)

cb = CodeBlockFake("ruby", "<cmd>", None, "aard@my-host.com", "/the/other/path")
cmd = cb.get_run_cmd()
expected = """ssh -t aard@my-host.com 'cd /the/other/path
ruby -e '<cmd>''"""

omd_assert(expected, cmd)

@<test_passed(name="get_run_cmd")@>
```


To run the get_run_cmd test:

```bash {name=get_run_cmd_tests menu=true}
tests/get_run_cmd.py
```

[source code](get_run_cmd.o.md)
