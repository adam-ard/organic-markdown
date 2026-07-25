# Experimental Features

Below are some experimental features that are in development. They are not ready to be used. I am using them to help me develop a good work flow around importing source files into literate source files and generating polished documentation files with lots of bells and whistles (internal linking, expansion of refs, etc..)

`weave` renders every `.o.md` source in the project into a standalone `.html`
file. The source directory structure is retained below the requested
destination, while the `.o.md` suffix becomes `.html`.

References in prose are expanded as before. Fenced code is rendered as escaped
`<pre><code>` HTML with the original language class. Its text remains unchanged
visually, but literate reference tokens become links to their definition
blocks. Each block is preceded by a small Markdown section that exposes its
language and complete Pandoc info string. A named block uses its name in the
metadata, making a long weaved document much easier to scan in a Markdown
viewer. Each source reference also receives a stable HTML anchor. After every
code block, a **Referenced by** section links back to all references across the
generated HTML files, including references elsewhere on the same page.
Prose references link to their exact inline position; references inside fenced
code link to the generated heading for that referring block so the source code
itself remains unchanged.

For example:

````markdown
<div id="omd-code-1" class="omd-code-anchor"></div>

- Code block: `build`
- Language: `bash`
- menu: `true`

<pre><code class="language-bash">make
</code></pre>
````

```python {name=codeblocks__weave_file}
def weave(self, dest):
    reference_index = self.weave_reference_index()
    definition_index = self.weave_definition_index()
    for filename in self.file_order:
        self.weave_file(filename, dest, reference_index, definition_index)

def weave_fence_pattern(self):
    return re.compile(
        r"(?ms)^(?P<indent>[ \t]{0,3})"
        r"(?P<fence>`{3,}|~{3,})(?P<info>[^\n]*)\n"
        r"(?P<code>.*?)^(?P=indent)(?P=fence)[ \t]*$"
    )

def weave_output_name(self, filename):
    relative_source = os.path.normpath(os.path.relpath(filename))
    if relative_source == ".." or relative_source.startswith(f"..{os.sep}"):
        raise ValueError("weave source must be inside the current project")
    if not relative_source.endswith(".o.md"):
        raise ValueError("weave source must end in .o.md")
    return relative_source[:-len(".o.md")] + ".html"

def weave_html_document(self, title, body):
    escaped_title = html.escape(title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --page: #f7f5ef;
      --panel: #ffffff;
      --text: #27251f;
      --muted: #6d685c;
      --line: #d8d2c4;
      --accent: #087f5b;
      --block: #edf5f1;
      --block-line: #b8d2c6;
      --code: #e8f0ec;
      --code-line: #b8d2c6;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --page: #171815;
        --panel: #20221e;
        --text: #e9e5da;
        --muted: #aaa394;
        --line: #3b3e36;
        --accent: #63e6be;
        --block: #18251f;
        --block-line: #365247;
        --code: #19221e;
        --code-line: #365247;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--page);
      color: var(--text);
      font: 17px/1.65 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(100% - 2rem, 980px);
      margin: 2rem auto 5rem;
      padding: clamp(1.25rem, 4vw, 3.5rem);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 18px 60px rgb(0 0 0 / 8%);
    }}
    h1, h2, h3, h4, h5 {{ line-height: 1.25; scroll-margin-top: 1rem; }}
    .omd-code-block {{
      margin: 3.5rem 0;
      padding: 1.25rem 1.4rem;
      background: var(--block);
      border: 1px solid var(--block-line);
      border-radius: 14px;
    }}
    .omd-code-anchor {{
      scroll-margin-top: 1rem;
    }}
    a {{ color: var(--accent); text-underline-offset: 0.16em; }}
    pre {{
      overflow-x: auto;
      padding: 1.1rem 1.25rem;
      background: var(--code);
      border: 1px solid var(--code-line);
      border-radius: 10px;
      line-height: 1.5;
    }}
    code {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
    :not(pre) > code {{
      padding: 0.12rem 0.35rem;
      background: var(--code);
      border-radius: 5px;
    }}
    pre .omd-reference {{
      padding: 0.08em 0.18em;
      color: var(--accent);
      background: color-mix(in srgb, var(--accent) 13%, transparent);
      border-radius: 4px;
      font-weight: 700;
    }}
    blockquote {{
      margin-left: 0;
      padding-left: 1rem;
      color: var(--muted);
      border-left: 4px solid var(--line);
    }}
    @media (max-width: 640px) {{
      main {{ width: 100%; margin: 0; border: 0; border-radius: 0; }}
    }}
  </style>
</head>
<body>
  <main>
{body}
  </main>
</body>
</html>
"""

def weave_reference_names(self, text):
    names = []
    position = 0
    while True:
        match = get_match(text[position:])
        if match is None:
            break
        names.append(match["name"])
        names.extend(self.weave_reference_names(match.get("args", "")))
        names.extend(self.weave_reference_names(match.get("default", "")))
        position += match["end"]
    return names

def weave_code_info(self, info):
    info = info.strip()
    language = ""
    metadata = ""
    name = None

    if info.startswith("{") and info.endswith("}"):
        metadata = info[1:-1].strip()
        language_match = re.search(r"(?:^|\s)\.([^\s}]+)", metadata)
        if language_match is not None:
            language = language_match.group(1)
    elif info:
        info_parts = info.split(None, 1)
        language = info_parts[0]
        if len(info_parts) == 2:
            metadata = info_parts[1].strip()
            if metadata.startswith("{") and metadata.endswith("}"):
                metadata = metadata[1:-1].strip()

    name_match = re.search(
        r"(?:^|\s)name=(?:\"([^\"]*)\"|'([^']*)'|([^\s}]+))",
        metadata,
    )
    if name_match is not None:
        name = next(value for value in name_match.groups() if value is not None)
    return language, metadata, name

def weave_metadata_attributes(self, metadata, language):
    attributes = []
    try:
        tokens = shlex.split(metadata)
    except ValueError:
        tokens = metadata.split()

    for token in tokens:
        if token.startswith("."):
            value = token[1:]
            if value != language:
                attributes.append(("class", value))
        elif token.startswith("#"):
            attributes.append(("id", token[1:]))
        elif "=" in token:
            key, value = token.split("=", 1)
            if key != "name":
                attributes.append((key, value))
        elif token:
            attributes.append((token, "true"))
    return attributes

def weave_definition_index(self):
    definition_index = {}
    for filename in self.file_order:
        with open(filename, "r", encoding="utf-8") as source:
            content = source.read()
        for number, match in enumerate(
            self.weave_fence_pattern().finditer(content),
            start=1,
        ):
            _language, _metadata, name = self.weave_code_info(match.group("info"))
            if name:
                definition_index.setdefault(name, []).append(
                    {
                        "source": os.path.normpath(filename),
                        "anchor": f"omd-code-{number}",
                    }
                )
    return definition_index

def weave_reference_index(self):
    reference_index = {}
    for filename in self.file_order:
        with open(filename, "r", encoding="utf-8") as source:
            content = source.read()

        reference_number = 0
        code_block_number = 0
        position = 0
        for code_match in self.weave_fence_pattern().finditer(content):
            prose = content[position:code_match.start()]
            prose_position = 0
            while True:
                match = get_match(prose[prose_position:])
                if match is None:
                    break
                reference_number += 1
                anchor = f"omd-ref-{reference_number}"
                names = [match["name"]]
                names.extend(self.weave_reference_names(match.get("args", "")))
                names.extend(self.weave_reference_names(match.get("default", "")))
                for name in dict.fromkeys(names):
                    reference_index.setdefault(name, []).append(
                        {
                            "source": os.path.normpath(filename),
                            "anchor": anchor,
                            "number": reference_number,
                            "kind": "prose",
                        }
                    )
                prose_position += match["end"]

            code_block_number += 1
            for name in dict.fromkeys(self.weave_reference_names(code_match.group(0))):
                reference_index.setdefault(name, []).append(
                    {
                        "source": os.path.normpath(filename),
                        "anchor": f"omd-code-{code_block_number}",
                        "number": code_block_number,
                        "kind": "code",
                    }
                )
            position = code_match.end()

        prose = content[position:]
        prose_position = 0
        while True:
            match = get_match(prose[prose_position:])
            if match is None:
                break
            reference_number += 1
            anchor = f"omd-ref-{reference_number}"
            names = [match["name"]]
            names.extend(self.weave_reference_names(match.get("args", "")))
            names.extend(self.weave_reference_names(match.get("default", "")))
            for name in dict.fromkeys(names):
                reference_index.setdefault(name, []).append(
                    {
                        "source": os.path.normpath(filename),
                        "anchor": anchor,
                        "number": reference_number,
                        "kind": "prose",
                    }
                )
            prose_position += match["end"]
    return reference_index

def weave_definition_target(self, definition, filename):
    current_output = self.weave_output_name(filename)
    definition_output = self.weave_output_name(definition["source"])
    if definition["source"] == os.path.normpath(filename):
        return f"#{definition['anchor']}"
    current_dir = os.path.dirname(current_output) or "."
    target = os.path.relpath(definition_output, current_dir).replace(os.sep, "/")
    target = target.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    return f"{target}#{definition['anchor']}"

def weave_code_html(self, code, language, filename):
    rendered = []
    position = 0
    while True:
        match = get_match(code[position:])
        if match is None:
            break
        start = position + match["start"]
        end = position + match["end"]
        rendered.append(html.escape(code[position:start]))
        definitions = self._weave_definition_index.get(match["name"], [])
        reference = html.escape(code[start:end])
        if definitions:
            target = self.weave_definition_target(definitions[0], filename)
            rendered.append(
                f'<a class="omd-reference" href="{html.escape(target, quote=True)}">'
                f"{reference}</a>"
            )
        else:
            rendered.append(reference)
        position = end
    rendered.append(html.escape(code[position:]))

    language_class = ""
    if language:
        language_class = f' class="language-{html.escape(language, quote=True)}"'
    return f"<pre><code{language_class}>" + "".join(rendered) + "</code></pre>"

def weave_expand_prose(self, prose, reference_number):
    annotated = []
    position = 0
    while True:
        match = get_match(prose[position:])
        if match is None:
            break
        reference_number += 1
        start = position + match["start"]
        end = position + match["end"]
        annotated.append(prose[position:start])
        annotated.append(f'<a id="omd-ref-{reference_number}"></a>')
        annotated.append(prose[start:end])
        position = end
    annotated.append(prose[position:])
    return self.expand("".join(annotated)), reference_number

def weave_backlinks(self, name, filename):
    current_source = os.path.normpath(filename)
    current_output = self.weave_output_name(filename)
    current_dir = os.path.dirname(current_output) or "."
    links = []

    if name is not None:
        for reference in self._weave_reference_index.get(name, []):
            reference_output = self.weave_output_name(reference["source"])
            if reference["source"] == current_source:
                target = f"#{reference['anchor']}"
            else:
                target = os.path.relpath(reference_output, current_dir).replace(
                    os.sep,
                    "/",
                )
                target = target.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
                target += f"#{reference['anchor']}"
            label = reference_output.replace(os.sep, "/")
            label = label.replace("[", r"\[").replace("]", r"\]")
            if reference["kind"] == "code":
                place = f"code block {reference['number']}"
            else:
                place = f"reference {reference['number']}"
            links.append(f"- [{label}, {place}]({target})")

    if not links:
        return ""
    return "\n\n##### Referenced by\n\n" + "\n".join(links) + "\n"

def weave_file(
    self,
    filename,
    dest,
    reference_index=None,
    definition_index=None,
):
    if reference_index is None:
        reference_index = self.weave_reference_index()
    if definition_index is None:
        definition_index = self.weave_definition_index()
    self._weave_reference_index = reference_index
    self._weave_definition_index = definition_index

    with open(filename, "r", encoding="utf-8") as source:
        content = source.read()

    weaved_content = []
    position = 0
    reference_number = 0
    code_block_number = 0

    for match in self.weave_fence_pattern().finditer(content):
        code_block_number += 1
        expanded, reference_number = self.weave_expand_prose(
            content[position:match.start()],
            reference_number,
        )
        weaved_content.append(expanded)

        language, metadata, name = self.weave_code_info(match.group("info"))

        details = [
            "::: {.omd-code-block}",
            "",
            (
                f'<div id="omd-code-{code_block_number}" '
                'class="omd-code-anchor"></div>'
            ),
            "",
            f"- Code block: `{name}`" if name else "- Code block: _unnamed_",
            f"- Language: `{language}`" if language else "- Language: _not specified_",
        ]
        for key, value in self.weave_metadata_attributes(metadata, language):
            details.append(f"- {key}: `{value}`")
        details.extend(["", ""])
        weaved_content.append("\n".join(details))
        weaved_content.append(
            self.weave_code_html(match.group("code"), language, filename)
        )
        weaved_content.append(self.weave_backlinks(name, filename))
        weaved_content.append("\n:::\n")
        position = match.end()

    expanded, reference_number = self.weave_expand_prose(
        content[position:],
        reference_number,
    )
    weaved_content.append(expanded)

    relative_output = self.weave_output_name(filename)
    weaved_filename = os.path.join(dest, relative_output)
    output_dir = os.path.dirname(weaved_filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    markdown = "".join(weaved_content)
    body = pypandoc.convert_text(markdown, "html", format="md")
    title = relative_output[:-len(".html")]
    document = self.weave_html_document(title, body)
    with open(weaved_filename, "w", encoding="utf-8") as output:
        output.write(document)
    print(f"Weaved file created: {weaved_filename}")
```

# Tests

The test covers project-wide HTML output, nested source paths, suffix
conversion, prose expansion, metadata headings, clickable references inside
code, cross-file relative links, and same-page fragment links.

```python {name=codeblocks__weave_tests menu=true}
@<imports@>
@<omd_assert@>

o_sym = ":<"
c_sym = ":>"
@<parse_name@>
@<parse_exec@>
@<parse_args_str@>
@<parse_arg_name_value@>
@<parse_arg_name@>
@<parse_arg_value@>
@<eat@>
@<parse_default@>
@<parse_match@>
@<get_match@>

class CodeBlocks:
    def __init__(self, files):
        self.file_order = files

    def expand(self, text):
        return (
            text
            .replace(":<answer:>", "forty-two")
            .replace(":<hello:>", "hello")
        )

    @<codeblocks__weave_file@>

with tempfile.TemporaryDirectory() as directory:
    original = os.getcwd()
    try:
        os.chdir(directory)
        os.makedirs("nested")
        answer_ref = ":<answer:>"
        hello_ref = ":<hello:>"
        tool_ref = ":<tool:>"
        with open("guide.o.md", "w", encoding="utf-8") as output:
            output.write(
                f"# Guide\n\nThe answer is {answer_ref}.\n"
                f"This same-file reference is {hello_ref}.\n\n"
                f"The nested tool is {tool_ref}.\n\n"
                "```python {name=hello tangle=hello.py menu=true}\n"
                f'print("{answer_ref}")\n'
                "```\n"
            )
        with open("nested/tool.o.md", "w", encoding="utf-8") as output:
            output.write(
                f"# Tool\n\nUses {hello_ref}.\n\n"
                "```bash {name=tool}\necho tool\n```\n\n"
                "```text\nunnamed\n```\n\n"
                "```python {name=answer}\nanswer = 42\n```\n"
            )

        blocks = CodeBlocks(["guide.o.md", "nested/tool.o.md"])
        blocks.weave("site")

        with open("site/guide.html", "r", encoding="utf-8") as source:
            guide = source.read()
        with open("site/nested/tool.html", "r", encoding="utf-8") as source:
            tool = source.read()

        omd_assert(True, guide.startswith("<!doctype html>"))
        omd_assert(True, "<title>guide</title>" in guide)
        omd_assert(True, "--code: #e8f0ec;" in guide)
        omd_assert(True, "border: 1px solid var(--code-line);" in guide)
        omd_assert(True, '<div class="omd-code-block">' in guide)
        omd_assert(True, "background: var(--block);" in guide)
        omd_assert(
            True,
            'The answer is <a id="omd-ref-1"></a>forty-two.' in guide,
        )
        omd_assert(
            True,
            '<div id="omd-code-1" class="omd-code-anchor">' in guide,
        )
        omd_assert(True, "<li>Code block: <code>hello</code></li>" in guide)
        omd_assert(True, "<li>Language: <code>python</code></li>" in guide)
        omd_assert(True, "<li>tangle: <code>hello.py</code></li>" in guide)
        omd_assert(True, "<li>menu: <code>true</code></li>" in guide)
        omd_assert(False, "Metadata:" in guide)
        omd_assert(False, "OMD-CODE-1" in guide)
        omd_assert(True, '<pre><code class="language-python">' in guide)
        omd_assert(
            True,
            (
                '<a class="omd-reference" '
                'href="nested/tool.html#omd-code-3">:&lt;answer:&gt;</a>'
            ) in guide,
        )
        omd_assert(True, '<a id="omd-ref-2"></a>hello' in guide)
        omd_assert(True, '<a id="omd-ref-1"></a>hello' in tool)
        omd_assert(
            True,
            'href="nested/tool.html#omd-ref-1"' in guide,
        )
        omd_assert(
            True,
            'href="#omd-ref-2"' in guide,
        )
        omd_assert(
            True,
            '<div id="omd-code-1" class="omd-code-anchor">' in tool,
        )
        omd_assert(
            True,
            '<div id="omd-code-3" class="omd-code-anchor">' in tool,
        )
        omd_assert(True, "<li>Language: <code>bash</code></li>" in tool)
        omd_assert(False, "Metadata:" in tool)
        omd_assert(
            True,
            'href="../guide.html#omd-ref-3"' in tool,
        )
        omd_assert(
            True,
            'href="../guide.html#omd-code-1"' in tool,
        )
        omd_assert(False, "No references from other files." in tool)
        omd_assert(1, guide.count("Referenced by"))
        omd_assert(2, tool.count("Referenced by"))
    finally:
        os.chdir(original)

@<test_passed(name="CodeBlocks.weave")@>
```

```python {name=import_file}
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
