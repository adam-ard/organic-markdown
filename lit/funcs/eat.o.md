# Eat functions

Below are a couple function that are used in parsing. They are used to discard delimiting characters (whitespace and `=`).


```python {name=eat_ws}
def eat_ws(txt):
    return txt.lstrip()
```

```python {name=eat_eq}
def eat_eq(txt):
    if len(txt) == 0:
        return None

    if txt[0] == "=":
        return txt[1:]
    return None
```

## Tests

```python {name=eat_tests_file tangle=tests/eat_tests.py}
#!/usr/bin/env python3

@<omd_assert@>

@<eat_ws@>
@<eat_eq@>

# eat whitespace tests
txt = "    asdf"
expected = "asdf"

omd_assert(expected, eat_ws(txt))

txt = "    "
expected = ""

omd_assert(expected, eat_ws(txt))

txt = "   \t   "
expected = ""

omd_assert(expected, eat_ws(txt))

txt = "   \n\t   asdf"
expected = "asdf"

omd_assert(expected, eat_ws(txt))

# eat eq tests

txt = "=asdf"
expected = "asdf"

omd_assert(expected, eat_eq(txt))

txt = "=\""
expected = "\""

omd_assert(expected, eat_eq(txt))

txt = ""
expected = None

omd_assert(expected, eat_eq(txt))

txt = " = "
expected = None

omd_assert(expected, eat_eq(txt))

txt = "asdf"
expected = None

omd_assert(expected, eat_eq(txt))

@<test_passed(name="eat")@>
```

```bash {name=eat_tests menu=true}
tests/eat_tests.py
```
