# `CodeBlock::parse`

This function takes the Pandoc-generated JSON representation of a code block and extracts its metadata and content into the corresponding `CodeBlock` object.

Pandoc converts a code block like this:

````markdown
```bash {name=test-code-block menu=true}
echo "hello there friend"
```
````

Into a JSON structure that, once parsed into Python data, looks something like this:

```python
[['',
  ['bash'],
  [['name', 'test-code-block'],
   ['menu', 'true']
  ]],
 'echo "hello there friend"']
```

Here's how we extract and store that data:

---

### 🔗 `@<codeblock__parse@>`

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

This parser is intentionally flexible. It gracefully handles unexpected attributes with a warning instead of crashing.

---

## ✅ Tests for `CodeBlock::parse`

Here’s a test file that verifies parsing logic across various input scenarios:

```python {name=codeblock__parse_tests menu=true}
@<omd_assert@>

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
        omd_assert(code, self.code)
        omd_assert(lang, self.lang)
        omd_assert(menu, self.in_menu)
        omd_assert(name, self.name)
        omd_assert(dir, self.cwd)
        omd_assert(tangle_file, self.tangle_file)
        omd_assert(docker_container, self.docker_container)
        omd_assert(ssh_host, self.ssh_host)

    @<codeblock__parse@>

# No attributes
cb = CodeBlockFake()
cb.parse([['', [], []], ""])
cb.test_fields("", "", "", "", "", "", "", "")

# Name and menu
cb = CodeBlockFake()
cb.parse([['',
  ['bash'],
  [['name', 'test-code-block'],
   ['menu', 'true']
  ]],
 'echo "hello there friend"'])
cb.test_fields('echo "hello there friend"', "bash", "true", "test-code-block", "", "", "", "")

# Menu as boolean
cb = CodeBlockFake()
cb.parse([['',
  ['bash'],
  [['name', 'test-code-block'],
   ['menu', True]
  ]],
 'echo "hello there friend"'])
cb.test_fields('echo "hello there friend"', "bash", True, "test-code-block", "", "", "", "")

# All fields
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
