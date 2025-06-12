# Source

`get_match` returns the next match (or None if there isn't one) and whether or not it's a string execution replacement. It will return matches in a left to right order.


```python {name=get_match}
def get_match(txt):
    cur = 0
    while cur < len(txt):
        res, cur = get_match_inner(txt, cur)
        if res is not None:
            return res
    return None

def get_match_inner(txt, cur):
    open_count = 0
    start = -1

    while cur < len(txt):
        if cur + len(o_sym) <= len(txt) and txt[cur : cur + len(o_sym)] == o_sym:
            if start == -1:
                start = cur
            open_count += 1
            cur += len(o_sym) - 1

        elif cur + len(c_sym) <= len(txt) and txt[cur:cur+len(c_sym)] == c_sym:
            if start != -1:
                open_count -= 1
            cur += len(c_sym) - 1

        if open_count < 1 and start != -1:
            match = parse_match(txt[start + len(o_sym) : cur - 1])
            if match is None:
                print(f"content internal to {o_sym} and {c_sym} is invalid: {txt[start:cur + len(c_sym) - 1]}")
                return None, start + len(o_sym)
            return match | {"full": txt[start:cur + len(c_sym) - 1],
                            "start": start,
                            "end": cur + len(c_sym) - 1}, start + len(o_sym)
        cur += 1

    if start == -1:
        return None, len(txt)

    return None, start + len(o_sym)
```

# Testing

Here I swap out the `@<` and `@>` characters for the `:<` and `:>` characters. This drastically simplifies the test code. Otherwise I have to worry about escaping to avoid unwanted code substitutions that will happen during the tangle step.

```python {name=get_match_tests menu=true}
o_sym = ":<"
c_sym = ":>"

@<omd_assert@>

@<parse_name@>
@<parse_exec@>
@<parse_args_str@>
@<parse_default@>
@<parse_match@>
@<get_match@>

def test_error(txt):
    match = get_match(txt)
    omd_assert(None, match)

def test(txt, start, full, name, exec, args, default):
    match = get_match(txt)
    omd_assert({"start": start,
                "end": start + len(full),
                "full": full,
                "name": name,
                "exec": exec,
                "args": args,
                "default": default}, match)

def test_one(txt, start, name, exec, args, default):
    match = get_match(txt)
    omd_assert({"start": start,
                "end": start + len(txt),
                "full": txt,
                "name": name,
                "exec": exec,
                "args": args,
                "default": default}, match)

test_error("asdf:<one()>asdf")
test_error('')
test_error(':<one()[]:>'),
test_error(':<one()(:>')
test_error(':<one(){:>')
test_error(':<one)(:>')
test_error(':<one(:>')

test(":<one:>asdf:<two:>", 0, ":<one:>", "one", False, "", "")
test("asdf:<one:>asdf", 4, ":<one:>", "one", False, "", "")
test(":<one*:>asdf:<two*:>", 0, ":<one*:>", "one", True, "", "")
test("asdf:<one*:>asdf", 4, ":<one*:>", "one", True, "", "")
test("asdf:<asdf() asdf() asdf:>asdf:<asdf:>asdf", 30, ":<asdf:>", "asdf", False, "", "")

test_one(':<one:>', 0, 'one', False, '', '')
test_one(':<one:>', 0, 'one', False, '', '')
test_one(':<one*:>', 0, 'one', True, '', '')
test_one(':<one(arg1="val1"):>', 0, 'one', False, 'arg1="val1"', '')
test_one(':<one*(arg1="val1"):>', 0, 'one', True, 'arg1="val1"', '')
test_one(':<one(){1}:>', 0, 'one', False, '', '1')
test_one(':<one*(){1}:>', 0, 'one', True, '', '1')
test_one(':<one*(){lots of stuff}:>', 0, 'one', True, '', 'lots of stuff')
test_one(':<one*(){:<two(){5}:>}:>', 0, 'one', True, '', ':<two(){5}:>')
test_one(':<one*(two=":<two(){5}:>"):>', 0, 'one', True, 'two=":<two(){5}:>"', '')
test_one(':<two_sentences(one=":<three_lines:>"):>', 0, 'two_sentences', False, 'one=":<three_lines:>"', '')
test_one(':<one*(two=":<three*:>"):>', 0, 'one', True, 'two=":<three*:>"', '')

@<test_passed(name="get_match")@>
```

