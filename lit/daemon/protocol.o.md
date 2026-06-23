# Loopback protocol

Each connection carries one newline-terminated JSON request and response.
Snapshot bytes are base64 encoded because JSON keeps diagnostics and protocol
versioning inspectable. Requests are bounded to prevent an accidental or
hostile local client from consuming unbounded memory.

```python {name=daemon_protocol}
DAEMON_PROTOCOL = 2

def daemon_send(sock, value):
    sock.sendall(json.dumps(value).encode("utf-8") + b"\n")

def daemon_receive(sock):
    data = bytearray()
    while not data.endswith(b"\n"):
        chunk = sock.recv(65536)
        if not chunk:
            raise ConnectionError("daemon closed the connection")
        data.extend(chunk)
        if len(data) > 256 * 1024 * 1024:
            raise ValueError("daemon message is too large")
    return json.loads(data.decode("utf-8"))

def daemon_request(record, operation, **values):
    with socket.create_connection(("127.0.0.1", record["port"]), timeout=10) as sock:
        daemon_send(sock, {"token": record["token"], "operation": operation, **values})
        return daemon_receive(sock)
```
