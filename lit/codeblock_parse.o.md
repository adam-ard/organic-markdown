# CodeBlock::parse

```python {name=codeblock__parse}
def parse(self, the_json):
    self.code = the_json[1]
    if self.code is not None and len(self.code) > 0:
        self.code = self.code.replace(o_sym + "br" + c_sym, "\n")

    for attrib in the_json[0][1]:
        if attrib in languages:
            self.lang = attrib

    for attrib in the_json[0][2]:
        if attrib[0] == "menu":
            self.in_menu = parse_menu_attrib(attrib[1])
        elif attrib[0] == "lang":
            self.lang = attrib[1]
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
