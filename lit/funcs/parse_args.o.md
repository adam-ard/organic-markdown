# Source

This function takes the arguments from a reference string and returns all the name/value pairs in a python dict. For example, the ref string `@<ref-name(one=1 two=2){asdf}@>` yeilds a string of argument `one=1 two=2` which gets passed to `parse_args`. `parse_args` returns: `{"one":"1", "two":"2"}`.

This function makes use of [parse_arg_name_value](parse_arg_name_value.o.md).

```python {name=parse_args}
def parse_args(txt):
    args = {}
    while len(txt) > 0:
        name, value, txt = parse_arg_name_value(txt)
        if name == None:
            return {}
        if name == "":
            return args
        args[name] = value
    return args
```

# Testing

Here I swap out the `@<` and `@>` characters for the `:<` and `:>` characters. This drastically simplifies the test code. Otherwise I have to worry about escaping to avoid unwanted code substitutions that will happen during the tangle step.

```python {name=parse_args_tests menu=true}
o_sym = ":<"
c_sym = ":>"

@<omd_assert@>

@<eat_ws@>
@<eat_eq@>
@<parse_arg_name@>
@<parse_arg_value@>
@<parse_arg_name_value@>
@<parse_args@>

def test(txt, expected_args):
    args = parse_args(txt)
    omd_assert(expected_args, args)

test('', {})
test('a1=v1 a2=v2', {"a1": "v1", "a2": "v2"})
test('a1=:<v1:> a2=v2', {"a1": ":<v1:>", "a2": "v2"})
test('a1="v1" a2="v2"', {"a1": "v1", "a2": "v2"})
test('arg1="val1" arg2="val2"', {"arg1": "val1", "arg2": "val2"})
test('arg1="val1" arg2="val2"', {"arg1": "val1", "arg2": "val2"})
test('arg1="val1"   arg2="val2"', {"arg1": "val1", "arg2": "val2"})
test('arg1  =   "val1" arg2  =   "val2"', {"arg1": "val1", "arg2": "val2"})
test('arg1="" arg2=""', {"arg1": "", "arg2": ""})
test('arg1=" " arg2=" "', {"arg1": " ", "arg2": " "})
test('arg1="val one"   arg2="val one"', {"arg1": "val one", "arg2": "val one"})
test('   arg1  =  " val1 "   arg2  =  " val2 "', {"arg1": " val1 ", "arg2": " val2 "})

txt = 'ret_name="parsed_bool" ret="bool value, float one" name="myFunc" args="char *filename, float two"'
test(txt, {"ret_name": "parsed_bool",
            "ret": "bool value, float one",
            "name": "myFunc",
            "args": "char *filename, float two"})


@<test_passed(name="parse_args")@>
```
