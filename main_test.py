import omd

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
                    "c": "@<project_name@>"
                }
            ]
        }
    }
}}


code_block = [["",
               ["bash"],
               [["name", "build_project"],
                ["what_is_this", "blah"],
                ["docker", "@<docker_container_name@>"],
                ["ssh", "aard@localhost.com"],
                ["menu", "true"],
                ["dir", "@<project_name@>"],
                ["tangle", "@<project_name@>/main.c"]
                ]],
              "gcc --version"]

code_block_alt_syntax = [["",
                          ["python"],
                          [["name", "build_project"],
                           ["what_is_this", "blah"],
                           ["docker", "@<docker_container_name@>"],
                           ["ssh", "aard@localhost.com"],
                           ["menu", "true"],
                           ["dir", "@<project_name@>"],
                           ["tangle", "@<project_name@>/main.c"]
                           ]],
                         "gcc --version"]

code_block_alt_syntax2 = [["",
                           ["bash"],
                           [["name", "build_project"],
                            ["what_is_this", "blah"],
                            ["docker", "@<docker_container_name@>"],
                            ["ssh", "aard@localhost.com"],
                            ["menu", "true"],
                            ["dir", "@<project_name@>"],
                            ["tangle", "@<project_name@>/main.c"]
                            ]],
                          "gcc --version"]

code_block_alt_syntax3 = [["",
                           [],
                           [["name", "build_project"],
                            ["what_is_this", "blah"],
                            ["docker", "@<docker_container_name@>"],
                            ["ssh", "aard@localhost.com"],
                            ["menu", "true"],
                            ["dir", "@<project_name@>"],
                            ["tangle", "@<project_name@>/main.c"]
                            ]],
                          "gcc --version"]


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
                  "[This is the text from block one:@<one@>, wasn't that nice?]"]

code_block_2_1 = [["",
                   [],
                   [["name", "two_1"],
                    ]],
                  "[This is the text from block one:@<one*@>, wasn't that nice?]"]

code_block_2_sentences = [["",
                           [],
                           [["name", "two_sentences"],
                            ]],
                          "This is sentence 1 - @<one@>\nThis is sentence 2 - @<one@>"]

code_block_3 = [["",
                     [],
                     [["name", "three"],
                      ]],
                    "[This is the text from block two:@<two@>, can you believe it?]"]

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
                   'echo @<msg@>']

code_block_5 = [["",
                    ["python"],
                    [["name", "five"],
                     ["menu", "true"],
                     ["dir", "."],
                     ]],
                   'print("I am python!! @<msg@>")']


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
    @<indent_3@>
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
    // @<indent_5@>
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

def test_origin_file():
    code_blocks = omd.CodeBlocks()
    code_blocks.parse_json(full_file, "test_file.omd")

    def check(blk):
        assert blk.origin_file == "test_file.omd"

    code_blocks.run_all_blocks_fn(check)


def test_expand():
    code_blocks = omd.CodeBlocks()
    code_blocks.parse_json(full_file, "test_file.omd")

    blk = code_blocks.get_code_block("three")
    assert blk != None

    txt = code_blocks.expand(blk.code)
    assert txt == "[This is the text from block two:[This is the text from block one:[This is some text], wasn't that nice?], can you believe it?]"

    # test with args
    txt = code_blocks.expand('@<three(two="asdf")@>')
    assert txt == "[This is the text from block two:asdf, can you believe it?]"

    txt = code_blocks.expand('@<two(one="qwerty")@>')
    assert txt == "[This is the text from block one:qwerty, wasn't that nice?]"

    txt = code_blocks.expand('@<four*@>')
    assert txt == "this is great"

    txt = code_blocks.expand('@<five*(msg="asdf")@>')
    assert txt == "I am python!! asdf"

    txt = code_blocks.expand('@<two_sentences(one="@<three_lines@>")@>')
    assert txt == """\
This is sentence 1 - 1
This is sentence 1 - 2
This is sentence 1 - 3
This is sentence 2 - 1
This is sentence 2 - 2
This is sentence 2 - 3"""

    txt = code_blocks.expand('@<four*(msg="here is a msg")@>')
    assert txt == "here is a msg"

    txt = code_blocks.expand('@<two_1(one="qwerty")@>')
    assert txt == "[This is the text from block one:qwerty, wasn't that nice?]"

    txt = code_blocks.expand('@<indent_4@>')
    assert txt == f"""indent_block {{
    one
        {""}
    {""}
    two
      three
    four
}}"""

    txt = code_blocks.expand('@<indent_6@>')
    assert txt == f"""indent_block {{
    // one
    // {"    "}
    // {""}
    // two
    //   three
    // four
}}"""

    txt = code_blocks.expand('--->@<indent_2@>@<one@><-----')
    assert txt == """--->one[This is some text]<-----
--->two[This is some text]<-----
--->three[This is some text]<-----
--->four[This is some text]<-----"""

    txt = code_blocks.expand('a@<b@>c@<d@>e')  # this will cause an infinite loop if we do this wrong
    lines = txt.split("\n")
    assert len(lines) == 2
    assert "a1c3e" in lines
    assert "a2c4e" in lines

    # multi-line
    txt = code_blocks.expand("a@<three(two=\n2)@>b")
    assert "a[This is the text from block two:2, can you believe it?]b"

    txt = code_blocks.expand('@<append@>')
    assert txt == "1\n2\n3\n4"

    txt = code_blocks.expand('@<code_dir@>')
    assert txt == "~/code"

    txt = code_blocks.expand('@<project_name_recurse@>')
    assert txt == ""

    txt = code_blocks.expand('@<asdfasdfasdf@>')
    assert txt == ""
