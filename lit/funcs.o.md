# Functions

All the function definitions. This file will shrink and eventually disappear as I explain each function individually in the documentation.

```python {name=funcs}
# do this so that the timestamp doesn't change on all files, even when they don't change
#   make assumes that it needs to rebuild when that happens
def write_if_different(file_path, new_content):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            current_content = file.read()

        if current_content.rstrip('\n') == new_content:
            return

    with open(file_path, 'w') as file:
        file.write(new_content)
        file.write("\n")  # put a newline at the end of the file
        file.close()

def split_lines_line_cont_char(txt):
    new_lines = [""]
    lines = txt.split('\n')

    j = 0
    for i, line in enumerate(lines):
        if len(line) > 0 and line[-1:] == "\\":
            new_lines[j] += line[:-1]
        else:
            new_lines[j] += line
            if i < len(lines) - 1:  # don't add if it is the last one
                new_lines.append("")
                j+=1

    return new_lines

def split_lines(txt):
    new_lines = []

    ref_num = 0
    length = len(txt)
    i = 0
    start = 0
    while i < length:
        if txt[i] == "\n" and ref_num == 0:   # need a newline
            new_lines.append(txt[start:i])
            start=i+1
        if txt[i : i + 2] == o_sym:
            ref_num += 1
            i += len(o_sym) - 1
        if txt[i : i + 2] == c_sym:
            ref_num -= 1
            i += len(c_sym) - 1
        i += 1

    new_lines.append(txt[start:i])
    return new_lines

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

def parse_name(txt):
    o_txt = txt
    name = ""
    while len(txt) > 0:
        if len(txt) > 1 and txt[0] == "\\" and txt[1] in ['(', '{']:
            name += txt[:2]
            txt = txt[2:]
            continue

        if txt[0] in ['(', '{']:
            break

        name += txt[0]
        txt = txt[1:]
    return name, txt

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

def parse_args_str(txt):
    args = ""
    if len(txt) == 0:
        return args, txt

    if txt[0] == '{':
        return args, txt

    if txt[0] != '(':
        print(f'Bad char: {txt[0]} while parsing args from: "{txt}"')
        return None, txt

    txt = txt[1:]    # eat the opening paren
    open_count = 1
    while len(txt) > 0:
        if txt[0] == '(':
            open_count += 1
        elif txt[0] == ')':
            open_count -= 1

        if open_count < 1:
            return args, txt[1:]

        args += txt[0]
        txt = txt[1:]

    return None, False

def parse_default(txt):
    if len(txt) == 0:
        return "", txt

    if txt[0] != "{":
        print(f'Bad char: {txt[0]} while parsing default from: "{txt}"')
        return None, txt

    open_count = 1
    default = ""
    o_txt = txt
    txt = txt[1:]
    while len(txt) > 0:
        if txt[0] == '{':
            open_count += 1
        elif txt[0] == '}':
            open_count -= 1

        if open_count < 1:
            return default, txt[1:]

        default += txt[0]
        txt = txt[1:]

    print(f'End of string before getting a "}}" char: "{o_txt}"')
    return None, txt

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

def eat_ws(txt):
    return txt.lstrip()

def eat_eq(txt):
    if len(txt) == 0:
        return None

    if txt[0] == "=":
        return txt[1:]
    return None

def parse_arg_name(txt):
    if txt == "" or txt[0].isspace():
        return None, txt

    name = ""
    while len(txt) > 0:
        if txt[0].isspace() or txt[0] == "=":
            return name, txt

        name += txt[0]
        txt = txt[1:]

    return name, txt

def parse_arg_value(txt):
    if txt == "" or txt[0].isspace():
        return None, txt

    value = ""
    quoted = False
    in_ref = 0

    if txt[0] == '"':
        quoted = True
        txt = txt[1:]

    while len(txt) > 0:
        if len(txt) > 1 and txt[0] == "\\" and txt[1] in [o_sym[0], c_sym[0], '"']:
            value += txt[1:2]
            txt = txt[2:]

        if len(txt) >= len(o_sym) and txt[:len(o_sym)] == o_sym:
            in_ref += 1
            value += o_sym
            txt = txt[len(o_sym):]
            continue

        if len(txt) >= len(c_sym) and txt[:len(c_sym)] == c_sym:
            in_ref -= 1
            value += c_sym
            txt = txt[len(c_sym):]
            continue

        if not quoted and in_ref < 1 and txt[0].isspace():
            return value, txt

        if quoted and in_ref < 1 and txt[0] == '"':
            return value, txt[1:]

        value += txt[0]
        txt = txt[1:]

    return value, txt

def parse_arg_name_value(txt):
    txt = eat_ws(txt)
    if txt == "":
        return "", "", ""

    name, txt = parse_arg_name(txt)
    if name == None:
        return None, None, ""

    txt = eat_ws(txt)
    txt = eat_eq(txt)
    if txt == None:
        return None, None, ""

    txt = eat_ws(txt)
    value, txt = parse_arg_value(txt)
    if value == None:
        return None, None, ""

    return name, value, txt

# TODO return None for errors
def parse_args(txt):
    args = {}
    while len(txt) > 0:
        name, value, txt = parse_arg_name_value(txt)
        if name == None:
            return {}   # TODO switch this to error
        if name == "":
            return args
        args[name] = value
    return args

def parse_menu_attrib(val):
    if isinstance(val, bool):
        return val

    if isinstance(val, str):
        return val.lower() != "false" and val != "0" and val != ""

    return str(val).lower() != "false" and str(val) != "0" and val is not None
```

[classes](classes.o.md)
