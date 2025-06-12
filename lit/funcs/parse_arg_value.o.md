# Source

This function takes the argument string that remains after an argument name is removed from a ref string, and parses the value. For example, the ref string `@<ref-name(one=1 two=2){asdf}@>`, will yeild the argument list `one=1 two=2`. Next the argument name will be removed and you'll be left with `1 two=2`. If you pass that to `parse_arg_value` it will return `1` for the first return value and the rest of the string for the second return value: ` two=2`. If something goes wrong, `None` is returned in the value return value. Here is the function:

```python {name=parse_arg_value}
def parse_arg_value(txt):
    if txt == "" or txt[0].isspace():
        return None, txt

    value = ""
    quoted = False
    in_ref = 0

    if txt[0] == '"':
        quoted = True
        txt = txt[1:]

    while len(txt) > 0:
        if len(txt) > 1 and txt[0] == "\\" and txt[1] in [o_sym[0], c_sym[0], '"']:
            value += txt[1:2]
            txt = txt[2:]

        if len(txt) >= len(o_sym) and txt[:len(o_sym)] == o_sym:
            in_ref += 1
            value += o_sym
            txt = txt[len(o_sym):]
            continue

        if len(txt) >= len(c_sym) and txt[:len(c_sym)] == c_sym:
            in_ref -= 1
            value += c_sym
            txt = txt[len(c_sym):]
            continue

        if not quoted and in_ref < 1 and txt[0].isspace():
            return value, txt

        if quoted and in_ref < 1 and txt[0] == '"':
            return value, txt[1:]

        value += txt[0]
        txt = txt[1:]

    return value, txt
```

# Testing

Here I swap out the `@<` and `@>` characters for the `:<` and `:>` characters. This drastically simplifies the test code. Otherwise I have to worry about escaping to avoid unwanted code substitutions that will happen during the tangle step.

```python {name=parse_arg_value_tests menu=true}
o_sym = ":<"
c_sym = ":>"

@<omd_assert@>

def test(txt, expected_value, expected_rest):
    value, rest = parse_arg_value(txt)
    if expected_value is not None:
        omd_assert(expected_rest, rest)
    omd_assert(expected_value, value)

@<parse_arg_value@>

test("", None, None)
test("  ", None, None)

test("1 two=2", "1", " two=2")
test("val1", "val1", "")
test("val1 name2=val2", "val1", " name2=val2")
test('"val1 val2" name2=val2', "val1 val2", " name2=val2")
test('"val1 val2"name2=val2', "val1 val2", "name2=val2")
test(':<one:> name2=val2', ":<one:>", " name2=val2")
test(':<one(two="frog toads"):> name2=val2', ':<one(two="frog toads"):>', " name2=val2")
test('":<one(two="frog toads"):> :<three:>" name2=val2', ':<one(two="frog toads"):> :<three:>', " name2=val2")
test("val1\\:< name2=val2", "val1:<", " name2=val2")
test('val1\" name2=val2', 'val1"', " name2=val2")
test('val1\\:> name2=val2', 'val1:>', " name2=val2")

@<test_passed(name="parse_arg_value")@>
```
