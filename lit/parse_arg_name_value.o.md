# Source

This function takes the arguments from a reference string and returns the first name/value pair, and the rest of the string. For example, the ref string `@<ref-name(one=1 two=2){asdf}@>` yeilds a string of argument `one=1 two=2` which gets passed to `parse_arg_name_value`. `parse_arg_name_value` returns three arguments: first arg name `one`, first arg value `1`, and the rest of the string ` two=2`. I something goes wrong, `None` will be returned as the first return value.

This function makes use of [parse_arg_name](parse_arg_name.o.md), [parse_arg_value](parse_arg_value.o.md), [eat_ws](parse_eat.o.md), and [eat_eq](parse_eat.o.md).

```python {name=parse_arg_name_value}
def parse_arg_name_value(txt):
    txt = eat_ws(txt)
    if txt == "":
        return "", "", ""

    name, txt = parse_arg_name(txt)
    if name == None:
        return None, None, ""

    txt = eat_ws(txt)
    txt = eat_eq(txt)
    if txt == None:
        return None, None, ""

    txt = eat_ws(txt)
    value, txt = parse_arg_value(txt)
    if value == None:
        return None, None, ""

    return name, value, txt
```

# Testing

Here I swap out the `@<` and `@>` characters for the `:<` and `:>` characters. This drastically simplifies the test code. Otherwise I have to worry about escaping to avoid unwanted code substitutions that will happen during the tangle step.

```python {tangle=tests/parse_arg_name_value.py}
#!/usr/bin/env python3

o_sym = ":<"
c_sym = ":>"

@<omd_assert@>

def test(txt, expected_name, expected_value, expected_rest):
    name, value, rest = parse_arg_name_value(txt)
    if expected_name is not None:
        omd_assert(expected_value, value)
        omd_assert(expected_rest, rest)
    omd_assert(expected_name, name)

@<eat_ws@>
@<eat_eq@>
@<parse_arg_name@>
@<parse_arg_value@>
@<parse_arg_name_value@>

test("", "", "", "")
test("name=val1", "name", "val1", "")
test("name=val1 name2=asdf", "name", "val1", " name2=asdf")
test("name = val1", "name", "val1", "")
test("name \t = \t val1", "name", "val1", "")
test('name = "val1 val2"', "name", "val1 val2", "")
test('name = ":<one(two = "blah blah"):> :<three:>" name2=asdf', "name", ':<one(two = "blah blah"):> :<three:>', " name2=asdf")

@<test_passed(name="parse_arg_name_value")@>
```

# Run Tests

```bash {name=parse_arg_name_value_tests menu=true}
tests/parse_arg_name_value.py
```
