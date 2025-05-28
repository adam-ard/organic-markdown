# CodeBlock::get_run_cmd

This function will return the bash command to run the expanded text in `self.code` in the language specified for the block. It gets executed directly by the run command `omd run <name>` or as part of a string substitution like this `@<name*@>`. Note that we use `ssh -t` to make sure that the ssh session opens up with a proper terminal. The same is true with docker where we run `docker exec -it`.

### @<codeblock\_\_get\_run\_cmd@>

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

[tests](get_run_cmd_tests.o.md)
