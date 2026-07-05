# Parsed project cache

The parsed project cache is a generated artifact stored in the current project
directory. It lets ordinary `omd` invocations skip Pandoc work when the `.o.md`
files have not changed, while keeping all command execution in the foreground
process. That foreground ownership matters for `omd run`, terminal behavior,
environment variables, and `@<name*@>` execution during expansion.

The cache records the OMD version, canonical root, and cheap validity metadata
for every source file. On each load, OMD stats the current `.o.md` files. If the
cache is missing or incompatible, the whole project is parsed and written. If
the cache is usable but a subset of files changed, only those files are reparsed
and deleted files are removed before the refreshed object is written back. The
pickle is therefore treated like tangled source: useful when present, safe to
delete, and never the source of truth.

```python {name=parsed_project_cache}
OMD_CACHE_FILE = ".omd-cache.pickle"

def omd_project_root(root):
    return os.path.realpath(os.path.abspath(root))

def omd_source_files(root):
    files = []
    for cur_root, _dirs, cur_files in os.walk(root):
        for cur_file in cur_files:
            full_path = os.path.join(cur_root, cur_file)
            if full_path.endswith(".o.md"):
                files.append(os.path.normpath(os.path.relpath(full_path, root)))
    return files

def omd_source_metadata(files):
    metadata = {}
    for filename in files:
        stat = os.stat(filename)
        metadata[filename] = {"mtime_ns": stat.st_mtime_ns, "size": stat.st_size}
    return metadata

def omd_read_cache(cache_path, root):
    try:
        with open(cache_path, "rb") as source:
            payload = pickle.load(source)
    except (OSError, ValueError, pickle.PickleError, EOFError):
        return None

    if payload.get("version") != "@<version@>":
        return None
    if payload.get("root") != root:
        return None
    code_blocks = payload.get("code_blocks")
    if code_blocks is None:
        return None
    if not hasattr(code_blocks, "file_contributions") or not hasattr(code_blocks, "file_order"):
        return None
    return payload

def omd_write_cache(cache_path, root, metadata, code_blocks):
    payload = {
        "version": "@<version@>",
        "root": root,
        "files": metadata,
        "code_blocks": code_blocks,
    }
    temporary = cache_path + ".new"
    with open(temporary, "wb") as output:
        pickle.dump(payload, output)
    os.replace(temporary, cache_path)

def omd_load_code_blocks(root):
    root = omd_project_root(root)
    cache_path = os.path.join(root, OMD_CACHE_FILE)
    files = omd_source_files(root)
    metadata = omd_source_metadata(files)

    payload = omd_read_cache(cache_path, root)
    if payload is None:
        code_blocks = CodeBlocks()
        code_blocks.parse()
        omd_write_cache(cache_path, root, metadata, code_blocks)
        return code_blocks

    code_blocks = payload["code_blocks"]
    cached_metadata = payload.get("files", {})
    if any(filename not in code_blocks.file_contributions for filename in files):
        code_blocks = CodeBlocks()
        code_blocks.parse()
        omd_write_cache(cache_path, root, metadata, code_blocks)
        return code_blocks

    stale_files = [filename for filename in files if cached_metadata.get(filename) != metadata[filename]]
    deleted_files = [filename for filename in cached_metadata if filename not in metadata]

    if stale_files or deleted_files or code_blocks.file_order != files:
        for filename in deleted_files:
            code_blocks.reparse_file(filename)
        for filename in stale_files:
            code_blocks.reparse_file(filename)
        code_blocks.file_order = files
        code_blocks.rebuild()
        omd_write_cache(cache_path, root, metadata, code_blocks)
    else:
        code_blocks.rebuild()

    return code_blocks
```

# Tests

The cache tests use a fake Pandoc adapter so they can prove the important cache
behavior without paying the real parser cost. The first load parses every file
and writes a cache. The second load returns the cached object without parsing.
After a source file changes, only that file is reparsed and the unchanged file's
contribution is reused.

```python {name=parsed_project_cache_tests menu=true}
@<imports@>
@<omd_assert@>

class CodeBlock:
    def __init__(self):
        self.name = None
        self.code = ""
        self.origin_file = None
        self.code_blocks = None

    def parse(self, value):
        self.name = value[0][0]
        self.code = value[1]

class FakePandoc:
    calls = []

    @staticmethod
    def convert_file(filename, _output, format=None):
        FakePandoc.calls.append(filename)
        with open(filename, "r", encoding="utf-8") as source:
            code = source.read()
        name = os.path.basename(filename)[:-len(".o.md")]
        return json.dumps({"meta": {}, "blocks": [
            {"t": "CodeBlock", "c": [[name, [], []], code]}
        ]})

pypandoc = FakePandoc

class CodeBlocks:
    def __init__(self):
        self.code_blocks = []
        self.file_contributions = {}
        self.file_order = []

    def get_code_block(self, name):
        for block in self.code_blocks:
            if block.name == name:
                return block

    @<codeblocks__parse@>

@<parsed_project_cache@>

with tempfile.TemporaryDirectory() as directory:
    original = os.getcwd()
    try:
        os.chdir(directory)
        with open("one.o.md", "w", encoding="utf-8") as output:
            output.write("one")
        with open("two.o.md", "w", encoding="utf-8") as output:
            output.write("two")

        FakePandoc.calls = []
        blocks = omd_load_code_blocks(directory)
        omd_assert(["one.o.md", "two.o.md"], sorted(FakePandoc.calls))
        omd_assert("one", blocks.get_code_block("one").code)

        FakePandoc.calls = []
        blocks = omd_load_code_blocks(directory)
        omd_assert([], FakePandoc.calls)
        omd_assert("two", blocks.get_code_block("two").code)

        with open("one.o.md", "w", encoding="utf-8") as output:
            output.write("changed")

        FakePandoc.calls = []
        blocks = omd_load_code_blocks(directory)
        omd_assert(["one.o.md"], FakePandoc.calls)
        omd_assert("changed", blocks.get_code_block("one").code)
        omd_assert("two", blocks.get_code_block("two").code)
    finally:
        os.chdir(original)

@<test_passed(name="Parsed Project Cache")@>
```
