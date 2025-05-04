# Command Mode

Command mode is straight forward. We take all arguments to the script
except the first one (which will be the name of the script itself) and
pass them to the `handle_cmd` function on the `code_blocks` object. We
exit the program with the exit code returned from the `handle_cmd`
function.

```python {name=cmd_exit}
sys.exit(code_blocks.handle_cmd(sys.argv[1:]))
```
