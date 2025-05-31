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

def test_get_code_block():
    code_blocks = omd.CodeBlocks()
    code_blocks.parse_json(full_file, "test_file.omd")

    blk = code_blocks.get_code_block("three")
    assert blk != None
