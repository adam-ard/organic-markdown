# Main

Every good program starts with a `main`—and this one is no exception.

In Python, the special variable `__name__` is set to `"__main__"` when the file is run directly. This allows us to distinguish between two use cases:

* Running the file as a **standalone script** (when we do want to run the main logic), and
* Importing the file as a **module** (when we don’t want any top-level code to execute automatically).

This pattern helps keep `omd` both scriptable and import-friendly.

---

### 🔗 `@<main@>`

```python {name=main}
if __name__ == '__main__':
    @<main_code@>
```
