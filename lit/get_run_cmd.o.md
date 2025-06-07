# `CodeBlock::get_run_cmd`

This method returns the shell command needed to execute the expanded contents of `self.code`, according to the block’s declared language and execution context.

It is used internally by `omd run <name>` and also for inline substitution with `@<name*@>`.

If the block is configured to run in a Docker container or over SSH, this method will wrap the command accordingly using `docker exec -it` or `ssh -t` to ensure an interactive terminal session.

---

### 🔗 `@<codeblock__get_run_cmd@>`

```python {name=codeblock__get_run_cmd}
def get_run_cmd(self, args={}):
    code = self.code_blocks.expand(self.code, args)

    if self.lang == "bash":
        cmd = code
    elif self.lang == "python":
        cmd = f"python3 -c '{code}'"
    elif self.lang == "ruby":
        cmd = f"ruby -e '{code}'"
    elif self.lang == "haskell":
        cmd = f"ghci -e '{code}'"
    elif self.lang == "racket":
        cmd = f"racket -e '{code}'"
    elif self.lang == "perl":
        cmd = f"perl -E '{code}'"
    elif self.lang == "javascript":
        cmd = f"node -e '{code}'"
    else:
        print(f"language {self.lang} is not supported for execution")
        return

    if self.docker_container is not None:
        docker_container = self.code_blocks.expand(self.docker_container, args)
    if self.ssh_host is not None:
        ssh_host = self.code_blocks.expand(self.ssh_host, args)

    cwd = self.code_blocks.expand(self.cwd, args)
    cmd_in_dir = f"cd {cwd}\n{cmd}"

    if self.docker_container is not None:
        return f"docker exec -it {self.docker_container} '{escape_code(cmd_in_dir)}'"
    elif self.ssh_host is not None:
        return f"ssh -t {ssh_host} '{escape_code(cmd_in_dir)}'"
    else:
        return cmd_in_dir
```

---

# Tests

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

