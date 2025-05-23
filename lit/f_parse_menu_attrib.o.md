# Function: parse_menu_attrib

To determine in a code_block should appear in the menu the displays when you run `omd status`, omd checks for the `menu` fenced code block attribute:

``````
```{name=say-hello menu=true}
echo "Hello"
```
``````

When the menu attribute is found (see the parse function), then this function gets call with the attribute value as an argument. When the value is true, or has a string value that is not something that seems false-like, then the following function will return true (otherwise false).


Add the function to `@<funcs@>`

### @<funcs@>

```python {name=funcs}
@<parse_menu_attrib@>
```

function body:

### @<parse_menu_attrib@>

```python {name=parse_menu_attrib}
def parse_menu_attrib(val):
    if val is None:
        return False

    return str(val).lower() not in ["false", "0", "", "nil", "null", "none"]
```

[test code](f_parse_menu_attrib_tests.o.md)
