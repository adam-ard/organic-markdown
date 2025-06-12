# Run all tests

We could just add to this list in the individual test files and delete this file eventually.

```bash {name=all_tests menu=true}
set -e

omd run main_code_tests
omd run handle_cmd_tests
omd run f_parse_menu_attrib_tests
omd run intersperse_tests
omd run get_run_cmd_tests

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
@<expand_tests@>
```
