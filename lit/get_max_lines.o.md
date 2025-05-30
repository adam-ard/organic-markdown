# get_max_lines

Get a line count for each section and return the largest count. Used in CodeBlocks::intersperse:

```python {name=get_max_lines}
def get_max_lines(sections):
    if sections == []:
        return 0

    return max(len(s.splitlines()) for s in sections)
```

