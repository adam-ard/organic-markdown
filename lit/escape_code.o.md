# Escape Code

This function will escape problemmatic characters in a bash command. I used the following strategy:

1. Use single quotes `'` around the entire command
2. Escape any single quotes inside that command using this idiom: '\\'' — which ends the current single quote, adds an escaped quote, and starts a new one.

For example, to run the following on a remote host through ssh:

```
echo 'hello "world"'
```

I would escape like this:

```
ssh user@remotehost 'echo '\''hello "world"'\'''
```

I take this one step further, so I can wrap calls inside of a call to bash like this:

```
bash -c '<escaped_cmd>'
```

So in my escape function, you'll see me apply the above strategy to my command, then wrap a call to bash around that (using single quotes), then escape everything once more. This lets me run commands in a docker container or ssh command like this:

```
ssh -t {ssh_host} '<double_escaped_code>'
```

Now, without further ado, here is my double escape function:

### @<funcs@>

```python {name=funcs}
def escape_code(command):
    # escaped all single quotes
    escaped_cmd = command.replace("'", "'\\''")

    # wrap in a single quoted bash call
    remote_cmd = f"bash -c '{escaped_cmd}'"

    # escape everything one more time
    return remote_cmd.replace("'", "'\\''")
```

To see how this is applied, see CodeBlock::get_run_cmd.
