# Run all tests

We could just add to this list in the individual test files and delete this file eventually.

### @<all_tests@>

```bash {name=all_tests menu=true}
set -e

tests/main_code.py
tests/handle_cmd.py
tests/f_parse_menu_attrib.py
@<intersperse_tests@>
```
