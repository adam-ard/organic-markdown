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
            if self.path != "/__omd__/run":
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
                name = payload.get("name")
            except (ValueError, json.JSONDecodeError, AttributeError):
                self.send_text_error(400, "Invalid command request.\n")
                return

            block = code_blocks.get_code_block(name)
            if block is None or not block.in_menu:
                self.send_text_error(403, "Command is not available.\n")
                return

            try:
                process = subprocess.Popen(
                    [sys.executable, omd_executable, "run", name],
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
                self.wfile.write(f"\n[exit {return_code}]\n".encode("utf-8"))
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
      --command-block: #eef1fb;
      --command-line: #b9c5e7;
      --command-code: #e4e9f8;
      --command-accent: #405da8;
      --file-block: #faf2e3;
      --file-line: #dfc38e;
      --file-code: #f3e7d1;
      --file-accent: #986408;
      --example-block: #f6eef9;
      --example-line: #d7bce2;
      --example-code: #f0e5f4;
      --example-accent: #81519a;
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
        --example-block: #291e2e;
        --example-line: #664775;
        --example-code: #322339;
        --example-accent: #d6a6ea;
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
    .omd-card-example {{
      --card-bg: var(--example-block);
      --card-line: var(--example-line);
      --card-code: var(--example-code);
      --card-accent: var(--example-accent);
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
    .omd-code-panel.has-language pre {{
      padding-top: 1.65rem;
    }}
    .omd-language-label {{
      position: absolute;
      top: 0;
      left: 1rem;
      z-index: 1;
      transform: translateY(-50%);
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
    @media (min-width: 1000px) {{
      body.omd-runner-open main {{
        width: min(calc(54vw - 3rem), 980px);
        margin-left: 2rem;
        margin-right: auto;
      }}
    }}
    @media (max-width: 640px) {{
      main {{ width: 100%; margin: 0; border: 0; border-radius: 0; }}
      .omd-runner {{ width: 100%; }}
    }}
  </style>
</head>
<body>
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
  <script>
    (() => {{
      const runner = document.querySelector("#omd-runner");
      const output = document.querySelector("#omd-runner-output");
      const title = document.querySelector("#omd-runner-title");

      document.querySelector("#omd-runner-close").addEventListener("click", () => {{
        runner.hidden = true;
        document.body.classList.remove("omd-runner-open");
      }});
      document.querySelector("#omd-runner-clear").addEventListener("click", () => {{
        output.textContent = "";
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
          if (!response.ok) {{
            output.textContent += await response.text();
            return;
          }}

          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          while (true) {{
            const {{ value, done }} = await reader.read();
            if (done) break;
            output.textContent += decoder.decode(value, {{ stream: true }});
            output.scrollTop = output.scrollHeight;
          }}
          output.textContent += decoder.decode();
        }} catch (error) {{
          output.textContent +=
            `Unable to run command. Open this weave with "omd serve <dest>".\\n${{error}}\\n`;
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
    elif not name:
        kind = "example"
        title = None
        hidden_attributes = set()
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
    panel_class = "omd-code-panel"
    language_label = ""
    if language:
        language_class = f' class="language-{html.escape(language, quote=True)}"'
        panel_class += " has-language"
        language_label = (
            '<div class="omd-language-label">'
            f"{html.escape(language)}</div>"
        )
    return (
        f'<div class="{panel_class}">'
        f"{language_label}<pre><code{language_class}>"
        + "".join(rendered)
        + "</code></pre></div>"
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

        attributes = self.weave_metadata_attributes(metadata, language)
        card_kind, card_title, visible_attributes = self.weave_card_info(
            name,
            attributes,
        )
        details = [
            f"::: {{.omd-code-block .omd-card-{card_kind}}}",
            "",
            (
                f'<div id="omd-code-{code_block_number}" '
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
            if card_kind == "command":
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
        for key, value in visible_attributes:
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
    body = pypandoc.convert_text(
        markdown,
        "html",
        format="md",
        extra_args=["--mathml"],
    )
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
                f"# Guide\n\n$$\\bar K(p)=\\frac{{2\\pi}}{{n}}I(p).$$\n\n"
                f"The answer is {answer_ref}.\n"
                f"This same-file reference is {hello_ref}.\n\n"
                f"The nested tool is {tool_ref}.\n\n"
                "```python {name=hello menu=true}\n"
                f'print("{answer_ref}")\n'
                "```\n"
            )
        with open("nested/tool.o.md", "w", encoding="utf-8") as output:
            output.write(
                f"# Tool\n\nUses {hello_ref}.\n\n"
                "```bash {name=tool}\necho tool\n```\n\n"
                "```text\nunnamed\n```\n\n"
                "```python {name=answer tangle=generated/answer.py}\n"
                "answer = 42\n```\n"
            )

        blocks = CodeBlocks(["guide.o.md", "nested/tool.o.md"])
        blocks.weave("site")

        with open("site/guide.html", "r", encoding="utf-8") as source:
            guide = source.read()
        with open("site/nested/tool.html", "r", encoding="utf-8") as source:
            tool = source.read()

        omd_assert(True, guide.startswith("<!doctype html>"))
        omd_assert(True, "<title>guide</title>" in guide)
        omd_assert(True, "<math" in guide)
        omd_assert(True, "<mfrac>" in guide)
        omd_assert(True, "--code: #e8f0ec;" in guide)
        omd_assert(True, "border: 1px solid var(--code-line);" in guide)
        omd_assert(True, "omd-card-command" in guide)
        omd_assert(True, "background: var(--card-bg);" in guide)
        omd_assert(True, "transform: translateY(-50%);" in guide)
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
        omd_assert(True, 'id="omd-runner-output"' in guide)
        omd_assert(True, 'fetch("/__omd__/run"' in guide)
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
        omd_assert(
            True,
            '<h4 class="omd-code-title">' in tool
            and "omd-card-example" in tool,
        )
        omd_assert(False, "Unnamed code block" in tool)
        omd_assert(True, "omd-code-title kind-only" in tool)
        omd_assert(True, "example</span>" in tool)
        omd_assert(True, "omd-card-code" in tool)
        omd_assert(True, "omd-card-file" in tool)
        omd_assert(
            False,
            '<button type="button" class="omd-run-command"' in tool,
        )
        omd_assert(True, "generated/answer.py" in tool)
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

        runner = os.path.join(directory, "fake_omd.py")
        with open(runner, "w", encoding="utf-8") as output:
            output.write(
                "import sys\n"
                "print(f'ran {sys.argv[-1]}', flush=True)\n"
            )

        original_argv_zero = sys.argv[0]
        try:
            sys.argv[0] = runner
            try:
                server, url = blocks.weave_server("site", 0)
            except PermissionError:
                server = None
        finally:
            sys.argv[0] = original_argv_zero

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
                omd_assert(True, "ran hello" in command_output)
                omd_assert(True, "[exit 0]" in command_output)

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
