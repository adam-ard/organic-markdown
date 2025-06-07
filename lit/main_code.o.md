# Main Code

The `main_code` section is where our program gets going. Two modes are available: interactive and command. In interactive mode all the literate code is parsed and then you get dropped into a repl, where you can ask questions. Command mode parses the code, runs a single command, and then exits. Usually command mode is sufficient, because the parsing is fast, but if you had a lot of code, it might be nice to parse it once and run several commands in a row without having to pay the price of parsing over and over.

The way the code determines which mode to invoke is by the number of command-line arguments. If there are zero args, then OMD invokes interactive mode. Otherwise, it executes a single command in command mode.

### @<main_code@>

```python {name=main_code}
@<parse@>

if len(sys.argv) > 1:
    @<cmd_exit@>

else:
    @<interactive_mode@>
```

# Tests

Simple test that check that the right mode is executed at the right time: command mode when there are more than one argument, and interactive mode otherwise. Also assures that the program exits with an error code if it fails.

### tangle: tests/main_code.py

```python {tangle=tests/main_code.py}
#!/usr/bin/env python3

@<omd_assert@>

class sys:
  argv = ["script_name"]

interactive_mode_ran = False;
@<main_code(parse="pass" cmd_exit="pass" interactive_mode="interactive_mode_ran=True")@>

omd_assert(True, interactive_mode_ran)

sys.argv.append("extra")
sys.argv.append("args")
@<main_code(parse="pass" cmd_exit="interactive_mode_ran=False" interactive_mode="pass")@>

omd_assert(False, interactive_mode_ran)

@<test_passed(name="Main Code")@>
```

# Run Tests

```bash {name=main_code_tests menu=true}
tests/main_code.py
```
