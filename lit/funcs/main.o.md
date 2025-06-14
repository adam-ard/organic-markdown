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
@<import_file@>
```

### @<funcs@> used

- [@<code@>](code.o.md)

### @<funcs@> deps

- [@<get_max_lines@>](get_max_lines.o.md)
- [@<write_if_different@>](f_write_if_different.o.md)
- [@<parse_menu_attrib@>](f_parse_menu_attrib.o.md)
- [@<intersperse@>](intersperse.o.md)
- [@<split_lines@>](split_lines.o.md)
- [@<get_match@>](get_match.o.md)
- [@<parse_name@>](parse_name.o.md)
- [@<parse_exec@>](parse_exec.o.md)
- [@<parse_args_str@>](parse_args_str.o.md)
- [@<parse_default@>](parse_default.o.md)
- [@<parse_match@>](parse_match.o.md)
- [@<eat_ws@>](eat.o.md)
- [@<eat_eq@>](eat.o.md)
- [@<parse_arg_name@>](parse_arg_name.o.md)
- [@<parse_arg_value@>](parse_arg_value.o.md)
- [@<parse_arg_name_value@>](parse_arg_name_value.o.md)
- [@<parse_args@>](parse_args.o.md)
- [@<import_file@>](experimental_features.o.md)
