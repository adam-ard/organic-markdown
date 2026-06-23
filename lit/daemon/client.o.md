# Daemon client and startup

The client first validates an existing record by making a real request. When no
daemon answers, an exclusive lock elects one starter. Other simultaneous
clients wait for the published record. A stale lock is reclaimed after the
bounded startup window. The daemon is detached using the platform facilities
provided by `subprocess`.

`omd kill` is intentionally different from normal daemon calls: it should only
stop an already-running daemon for the current directory, not start a new daemon
just so it can be stopped. For that reason `daemon_kill()` reads the registry
directly, sends the server's existing `stop` operation when possible, and cleans
up stale registry records when the process is already gone.

```python {name=daemon_client}
def daemon_read_record(registry_path, root):
    try:
        with open(registry_path, "r", encoding="utf-8") as source:
            record = json.load(source)
        if (record.get("protocol") != DAEMON_PROTOCOL
                or record.get("version") != "@<version@>"
                or record.get("root") != root):
            return None
        return record
    except (OSError, ValueError):
        return None

def daemon_start(root, registry_path, lock_path):
    # Large projects invoke Pandoc once per source file during first startup.
    # Keep the bound generous while still allowing a crashed starter's lock to
    # be reclaimed.
    deadline = time.monotonic() + 120
    owns_lock = False
    while time.monotonic() < deadline:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(descriptor)
            owns_lock = True
            break
        except FileExistsError:
            record = daemon_read_record(registry_path, root)
            if record:
                return record
            if time.time() - os.path.getmtime(lock_path) > 120:
                try:
                    os.remove(lock_path)
                except FileNotFoundError:
                    pass
            time.sleep(0.05)
    if not owns_lock:
        raise RuntimeError("timed out starting the project daemon")
    try:
        token = secrets.token_hex(32)
        command = [sys.executable, os.path.abspath(__file__), "--omd-daemon", root, token, registry_path]
        options = {"cwd": root, "stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "close_fds": True}
        if os.name == "nt":
            options["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            options["start_new_session"] = True
        process = subprocess.Popen(command, **options)
        while time.monotonic() < deadline:
            record = daemon_read_record(registry_path, root)
            if record:
                return record
            if process.poll() is not None:
                raise RuntimeError("project daemon failed during initial parse")
            time.sleep(0.05)
        raise RuntimeError("project daemon did not become ready")
    finally:
        try:
            os.remove(lock_path)
        except FileNotFoundError:
            pass

def daemon_call(root, operation, **values):
    root = daemon_project_root(root)
    registry_path, lock_path = daemon_paths(root)
    record = daemon_read_record(registry_path, root)
    if record:
        try:
            response = daemon_request(record, operation, **values)
            if response.get("ok"):
                return response
            raise RuntimeError(response.get("error", "daemon request failed"))
        except RuntimeError:
            raise
        except (OSError, ValueError, ConnectionError):
            pass
        try:
            os.remove(registry_path)
        except FileNotFoundError:
            pass
    record = daemon_start(root, registry_path, lock_path)
    response = daemon_request(record, operation, **values)
    if not response.get("ok"):
        raise RuntimeError(response.get("error", "daemon request failed"))
    return response

def daemon_snapshot(root):
    response = daemon_call(root, "snapshot")
    return pickle.loads(base64.b64decode(response["snapshot"]))

def daemon_reparse(root, filename):
    try:
        daemon_call(root, "reparse", filename=filename)
        return 0
    except Exception as error:
        print(f"reparse failed: {error}", file=sys.stderr)
        return 1

def daemon_reload(root):
    daemon_call(root, "reload")
    return daemon_snapshot(root)

def daemon_kill(root):
    root = daemon_project_root(root)
    registry_path, _lock_path = daemon_paths(root)
    record = daemon_read_record(registry_path, root)
    if not record:
        return 0
    try:
        response = daemon_request(record, "stop")
        if not response.get("ok"):
            print(f"kill failed: {response.get('error', 'daemon request failed')}", file=sys.stderr)
            return 1
    except (OSError, ValueError, ConnectionError):
        pass
    try:
        os.remove(registry_path)
    except FileNotFoundError:
        pass
    return 0
```
