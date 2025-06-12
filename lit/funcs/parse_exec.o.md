# Source 

This function is used to determine if the name has an exec annotation. Meaning that when the ref is expanded it will be replaced with the result of running the text it represents in the language it is annotated to be. The exec annotation is add by placing a `*` directly after the name. For example, the reference `@<say_hello*@>` will be expanded to `Hello There` for the code block:

``````
```bash {name=say_hello}
echo "Hello There"
```
``````

Here is the code to check for the exec annotation. It takes the text for the name that has been parsed and checks for the `*` character at the end. I returns three values: the name of the ref without the annotation, a True/False value indicating whether the exec annotation was present, and a True/False value indicating the presence (or absense) of an error in the parsing syntax.

```python {name=parse_exec}
def parse_exec(txt):
    if len(txt) == 0:
        print(f'name has zero length')
        return "", False, False

    if txt[-1:] == "*":
        if len(txt) == 1:
            print(f'name has zero length')
            return "", False, False

        return txt[:-1], True, True

    return txt, False, True
```

# Testing

```python {name=parse_exec_tests menu=true}
@<omd_assert@>

def test(txt, expected_name, expected_exec, expected_success):
    name, exec, success = parse_exec(txt)
    if expected_success:
        omd_assert(expected_name, name)
        omd_assert(expected_exec, exec)
    omd_assert(expected_success, success)

@<parse_exec@>

test("", None, None, False)
test("*", None, None, False)
test("one", "one", False, True)
test("one*", "one", True, True)
test("a*", "a", True, True)

@<test_passed(name="parse_exec")@>
```
