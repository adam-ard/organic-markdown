# CodeBlock::parse

We use pandoc to parse a markdown file and output json. That json is then translated into python data structures. For example, a markdown file that looks like this:

``````
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

would be parsed into json and converted to python data structures that that looks like this:

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

Here is the code where we traverse the current directory and any subdirectories recursively, to find all markdown file. Each markdown file is parsed with pandoc.

```python {name=codeblocks__parse}
def parse(self):
    # read all file in the curren directory (recursively) with .o.md extenstion
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

                # append the code block contents if the name is the same
                # Note: the yaml parser only uses the last value for any given name, so you utilize more than
                # one entry with the same name.
                self.add_code_block(cb)

    for block in data['blocks']:
        if block['t'] == "CodeBlock":
            cb = CodeBlock()
            cb.origin_file = origin_file
            cb.parse(block['c'])
            cb.code_blocks = self

            # append the code block contents if the name is the same
            self.add_code_block(cb)
```
