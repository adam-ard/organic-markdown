# Daemon runtime

The daemon runtime is assembled from small protocol, server, and client units.
It deliberately transfers a pickled `CodeBlocks` snapshot only after a
token-authenticated loopback connection. The foreground CLI therefore keeps
all execution and terminal semantics while Pandoc parsing remains resident in
one process per canonical working directory.

```python {name=daemon_runtime}
@<daemon_paths@>
@<daemon_protocol@>
@<daemon_server@>
@<daemon_client@>
```

