# Run all tests

We could just add to this list in the individual test files and delete this file eventually.

```bash {name=all_tests menu=true}
set -e

@<main_code_tests@>
@<handle_cmd_tests@>
@<f_parse_menu_attrib_tests@>
@<intersperse_tests@>
@<get_run_cmd_tests@>
@<codeblock__parse_tests@>
@<split_lines_tests@>
@<eat_tests@>
@<parse_name_tests@>
@<parse_exec_tests@>
@<parse_args_str_tests@>
@<parse_arg_name_tests@>
@<parse_arg_value_tests@>
@<parse_default_tests@>
@<parse_arg_name_value_tests@>
@<parse_args_tests@>
@<parse_match_tests@>
@<get_match_tests@>
```
