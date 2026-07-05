# `CodeBlocks::parse`

This method walks the current directory tree, locates all `.o.md` files, and uses Pandoc to parse them into JSON. Parsed blocks are retained per source file before a merged working collection is built. Keeping the unmerged contributions makes cache refreshes incremental: one changed file can be replaced without reparsing its neighbors, including when names are shared across files.

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
    self.code_blocks = []
    self.file_contributions = {}
    self.file_order = []
    for root, dirs, files in os.walk("."):
        for cur_file in files:
            cur_full_file = f"{root}/{cur_file}"
            if cur_full_file.endswith(".o.md"):
                self.parse_file(cur_full_file)
    self.rebuild()

def parse_file(self, filename):
    key = os.path.normpath(filename)
    data = json.loads(pypandoc.convert_file(key, 'json', format="md"))
    contribution = self.parse_json(data, filename)
    self.file_contributions[key] = contribution
    if key not in self.file_order:
        self.file_order.append(key)

def reparse_file(self, filename):
    filename = os.path.normpath(filename)
    if not filename.endswith(".o.md"):
        raise ValueError("reparse requires an .o.md file")
    if os.path.exists(filename):
        data = json.loads(pypandoc.convert_file(filename, 'json', format="md"))
        previous = self.file_contributions.get(filename, [])
        origin = previous[0].origin_file if previous else filename
        contribution = self.parse_json(data, origin)
        self.file_contributions[filename] = contribution
        if filename not in self.file_order:
            self.file_order.append(filename)
    else:
        self.file_contributions.pop(filename, None)
        if filename in self.file_order:
            self.file_order.remove(filename)
    self.rebuild()

def rebuild(self):
    self.code_blocks = []
    for filename in self.file_order:
        for source in self.file_contributions.get(filename, []):
            cb = pickle.loads(pickle.dumps(source))
            cb.code_blocks = self
            self.add_code_block(cb)

def add_code_block(self, code_block):
    if code_block.name is not None:
        blk = self.get_code_block(code_block.name)
        if blk is not None:
            code_block.code = blk.code + "\n" + code_block.code
            self.code_blocks.remove(blk)

    self.code_blocks.append(code_block)

def parse_json(self, data, origin_file):
    contribution = []
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
                contribution.append(cb)

    for block in data['blocks']:
        if block['t'] == "CodeBlock":
            cb = CodeBlock()
            cb.origin_file = origin_file
            cb.parse(block['c'])
            contribution.append(cb)
    return contribution
```

# Tests

The incremental test uses a small Pandoc double to prove that replacing one
file rebuilds same-named blocks in project order, deleting a file removes its
contribution, and a parser failure retains the last valid state.

```python {name=codeblocks__reparse_tests menu=true}
@<imports@>
@<omd_assert@>

class CodeBlock:
    def __init__(self):
        self.name = None
        self.code = ""
        self.origin_file = None
        self.code_blocks = None

    def parse(self, value):
        self.name = value[0][0]
        self.code = value[1]

class FakePandoc:
    fail = False

    @staticmethod
    def convert_file(filename, _output, format=None):
        if FakePandoc.fail:
            raise RuntimeError("bad markdown")
        with open(filename, "r", encoding="utf-8") as source:
            code = source.read()
        return json.dumps({"meta": {}, "blocks": [
            {"t": "CodeBlock", "c": [["shared", [], []], code]}
        ]})

pypandoc = FakePandoc

class CodeBlocks:
    def __init__(self):
        self.code_blocks = []
        self.file_contributions = {}
        self.file_order = []

    def get_code_block(self, name):
        for block in self.code_blocks:
            if block.name == name:
                return block

    @<codeblocks__parse@>

with tempfile.TemporaryDirectory() as directory:
    original = os.getcwd()
    try:
        os.chdir(directory)
        with open("one.o.md", "w", encoding="utf-8") as output:
            output.write("one")
        with open("two.o.md", "w", encoding="utf-8") as output:
            output.write("two")
        blocks = CodeBlocks()
        blocks.parse_file("one.o.md")
        blocks.parse_file("two.o.md")
        blocks.rebuild()
        omd_assert(["one", "two"], blocks.get_code_block("shared").code.splitlines())

        with open("one.o.md", "w", encoding="utf-8") as output:
            output.write("changed")
        blocks.reparse_file("one.o.md")
        omd_assert(["changed", "two"], blocks.get_code_block("shared").code.splitlines())

        FakePandoc.fail = True
        try:
            blocks.reparse_file("one.o.md")
        except RuntimeError:
            pass
        FakePandoc.fail = False
        omd_assert(["changed", "two"], blocks.get_code_block("shared").code.splitlines())

        os.remove("two.o.md")
        blocks.reparse_file("two.o.md")
        omd_assert("changed", blocks.get_code_block("shared").code)
    finally:
        os.chdir(original)

@<test_passed(name="CodeBlocks.reparse")@>
```
