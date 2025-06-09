# `CodeBlock::get_run_cmd`

This method returns the shell command needed to execute the expanded contents of `self.code`, according to the block’s declared language and execution context.

It is used internally by `omd run <name>` and also for inline substitution with `@<name*@>`.

If the block is configured to run in a Docker container or over SSH, this method will wrap the command accordingly using `docker exec -it` or `ssh -t` to ensure an interactive terminal session.

---

### 🔗 `@<codeblock__get_run_cmd@>`

```python {name=codeblock__get_run_cmd}
def get_run_cmd(self, args={}):
    code = self.code_blocks.expand(self.code, args)
    lang = self.lang

    # Decide file extension and interpreter
    lang_info = {
        "bash": (".sh", "bash"),
        "python": (".py", "python3"),
        "ruby": (".rb", "ruby"),
        "haskell": (".hs", "runhaskell"),
        "racket": (".rkt", "racket"),
        "perl": (".pl", "perl"),
        "javascript": (".js", "node"),
    }

    if lang not in lang_info:
        print(f"language {lang} is not supported for execution")
        return None

    ext, interpreter = lang_info[lang]

    # Generate consistent UUID-based temp file name in /tmp
    uid = uuid.uuid4().hex
    filename = f"omd-temp-{uid}{ext}"
    tmp_path = f"/tmp/{filename}"
    remote_path = tmp_path

    with open(tmp_path, "w") as tmp_file:
        tmp_file.write(code)

    cwd = self.code_blocks.expand(self.cwd, args) if hasattr(self, "cwd") and self.cwd else None
    cd_prefix = f"cd {cwd} && " if cwd else ""

    if self.docker_container is not None:
        container = self.code_blocks.expand(self.docker_container, args)
        return f"docker cp {tmp_path} {container}:{remote_path} && docker exec {container} bash -c \"{cd_prefix}{interpreter} {remote_path}\" && docker exec {container} rm {remote_path}"

    elif self.ssh_host is not None:
        ssh = self.code_blocks.expand(self.ssh_host, args)
        return f"scp {tmp_path} {ssh}:{remote_path} && ssh {ssh} '{cd_prefix}{interpreter} {remote_path}' && ssh {ssh} rm {remote_path}"

    else:
        return f"{cd_prefix}{interpreter} {tmp_path}"
```

---

# Tests

Here are a few tests to confirm that the get_run_cmd functionality is working correctly:


```python {name=get_run_cmd_tests_file tangle=tests/get_run_cmd.py}
#!/usr/bin/env python3

import os
import uuid

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

### when there is an invalid language specified

cb = CodeBlockFake("not_a_language", "<cmd>", None, None, "/the/path")
cmd = cb.get_run_cmd()

omd_assert(None, cmd)

### when there is no language specified

cb = CodeBlockFake(None, "<cmd>", None, None, "/the/path")
cmd = cb.get_run_cmd()

omd_assert(None, cmd)

#### When there is no cwd

cb = CodeBlockFake("bash", "<cmd>", None, None, None)
cmd = cb.get_run_cmd()

expected_regex = r"bash /tmp/[^\s]+\.sh"

omd_assert_regex(expected_regex, cmd)

#### normal local

cb = CodeBlockFake("bash", "<cmd>", None, None, "/the/path")
cmd = cb.get_run_cmd()

expected_regex = r"cd /the/path && bash /tmp/[^\s]+\.sh"

omd_assert_regex(expected_regex, cmd)

### docker 

cb = CodeBlockFake("bash", "<cmd>", "my_docker", None, "/the/path")
cmd = cb.get_run_cmd()

expected_regex=r"""docker cp /tmp/[^\s]+\.sh my_docker:/tmp/[^\s]+\.sh && docker exec my_docker bash -c "cd /the/path && bash /tmp/[^\s]+\.sh" && docker exec my_docker rm /tmp/omd-[^\s]+\.sh"""

omd_assert_regex(expected_regex, cmd)

#### docker no cwd

cb = CodeBlockFake("bash", "<cmd>", "my_docker", None, None)
cmd = cb.get_run_cmd()

expected_regex=r"""docker cp /tmp/[^\s]+\.sh my_docker:/tmp/[^\s]+\.sh && docker exec my_docker bash -c "bash /tmp/[^\s]+\.sh" && docker exec my_docker rm /tmp/omd-[^\s]+\.sh"""

omd_assert_regex(expected_regex, cmd)

#### different language

cb = CodeBlockFake("perl", "<cmd>", None, None, "/the/path")
cmd = cb.get_run_cmd()

expected_regex=r"""cd /the/path && perl /tmp/[^\s]+\.pl"""
omd_assert_regex(expected_regex, cmd)

#### ssh

cb = CodeBlockFake("ruby", "<cmd>", None, "aard@my-host.com", "/the/other/path")
cmd = cb.get_run_cmd()

expected_regex=r"""scp /tmp/[^\s]+\.rb aard@my-host.com:/tmp/[^\s]+\.rb && ssh aard@my-host.com 'cd /the/other/path && ruby /tmp/[^\s]+\.rb' && ssh aard@my-host.com rm /tmp/[^\s]+\.rb"""

omd_assert_regex(expected_regex, cmd)

@<test_passed(name="get_run_cmd")@>
```

To run the get_run_cmd test:

```bash {name=get_run_cmd_tests menu=true}
tests/get_run_cmd.py
```

