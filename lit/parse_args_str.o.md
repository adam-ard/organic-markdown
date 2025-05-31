# Source

This function is used to parse out the string that contains all the arguments from a reference string. For example, the ref string `@<ref-name(one=1 two=2){asdf}@>` would first get parsed for the name and pass the rest of the string `(one=1 two=2){asdf}` to `parse_args_str`. `parse_args_str` would return `one=1 two=2` and the rest of the string as the second return value: `{asdf}`.

Here is the code used to parse out the args. If there is an error in the parsing, `None` is returned for the args return value.

```python {name=parse_args_str}
def parse_args_str(txt):
    args = ""
    if len(txt) == 0:
        return args, txt

    if txt[0] == '{':
        return args, txt

    if txt[0] != '(':
        print(f'Bad char: {txt[0]} while parsing args from: "{txt}"')
        return None, txt

    txt = txt[1:]    # eat the opening paren
    open_count = 1
    while len(txt) > 0:
        if txt[0] == '(':
            open_count += 1
        elif txt[0] == ')':
            open_count -= 1

        if open_count < 1:
            return args, txt[1:]

        args += txt[0]
        txt = txt[1:]

    return None, False
```

# Testing

```python {tangle=tests/parse_args_str.py}
#!/usr/bin/env python3

@<omd_assert@>

def test(txt, expected_args, expected_rest):
    args, rest = parse_args_str(txt)
    if expected_args is not None:
        omd_assert(expected_rest, rest)
    omd_assert(expected_args, args)

@<parse_args_str@>

test("", "", "")
test("(one=1 two=2){asdf}", "one=1 two=2", "{asdf}")
test("{}", "", "{}")
test("aa", None, None)
test("()", "", "")
test("(a=5 b=6)", "a=5 b=6", "")
test("(a=5 b=6)asdf", "a=5 b=6", "asdf")
test('(a="5" b="6")', 'a="5" b="6"', "")
test("(asdf", None, None)
test("(a=5 b=@<six@>)", "a=5 b=@<six@>", "")
test("(((())))", "((()))", "")

@<test_passed(name="parse_args_str")@>
```

# Run Tests

```bash {name=parse_args_str_tests menu=true}
tests/parse_args_str.py
```
