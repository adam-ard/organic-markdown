# Source

This function takes a reference string, after the name and args have be removed and checks if there is a default value. For example, the ref string `@<ref-name(one=1 two=2){asdf}@>`, after parsing the name and arguments is `{asdf}`. If you pass that to `parse_default`, it will return the default value `asdf` and the rest of the string which will be empty. I something goes wrong, None will be returned as the first return value.

```python {name=parse_default}
def parse_default(txt):
    if len(txt) == 0:
        return "", txt

    if txt[0] != "{":
        print(f'Bad char: {txt[0]} while parsing default from: "{txt}"')
        return None, txt

    open_count = 1
    default = ""
    o_txt = txt
    txt = txt[1:]
    while len(txt) > 0:
        if txt[0] == '{':
            open_count += 1
        elif txt[0] == '}':
            open_count -= 1

        if open_count < 1:
            return default, txt[1:]

        default += txt[0]
        txt = txt[1:]

    print(f'End of string before getting a "}}" char: "{o_txt}"')
    return None, txt
```

# Testing

Here I swap out the `@<` and `@>` characters for the `:<` and `:>` characters. This drastically simplifies the test code. Otherwise I have to worry about escaping to avoid unwanted code substitutions that will happen during the tangle step.

```python {name=parse_default_tests_file tangle=tests/parse_default.py}
#!/usr/bin/env python3

o_sym = ":<"
c_sym = ":>"

@<omd_assert@>

def test(txt, expected_default, expected_rest):
    default, rest = parse_default(txt)
    if expected_default is not None:
        omd_assert(expected_rest, rest)
    omd_assert(expected_default, default)

@<parse_default@>

test("", "", "")
test("{asdf}", "asdf", "")
test("()", None, None)
test("aa", None, None)
test("{}", "", "")
test("{a}", "a", "")
test("{:<a:>}", ":<a:>", "")
test("{aasfd", None, None)
test("{:<a{5}:>}", ":<a{5}:>", "")
test("{{{{{{}}}}}}", "{{{{{}}}}}", "")

@<test_passed(name="parse_default")@>
```

# Run Tests

```bash {name=parse_default_tests menu=true}
tests/parse_default.py
```
