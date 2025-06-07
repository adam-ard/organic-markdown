# Source

This function takes a reference string's arguments and return the name of the first argument. For example, the ref string `@<ref-name(one=1 two=2){asdf}@>`, when the arguments are extracted `one=1 two=2` and passed to `parse_arg_name` will yield two return values: the name for the first argument `one`, and the rest of the string `=1 two=2`.

If something goes wrong, `None` is returned in the name return value. Here is the function:

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
test("one=1 two=2", "one", "=1 two=2")
test("name=value", "name", "=value")
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
