# Main Code

The `main_code` section routes private daemon startup separately from the public
CLI. Public invocations obtain the parsed project snapshot from the per-project
daemon, then retain the established local command and interactive behavior. This
keeps terminal ownership in the foreground process while avoiding repeated
Pandoc work.

The way the code determines which mode to invoke is by the number of command-line arguments. If there are zero args, then OMD invokes interactive mode. Otherwise, it executes a single command in command mode.

### @<main_code@>

```python {name=main_code}
if len(sys.argv) > 1 and sys.argv[1] == "--omd-daemon":
    daemon_main(sys.argv[2], sys.argv[3], sys.argv[4])
elif len(sys.argv) > 1 and sys.argv[1] == "reparse":
    if len(sys.argv) != 3:
        print("usage: omd reparse <filename>", file=sys.stderr)
        sys.exit(2)
    sys.exit(daemon_reparse(os.getcwd(), sys.argv[2]))
else:
    code_blocks = daemon_snapshot(os.getcwd())

if len(sys.argv) > 1 and sys.argv[1] not in ["--omd-daemon", "reparse"]:
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

def daemon_snapshot(_root):
  return None

def daemon_main(_root, _token, _registry):
  pass

def daemon_reparse(_root, _filename):
  return 0

interactive_mode_ran = False;
@<main_code(cmd_exit="pass" interactive_mode="interactive_mode_ran=True")@>

omd_assert(True, interactive_mode_ran)

sys.argv.append("extra")
sys.argv.append("args")
@<main_code(cmd_exit="interactive_mode_ran=False" interactive_mode="pass")@>

omd_assert(False, interactive_mode_ran)

@<test_passed(name="Main Code")@>
```
