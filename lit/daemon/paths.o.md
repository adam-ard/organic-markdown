# Per-project daemon files

Runtime records live in a user-specific temporary directory and are keyed by
the canonical project path. A token in the record authenticates requests; the
record is not a durable cache and may be discarded at any time.

```python {name=daemon_paths}
DAEMON_IDLE_SECONDS = 30 * 60

def daemon_project_root(root):
    return os.path.realpath(os.path.abspath(root))

def daemon_paths(root):
    root = daemon_project_root(root)
    key = hashlib.sha256(root.encode("utf-8")).hexdigest()[:24]
    runtime_dir = os.path.join(tempfile.gettempdir(), f"omd-{os.getuid() if hasattr(os, 'getuid') else os.environ.get('USERNAME', 'user')}")
    os.makedirs(runtime_dir, mode=0o700, exist_ok=True)
    return (
        os.path.join(runtime_dir, key + ".json"),
        os.path.join(runtime_dir, key + ".lock"),
    )
```

