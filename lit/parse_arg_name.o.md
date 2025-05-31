# Source

This function takes the argument string, and returns the first argument's name. For example, a block like this:

``````
```bash {name=say_hello menu=true}
echo "Hello There"
```
``````

would yield an argument string: `name=say_hello menu=true`. This string would be passed to `parse_arg_name` which would return `name`. It will also return the remaining text after the name it retreived. In this case: `=say_hello menu=true`. If something goes wrong, `None` is returned in the name return value. Here is the function:

```python {name=parse_arg_name}
def parse_arg_name(txt):
    if txt == "" or txt[0].isspace():
        return None, txt

    name = ""
    while len(txt) > 0:
        if txt[0].isspace() or txt[0] == "=":
            return name, txt

        name += txt[0]
        txt = txt[1:]

    return name, txt
```

# Testing

```python {tangle=tests/parse_arg_name.py}
#!/usr/bin/env python3

@<omd_assert@>

def test(txt, expected_name, expected_rest):
    name, rest = parse_arg_name(txt)
    if expected_name is not None:
        omd_assert(expected_rest, rest)
    omd_assert(expected_name, name)

@<parse_arg_name@>

test("", None, None)
test("name=value", "name", "=value")
test("name=say_hello menu=true", "name", "=say_hello menu=true")
test("name   ", "name", "   ")
test("  stuff", None, None)
test("name1=value1", "name1", "=value1")
test("name1 = value1", "name1", " = value1")
test("name1 \t = value1", "name1", " \t = value1")

@<test_passed(name="parse_arg_name")@>
```

# Run Tests

```bash {name=parse_arg_name_tests menu=true}
tests/parse_arg_name.py
```
