# get_max_lines

Get a line count for each section and return the largest count. Used in CodeBlocks::intersperse:

```python {name=funcs}
def get_max_lines(sections):
    return max(len(s.splitlines()) for s in sections)
```
