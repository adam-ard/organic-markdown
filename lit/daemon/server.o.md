# Project daemon server

The server parses once before publishing its port. Snapshot reads and reparses
are serialized by the single-threaded TCP server. Reparsing validates that the
requested path stays inside the project; parsing completes before replacing a
file contribution, so a failure leaves the previous snapshot intact. Socket
timeouts provide the idle shutdown without a monitoring thread.

```python {name=daemon_server}
class OmdDaemonHandler(socketserver.BaseRequestHandler):
    def handle(self):
        server = self.server
        try:
            request = daemon_receive(self.request)
            if not secrets.compare_digest(request.get("token", ""), server.token):
                daemon_send(self.request, {"ok": False, "error": "authentication failed"})
                return
            operation = request.get("operation")
            if operation == "snapshot":
                payload = base64.b64encode(pickle.dumps(server.code_blocks)).decode("ascii")
                response = {"ok": True, "snapshot": payload}
            elif operation == "reparse":
                filename = request.get("filename", "")
                absolute = os.path.realpath(os.path.join(server.root, filename))
                if os.path.commonpath([server.root, absolute]) != server.root:
                    raise ValueError("reparse path is outside the project")
                relative = os.path.relpath(absolute, server.root)
                server.code_blocks.reparse_file(relative)
                response = {"ok": True}
            elif operation == "reload":
                replacement = CodeBlocks()
                replacement.parse()
                server.code_blocks = replacement
                response = {"ok": True}
            elif operation == "stop":
                response = {"ok": True}
                server.stop_requested = True
            else:
                raise ValueError("unknown daemon operation")
        except Exception as error:
            response = {"ok": False, "error": str(error)}
        daemon_send(self.request, response)

class OmdDaemonServer(socketserver.TCPServer):
    allow_reuse_address = False

def daemon_main(root, token, registry_path):
    root = daemon_project_root(root)
    os.chdir(root)
    code_blocks = CodeBlocks()
    code_blocks.parse()
    with OmdDaemonServer(("127.0.0.1", 0), OmdDaemonHandler) as server:
        server.root = root
        server.token = token
        server.code_blocks = code_blocks
        server.stop_requested = False
        server.timeout = DAEMON_IDLE_SECONDS
        record = {"protocol": DAEMON_PROTOCOL, "version": "@<version@>", "root": root, "port": server.server_address[1], "token": token, "pid": os.getpid()}
        temporary = registry_path + ".new"
        with open(temporary, "w", encoding="utf-8") as output:
            json.dump(record, output)
        os.chmod(temporary, 0o600)
        os.replace(temporary, registry_path)
        try:
            while not server.stop_requested:
                before = time.monotonic()
                server.handle_request()
                if time.monotonic() - before >= DAEMON_IDLE_SECONDS - 1:
                    break
        finally:
            try:
                with open(registry_path, "r", encoding="utf-8") as source:
                    current = json.load(source)
                if current.get("pid") == os.getpid():
                    os.remove(registry_path)
            except (FileNotFoundError, ValueError):
                pass
```
