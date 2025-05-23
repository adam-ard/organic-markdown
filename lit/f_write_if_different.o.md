# function: write_if_different()

I wrote this function so that when `omd tangle` is called we don't rewrite files that haven't changed. If we re-write all the files, then the timestamp updates on all files, and then programs that use that timestamp (like `make`) think a bunch of files changed that didn't and a bunch of unneccessary work if initiated.

### @<funcs@>

```python {name=funcs}
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
```
