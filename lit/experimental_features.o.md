# Experimental Features

Below are some experimental features that are in development. They are
not ready to be used. I am using them to help me develop a good work
flow around importing source files into literate source files and
generating polished documentation files with lots of bells and
whistles (internal linking, expansion of refs, etc..)

```python {name=CodeBlocks_funcs}
def weave_file(self, filename, dest):
    with open(filename, 'r') as f:
        content = f.read()

    # Split by triple backticks to find code and non-code sections
    parts = re.split(r'(```.*?```)', content, flags=re.DOTALL)
    weaved_content = []

    for part in parts:
        if part.startswith("```"):
            # Code section - keep as-is
            weaved_content.append(part)
        else:
            # Non-code section
            expanded_part = self.expand(part)
            weaved_content.append(expanded_part)

    # Write the weaved output to a new Markdown file
    weaved_filename = f"{dest}/{filename}"
    with open(weaved_filename, 'w') as f:
        f.write("".join(weaved_content))
    print(f"Weaved file created: {weaved_filename}")
```

```python {name=funcs}
def import_file(lang, file_path):
    print(f"importing {file_path}")

    # Get the absolute path of the file and the current directory
    abs_file_path = os.path.abspath(file_path)
    current_directory = os.path.abspath(os.getcwd())

    # Check if the file path is a descendant of the current directory
    if not abs_file_path.startswith(current_directory):
        raise ValueError("The file path must be a descendant of the current directory.")

    # Ensure the file exists
    if not os.path.isfile(abs_file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Extract the filename and create the new filename with ".o.md" extension
    original_filename = os.path.basename(file_path)
    new_filename = f"{original_filename}.o.md"
    new_file_path = os.path.join(current_directory, new_filename)

    # Read the content of the original file
    with open(abs_file_path, 'r') as original_file:
        content = original_file.read()

    # Modify the content by adding triple backticks and the {name=<path>} tag
    modified_content = f"```{lang} {{tangle={abs_file_path}}}\n{content}```\n"

    # Write the modified content to the new file in the current directory
    with open(new_file_path, 'w') as new_file:
        new_file.write(modified_content)
```
