# `CodeBlocks::expand`

This is the **core engine** of Organic Markdown.
Everything dynamic—literate references, substitutions, code output injection, templates with arguments—is powered by this elegant yet deeply recursive expansion system.

Despite its brevity, this function enables:

* Named reference substitution: `@<name@>`
* Execution injection: `@<name*@>`
* Defaults: `@<name{default}@>`
* Argument passing: `@<template(arg=value)@>`
* Nesting, recursion, and multi-line expansion

It’s deceptively small—and very sensitive to change—but it's where all the magic happens.

---

### How it Works

* `expand(txt)` splits input into lines, and processes each line via `expand_line()`.
* `expand_line()`:

  * Scans the string for the next literate reference (e.g., `@<foo@>`)
  * If found:

    * Expands arguments, defaults, and whether it should execute (`*@`)
    * Recursively expands the referenced content or command output
    * Splices it into the output string
  * If not found:

    * Appends the rest of the string
  * Returns the fully resolved, recursively substituted line.
* The final output is reassembled line-by-line using `intersperse()` to preserve context and indentation.

---

### 🔗 `@<codeblocks__expand@>`

```python {name=codeblocks__expand}
def expand(self, txt, args={}):
    return "\n".join(
        [self.expand_line(x, args) for x in split_lines(txt)]
    )

def expand_line(self, txt, args={}):
    out = []
    while True:
        match = get_match(txt)
        if match is None:
            out.append(txt)
            break

        out.append(txt[:match["start"]])

        name = match["name"]
        new_args = parse_args(match["args"])
        blk = self.get_code_block(name)

        # Case 1: An argument override is provided
        if args is not None and name in args:
            out.append(self.expand(args[name], args | new_args))

        # Case 2: No block exists — use the default
        elif blk is None:
            out.append(self.expand(match["default"], args | new_args))

        # Case 3: Execute block and insert result
        elif match["exec"]:
            out.append(self.expand(blk.run_return_results(args | new_args), args | new_args))

        # Case 4: Regular substitution
        else:
            out.append(self.expand(blk.code, args | new_args))

        txt = txt[match["end"]:]

    return intersperse(out)
```

---

# 🧪 Testing

This functionality is tested using a parallel syntax that replaces `@<...@>` with `:<...:>` to prevent substitutions from interfering during the tangle phase.

The test suite covers:

* Basic substitution
* Nested substitution
* Execution injection
* Argument passing
* Indentation preservation
* Infinite loop protection
* Recursion
* Defaults
* Missing values

---

Here is some test data, representing a full file:

```python {name=full_file}
meta_block = { "constants": {
    "t": "MetaMap",
    "c": {
        "code_dir": {
            "t": "MetaInlines",
            "c": [
                {
                    "t": "Str",
                    "c": "~/code"
                }
            ]
        },
        "project_name_recurse": {
            "t": "MetaInlines",
            "c": [
                {
                    "t": "Str",
                    "c": ":<project_name:>"
                }
            ]
        }
    }
}}

code_block_append1 = [["",
                       [],
                       [["name", "append"],
                        ]],
                      "1"]

code_block_append2 = [["",
                       [],
                       [["name", "append"],
                        ]],
                      "2"]

code_block_append3 = [["",
                       [],
                       [["name", "append"],
                        ]],
                      "3"]

code_block_append4 = [["",
                       [],
                       [["name", "append"],
                        ]],
                      "4"]

code_block_append1_no_name = [["", [], []], "no_name_1"]
code_block_append2_no_name = [["", [], []], "no_name_2"]
code_block_append3_no_name = [["", [], []], "no_name_3"]
code_block_append4_no_name = [["", [], []], "no_name_4"]

code_block_3_lines = [["",
                       [],
                       [["name", "three_lines"],
                        ]],
                      "1\n2\n3"]

code_block_b = [["",
                 [],
                 [["name", "b"],
                  ]],
                "1\n2"]

code_block_d = [["",
                 [],
                 [["name", "d"],
                  ]],
                "3\n4"]

code_block_1 = [["",
                   [],
                   [["name", "one"],
                    ]],
                  "[This is some text]"]

code_block_2 = [["",
                   [],
                   [["name", "two"],
                    ]],
                  "[This is the text from block one::<one:>, wasn't that nice?]"]

code_block_2_1 = [["",
                   [],
                   [["name", "two_1"],
                    ]],
                  "[This is the text from block one::<one*:>, wasn't that nice?]"]

code_block_2_sentences = [["",
                           [],
                           [["name", "two_sentences"],
                            ]],
                          "This is sentence 1 - :<one:>\nThis is sentence 2 - :<one:>"]

code_block_3 = [["",
                     [],
                     [["name", "three"],
                      ]],
                    "[This is the text from block two::<two:>, can you believe it?]"]

code_block_3_1 = [["",
                   [],
                   [["name", "msg"],
                    ]],
                  "this is great"]

code_block_4 = [["",
                    ["bash"],
                    [["name", "four"],
                     ["menu", "true"],
                     ["dir", "."],
                     ]],
                   'echo :<msg:>']

code_block_5 = [["",
                    ["python"],
                    [["name", "five"],
                     ["menu", "true"],
                     ["dir", "."],
                     ]],
                   'print("I am python!! :<msg:>")']


indent_2 = [["",
             [],
             [["name", "indent_2"],
              ]],
            f"""one
two
three
four"""]

# note that I use the {""} syntax so when I run whitespace-cleanup it doesn't mess with the spaces
indent_3 = [["",
             [],
             [["name", "indent_3"],
              ]],
            f"""one
    {""}

two
  three
four"""]

indent_4 = [["",
             [],
             [["name", "indent_4"],
              ]],
            """indent_block {
    :<indent_3:>
}"""]

indent_5 = [["",
             [],
             [["name", "indent_5"],
              ]],
            f"""one
{"    "}

two
  three
four"""]

indent_6 = [["",
             [],
             [["name", "indent_6"],
              ]],
            """indent_block {
    // :<indent_5:>
}"""]



full_file = {"blocks": [{"t": "",
                         "c": meta_block
                         },
                        {"t": "CodeBlock",
                         "c": code_block_1
                         },
                        {"t": "CodeBlock",
                         "c": code_block_3_lines
                         },
                        {"t": "CodeBlock",
                         "c": code_block_b
                         },
                        {"t": "CodeBlock",
                         "c": code_block_append1
                         },
                        {"t": "CodeBlock",
                         "c": code_block_2_sentences
                         },
                        {"t": "CodeBlock",
                         "c": code_block_append2
                         },
                        {"t": "CodeBlock",
                         "c": code_block_append3
                         },
                        {"t": "CodeBlock",
                         "c": code_block_append4
                         },
                        {"t": "CodeBlock",
                         "c": code_block_append1_no_name
                         },
                        {"t": "CodeBlock",
                         "c": code_block_append2_no_name
                         },
                        {"t": "CodeBlock",
                         "c": code_block_append3_no_name
                         },
                        {"t": "CodeBlock",
                         "c": code_block_append4_no_name
                         },
                        {"t": "CodeBlock",
                         "c": code_block_d
                         },
                        {"t": "CodeBlock",
                         "c": code_block_2
                         },
                        {"t": "CodeBlock",
                         "c": code_block_2_1
                         },
                        {"t": "CodeBlock",
                         "c": indent_2
                         },
                        {"t": "CodeBlock",
                         "c": indent_3
                         },
                        {"t": "CodeBlock",
                         "c": indent_4
                         },
                        {"t": "CodeBlock",
                         "c": indent_5
                         },
                        {"t": "CodeBlock",
                         "c": indent_6
                         },
                        {"t": "CodeBlock",
                         "c": code_block_3
                         },
                        {"t": "CodeBlock",
                         "c": code_block_3_1
                         },
                        {"t": "CodeBlock",
                         "c": code_block_5
                         },
                        {"t": "CodeBlock",
                         "c": code_block_4
                         },],
             "pandoc-api-version": [1, 20],
             "meta": meta_block
             }
```

### 🧪 Expand Tests

```python {name=expand_tests menu=true}
@<imports@>

o_sym = ":<"
c_sym = ":>"

@<omd_assert@>
@<full_file@>

@<funcs@>
@<class__codeblock@>

class CodeBlocks:
    def __init__(self):
        self.code_blocks = []
    @<codeblocks__get_code_block@>
    @<codeblocks__parse@>
    @<codeblocks__expand@>

blks = CodeBlocks()
blks.parse_json(full_file, "test_file.omd")

def test(txt, expected_expanded):
    expanded = blks.expand(txt)
    omd_assert(expected_expanded, expanded)

test(':<three(two="asdf"):>', "[This is the text from block two:asdf, can you believe it?]")
test(':<two(one="qwerty"):>', "[This is the text from block one:qwerty, wasn't that nice?]")
test(':<four*:>', "this is great")
test(':<five*(msg="asdf"):>', "I am python!! asdf")
test(':<two_sentences(one=":<three_lines:>"):>', """This is sentence 1 - 1
This is sentence 1 - 2
This is sentence 1 - 3
This is sentence 2 - 1
This is sentence 2 - 2
This is sentence 2 - 3""")
test(':<four*(msg="here is a msg"):>', "here is a msg")
test(':<two_1(one="qwerty"):>', "[This is the text from block one:qwerty, wasn't that nice?]")
test(':<indent_4:>', f"""indent_block {{
    one
        {""}
    {""}
    two
      three
    four
}}""")
test(':<indent_6:>', f"""indent_block {{
    // one
    // {"    "}
    // {""}
    // two
    //   three
    // four
}}""")


test('--->:<indent_2:>:<one:><-----', """--->one[This is some text]<-----
--->two[This is some text]<-----
--->three[This is some text]<-----
--->four[This is some text]<-----""")

# this will cause an infinite loop if we do this wrong
test('a:<b:>c:<d:>e', "a1c3e\na2c4e")
test("a:<three(two=\n2):>b", "a[This is the text from block two:2, can you believe it?]b")
test(':<append:>', "1\n2\n3\n4")
test(':<code_dir:>', "~/code")
test(':<project_name_recurse:>', "")
test(':<asdfasdfasdf:>', "")

test("[This is the text from block two::<two:>, can you believe it?]", "[This is the text from block two:[This is the text from block one:[This is some text], wasn't that nice?], can you believe it?]")
@<test_passed(name="expand")@>
```
