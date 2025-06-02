# Escape Code

When executing commands over SSH or inside a Docker container, it’s important to escape them properly—especially when they contain quotes or special characters. This function handles those edge cases with care.

The strategy:

1. **Wrap the entire command in single quotes** `'...'`
2. **Escape any single quotes inside the command** using the idiom: `'\''`
   This temporarily closes the quote, inserts an escaped quote, and then reopens the quote.

For example, suppose you want to run the following remotely:

```bash
echo 'hello "world"'
```

It would be escaped like this:

```bash
ssh user@remotehost 'echo '\''hello "world"'\'''
```

We take it a step further by wrapping the whole thing in a `bash -c` call:

```bash
bash -c '<escaped_cmd>'
```

Then, since the `bash -c` expression itself might be nested inside `ssh -t` or `docker exec -it`, we escape that whole thing again.

This allows us to safely run:

```bash
ssh -t user@host 'bash -c '\''echo '\''\''hello "world"'\'''\'''
```

Yes—it’s messy. But it works reliably.

---

### 🔗 `@<escape_code@>`

```python {name=escape_code}
def escape_code(command):
    # Escape all single quotes inside the command
    escaped_cmd = command.replace("'", "'\\''")

    # Wrap in a single-quoted bash call
    remote_cmd = f"bash -c '{escaped_cmd}'"

    # Escape the outer call for use in ssh/docker
    return remote_cmd.replace("'", "'\\''")
```

This function is used by [`CodeBlock::get_run_cmd`](#codeblock__get_run_cmd), where the resulting string is injected into SSH or Docker execution contexts.
