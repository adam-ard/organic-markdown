# Main Code

The `main_code` section loads the current `CodeBlocks` collection through the
parsed project cache before dispatching either command mode or interactive mode.
The cache keeps Pandoc work out of the hot path when source files are unchanged,
but all command execution still happens in the foreground process. That keeps
terminal behavior, environment variables, and expansion-time command execution
attached to the user's `omd` invocation.

There is no explicit reload command in the normal CLI path. Each invocation
checks the cache metadata and reparses any stale `.o.md` files before running the
requested command. Deleting `.omd-cache.pickle` forces a full parse on the next
invocation.

The way the code determines which mode to invoke is by the number of command-line arguments. If there are zero args, then OMD invokes interactive mode. Otherwise, it executes a single command in command mode.

### @<main_code@>

```python {name=main_code}
code_blocks = omd_load_code_blocks(os.getcwd())

if len(sys.argv) > 1:
    @<cmd_exit@>

elif len(sys.argv) == 1:
    @<interactive_mode@>
```

# Tests

Simple test that check that the right mode is executed at the right time: command mode when there are more than one argument, and interactive mode otherwise. Also assures that the program exits with an error code if it fails.

```python {name=main_code_tests menu=true}
@<omd_assert@>

class sys:
  argv = ["script_name"]
  def exit(code):
    raise SystemExit(code)

class os:
  def getcwd():
    return "."

def omd_load_code_blocks(_root):
  return None

interactive_mode_ran = False;
@<main_code(cmd_exit="pass" interactive_mode="interactive_mode_ran=True")@>

omd_assert(True, interactive_mode_ran)

sys.argv.append("extra")
sys.argv.append("args")
@<main_code(cmd_exit="interactive_mode_ran=False" interactive_mode="pass")@>

omd_assert(False, interactive_mode_ran)

@<test_passed(name="Main Code")@>
```
