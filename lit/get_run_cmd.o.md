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

### 🧪 Related Tests

See: [get\_run\_cmd\_tests.o.md](get_run_cmd_tests.o.md)
