# Functions

All the function definitions. This file will shrink and eventually disappear as I explain each function individually in the documentation.

```python {name=funcs}
@<get_max_lines@>
@<write_if_different@>
@<parse_menu_attrib@>
@<intersperse@>
@<split_lines@>
# returns match (or None if there isn't one) and whether or not it is
#  string replacement or results of a string execution replacement. It
#  will return matches in a left to right order
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
@<parse_name@>
@<parse_exec@>
@<parse_args_str@>
@<parse_default@>
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
@<eat_ws@>
@<eat_eq@>
@<parse_arg_name@>
@<parse_arg_value@>
@<parse_arg_name_value@>
@<parse_args@>
@<escape_code@>
@<import_file@>
```

