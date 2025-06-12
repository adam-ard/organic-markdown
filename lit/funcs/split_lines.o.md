# split_lines

This function is a slightly modified way of spliting lines so that refs can span multiple lines like this:

```
@<example(arg1=stuff
          arg2=more_stuff
          arg3=yet_more_stuff)@>
```

This can be really handy when there are lots of arguments. This function splits lines up anywhere there is a `\n` character, unless the newline character is inbetween the ref symbols (`o_sym` and `c_sym`). Note that I use an int for `ref_num` not a `bool`, so that I can handle cases where there are refs nested inside of refs (see the tests below).

```python {name=split_lines}
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
        if txt[i : i + len(o_sym)] == o_sym:
            ref_num += 1
            i += len(o_sym) - 1
        if txt[i : i + len(c_sym)] == c_sym:
            ref_num -= 1
            i += len(c_sym) - 1
        i += 1

    new_lines.append(txt[start:i])
    return new_lines
```

## Testing

Here I swap out the `@<` and `@>` characters for the `:<` and `:>` characters. This drastically simplifies the test code. Otherwise I have to worry about escaping to avoid unwanted code substitutions that will happen during the tangle step.

```python {name=split_lines_tests menu=true}
o_sym = ":<"
c_sym = ":>"

@<omd_assert@>

@<split_lines@>

txt = "test"
expected = ["test"]

omd_assert(expected, split_lines(txt))

txt = "a\nb\nc"
expected = ["a", "b", "c"]

omd_assert(expected, split_lines(txt))

txt = "A:<B(a=1\nb=2):>\nC\nD"
expected = ["A:<B(a=1\nb=2):>", "C", "D"]

omd_assert(expected, split_lines(txt))

# Test that refs nested in refs work
txt = """A:<B(a=":<j(a=one
b=two):>"
b=2):>
C
D"""
expected = ["""A:<B(a=":<j(a=one
b=two):>"
b=2):>""", "C", "D"]

omd_assert(expected, split_lines(txt))

# test asymmetric opening and closing symbols
o_sym = "::::::<"
c_sym = ":::>"

txt = "A::::::<B(a=1\nb=2):::>\nC\nD"
expected = ["A::::::<B(a=1\nb=2):::>", "C", "D"]

omd_assert(expected, split_lines(txt))

@<test_passed(name="split_lines")@>
```
