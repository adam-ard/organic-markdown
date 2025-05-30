# Source

This function is used to parse out the string that container all the arguments from the reference definition. For example, the args string of this code block:

``````
```bash {name=say_hello menu=true}
echo "Hello There"
```
``````

would be `name=say_hello menu=true`. Here is the code used to parse out the args. It returns the string representing the arguments and the remaining text in the ref (to be further parsed). If there is an error in the parsing, `None` is returned for the args return value.

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
