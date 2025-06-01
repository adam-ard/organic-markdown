---
constants:
  open_sym: \@<
  close_sym: \@>
---

# Globals

This section defines the global data used throughout the `omd` system.

These constants control the supported languages and the special symbols used to mark substitution points in the source.

### 🔗 `@<globals@>`

```python {name=globals}
languages = ["bash", "python", "ruby", "haskell", "racket", "perl", "javascript"]
o_sym = "@<open_sym@>"
c_sym = "@<close_sym@>"
```
