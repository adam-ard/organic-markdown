# Main Code

The `main_code` section is where our program gets going. Two modes are
available: interactive and command. In interactive mode all the
literate code is parsed and then you get dropped into a repl, where
you can ask questions. Command mode parses the code, runs a single
command, and then exits. Usually command mode is sufficient, because
the parsing is fast, but if you had a lot of code, it might be nice to
parse it once and run several commands in a row without having to pay the
price of parsing over and over.

The way the code determines which mode to invoke is by the number of
command-line arguments. If there are zero args, then OMD invokes
interactive mode. Otherwise, it executes a single command in command mode.

```python {name=main_code}
@<parse@>

if len(sys.argv) > 1:
    @<cmd_exit@>

else:
    @<interactive_mode@>
```
