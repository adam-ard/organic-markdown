# Function: parse_menu_attrib

To determine in a code_block should appear in the menu the displays when you run `omd status`, omd checks for the `menu` fenced code block attribute:

``````
```{name=say-hello menu=true}
echo "Hello"
```
``````

When the menu attribute is found (see the parse function), then this function gets call with the attribute value as an argument. When the value is true, or has a string value that is not something that seems false-like, then the following function will return true (otherwise false).

function body:

### @<parse_menu_attrib@>

```python {name=parse_menu_attrib}
def parse_menu_attrib(val):
    return str(val).lower() not in ["false", "0", "", "nil", "null", "none"]
```


# Tests

Test that the [parse_menu_attrib](f_parse_menu_attrib.o.md) function returns true/false correctly based on the input.

```python {name=f_parse_menu_attrib_tests menu=true}
@<omd_assert@>
@<parse_menu_attrib@>

for val in [True, "true", "True", "asdf", "1", 1]:
    omd_assert(True, parse_menu_attrib(val))

for val in [False, "False", "false", "0", 0, "", None, "nil", "Nil", "null", "Null", "None"]:
    omd_assert(False, parse_menu_attrib(val))

@<test_passed(name="parse_menu_attrib")@>
```
