# Run all tests

We could just add to this list in the individual test files and delete this file eventually.

```bash {name=all_tests menu=true}
set -e

tests/main_code.py
tests/handle_cmd.py
tests/f_parse_menu_attrib.py
@<intersperse_tests@>
@<get_run_cmd_tests@>
@<codeblock__parse_tests@>
@<split_lines_tests@>
@<eat_tests@>
@<parse_name_tests@>
@<parse_exec_tests@>
@<parse_args_str_tests@>
```
