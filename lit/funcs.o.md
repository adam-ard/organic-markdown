# Functions

This section includes all the top-level function definitions used throughout `omd`.

Some of these are simple utilities (like whitespace trimming or string parsing), while others form the core of how `omd` processes and generates code from literate files. You can think of this as the tool's functional backbone.

Each function is documented and defined in its own separate file. Here, we’re just wiring them together to build the final output in the correct order.

---

### 🔗 `@<funcs@>`

```python {name=funcs}
@<get_max_lines@>
@<write_if_different@>
@<parse_menu_attrib@>
@<intersperse@>
@<split_lines@>
@<get_match@>
@<parse_name@>
@<parse_exec@>
@<parse_args_str@>
@<parse_default@>
@<parse_match@>
@<eat_ws@>
@<eat_eq@>
@<parse_arg_name@>
@<parse_arg_value@>
@<parse_arg_name_value@>
@<parse_args@>
@<escape_code@>
@<import_file@>
```
