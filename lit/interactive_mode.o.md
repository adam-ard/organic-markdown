# Interactive Mode

Interactive mode is an infinite loop. After printing a command prompt it reads input from the user. After splitting the input into a list based on characters separated by whitespace, it check the first word for a couple simple matches. If the word is `exit`, we break out of the loop and exit the program. If the word is `reload`, we parse the literate files again and continue. Otherwise, we pass the command to `handle_cmd` function to execute a single command. After which we loop back and print another command prompt, and wait for the next command.

```python {name=interactive_mode}
while True:
    cmd = input("> ") # print prompt
    @<handle_cmd@>
```

Each iteration of the while loop executes the following code:

```python {name=handle_cmd}
words = cmd.split(" ")

if words[0] == "exit":
    break

if words[0] == "reload":
    code_blocks = CodeBlocks()
    code_blocks.parse()
    print("code reloaded")
    continue

code_blocks.handle_cmd(words)
```

