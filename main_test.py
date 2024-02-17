import xmd

code_block = [["",
               [],
               [["name", "build_project"],
                ["lang", "bash"],
                ["what_is_this", "blah"],
                ["docker", "<<docker_container_name()>>"],
                ["runnable", "true"],
                ["dir", "<<project_name()>>"],
                ["tangle", "<<project_name()>>/main.c"]
                ]],
              "gcc --version"]

code_block_1 = [["",
                   [],
                   [["name", "one"],
                    ]],
                  "[This is some text]"]

code_block_2 = [["",
                   [],
                   [["name", "two"],
                    ]],
                  "[This is the text from block one:<<one()>>, wasn't that nice?]"]

code_block_2_1 = [["",
                   [],
                   [["name", "two_1"],
                    ]],
                  "[This is the text from block one:<<one()()>>, wasn't that nice?]"]

code_block_3 = [["",
                     [],
                     [["name", "three"],
                      ]],
                    "[This is the text from block two:<<two()>>, can you believe it?]"]

code_block_3_1 = [["",
                   [],
                   [["name", "msg"],
                    ]],
                  "this is great"]

code_block_4 = [["",
                    [],
                    [["name", "four"],
                     ["lang", "bash"],
                     ["runnable", "true"],
                     ["dir", "."],
                     ]],
                   'echo <<msg()>>']



# note that I use the {"    "} syntax so when I run whitespace-cleanup it doesn't mess with the spaces
indent_3 = [["",
             [],
             [["name", "indent_3"],
              ]],
            f"""one
{"    "}

two
  three
four"""]

indent_4 = [["",
             [],
             [["name", "indent_4"],
              ]],
            """indent_block {
    <<indent_3()>>
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
    // <<indent_5()>>
}"""]



full_file = {"blocks": [{"t": "CodeBlock",
                         "c": code_block_1
                         },
                        {"t": "CodeBlock",
                         "c": code_block_2
                         },
                        {"t": "CodeBlock",
                         "c": code_block_2_1
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
                         "c": code_block_4
                         },],
             "pandoc-api-version": [1, 20],
             "meta": {
                 "includes": {
                     "t": "MetaList",
                     "c": [{"t": "MetaInlines", "c": [{"t": "Str", "c": "constants.md"}]},
                           {"t": "MetaInlines", "c": [{"t": "Str", "c": "docker.md"}]}]}}}

def test_expand():
    code_blocks = xmd.CodeBlocks()
    code_blocks.parse(full_file)

    blk = code_blocks.get_code_block("three")
    assert blk != None

    txt = blk.get_expanded_code()
    assert txt == "[This is the text from block two:[This is the text from block one:[This is some text], wasn't that nice?], can you believe it?]"

    # test with args
    txt = code_blocks.expand('<<three(two="asdf")>>')
    assert txt == "[This is the text from block two:asdf, can you believe it?]"

    txt = code_blocks.expand('<<two(one="qwerty")>>')
    assert txt == "[This is the text from block one:qwerty, wasn't that nice?]"

    # this one takes some work, worth doing in the future?
    # txt = code_blocks.expand('<<three(one="asdf")>>')
    # assert txt == "[This is the text from block two:[This is the text from block one:asdf, wasn't that nice?], can you believe it?]"

    txt = code_blocks.expand('<<four()()>>')
    assert txt == "this is great\n"

    txt = code_blocks.expand('<<four(msg="here is a msg")()>>')
    assert txt == "here is a msg\n"

    txt = code_blocks.expand('<<two_1(one="qwerty")>>')
    assert txt == "[This is the text from block one:qwerty, wasn't that nice?]"

    txt = code_blocks.expand('<<indent_4()>>')
    assert txt == f"""indent_block {{
    one
{"    "}

    two
      three
    four
}}"""

    txt = code_blocks.expand('<<indent_6()>>')
    assert txt == f"""indent_block {{
    // one
    //{"    "}
    //
    // two
    //   three
    // four
}}"""

def test_parse_block():
    cb = xmd.CodeBlock()
    cb.parse(code_block)

    assert cb.name == "build_project"
    assert cb.code == "gcc --version"
    assert cb.lang == "bash"
    assert cb.cwd == "<<project_name()>>"
    assert cb.tangle_file == "<<project_name()>>/main.c"
    assert cb.is_runnable == True
    assert cb.docker_container == "<<docker_container_name()>>"

def test_parse_runnable():
    assert xmd.parse_runnable_attrib("true") == True
    assert xmd.parse_runnable_attrib("True") == True
    assert xmd.parse_runnable_attrib("1") == True
    assert xmd.parse_runnable_attrib(1) == True
    assert xmd.parse_runnable_attrib(True) == True
    assert xmd.parse_runnable_attrib("asdf") == True

    assert xmd.parse_runnable_attrib("false") == False
    assert xmd.parse_runnable_attrib("False") == False
    assert xmd.parse_runnable_attrib("FaLse") == False
    assert xmd.parse_runnable_attrib("0") == False
    assert xmd.parse_runnable_attrib("") == False
    assert xmd.parse_runnable_attrib(None) == False
    assert xmd.parse_runnable_attrib(0) == False
    assert xmd.parse_runnable_attrib(False) == False

def test_arg_parse():
    assert xmd.arg_parse('a="v1", a="v2"') == {"a": "v1", "a": "v2"}
    assert xmd.arg_parse('arg1="val1", arg2="val2"') == {"arg1": "val1", "arg2": "val2"}
    assert xmd.arg_parse('arg1="val1",arg2="val2"') == {"arg1": "val1", "arg2": "val2"}
    assert xmd.arg_parse('arg1="val1",   arg2="val2"') == {"arg1": "val1", "arg2": "val2"}
    assert xmd.arg_parse('arg1  =   "val1",arg2  =   "val2"') == {"arg1": "val1", "arg2": "val2"}
    assert xmd.arg_parse('arg1="", arg2=""') == {"arg1": "", "arg2": ""}
    assert xmd.arg_parse('arg1=" ", arg2=" "') == {"arg1": " ", "arg2": " "}
    assert xmd.arg_parse('arg1="val one",   arg2="val one"') == {"arg1": "val one", "arg2": "val one"}
    assert xmd.arg_parse('   arg1  =  " val1 ",   arg2  =  " val2 "') == {"arg1": " val1 ", "arg2": " val2 "}

def test_add_prefix():
    assert xmd.add_prefix("", "word\nword") == "word\nword"

    assert xmd.add_prefix("    ", "word") == "word"
    assert xmd.add_prefix("    ", "word\nword") == "word\n    word"
    assert xmd.add_prefix("    ", "word\n\nword") == "word\n\n    word"
    assert xmd.add_prefix("    ", "word\n    \nword") == "word\n    \n    word"
    assert xmd.add_prefix("    ", "word\n    word") == "word\n        word"

    assert xmd.add_prefix("----", "word") == "word"
    assert xmd.add_prefix("----", "word\nword") == "word\n----word"
    assert xmd.add_prefix("----", "word\n\nword") == "word\n----\n----word"
    assert xmd.add_prefix("----  ", "word\n\nword") == "word\n----\n----  word"
    assert xmd.add_prefix("----  ", "word\n    \nword") == "word\n----    \n----  word"
    assert xmd.add_prefix("----", "word\n    word") == "word\n----    word"
