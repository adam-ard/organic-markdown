# Main Code Test

Simple test that check that the right mode is executed at the right time: command mode when there are more than one argument, and interactive mode otherwise. Also assures that the program exits with an error code if it fails.

### tangle: tests/main_code.py

```python {tangle=tests/main_code.py}
#!/usr/bin/env python3

class sys:
  argv = ["script_name"]

interactive_mode_ran = False;
@<main_code(parse="pass" cmd_exit="pass" interactive_mode="interactive_mode_ran=True")@>

if not interactive_mode_ran:
    @<test_failed(name="Main Code" msg="command mode not invoked")@>

sys.argv.append("extra")
sys.argv.append("args")
@<main_code(parse="pass" cmd_exit="interactive_mode_ran=False" interactive_mode="pass")@>

if interactive_mode_ran:
    @<test_failed(name="Main Code" msg="interactive mode not invoked")@>

@<test_passed(name="Main Code")@>
```

# Run Tests

```bash {name=main_code_tests menu=true}
tests/main_code.py
```


[Main Code](main_code.o.md)
