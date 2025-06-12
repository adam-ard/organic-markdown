# Source

The `parse_match` function parses a ref string into its separate parts. For example, the ref string `@<ref-name*(one=1 two=2){asdf}@>`, when passed to the function, would yeild: `{"name": "ref-name", "exec": True, "args": "one=1 two=2", "default": "asdf"}`. If there are any problems parsing the parts of a match, `None` is returned instead a dict.

```python {name=parse_match}
def parse_match(txt):
    o_txt = txt
    name, txt = parse_name(txt)
    if name is None:
        print(f'Error parsing name from: "{o_txt}"')
        return None

    name, exec, success = parse_exec(name)
    if success == False:
        print(f'Error parsing exec from: "{name}"')
        return None

    args, txt = parse_args_str(txt)
    if args == None:
        print(f'Error parsing args from: "{o_txt}"')
        return None

    default, txt = parse_default(txt)
    if default == None:
        print(f'Error parsing default from: "{o_txt}"')
        return None

    return {"name": name,
            "exec": exec,
            "args": args,
            "default": default.strip('"')}
```

# Testing

Here I swap out the `@<` and `@>` characters for the `:<` and `:>` characters. This drastically simplifies the test code. Otherwise I have to worry about escaping to avoid unwanted code substitutions that will happen during the tangle step.

```python {name=parse_match_tests menu=true}
o_sym = ":<"
c_sym = ":>"

@<omd_assert@>

@<parse_name@>
@<parse_exec@>
@<parse_args_str@>
@<parse_default@>
@<parse_match@>

def test(txt, expected_args):
    args = parse_match(txt)
    omd_assert(expected_args, args)

test('', None)
test('one(', None)
test('one)(', None)
test('one()(', None)
test("one", {"name": "one", "exec": False, "args":"", "default": ""})
test('one(){}', {"name": "one", "exec": False, "args":"", "default": ""})
test("one*(){}", {"name": 'one', "exec": True, "args": "", "default": ""})
test('one(){1}', {"name": 'one', "exec": False, "args": '', "default": "1"})
test("one*(){1}", {"name": 'one', "exec": True, "args": '', "default": "1"})
test('one(){"1"}', {"name": 'one', "exec": False, "args": '', "default": '1'})
test("one*(){lots of stuff}", {"name": 'one', "exec": True, "args": '', "default": "lots of stuff"})
test("one*(a=5 b=6){lots of stuff}", {"name": 'one', "exec": True, "args": 'a=5 b=6', "default": "lots of stuff"})
test('one(){:<two(){5}:>}', {"name": 'one', "exec": False, "args": '', "default": ":<two(){5}:>"})
test('one(two=":<two(){5}:>")', {"name": 'one', "exec": False, "args": 'two=":<two(){5}:>"', "default": ""})
test('two_sentences(one=":<three_lines:>")', {"name": 'two_sentences', "exec": False, "args": 'one=":<three_lines:>"', "default": ""})
test('two_sentences*(one=":<three_lines:>")', {"name": 'two_sentences', "exec": True, "args": 'one=":<three_lines:>"', "default": ""})
test('one(arg1="val1")', {"name": 'one', "exec": False, "args": 'arg1="val1"', "default": ""})
test("one()", {"name": 'one', "exec": False, "args": '', "default": ""})
test("one", {"name": 'one', "exec": False, "args": '', "default": ""})
test("one*", {"name": 'one', "exec": True, "args": '', "default": ""})
test("one*()", {"name": 'one', "exec": True, "args": '', "default": ""})
test('one*(two=":<three*:>")', {"name": 'one', "exec": True, "args": 'two=":<three*:>"', "default": ""})
test('one*(arg1="val1")', {"name": 'one', "exec": True, "args": 'arg1="val1"', "default": ""})


@<test_passed(name="parse_match")@>
```
