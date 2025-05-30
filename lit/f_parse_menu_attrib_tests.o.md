# parse_menu_attrib tests

Test that the [parse_menu_attrib](f_parse_menu_attrib.o.md) function returns true/false correctly based on the input.

```python {tangle=tests/f_parse_menu_attrib.py}
#!/usr/bin/env python3

@<parse_menu_attrib@>

for val in [True, "true", "True", "asdf", "1", 1]:
    if parse_menu_attrib(val) != True:
        @<test_failed(name="parse_menu_attrib" msg="parse_menu_attrib should have returned True")@>

for val in [False, "False", "false", "0", 0, "", None, "nil", "Nil", "null", "Null", "None"]:
    if parse_menu_attrib(val) != False:
        @<test_failed(name="parse_menu_attrib" msg="parse_menu_attrib should have returned False")@>

@<test_passed(name="parse_menu_attrib")@>
```

# Run Tests

```bash {name=f_parse_menu_attrib_tests menu=true}
tests/f_parse_menu_attrib.py
```


[source code](f_parse_menu_attrib.o.md)
