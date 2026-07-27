#### The Code :CARD:

This is the main code file.

Yes, everything is defined in a single file—but that's totally OK! With literate programming, the code that gets generated is more like **compiled output**. You’re not meant to read it directly (or even commit it to Git).

This represents a shift in mindset: the *source of truth* becomes your literate files, not the tangled code they produce. And once you get used to it, it’s a really pleasant way to work.

```python {name=omd_file tangle=lit/omd}
#!/usr/bin/env python3

@<imports@>
@<globals@>
@<funcs@>
@<class__codeblock@>
@<class__codeblocks@>
@<parsed_project_cache@>

@<main@>
```
