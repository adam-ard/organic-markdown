# Main

Any good program starts with main. This one is no exception. Python
sets a global variable called `__name__` to the value `__main__` if
you happen to be calling it as a program. This helps you distiguish
from when the file is being used as a library that has been import (in
which case you would not want to run any "main" code, because you have
a main already in the program the is importing you as a
library).

```python {name=main}
if __name__ == '__main__':
    @<main_code@>
```

