# Interactive Mode

Interactive mode is an infinite loop. Before each prompt it refreshes the
`CodeBlocks` collection through the parsed project cache, so edits made while
the session is open are picked up automatically without a manual reload command.
After reading input, `exit` leaves the loop and every other command is delegated
to the normal `CodeBlocks.handle_cmd()` dispatcher.

### @<interactive_mode@>

```python {name=interactive_mode}
while True:
    code_blocks = omd_load_code_blocks(os.getcwd())
    cmd = input("> ") # print prompt
    @<handle_cmd@>
```

Each iteration of the while loop executes the following code:

### @<handle_cmd@>

```python {name=handle_cmd}
words = cmd.split(" ")

if words[0] == "exit":
    break

code_blocks.handle_cmd(words)
```
