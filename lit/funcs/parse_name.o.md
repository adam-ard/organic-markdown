# Source

The follow function is used to parse the name of a ref (`@<name(arg=1 arg2=2){asdf}@>`). It returns two arguments: the name and the rest of the ref string.

```python {name=parse_name}
def parse_name(txt):
    o_txt = txt
    name = ""
    while len(txt) > 0:
        if len(txt) > 1 and txt[0] == "\\" and txt[1] in ['(', '{']:
            name += txt[:2]
            txt = txt[2:]
            continue

        if txt[0] in ['(', '{']:
            break

        name += txt[0]
        txt = txt[1:]
    return name, txt
```

# Tests

```python {name=parse_name_tests_file tangle=tests/parse_name.py}
#!/usr/bin/env python3

@<omd_assert@>

def test(txt, expected_name, expected_rest):
    name, rest = parse_name(txt)
    omd_assert(expected_name, name)
    omd_assert(expected_rest, rest)

@<parse_name@>

test("one", "one", "")
test("one'", "one'", "")
test("one*", "one*", "")
test("one_two", "one_two", "")
test("one_two(){}", "one_two", "(){}")
test("one_two()", "one_two", "()")
test("one_two{}", "one_two", "{}")
test("one_two)", "one_two)", "")
test("one_two}", "one_two}", "")
test("one}_two", "one}_two", "")
test("one<_two", "one<_two", "")
test("one>_two", "one>_two", "")
test("one=_two", "one=_two", "")
test('one"_two', 'one"_two', "")
test('one two', 'one two', "")
test('one\\()()', 'one\\()', "()")
test('one\\{}()', 'one\\{}', "()")

@<test_passed(name="parse_name")@>
```

# Run Tests

```bash {name=parse_name_tests menu=true}
tests/parse_name.py
```
