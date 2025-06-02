# `CodeBlocks::parse`

This method walks the current directory tree, locates all `.o.md` files, and uses Pandoc to parse them into JSON. That JSON is then translated into Python data structures so that each code block—and any constants defined in YAML—can be loaded into the system.

---

### Example Input

Here’s a simple `.o.md` file that includes YAML metadata, a heading, a paragraph, and a code block:

``````markdown
---
constants:
  test1: "one"
  test2: "two"
---

# Test file heading

Here is some explanation

```bash {name=test-code-block menu=true lang=python}
echo "hello there friend"
echo "hello there friend2"
```
``````

This would be converted by Pandoc into JSON, and from there into Python structures like the following:

```python
{'blocks': [{'c': [1,
                   ['test-file-heading', [], []],
                   [{'c': 'Test', 't': 'Str'},
                    {'t': 'Space'},
                    {'c': 'file', 't': 'Str'},
                    {'t': 'Space'},
                    {'c': 'heading', 't': 'Str'}]],
             't': 'Header'},
            {'c': [{'c': 'Here', 't': 'Str'},
                   {'t': 'Space'},
                   {'c': 'is', 't': 'Str'},
                   {'t': 'Space'},
                   {'c': 'some', 't': 'Str'},
                   {'t': 'Space'},
                   {'c': 'explanation', 't': 'Str'}],
             't': 'Para'},
            {'c': [['',
                    ['bash'],
                    [['name', 'test-code-block'],
                     ['menu', 'true'],
                     ['lang', 'python']]],
                   'echo "hello there friend"\necho "hello there friend2"'],
             't': 'CodeBlock'}],
 'meta': {'constants': {'c': {'test1': {'c': [{'c': 'one', 't': 'Str'}],
                                        't': 'MetaInlines'},
                              'test2': {'c': [{'c': 'two', 't': 'Str'}],
                                        't': 'MetaInlines'}},
                        't': 'MetaMap'}},
 'pandoc-api-version': [1, 23, 1]}
```

---

### Parsing Logic

The code below does the following:

* **`parse()`**: Recursively searches for `.o.md` files in the current directory and its subdirectories.
* **`parse_file()`**: Converts a Markdown file into Pandoc JSON.
* **`parse_json()`**:

  * Loads constants from the YAML metadata block into `CodeBlock` objects.
  * Parses each actual code block into a `CodeBlock` object.
* **`add_code_block()`**:

  * Merges contents if multiple blocks share the same name (concatenating their code).

---

### 🔗 `@<codeblocks__parse@>`

```python {name=codeblocks__parse}
def parse(self):
    # Read all files in the current directory (recursively) with .o.md extension
    for root, dirs, files in os.walk("."):
        for cur_file in files:
            cur_full_file = f"{root}/{cur_file}"
            if cur_full_file.endswith(".o.md"):
                self.parse_file(cur_full_file)

def parse_file(self, filename):
    data = json.loads(pypandoc.convert_file(filename, 'json', format="md"))
    self.parse_json(data, filename)

def add_code_block(self, code_block):
    if code_block.name is not None:
        blk = self.get_code_block(code_block.name)
        if blk is not None:
            code_block.code = blk.code + "\n" + code_block.code
            self.code_blocks.remove(blk)

    self.code_blocks.append(code_block)

def parse_json(self, data, origin_file):
    for section, constants in data['meta'].items():
        if section == "constants":
            for key, val in constants['c'].items():
                str = ""
                for i in val['c']:
                    if i['t'] == "Str":
                        str += i['c']
                    if i['t'] == "Space":
                        str += " "

                cb = CodeBlock()
                cb.origin_file = origin_file
                cb.name = key
                cb.code = str
                cb.code_blocks = self

                # Append to existing block with same name if needed
                self.add_code_block(cb)

    for block in data['blocks']:
        if block['t'] == "CodeBlock":
            cb = CodeBlock()
            cb.origin_file = origin_file
            cb.parse(block['c'])
            cb.code_blocks = self

            # Append to existing block with same name if needed
            self.add_code_block(cb)
```
