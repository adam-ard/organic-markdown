# CodeBlocks::handle_cmd function

The `handle_cmd` methods is used in both interactive mode and command mode. It is a member of the `CodeBlocks` class explained below. It dispatches different commands to different methods on the class:

### @<CodeBlocks_funcs@>

```python {name=CodeBlocks_funcs}
def handle_cmd(self, words):
    if len(words) == 1:
        @<handle_one_word_commands@>

    elif len(words) == 2:
        @<handle_two_word_commands@>

    elif len(words) > 2:
        @<handle_gt_two_word_commands@>

    else:
        print("missing cmd")
```

The following one word commands are dispatched to corresponding methods in the source block below.

1. cmds - print all available cmds found in literate source files
2. files - print filenames of files that `omd tangle` will output
3. status - print a more human readable listing of cmds and files from `omd cmds` and `omd files`
4. tangle - emit all files marked for tangling in literate source files
5. info - print information for all src blocks in literate source files

### @<handle_one_word_commands@>

```python {name=handle_one_word_commands}
if words[0] == "cmds":
    self.print_parseable_cmds()
elif words[0] == "files":
    self.print_files()
elif words[0] == "status":
    self.print_summary()
elif words[0] == "tangle":
    self.run_all_blocks_fn(CodeBlock.tangle)
elif words[0] == "info":
    self.run_all_blocks_fn(CodeBlock.info)
else:
    print(f"unknown command: {words[0]}")
```

The following two word commands are dispatched to corresponding methods in the source block below.

1. tangle \<name> - tangle only the file describe by the block: \<name\>
2. run \<name> - execute the block: \<name>, and print the output to stdout
3. info \<name> - print information for a specific source block
4. origin \<name> - print the name of the literate source file where the block \<name> is defined
5. expand \<name> - expand all refs in source block: \<name>, and print to stdout

### @<handle_two_word_commands@>

```python {name=handle_two_word_commands}
rest = " ".join(words[1:])

if words[0] == "tangle":
    return self.run_block_fn(rest, CodeBlock.tangle)
elif words[0] == "run":
    return self.run_block_fn(rest, CodeBlock.run)
elif words[0] == "info":
    return self.run_block_fn(rest, CodeBlock.info)
elif words[0] == "origin":
    return self.run_block_fn(rest, CodeBlock.origin)
elif words[0] == "expand":
    print(self.expand(rest))
else:
    print(f"unknown command: {' '.join(words)}")
```

Finally all commands that have greater than two words. I won't explain these commands in detail since they are experimental.

### @<handle_gt_two_word_commands@>

```python {name=handle_gt_two_word_commands}
if words[0] == "import":
    import_file(words[1], words[2])
elif words[0] == "weave":
    self.weave_file(words[1], words[2])
else:
    print(f"unknown command: {words[0]}")
```

[tests](handle_cmd_tests.o.md)

### refs
[import_file](experimental_features.o.md)
[weave_file](experimental_features.o.md)
[run_block_fn](f_run_block_fn.o.md)
