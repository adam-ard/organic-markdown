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

Command cards become runnable when the output is opened through the local
server:

```text
omd serve site
```

This rebuilds `site`, binds only to `127.0.0.1`, and prints the URL to open.
Clicking **Run** streams combined standard output and errors into a drawer on
the right. The endpoint accepts only blocks currently parsed with `menu=true`.
Every named card also has an **Expand** button that runs `omd expand <name>` and
shows the fully expanded block in a modal code window.

For example:

````markdown
<div id="omd-code-1" class="omd-code-anchor"></div>

<h4 class="omd-code-title"><span class="omd-card-kind">command</span><code>build</code></h4>

<div class="omd-code-panel has-language">
<div class="omd-language-label">bash</div>
<pre><code class="language-bash">make
</code></pre>
</div>
````

```python {name=codeblocks__weave_file}
def weave(self, dest):
    reference_index = self.weave_reference_index()
    definition_index = self.weave_definition_index()
    for filename in self.file_order:
        self.weave_file(filename, dest, reference_index, definition_index)

def weave_server(self, dest, port=8000):
    output_root = os.path.abspath(dest)
    project_root = os.getcwd()
    omd_executable = os.path.abspath(sys.argv[0])
    editor_command = (
        shlex.split(os.environ.get("OMD_EDITOR", "emacs")) or ["emacs"]
    )
    editable_sources = {
        os.path.normpath(os.path.relpath(source)): os.path.abspath(source)
        for source in self.file_order
    }
    port = int(os.environ.get("OMD_PORT", port))
    code_blocks = self

    class WeaveRequestHandler(SimpleHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def send_text_error(self, status, message):
            encoded = message.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

        def do_POST(self):
            actions = {
                "/__omd__/run": "run",
                "/__omd__/expand": "expand",
                "/__omd__/edit": "edit",
            }
            action = actions.get(self.path)
            if action is None:
                self.send_text_error(404, "Unknown endpoint.\n")
                return

            content_type = self.headers.get("Content-Type", "").split(";", 1)[0]
            if content_type != "application/json":
                self.send_text_error(415, "Expected application/json.\n")
                return

            origin = self.headers.get("Origin")
            allowed_origins = {
                f"http://127.0.0.1:{self.server.server_port}",
                f"http://localhost:{self.server.server_port}",
            }
            if origin is not None and origin not in allowed_origins:
                self.send_text_error(403, "Origin is not allowed.\n")
                return

            try:
                content_length = int(self.headers.get("Content-Length", "0"))
                if content_length < 1 or content_length > 65536:
                    raise ValueError
                payload = json.loads(self.rfile.read(content_length))
            except (ValueError, json.JSONDecodeError, AttributeError):
                self.send_text_error(400, "Invalid command request.\n")
                return

            if action == "edit":
                source = payload.get("source")
                line = payload.get("line")
                if (
                    not isinstance(source, str)
                    or not isinstance(line, int)
                    or isinstance(line, bool)
                    or line < 1
                ):
                    self.send_text_error(400, "Invalid edit request.\n")
                    return
                source = os.path.normpath(source)
                source_path = editable_sources.get(source)
                if source_path is None:
                    self.send_text_error(403, "Source file is not available.\n")
                    return
                try:
                    subprocess.Popen(
                        editor_command + [f"+{line}", source_path],
                        cwd=project_root,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True,
                    )
                except OSError as error:
                    self.send_text_error(
                        500,
                        f"Unable to start editor: {error}\n",
                    )
                    return
                response = f"Opened {source}:{line} in Emacs.\n".encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(response)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(response)
                return

            name = payload.get("name")
            if not isinstance(name, str) or not name:
                self.send_text_error(400, "Invalid command request.\n")
                return
            block = code_blocks.get_code_block(name)
            if block is None:
                self.send_text_error(403, "Block is not available.\n")
                return
            if action == "run" and not block.in_menu:
                self.send_text_error(403, "Command is not available.\n")
                return

            try:
                process = subprocess.Popen(
                    [sys.executable, omd_executable, action, name],
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
            except OSError as error:
                self.send_text_error(500, f"Unable to start command: {error}\n")
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True

            try:
                while True:
                    chunk = os.read(process.stdout.fileno(), 4096)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
                return_code = process.wait()
                if action == "run":
                    self.wfile.write(
                        f"\n[exit {return_code}]\n".encode("utf-8")
                    )
                elif return_code != 0:
                    self.wfile.write(
                        (
                            "\nExpansion failed with exit code "
                            f"{return_code}.\n"
                        ).encode("utf-8")
                    )
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                process.terminate()
                process.wait()

    def handler(*args, **kwargs):
        return WeaveRequestHandler(*args, directory=output_root, **kwargs)

    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    return server, url

def serve(self, dest, port=8000):
    self.weave(dest)
    server, url = self.weave_server(dest, port)
    print(f"Serving woven documentation at {url}")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()

def weave_fence_pattern(self):
    return re.compile(
        r"(?ms)^(?P<indent>[ \t]{0,3})"
        r"(?P<fence>`{3,}|~{3,})(?P<info>[^\n]*)\n"
        r"(?P<code>.*?)^(?P=indent)(?P=fence)[ \t]*$"
    )

def weave_split_front_matter(self, text):
    match = re.match(
        r"\A(?:\ufeff)?---[ \t]*\n.*?^(?:---|\.\.\.)[ \t]*\n",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    if match is None:
        return "", text
    return text[:match.end()], text[match.end():]

def weave_card_sections(self, content, filename):
    fences = list(self.weave_fence_pattern().finditer(content))
    headings = []
    fence_index = 0
    for match in re.finditer(
        r"(?m)^[ \t]{0,3}(#{1,6})[ \t]+.+$",
        content,
    ):
        while (
            fence_index < len(fences)
            and fences[fence_index].end() <= match.start()
        ):
            fence_index += 1
        if (
            fence_index < len(fences)
            and fences[fence_index].start() <= match.start()
        ):
            continue
        line = match.group()
        title = re.sub(
            r"[ \t]+#+[ \t]*$",
            "",
            line.lstrip().lstrip("#").strip(),
        )
        headings.append(
            {
                "start": match.start(),
                "end": match.end(),
                "level": len(match.group(1)),
                "is_card": bool(
                    re.search(r"(?:^|\s):CARD:[ \t]*$", title, re.I)
                ),
            }
        )

    sections = []
    for index, heading in enumerate(headings):
        if not heading["is_card"]:
            continue
        end = len(content)
        for candidate in headings[index + 1:]:
            if candidate["level"] <= heading["level"]:
                end = candidate["start"]
                break
            if candidate["is_card"]:
                line = content.count("\n", 0, candidate["start"]) + 1
                raise ValueError(
                    f"{filename}:{line}: a card cannot contain another card"
                )

        section_fences = [
            (number, fence)
            for number, fence in enumerate(fences, start=1)
            if heading["end"] <= fence.start() < end
        ]
        metadata_fences = [
            (number, fence)
            for number, fence in section_fences
            if self.weave_code_info(fence.group("info"))[1]
        ]
        heading_line = content.count("\n", 0, heading["start"]) + 1
        if len(metadata_fences) != 1:
            raise ValueError(
                f"{filename}:{heading_line}: a :CARD: section must contain "
                "exactly one code block with metadata "
                f"(found {len(metadata_fences)})"
            )
        number, metadata_fence = metadata_fences[0]
        sections.append(
            {
                **heading,
                "section_end": end,
                "metadata_fence": metadata_fence.start(),
                "metadata_number": number,
            }
        )
    return sections

def weave_output_name(self, filename):
    relative_source = os.path.normpath(os.path.relpath(filename))
    if relative_source == ".." or relative_source.startswith(f"..{os.sep}"):
        raise ValueError("weave source must be inside the current project")
    if not relative_source.endswith(".o.md"):
        raise ValueError("weave source must end in .o.md")
    return relative_source[:-len(".o.md")] + ".html"

def weave_navigation(self, current_output):
    tree = {"directories": {}, "files": []}
    for source in self.file_order:
        source = os.path.normpath(source)
        commands = []
        with open(source, "r", encoding="utf-8") as source_file:
            source_content = source_file.read()
        for number, match in enumerate(
            self.weave_fence_pattern().finditer(source_content),
            start=1,
        ):
            language, metadata, name = self.weave_code_info(
                match.group("info")
            )
            attributes = self.weave_metadata_attributes(metadata, language)
            menu = next(
                (value for key, value in attributes if key == "menu"),
                None,
            )
            if name and menu is not None and parse_menu_attrib(menu):
                commands.append(
                    {
                        "name": name,
                        "anchor": f"omd-code-{number}",
                    }
                )
        parts = source.split(os.sep)
        node = tree
        for directory in parts[:-1]:
            node = node["directories"].setdefault(
                directory,
                {"directories": {}, "files": []},
            )
        node["files"].append(
            {
                "source": source,
                "output": self.weave_output_name(source),
                "commands": commands,
            }
        )

    current_output = os.path.normpath(current_output)
    current_dir = os.path.dirname(current_output) or "."
    current_directories = os.path.dirname(current_output).split(os.sep)
    if current_directories == ["."]:
        current_directories = []

    def render_node(node, directory_parts):
        output = ["<ul>"]
        for name in sorted(node["directories"], key=str.casefold):
            child_parts = directory_parts + [name]
            is_current_branch = (
                current_directories[:len(child_parts)] == child_parts
            )
            open_attribute = " open" if is_current_branch else ""
            output.append(
                f"<li><details{open_attribute}>"
                f"<summary>{html.escape(name)}</summary>"
            )
            output.append(render_node(node["directories"][name], child_parts))
            output.append("</details></li>")

        for item in sorted(
            node["files"],
            key=lambda value: os.path.basename(value["source"]).casefold(),
        ):
            target = os.path.relpath(item["output"], current_dir).replace(
                os.sep,
                "/",
            )
            target = target.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
            label = html.escape(os.path.basename(item["source"]))
            output.append('<li class="omd-nav-file">')
            output.append('<div class="omd-nav-file-row">')
            if item["output"] == current_output:
                output.append(
                    '<a class="current" aria-current="page" '
                    f'href="{html.escape(target, quote=True)}">{label}</a>'
                )
            else:
                output.append(
                    f'<a href="{html.escape(target, quote=True)}">'
                    f"{label}</a>"
                )
            source_name = html.escape(item["source"], quote=True)
            output.append(
                '<button type="button" '
                'class="omd-edit-source omd-nav-edit" '
                f'data-source="{source_name}" data-line="1" '
                f'aria-label="Edit {label}">✎</button></div>'
            )
            if item["commands"]:
                output.append('<ul class="omd-nav-commands">')
                for command in item["commands"]:
                    command_name = html.escape(command["name"])
                    command_value = html.escape(command["name"], quote=True)
                    command_target = html.escape(
                        f'{target}#{command["anchor"]}',
                        quote=True,
                    )
                    output.append(
                        '<li><a class="omd-nav-command-link" '
                        f'href="{command_target}">{command_name}</a>'
                        '<button type="button" '
                        'class="omd-run-command omd-nav-run" '
                        f'data-command="{command_value}" '
                        f'aria-label="Run {command_value}">▶</button></li>'
                    )
                output.append("</ul>")
            output.append("</li>")
        output.append("</ul>")
        return "".join(output)

    return (
        '<nav class="omd-site-nav" aria-label="Literate files">'
        '<div class="omd-site-nav-title">Project</div>'
        f"{render_node(tree, [])}</nav>"
    )

def weave_html_document(self, title, body, navigation):
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
      --command-block: #eef1fb;
      --command-line: #b9c5e7;
      --command-code: #e4e9f8;
      --command-accent: #405da8;
      --file-block: #faf2e3;
      --file-line: #dfc38e;
      --file-code: #f3e7d1;
      --file-accent: #986408;
      --nav-width: 18rem;
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
        --command-block: #1c2234;
        --command-line: #3f4f7b;
        --command-code: #202941;
        --command-accent: #9cb4ff;
        --file-block: #2a2318;
        --file-line: #6c5530;
        --file-code: #332919;
        --file-accent: #f2c46d;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      padding-left: var(--nav-width);
      background: var(--page);
      color: var(--text);
      font: 17px/1.65 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .omd-site-nav {{
      position: fixed;
      inset: 0 auto 0 0;
      z-index: 5;
      width: var(--nav-width);
      padding: 1.2rem 0.9rem 2rem;
      overflow: auto;
      background: var(--panel);
      border-right: 1px solid var(--line);
    }}
    .omd-site-nav-title {{
      margin: 0 0.5rem 0.9rem;
      color: var(--muted);
      font: 800 0.75rem/1.2 system-ui, sans-serif;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}
    .omd-site-nav ul {{
      margin: 0;
      padding-left: 0.85rem;
      list-style: none;
    }}
    .omd-site-nav > ul {{ padding-left: 0; }}
    .omd-site-nav li {{ margin: 0.12rem 0; }}
    .omd-site-nav summary {{
      padding: 0.26rem 0.45rem;
      color: var(--muted);
      border-radius: 6px;
      cursor: pointer;
      font-weight: 700;
    }}
    .omd-site-nav a {{
      display: block;
      padding: 0.28rem 0.48rem;
      overflow: hidden;
      color: var(--text);
      border-radius: 6px;
      font: 0.86rem/1.35 ui-monospace, SFMono-Regular, Consolas, monospace;
      text-decoration: none;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .omd-site-nav a:hover {{ background: var(--code); }}
    .omd-site-nav a.current {{
      color: var(--panel);
      background: var(--accent);
      font-weight: 800;
    }}
    .omd-nav-file-row {{
      display: flex;
      align-items: center;
      gap: 0.3rem;
    }}
    .omd-nav-file-row > a {{
      min-width: 0;
      flex: 1;
    }}
    .omd-nav-edit.omd-edit-source {{
      flex: 0 0 auto;
      margin: 0;
      padding: 0.16rem 0.42rem;
      color: var(--muted);
      background: transparent;
      border-color: var(--line);
      font-size: 0.72rem;
    }}
    .omd-nav-edit.omd-edit-source:hover {{
      color: var(--text);
      background: var(--code);
    }}
    .omd-site-nav .omd-nav-commands {{
      padding: 0.18rem 0 0.28rem 0.65rem;
    }}
    .omd-nav-commands li {{
      display: flex;
      align-items: center;
      gap: 0.3rem;
    }}
    .omd-site-nav .omd-nav-command-link {{
      min-width: 0;
      flex: 1;
      padding-block: 0.18rem;
      color: var(--muted);
      font-size: 0.8rem;
    }}
    .omd-nav-run.omd-run-command {{
      flex: 0 0 auto;
      margin: 0;
      padding: 0.16rem 0.42rem;
      color: white;
      background: var(--command-accent);
      font-size: 0.68rem;
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
      position: relative;
      margin: 3.5rem 0;
      padding: 1.75rem 1.4rem 1.25rem;
      background: var(--card-bg);
      border: 1px solid var(--card-line);
      border-radius: 14px;
    }}
    .omd-card-code {{
      --card-bg: var(--block);
      --card-line: var(--block-line);
      --card-code: var(--code);
      --card-accent: var(--accent);
    }}
    .omd-card-command {{
      --card-bg: var(--command-block);
      --card-line: var(--command-line);
      --card-code: var(--command-code);
      --card-accent: var(--command-accent);
    }}
    .omd-card-file {{
      --card-bg: var(--file-block);
      --card-line: var(--file-line);
      --card-code: var(--file-code);
      --card-accent: var(--file-accent);
    }}
    .omd-code-anchor {{
      scroll-margin-top: 1rem;
    }}
    .omd-code-title {{
      position: absolute;
      top: 0;
      left: 1.4rem;
      transform: translateY(-50%);
      margin: 0;
      padding: 0.28rem 0.8rem;
      max-width: calc(100% - 2.8rem);
      overflow-x: auto;
      background: var(--card-bg);
      border: 1px solid var(--card-line);
      border-radius: 999px;
      box-shadow: 0 3px 10px rgb(0 0 0 / 8%);
      font-size: 1rem;
      letter-spacing: -0.01em;
    }}
    .omd-code-title code {{
      padding: 0;
      color: var(--text);
      background: transparent;
    }}
    .omd-code-title.unnamed {{
      color: var(--muted);
      font-weight: 500;
    }}
    .omd-card-kind {{
      margin-right: 0.55rem;
      color: var(--card-accent);
      font: 700 0.68rem/1 ui-monospace, SFMono-Regular, Consolas, monospace;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .omd-code-title.kind-only .omd-card-kind {{ margin-right: 0; }}
    .omd-code-block a {{ color: var(--card-accent); }}
    .omd-run-command {{
      margin-left: 0.75rem;
      padding: 0.2rem 0.62rem;
      color: white;
      background: var(--card-accent);
      border: 0;
      border-radius: 999px;
      font: 700 0.78rem/1.3 system-ui, sans-serif;
      cursor: pointer;
    }}
    .omd-run-command:disabled {{ cursor: wait; opacity: 0.6; }}
    .omd-expand-code,
    .omd-edit-source {{
      padding: 0.2rem 0.62rem;
      color: var(--card-accent);
      background: var(--card-code);
      border: 1px solid var(--card-accent);
      border-radius: 999px;
      font: 700 0.78rem/1.3 system-ui, sans-serif;
      cursor: pointer;
    }}
    .omd-expand-code:disabled,
    .omd-edit-source:disabled {{ cursor: wait; opacity: 0.6; }}
    a {{ color: var(--accent); text-underline-offset: 0.16em; }}
    pre {{
      overflow-x: auto;
      padding: 1.1rem 1.25rem;
      background: var(--code);
      border: 1px solid var(--code-line);
      border-radius: 10px;
      line-height: 1.5;
    }}
    .omd-code-panel {{
      position: relative;
      margin: 1.75rem 0 1rem;
    }}
    .omd-code-panel pre {{
      margin: 0;
      background: var(--card-code);
      border-color: var(--card-line);
    }}
    .omd-code-panel.has-controls pre {{
      padding-top: 1.65rem;
    }}
    .omd-code-controls {{
      position: absolute;
      top: 0;
      left: 1rem;
      z-index: 1;
      transform: translateY(-50%);
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .omd-language-label {{
      padding: 0.2rem 0.65rem;
      color: var(--text);
      background: var(--card-code);
      border: 1px solid var(--card-line);
      border-radius: 999px;
      font: 600 0.82rem/1.2 ui-monospace, SFMono-Regular, Consolas, monospace;
    }}
    code {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
    :not(pre) > code {{
      padding: 0.12rem 0.35rem;
      background: var(--code);
      border-radius: 5px;
    }}
    .omd-code-block :not(pre) > code {{ background: var(--card-code); }}
    pre .omd-reference {{
      padding: 0.08em 0.18em;
      color: var(--card-accent);
      background: color-mix(in srgb, var(--card-accent) 13%, transparent);
      border-radius: 4px;
      font-weight: 700;
    }}
    blockquote {{
      margin-left: 0;
      padding-left: 1rem;
      color: var(--muted);
      border-left: 4px solid var(--line);
    }}
    math[display="block"] {{
      margin: 1.5rem auto;
      overflow-x: auto;
    }}
    .omd-runner {{
      position: fixed;
      inset: 0 0 0 auto;
      z-index: 10;
      display: grid;
      grid-template-rows: auto 1fr;
      width: min(46vw, 44rem);
      padding: 1rem;
      color: var(--text);
      background: var(--panel);
      border-left: 1px solid var(--line);
      box-shadow: -18px 0 50px rgb(0 0 0 / 16%);
    }}
    .omd-runner[hidden] {{ display: none; }}
    .omd-runner-header {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      min-width: 0;
      margin-bottom: 0.8rem;
    }}
    .omd-runner-title {{
      flex: 1;
      overflow: hidden;
      margin: 0;
      font: 700 0.95rem/1.3 ui-monospace, SFMono-Regular, Consolas, monospace;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .omd-runner-header button {{
      padding: 0.35rem 0.65rem;
      color: var(--text);
      background: var(--code);
      border: 1px solid var(--line);
      border-radius: 7px;
      cursor: pointer;
    }}
    .omd-runner-output {{
      min-height: 0;
      margin: 0;
      padding: 1rem;
      overflow: auto;
      color: #e9ecef;
      background: #111;
      border: 1px solid #333;
      border-radius: 10px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }}
    .omd-expand-dialog {{
      width: min(90vw, 68rem);
      height: min(82vh, 52rem);
      padding: 0;
      color: var(--text);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      box-shadow: 0 24px 80px rgb(0 0 0 / 28%);
    }}
    .omd-expand-dialog::backdrop {{
      background: rgb(0 0 0 / 48%);
      backdrop-filter: blur(2px);
    }}
    .omd-expand-dialog-inner {{
      display: grid;
      grid-template-rows: auto 1fr;
      height: 100%;
      padding: 1rem;
    }}
    .omd-expand-dialog-header {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      min-width: 0;
      margin-bottom: 0.8rem;
    }}
    .omd-expand-dialog-title {{
      flex: 1;
      overflow: hidden;
      margin: 0;
      font: 700 1rem/1.3 ui-monospace, SFMono-Regular, Consolas, monospace;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .omd-expand-dialog-close {{
      padding: 0.35rem 0.7rem;
      color: var(--text);
      background: var(--code);
      border: 1px solid var(--line);
      border-radius: 7px;
      cursor: pointer;
    }}
    .omd-expand-listing {{
      min-height: 0;
      overflow: auto;
      color: var(--text);
      background: var(--code);
      border: 1px solid var(--line);
      border-radius: 10px;
      box-shadow: inset 0 1px 3px rgb(0 0 0 / 8%);
    }}
    .omd-expand-lines {{
      min-width: max-content;
      margin: 0;
      padding: 1rem 1.25rem 1rem 4.2rem;
      font: 0.9rem/1.55 ui-monospace, SFMono-Regular, Consolas, monospace;
    }}
    .omd-expand-lines li {{
      min-height: 1.55em;
      padding-left: 0.9rem;
      color: var(--muted);
      border-left: 1px solid var(--line);
    }}
    .omd-expand-lines li::marker {{
      color: var(--muted);
      font-size: 0.78rem;
    }}
    .omd-expand-lines code {{
      padding: 0;
      color: var(--text);
      background: transparent;
      white-space: pre;
    }}
    @media (min-width: 1000px) {{
      body.omd-runner-open main {{
        width: min(calc(54vw - 3rem), 980px);
        margin-left: 2rem;
        margin-right: auto;
      }}
    }}
    @media (max-width: 800px) {{
      body {{ padding-left: 0; }}
      .omd-site-nav {{
        position: static;
        width: 100%;
        max-height: 42vh;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }}
    }}
    @media (max-width: 640px) {{
      main {{ width: 100%; margin: 0; border: 0; border-radius: 0; }}
      .omd-runner {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  {navigation}
  <main>
{body}
  </main>
  <aside class="omd-runner" id="omd-runner" hidden>
    <header class="omd-runner-header">
      <h2 class="omd-runner-title" id="omd-runner-title">Command output</h2>
      <button type="button" id="omd-runner-clear">Clear</button>
      <button type="button" id="omd-runner-close">Close</button>
    </header>
    <pre class="omd-runner-output" id="omd-runner-output"></pre>
  </aside>
  <dialog class="omd-expand-dialog" id="omd-expand-dialog">
    <div class="omd-expand-dialog-inner">
      <header class="omd-expand-dialog-header">
        <h2 class="omd-expand-dialog-title" id="omd-expand-dialog-title">
          Expanded block
        </h2>
        <button type="button" class="omd-expand-dialog-close"
                id="omd-expand-copy">Copy</button>
        <button type="button" class="omd-expand-dialog-close"
                id="omd-expand-dialog-close">Close</button>
      </header>
      <div class="omd-expand-listing" id="omd-expand-listing"></div>
    </div>
  </dialog>
  <script>
    (() => {{
      const runner = document.querySelector("#omd-runner");
      const output = document.querySelector("#omd-runner-output");
      const title = document.querySelector("#omd-runner-title");
      const expandDialog = document.querySelector("#omd-expand-dialog");
      const expandListing = document.querySelector("#omd-expand-listing");
      const expandTitle = document.querySelector("#omd-expand-dialog-title");
      const expandCopy = document.querySelector("#omd-expand-copy");
      let expandedSource = "";

      function renderExpandedSource(source) {{
        expandedSource = source;
        const lines = source.replace(/\\n$/, "").split("\\n");
        const list = document.createElement("ol");
        list.className = "omd-expand-lines";
        for (const line of lines) {{
          const item = document.createElement("li");
          const code = document.createElement("code");
          code.textContent = line || "\\u00a0";
          item.append(code);
          list.append(item);
        }}
        expandListing.replaceChildren(list);
      }}

      async function streamResponse(response, target) {{
        if (!response.ok) {{
          target.textContent += await response.text();
          return;
        }}
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        while (true) {{
          const {{ value, done }} = await reader.read();
          if (done) break;
          target.textContent += decoder.decode(value, {{ stream: true }});
          target.scrollTop = target.scrollHeight;
        }}
        target.textContent += decoder.decode();
      }}

      document.querySelector("#omd-runner-close").addEventListener("click", () => {{
        runner.hidden = true;
        document.body.classList.remove("omd-runner-open");
      }});
      document.querySelector("#omd-runner-clear").addEventListener("click", () => {{
        output.textContent = "";
      }});
      document.querySelector("#omd-expand-dialog-close").addEventListener(
        "click",
        () => expandDialog.close(),
      );
      expandCopy.addEventListener("click", async () => {{
        await navigator.clipboard.writeText(expandedSource);
        expandCopy.textContent = "Copied";
        setTimeout(() => {{ expandCopy.textContent = "Copy"; }}, 1200);
      }});

      document.addEventListener("click", async (event) => {{
        const button = event.target.closest(".omd-run-command");
        if (!button) return;

        const name = button.dataset.command;
        runner.hidden = false;
        document.body.classList.add("omd-runner-open");
        title.textContent = name;
        output.textContent = `$ omd run ${{name}}\\n\\n`;
        button.disabled = true;

        try {{
          const response = await fetch("/__omd__/run", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ name }}),
          }});
          await streamResponse(response, output);
        }} catch (error) {{
          output.textContent +=
            `Unable to run command. Open this weave with "omd serve <dest>".\\n${{error}}\\n`;
        }} finally {{
          button.disabled = false;
        }}
      }});

      document.addEventListener("click", async (event) => {{
        const button = event.target.closest(".omd-expand-code");
        if (!button) return;

        const name = button.dataset.block;
        expandTitle.textContent = `Expanded: ${{name}}`;
        renderExpandedSource("Loading…");
        expandDialog.showModal();
        button.disabled = true;

        try {{
          const response = await fetch("/__omd__/expand", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ name }}),
          }});
          renderExpandedSource(await response.text());
        }} catch (error) {{
          renderExpandedSource(
            `Unable to expand block. Open this weave with "omd serve <dest>".\\n${{error}}\\n`
          );
        }} finally {{
          button.disabled = false;
        }}
      }});

      document.addEventListener("click", async (event) => {{
        const button = event.target.closest(".omd-edit-source");
        if (!button) return;

        const source = button.dataset.source;
        const line = Number(button.dataset.line);
        const originalLabel = button.textContent;
        button.disabled = true;

        try {{
          const response = await fetch("/__omd__/edit", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ source, line }}),
          }});
          if (!response.ok) throw new Error(await response.text());
          button.textContent = "Opened";
          setTimeout(() => {{ button.textContent = originalLabel; }}, 1200);
        }} catch (error) {{
          window.alert(
            `Unable to open source. Use "omd serve <dest>" and ensure Emacs is installed.\\n${{error}}`
          );
        }} finally {{
          button.disabled = false;
        }}
      }});
    }})();
  </script>
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

def weave_card_info(self, name, attributes):
    menu = next((value for key, value in attributes if key == "menu"), None)
    tangle = next((value for key, value in attributes if key == "tangle"), None)

    if menu is not None and parse_menu_attrib(menu):
        kind = "command"
        title = name if name else "Unnamed command"
        hidden_attributes = {"menu"}
    elif tangle:
        kind = "file"
        title = os.path.abspath(self.expand(tangle))
        hidden_attributes = {"tangle"}
    else:
        kind = "code"
        title = name
        hidden_attributes = set()

    visible_attributes = [
        (key, value)
        for key, value in attributes
        if key not in hidden_attributes
    ]
    return kind, title, visible_attributes

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

def weave_code_html(
    self,
    code,
    language,
    filename,
    name=None,
    is_card=True,
):
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
    listing = (
        f"<pre><code{language_class}>"
        + "".join(rendered)
        + "</code></pre>"
    )
    if not is_card:
        return listing

    panel_class = "omd-code-panel"
    language_label = ""
    expand_button = ""
    if language:
        language_label = (
            '<div class="omd-language-label">'
            f"{html.escape(language)}</div>"
        )
    if name is not None:
        block_name = html.escape(name, quote=True)
        expand_button = (
            '<button type="button" class="omd-expand-code" '
            f'data-block="{block_name}">↗ Expand</button>'
        )
    controls = ""
    if language_label or expand_button:
        panel_class += " has-controls"
        controls = (
            '<div class="omd-code-controls">'
            f"{language_label}{expand_button}</div>"
        )
    return (
        f'<div class="{panel_class}">'
        f"{controls}{listing}</div>"
    )

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

    fences = list(self.weave_fence_pattern().finditer(content))
    card_sections = self.weave_card_sections(content, filename)
    fences_by_start = {match.start(): match for match in fences}
    sections_by_fence = {
        match.start(): section
        for section in card_sections
        for match in fences
        if section["start"] <= match.start() < section["section_end"]
    }

    def append_code(match, section):
        language, metadata, name = self.weave_code_info(match.group("info"))
        if section is None or match.start() != section["metadata_fence"]:
            weaved_content.append(
                self.weave_code_html(
                    match.group("code"),
                    language,
                    filename,
                    is_card=False,
                )
            )
            return
        attributes = self.weave_metadata_attributes(metadata, language)
        _kind, _title, visible_attributes = self.weave_card_info(
            name,
            attributes,
        )
        if visible_attributes:
            attribute_lines = [
                f"- {key}: `{value}`"
                for key, value in visible_attributes
            ]
            weaved_content.append("\n\n" + "\n".join(attribute_lines) + "\n\n")
        weaved_content.append(
            self.weave_code_html(
                match.group("code"),
                language,
                filename,
                name,
            )
        )

    weaved_content = []
    position = 0
    reference_number = 0
    open_card = None
    open_card_backlinks = ""

    for match in fences:
        prose = content[position:match.start()]
        prose_start = position
        if position == 0:
            front_matter, prose = self.weave_split_front_matter(prose)
            prose_start += len(front_matter)
            expanded_front_matter, reference_number = self.weave_expand_prose(
                front_matter,
                reference_number,
            )
            weaved_content.append(expanded_front_matter)

        if open_card:
            if open_card["section_end"] <= match.start():
                boundary = open_card["section_end"] - prose_start
                card_tail, prose = prose[:boundary], prose[boundary:]
                prose_start = open_card["section_end"]
                expanded_tail, reference_number = self.weave_expand_prose(
                    card_tail,
                    reference_number,
                )
                weaved_content.append(expanded_tail)
                weaved_content.append(open_card_backlinks)
                weaved_content.append("\n:::\n")
                open_card = None
                open_card_backlinks = ""
            else:
                expanded_prose, reference_number = self.weave_expand_prose(
                    prose,
                    reference_number,
                )
                weaved_content.append(expanded_prose)
                append_code(match, open_card)
                position = match.end()
                continue

        section = sections_by_fence.get(match.start())
        if section is None:
            expanded_prose, reference_number = self.weave_expand_prose(
                prose,
                reference_number,
            )
            weaved_content.append(expanded_prose)
            append_code(match, None)
            position = match.end()
            continue

        heading_offset = section["start"] - prose_start
        page_prose = prose[:heading_offset]
        card_prose = prose[heading_offset:]
        card_prose = re.sub(
            r"(?im)(^[ \t]{0,3}#{1,6}[ \t]+.*?)"
            r"[ \t]+:CARD:(?=[ \t]*(?:#+[ \t]*)?$)",
            r"\1",
            card_prose,
            count=1,
        )
        expanded_page_prose, reference_number = self.weave_expand_prose(
            page_prose,
            reference_number,
        )
        weaved_content.append(expanded_page_prose)
        expanded_prose, reference_number = self.weave_expand_prose(
            card_prose,
            reference_number,
        )
        metadata_match = fences_by_start[section["metadata_fence"]]
        language, metadata, name = self.weave_code_info(
            metadata_match.group("info")
        )
        attributes = self.weave_metadata_attributes(metadata, language)
        card_kind, card_title, visible_attributes = self.weave_card_info(
            name,
            attributes,
        )
        details = [
            f"::: {{.omd-code-block .omd-card-{card_kind}}}",
            "",
            (
                f'<div id="omd-code-{section["metadata_number"]}" '
                'class="omd-code-anchor"></div>'
            ),
            "",
        ]
        if card_title is None:
            details.extend(
                [
                    (
                        '<h4 class="omd-code-title kind-only">'
                        f'<span class="omd-card-kind">{card_kind}</span></h4>'
                    ),
                    "",
                ]
            )
        else:
            run_button = ""
            if card_kind == "command" and name is not None:
                command = html.escape(name, quote=True)
                run_button = (
                    '<button type="button" class="omd-run-command" '
                    f'data-command="{command}">▶ Run</button>'
                )
            details.extend(
                [
                    (
                        '<h4 class="omd-code-title">'
                        f'<span class="omd-card-kind">{card_kind}</span>'
                        f"<code>{html.escape(card_title)}</code>"
                        f"{run_button}</h4>"
                    ),
                    "",
                ]
            )
        details.extend(["", ""])
        weaved_content.append("\n".join(details))
        weaved_content.append(expanded_prose)
        append_code(match, section)
        open_card = section
        open_card_backlinks = self.weave_backlinks(name, filename)
        position = match.end()

    tail = content[position:]
    if open_card:
        boundary = open_card["section_end"] - position
        card_tail, tail = tail[:boundary], tail[boundary:]
        expanded_card_tail, reference_number = self.weave_expand_prose(
            card_tail,
            reference_number,
        )
        weaved_content.append(expanded_card_tail)
        weaved_content.append(open_card_backlinks)
        weaved_content.append("\n:::\n")
    expanded_tail, reference_number = self.weave_expand_prose(
        tail,
        reference_number,
    )
    weaved_content.append(expanded_tail)

    relative_output = self.weave_output_name(filename)
    weaved_filename = os.path.join(dest, relative_output)
    output_dir = os.path.dirname(weaved_filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    markdown = "".join(weaved_content)
    body = pypandoc.convert_text(
        markdown,
        "html",
        format="md",
        extra_args=["--mathml"],
    )
    title = relative_output[:-len(".html")]
    navigation = self.weave_navigation(relative_output)
    document = self.weave_html_document(title, body, navigation)
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
@<parse_menu_attrib@>
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

    def get_code_block(self, name):
        class Block:
            def __init__(self, in_menu):
                self.in_menu = in_menu

        if name == "hello":
            return Block(True)
        if name == "hidden":
            return Block(False)
        return None

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
                "---\ntitle: Test Guide\n---\n\n"
                "# Guide\n\nPage introduction.\n\n"
                "## Hello command :CARD:\n\n"
                f"$$\\bar K(p)=\\frac{{2\\pi}}{{n}}I(p).$$\n\n"
                f"The answer is {answer_ref}.\n"
                f"This same-file reference is {hello_ref}.\n\n"
                f"The nested tool is {tool_ref}.\n\n"
                "```python {name=hello menu=true}\n"
                f'print("{answer_ref}")\n'
                "```\n\n"
                "After the command source.\n\n"
                "# Global notes\n\nGlobal document text.\n"
            )
        with open("nested/tool.o.md", "w", encoding="utf-8") as output:
            output.write(
                "# Tool\n\nTool page introduction.\n\n"
                f"## Tool block :CARD:\n\nUses {hello_ref}.\n\n"
                "```bash {name=tool}\necho tool\n```\n\n"
                "Inline example description.\n\n"
                "```text\nunnamed\n```\n\n"
                "# Generated files\n\nGlobal generated-file introduction.\n\n"
                "## Answer :CARD:\n\nGenerated answer output.\n\n"
                "```python {name=answer tangle=generated/answer.py}\n"
                "answer = 42\n```\n"
            )
        with open("top.o.md", "w", encoding="utf-8") as output:
            output.write(
                "# Page introduction\n\nOutside the card.\n\n"
                "# Top-level card section :CARD:\n\nInside the card.\n\n"
                "```python {name=top}\nprint('top')\n```\n\n"
                "After the top card source.\n\n"
                "# Following section\n\nOutside after the peer heading.\n"
            )

        blocks = CodeBlocks(["guide.o.md", "nested/tool.o.md", "top.o.md"])
        blocks.weave("site")

        with open("site/guide.html", "r", encoding="utf-8") as source:
            guide = source.read()
        with open("site/nested/tool.html", "r", encoding="utf-8") as source:
            tool = source.read()
        with open("site/top.html", "r", encoding="utf-8") as source:
            top = source.read()

        omd_assert(True, guide.startswith("<!doctype html>"))
        omd_assert(True, "<title>guide</title>" in guide)
        omd_assert(
            True,
            '<nav class="omd-site-nav" aria-label="Literate files">' in guide,
        )
        omd_assert(
            True,
            '<a class="current" aria-current="page" href="guide.html">'
            "guide.o.md</a>" in guide,
        )
        omd_assert(True, 'href="nested/tool.html">tool.o.md</a>' in guide)
        omd_assert(True, 'href="top.html">top.o.md</a>' in guide)
        omd_assert(
            True,
            (
                '<a class="omd-nav-command-link" '
                'href="guide.html#omd-code-1">hello</a>'
            ) in guide,
        )
        omd_assert(
            True,
            (
                'class="omd-run-command omd-nav-run" '
                'data-command="hello" aria-label="Run hello">▶</button>'
            ) in guide,
        )
        omd_assert(
            True,
            'href="../guide.html#omd-code-1">hello</a>' in tool,
        )
        omd_assert(
            1,
            guide.count('<ul class="omd-nav-commands">'),
        )
        omd_assert(
            True,
            '<details open><summary>nested</summary>' in tool,
        )
        omd_assert(True, 'href="../guide.html">guide.o.md</a>' in tool)
        omd_assert(
            True,
            '<a class="current" aria-current="page" href="tool.html">'
            "tool.o.md</a>" in tool,
        )
        omd_assert(True, "padding-left: var(--nav-width);" in guide)
        omd_assert(True, "<math" in guide)
        omd_assert(True, "<mfrac>" in guide)
        omd_assert(True, "--code: #e8f0ec;" in guide)
        omd_assert(True, "border: 1px solid var(--code-line);" in guide)
        omd_assert(True, "omd-card-command" in guide)
        omd_assert(True, "background: var(--card-bg);" in guide)
        omd_assert(True, "transform: translateY(-50%);" in guide)
        command_card = guide.index("omd-card-command", guide.index("<main>"))
        guide_heading = guide.index('<h1 id="guide">Guide</h1>')
        command_heading = guide.index(
            '<h2 id="hello-command">Hello command</h2>'
        )
        guide_code = guide.index('<pre><code class="language-python">')
        command_tail = guide.index("After the command source.")
        global_heading = guide.index('<h1 id="global-notes">Global notes</h1>')
        command_card_end = guide.rfind(
            "</div>",
            command_card,
            global_heading,
        )
        global_text = guide.index("Global document text.")
        omd_assert(True, guide_heading < command_card)
        omd_assert(True, command_card < command_heading < guide_code)
        omd_assert(
            True,
            guide_code
            < command_tail
            < command_card_end
            < global_heading
            < global_text,
        )
        omd_assert(True, guide.index("Page introduction.") < command_card)
        omd_assert(False, "title: Test Guide" in guide)
        omd_assert(
            True,
            'The answer is <a id="omd-ref-1"></a>forty-two.' in guide,
        )
        omd_assert(
            True,
            '<div id="omd-code-1" class="omd-code-anchor">' in guide,
        )
        omd_assert(
            True,
            '<h4 class="omd-code-title">' in guide
            and "<code>hello</code>" in guide,
        )
        omd_assert(False, "<li>Code block:" in guide)
        omd_assert(False, "<li>Language:" in guide)
        omd_assert(
            True,
            '<div class="omd-language-label">' in guide
            and "language-python" in guide,
        )
        omd_assert(True, "omd-card-kind" in guide and "command" in guide)
        omd_assert(
            True,
            (
                '<button type="button" class="omd-run-command" '
                'data-command="hello">'
            ) in guide,
        )
        omd_assert(
            True,
            (
                '<button type="button" class="omd-expand-code" '
                'data-block="hello">'
            ) in guide,
        )
        omd_assert(
            True,
            (
                '<button type="button" '
                'class="omd-edit-source omd-nav-edit" '
                'data-source="guide.o.md" data-line="1"'
            ) in guide,
        )
        code_controls = guide.index('<div class="omd-code-controls">')
        language_control = guide.index(
            '<div class="omd-language-label">',
            code_controls,
        )
        expand_control = guide.index(
            '<button type="button" class="omd-expand-code"',
            language_control,
        )
        source_listing = guide.index("<pre>", expand_control)
        omd_assert(
            True,
            code_controls
            < language_control
            < expand_control
            < source_listing,
        )
        omd_assert(True, 'id="omd-runner-output"' in guide)
        omd_assert(True, 'id="omd-expand-dialog"' in guide)
        omd_assert(True, 'id="omd-expand-listing"' in guide)
        omd_assert(True, 'id="omd-expand-copy"' in guide)
        omd_assert(True, "omd-expand-lines" in guide)
        omd_assert(True, "renderExpandedSource" in guide)
        omd_assert(False, 'id="omd-expand-output"' in guide)
        omd_assert(True, 'fetch("/__omd__/run"' in guide)
        omd_assert(True, 'fetch("/__omd__/expand"' in guide)
        omd_assert(True, 'fetch("/__omd__/edit"' in guide)
        omd_assert(False, "<li>tangle:" in guide)
        omd_assert(False, "<li>menu:" in guide)
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
        omd_assert(False, "omd-card-example" in tool)
        omd_assert(False, "Unnamed code block" in tool)
        omd_assert(False, "omd-code-title kind-only" in tool)
        omd_assert(True, "omd-card-code" in tool)
        omd_assert(True, "omd-card-file" in tool)
        example_description = tool.index("Inline example description.")
        example_code = tool.index(
            '<pre><code class="language-text">',
            example_description,
        )
        answer_card = tool.index("omd-card-file", example_code)
        tool_card = tool.index(
            '<div class="omd-code-block omd-card-code">',
            tool.index("<main>"),
        )
        tool_card_end = tool.rfind("</div>", tool_card, answer_card)
        omd_assert(
            True,
            tool_card
            < example_description
            < example_code
            < tool_card_end
            < answer_card,
        )
        omd_assert(
            2,
            tool.count('<div class="omd-code-block omd-card-'),
        )
        tool_main = tool[tool.index("<main>"):tool.index("</main>")]
        omd_assert(
            False,
            '<button type="button" class="omd-run-command"' in tool_main,
        )
        omd_assert(False, "omd-edit-source" in tool_main)
        omd_assert(
            2,
            tool.count(
                '<button type="button" class="omd-expand-code"'
            ),
        )
        omd_assert(
            3,
            tool.count(
                'class="omd-edit-source omd-nav-edit"'
            ),
        )
        omd_assert(
            True,
            'data-source="nested/tool.o.md" data-line="1"' in tool,
        )
        omd_assert(True, "generated/answer.py" in tool)
        file_card = tool.index("omd-card-file", tool.index("<main>"))
        generated_heading = tool.index(
            '<h1 id="generated-files">Generated files</h1>'
        )
        generated_intro = tool.index(
            "Global generated-file introduction."
        )
        answer_heading = tool.index('<h2 id="answer">Answer</h2>')
        answer_code = tool.index(
            '<pre><code class="language-python">',
            file_card,
        )
        omd_assert(
            True,
            generated_heading
            < generated_intro
            < file_card
            < answer_heading
            < answer_code,
        )
        omd_assert(False, "<li>tangle:" in tool)
        omd_assert(False, "<li>Language:" in tool)
        omd_assert(
            True,
            '<div class="omd-language-label">' in tool
            and "language-bash" in tool,
        )
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

        top_card = top.index("omd-card-code", top.index("<main>"))
        page_heading = top.index(
            '<h1 id="page-introduction">Page introduction</h1>'
        )
        card_heading = top.index(
            '<h1 id="top-level-card-section">Top-level card section</h1>'
        )
        top_code = top.index('<pre><code class="language-python">')
        trailing_text = top.index("After the top card source.")
        following_heading = top.index(
            '<h1 id="following-section">Following section</h1>'
        )
        top_card_end = top.rfind("</div>", top_card, following_heading)
        following_text = top.index("Outside after the peer heading.")
        omd_assert(True, page_heading < top_card)
        omd_assert(True, top_card < card_heading < top_code)
        omd_assert(True, top.index("Outside the card.") < top_card)
        omd_assert(True, top_card < top.index("Inside the card.") < top_code)
        omd_assert(
            True,
            top_code
            < trailing_text
            < top_card_end
            < following_heading
            < following_text,
        )

        invalid_cards = {
            "missing.o.md": (
                "# Missing implementation :CARD:\n\nNo code here.\n",
                "exactly one code block with metadata (found 0)",
            ),
            "multiple.o.md": (
                "# Too many :CARD:\n\n"
                "```python {name=one}\none = 1\n```\n\n"
                "```python {name=two}\ntwo = 2\n```\n",
                "exactly one code block with metadata (found 2)",
            ),
            "nested.o.md": (
                "# Outer :CARD:\n\n"
                "```python {name=outer}\nouter = True\n```\n\n"
                "## Inner :CARD:\n\n"
                "```python {name=inner}\ninner = True\n```\n",
                "a card cannot contain another card",
            ),
        }
        for invalid_filename, (invalid_source, expected_error) in (
            invalid_cards.items()
        ):
            try:
                blocks.weave_card_sections(
                    invalid_source,
                    invalid_filename,
                )
            except ValueError as error:
                omd_assert(True, expected_error in str(error))
                omd_assert(True, str(error).startswith(f"{invalid_filename}:"))
            else:
                omd_assert(True, False)
        omd_assert(
            0,
            len(
                blocks.weave_card_sections(
                    "# Plain\n\n```python {name=plain}\npass\n```\n",
                    "plain.o.md",
                )
            ),
        )

        runner = os.path.join(directory, "fake_omd.py")
        with open(runner, "w", encoding="utf-8") as output:
            output.write(
                "import sys\n"
                "print('ran ' + ' '.join(sys.argv[1:]), flush=True)\n"
            )

        original_argv_zero = sys.argv[0]
        original_editor = os.environ.get("OMD_EDITOR")
        try:
            sys.argv[0] = runner
            os.environ["OMD_EDITOR"] = "/bin/true"
            try:
                server, url = blocks.weave_server("site", 0)
            except PermissionError:
                server = None
        finally:
            sys.argv[0] = original_argv_zero
            if original_editor is None:
                os.environ.pop("OMD_EDITOR", None)
            else:
                os.environ["OMD_EDITOR"] = original_editor

        if server is not None:
            server_thread = threading.Thread(
                target=server.serve_forever,
                daemon=True,
            )
            server_thread.start()
            try:
                request = urllib.request.Request(
                    url + "__omd__/run",
                    data=json.dumps({"name": "hello"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=5) as response:
                    command_output = response.read().decode("utf-8")
                omd_assert(True, "ran run hello" in command_output)
                omd_assert(True, "[exit 0]" in command_output)

                expand = urllib.request.Request(
                    url + "__omd__/expand",
                    data=json.dumps({"name": "hidden"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(expand, timeout=5) as response:
                    expand_output = response.read().decode("utf-8")
                omd_assert(True, "ran expand hidden" in expand_output)
                omd_assert(False, "[exit " in expand_output)

                edit = urllib.request.Request(
                    url + "__omd__/edit",
                    data=json.dumps(
                        {"source": "guide.o.md", "line": 10}
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(edit, timeout=5) as response:
                    edit_output = response.read().decode("utf-8")
                omd_assert(True, "Opened guide.o.md:10" in edit_output)

                invalid_edit = urllib.request.Request(
                    url + "__omd__/edit",
                    data=json.dumps(
                        {"source": "../outside.o.md", "line": 1}
                    ).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    urllib.request.urlopen(invalid_edit, timeout=5)
                    omd_assert(True, False)
                except urllib.error.HTTPError as error:
                    omd_assert(403, error.code)

                forbidden = urllib.request.Request(
                    url + "__omd__/run",
                    data=json.dumps({"name": "hidden"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    urllib.request.urlopen(forbidden, timeout=5)
                    omd_assert(True, False)
                except urllib.error.HTTPError as error:
                    omd_assert(403, error.code)
            finally:
                server.shutdown()
                server.server_close()
                server_thread.join(timeout=5)
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
