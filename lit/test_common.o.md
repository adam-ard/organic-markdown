# Common Tests Code

Each test is a single python file. They use the literate references to import code NOT the import statement. This makes is easy to mock anything you would like. Below are a couple functions that are helpful to use in tests. They are also used through literate reference instead of import. I could do this with an import if I wanted to though.

### @<test_passed@>

```python {name=test_passed}
print("        PASSED: @<name@>!!")
exit(0)
```

```python {name=omd_assert}
import re

def omd_assert(expected, got):
    if expected != got:
        print(f"        FAIL: Expected '{expected}', Got '{got}'")
        exit(1)

def omd_assert_regex(expected_regex, got):
    res = re.search(expected_regex, got)
    if not res:
        print(f"        FAIL: Expected '{expected_regex}', Got '{got}'")
        exit(1)

```
