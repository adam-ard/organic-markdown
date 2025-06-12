# Run all tests

We could just add to this list in the individual test files and delete this file eventually.

```bash {name=all_tests menu=true}
set -e

omd run main_code_tests
omd run handle_cmd_tests
omd run f_parse_menu_attrib_tests
omd run intersperse_tests
omd run get_run_cmd_tests
omd run codeblock__parse_tests
omd run split_lines_tests
omd run eat_tests
omd run parse_name_tests
omd run parse_exec_tests
omd run parse_args_str_tests
omd run parse_arg_name_tests
omd run parse_arg_value_tests
omd run parse_default_tests
omd run parse_arg_name_value_tests
omd run parse_args_tests
omd run parse_match_tests
omd run get_match_tests
omd run expand_tests
```
