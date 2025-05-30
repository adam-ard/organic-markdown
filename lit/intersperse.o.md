# Intersperse

To be honest, I think intersperse is probably a bad name for this, but I couldn't come up with any thing else. What this function does is takes a list of input strings (conceivably each with multiple lines) and weaves them together, creating a resulting list of N strings, where N is the number of lines in the string that has the most lines. Each line will have one entry from the input string (if one string has less lines than N lines, we'll just repeat the last line.) This is a little hard to explain, so here is an example:

Input -> ["1\n2\n3", "4\n5", "6"]
Output -> ["146", "256", "356"]

Actually, the resulting list, right before being returned, get joined by `\n` characters, so a single string will get returned. Like this: "146\n256\n356". Here is the code for the `intersperse` function:

```python {name=intersperse}
def intersperse(sections):
    out = []
    max_lines = get_max_lines(sections)
    for i in range(max_lines):
        line = ""
        for s in sections:
            lines = s.split('\n')
            if i < len(lines):
                line += lines[i]
            else:
                line += lines[-1]   # repeat the last entry
        out.append(line)
    return "\n".join(out)
```

[test](intersperse_test.o.md)
