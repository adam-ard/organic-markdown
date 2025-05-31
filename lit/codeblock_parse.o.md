# CodeBlock::parse

We use pandoc to parse a markdown file and output json. That json is then translated into python data structures. We iterate through each CodeBlock in the python data and create an object for each one. For example, a markdown code block that looks like this:

``````
```bash {name=test-code-block menu=true}
echo "hello there friend"
```
``````

would be parsed as a json and converted to python data structures that that looks like this:

```python
[['',
  ['bash'],
  [['name', 'test-code-block'],
   ['menu', 'true']
   ]],
 'echo "hello there friend"']
```


Here is the code where we parse the resulting python structure:


```python {name=codeblock__parse}
def parse(self, the_json):
    self.code = the_json[1]
    if len(the_json[0][1]) > 0:
        self.lang = the_json[0][1][0]

    for attrib in the_json[0][2]:
        if attrib[0] == "menu":
            self.in_menu = parse_menu_attrib(attrib[1])
        elif attrib[0] == "name":
            self.name = attrib[1]
        elif attrib[0] == "dir":
            self.cwd = attrib[1]
        elif attrib[0] == "tangle":
            self.tangle_file = attrib[1]
        elif attrib[0] == "docker":
            self.docker_container = attrib[1]
        elif attrib[0] == "ssh":
            self.ssh_host = attrib[1]
        else:
            print(f"Warning: I don't know what attribute this is {attrib[0]}")
```

## CodeBlock::parse tests

```python {tangle=tests/codeblock__parse.py}
#!/usr/bin/env python3

def parse_menu_attrib(val):
    return val

class CodeBlockFake:
    def __init__(self):
        self.code = ""
        self.lang = ""
        self.in_menu = ""
        self.name = ""
        self.cwd = ""
        self.tangle_file = ""
        self.docker_container = ""
        self.ssh_host = ""
    def test_fields(self, code, lang, menu, name, dir, tangle_file, docker_container, ssh_host):
        assert self.code == code
        assert self.lang == lang
        assert self.in_menu == menu
        assert self.name == name
        assert self.cwd == dir
        assert self.tangle_file == tangle_file
        assert self.docker_container == docker_container
        assert self.ssh_host == ssh_host
    @<codeblock__parse@>

cb = CodeBlockFake()
cb.parse([['', [], []], ""])

cb.test_fields("", "", "", "", "", "", "", "")

cb = CodeBlockFake()
cb.parse([['',
  ['bash'],
  [['name', 'test-code-block'],
   ['menu', 'true']
  ]],
 'echo "hello there friend"'])

cb.test_fields('echo "hello there friend"', "bash", "true", "test-code-block", "", "", "", "")

cb = CodeBlockFake()
cb.parse([['',
  ['bash'],
  [['name', 'test-code-block'],
   ['menu', True]
  ]],
 'echo "hello there friend"'])

cb.test_fields('echo "hello there friend"', "bash", True, "test-code-block", "", "", "", "")

cb = CodeBlockFake()
cb.parse([["",
  ["python"],
  [["name", "build_project"],
   ["docker", "@<docker_container_name@>"],
   ["ssh", "aard@localhost.com"],
   ["menu", "true"],
   ["dir", "@<project_name@>"],
   ["tangle", "@<project_name@>/main.c"]
  ]],
 "gcc --version"])

cb.test_fields("gcc --version", "python", "true", "build_project", "@<project_name@>", "@<project_name@>/main.c", "@<docker_container_name@>", "aard@localhost.com")

@<test_passed(name="codeblock__parse")@>
```

To run test from `omd run <name>`:

```bash {name=codeblock__parse_tests menu=true}
tests/codeblock__parse.py
```
