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
                    "c": "<<project_name()>>"
                }
            ]
        }
    }
}
              }


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

code_block_alt_syntax = [["",
                          ["python"],
                          [["name", "build_project"],
                           ["what_is_this", "blah"],
                           ["docker", "<<docker_container_name()>>"],
                           ["runnable", "true"],
                           ["dir", "<<project_name()>>"],
                           ["tangle", "<<project_name()>>/main.c"]
                           ]],
                         "gcc --version"]

code_block_alt_syntax2 = [["",
                           ["bash"],
                           [["name", "build_project"],
                            ["what_is_this", "blah"],
                            ["docker", "<<docker_container_name()>>"],
                            ["runnable", "true"],
                            ["dir", "<<project_name()>>"],
                            ["tangle", "<<project_name()>>/main.c"]
                            ]],
                          "gcc --version"]

code_block_alt_syntax3 = [["",
                           [],
                           [["name", "build_project"],
                            ["what_is_this", "blah"],
                            ["docker", "<<docker_container_name()>>"],
                            ["runnable", "true"],
                            ["dir", "<<project_name()>>"],
                            ["tangle", "<<project_name()>>/main.c"]
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

code_block_5 = [["",
                    [],
                    [["name", "five"],
                     ["lang", "python"],
                     ["runnable", "true"],
                     ["dir", "."],
                     ]],
                   'print("I am python!! <<msg()>>")']


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



full_file = {"blocks": [{"t": "",
                         "c": meta_block
                         },
                        {"t": "CodeBlock",
                         "c": code_block_1
                         },
                        {"t": "CodeBlock",
                         "c": code_block_b
                         },
                        {"t": "CodeBlock",
                         "c": code_block_append1
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

def test_expand():
    code_blocks = omd.CodeBlocks("LIT.md")
    code_blocks.parse_json(full_file)

    blk = code_blocks.get_code_block("three")
    assert blk != None

    txt = code_blocks.expand(blk.code)
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

    txt = code_blocks.expand('<<five(msg="asdf")()>>')
    assert txt == "I am python!! asdf\n"

    txt = code_blocks.expand('<<four(msg="here is a msg")()>>')
    assert txt == "here is a msg\n"

    txt = code_blocks.expand('<<two_1(one="qwerty")>>')
    assert txt == "[This is the text from block one:qwerty, wasn't that nice?]"

    txt = code_blocks.expand('<<indent_4()>>')
    assert txt == f"""indent_block {{
    one
        {""}
    {""}
    two
      three
    four
}}"""

    txt = code_blocks.expand('<<indent_6()>>')
    assert txt == f"""indent_block {{
    // one
    // {"    "}
    // {""}
    // two
    //   three
    // four
}}"""

    txt = code_blocks.expand('---><<indent_2()>><<one()>><-----')
    assert txt == """--->one[This is some text]<-----
--->two[This is some text]<-----
--->three[This is some text]<-----
--->four[This is some text]<-----"""

    txt = code_blocks.expand('a<<b()>>c<<d()>>e')  # this will cause an infinite loop if we do this wrong
    lines = txt.split("\n")
    assert len(lines) == 4
    assert "a1c3e" in lines
    assert "a1c4e" in lines
    assert "a2c3e" in lines
    assert "a2c4e" in lines

    txt = code_blocks.expand('<<append()>>')
    assert txt == "1\n2\n3\n4"

    txt = code_blocks.expand('<<code_dir()>>')
    assert txt == "~/code"

    txt = code_blocks.expand('<<project_name_recurse()>>')
    assert txt == "<<project_name()>>"

    # testing that none of the no name block got appended, even though
    # they all the same name of None
    assert code_blocks.get_code_block_by_code("no_name_1") is not None
    assert code_blocks.get_code_block_by_code("no_name_2") is not None
    assert code_blocks.get_code_block_by_code("no_name_3") is not None
    assert code_blocks.get_code_block_by_code("no_name_4") is not None

def test_parse_block():
    cb = omd.CodeBlock()
    cb.parse(code_block)

    assert cb.name == "build_project"
    assert cb.code == "gcc --version"
    assert cb.lang == "bash"
    assert cb.cwd == "<<project_name()>>"
    assert cb.tangle_file == "<<project_name()>>/main.c"
    assert cb.is_runnable == True
    assert cb.docker_container == "<<docker_container_name()>>"


def test_parse_block_alt_syntax():
    cb = omd.CodeBlock()
    cb.parse(code_block_alt_syntax)

    assert cb.name == "build_project"
    assert cb.code == "gcc --version"
    assert cb.lang == "python"
    assert cb.cwd == "<<project_name()>>"
    assert cb.tangle_file == "<<project_name()>>/main.c"
    assert cb.is_runnable == True
    assert cb.docker_container == "<<docker_container_name()>>"

    cb = omd.CodeBlock()
    cb.parse(code_block_alt_syntax2)

    assert cb.name == "build_project"
    assert cb.code == "gcc --version"
    assert cb.lang == "bash"
    assert cb.cwd == "<<project_name()>>"
    assert cb.tangle_file == "<<project_name()>>/main.c"
    assert cb.is_runnable == True
    assert cb.docker_container == "<<docker_container_name()>>"

    cb = omd.CodeBlock()
    cb.parse(code_block_alt_syntax3)

    assert cb.name == "build_project"
    assert cb.code == "gcc --version"
    assert cb.lang == None
    assert cb.cwd == "<<project_name()>>"
    assert cb.tangle_file == "<<project_name()>>/main.c"
    assert cb.is_runnable == True
    assert cb.docker_container == "<<docker_container_name()>>"

def test_parse_runnable():
    assert omd.parse_runnable_attrib("true") == True
    assert omd.parse_runnable_attrib("True") == True
    assert omd.parse_runnable_attrib("1") == True
    assert omd.parse_runnable_attrib(1) == True
    assert omd.parse_runnable_attrib(True) == True
    assert omd.parse_runnable_attrib("asdf") == True

    assert omd.parse_runnable_attrib("false") == False
    assert omd.parse_runnable_attrib("False") == False
    assert omd.parse_runnable_attrib("FaLse") == False
    assert omd.parse_runnable_attrib("0") == False
    assert omd.parse_runnable_attrib("") == False
    assert omd.parse_runnable_attrib(None) == False
    assert omd.parse_runnable_attrib(0) == False
    assert omd.parse_runnable_attrib(False) == False

def test_arg_parse():
    assert omd.arg_parse('') == {}
    assert omd.arg_parse('a="v1" a="v2"') == {"a": "v1", "a": "v2"}
    assert omd.arg_parse('arg1="val1" arg2="val2"') == {"arg1": "val1", "arg2": "val2"}
    assert omd.arg_parse('arg1="val1" arg2="val2"') == {"arg1": "val1", "arg2": "val2"}
    assert omd.arg_parse('arg1="val1"   arg2="val2"') == {"arg1": "val1", "arg2": "val2"}
    assert omd.arg_parse('arg1  =   "val1" arg2  =   "val2"') == {"arg1": "val1", "arg2": "val2"}
    assert omd.arg_parse('arg1="" arg2=""') == {"arg1": "", "arg2": ""}
    assert omd.arg_parse('arg1=" " arg2=" "') == {"arg1": " ", "arg2": " "}
    assert omd.arg_parse('arg1="val one"   arg2="val one"') == {"arg1": "val one", "arg2": "val one"}
    assert omd.arg_parse('   arg1  =  " val1 "   arg2  =  " val2 "') == {"arg1": " val1 ", "arg2": " val2 "}
    assert omd.arg_parse('ret_name="parsed_bool" ret="bool value, float one" name="myFunc" args="char *filename, float two"') == {"ret_name": "parsed_bool",
                                                                                                                             "ret": "bool value, float one",
                                                                                                                             "name": "myFunc",
                                                                                                                             "args": "char *filename, float two"}

def test_add_pre_post():
    assert omd.add_pre_post("word", "---->", "<----") == "---->word<----"
    assert omd.add_pre_post("word", "", "") == "word"
    assert omd.add_pre_post("""one
two
three
four""", "---->", "<----") == """---->one<----
---->two<----
---->three<----
---->four<----"""

    assert omd.add_pre_post("""one
two
three
four""", "", "") == """one
two
three
four"""

def test_insert_blk():
    assert omd.insert_blk("abcdefg", "xyz", 1, 6) == "axyzg"
    assert omd.insert_blk("abcdefg", "xyz", 3, 4) == "abcxyzefg"
    assert omd.insert_blk("abcdefg", "xyz", 0, 6) == "xyzg"
    assert omd.insert_blk("abcdefg", "xyz", 0, 7) == "xyz"
    assert omd.insert_blk("abcdefg", "xyz", -10, 10) == "xyz"

    assert omd.insert_blk("ab\ncd\nefg", "1\n2", 3, 5) == "ab\n1\n2\nefg"
    assert omd.insert_blk("ab\n--cd--\nefg", "1\n2", 5, 7) == "ab\n--1--\n--2--\nefg"
    assert omd.insert_blk("ab\n---->cd--\nefg", "1\n2", 8, 10) == "ab\n---->1--\n---->2--\nefg"
    assert omd.insert_blk("ab\n--cd<----\nefg", "1\n2", 5, 7) == "ab\n--1<----\n--2<----\nefg"

    assert omd.insert_blk("ab\ncd\nef\ngh\nij\nkl\nm", "1\n2", 9, 11) == "ab\ncd\nef\n1\n2\nij\nkl\nm"
    assert omd.insert_blk("ab\ncd\nef\n----gh----\nij\nkl\nm", "1\n2", 13, 15) == "ab\ncd\nef\n----1----\n----2----\nij\nkl\nm"


def test_get_match():
    match, exec = omd.get_match('')
    assert match is None
    assert exec == False

    match, exec = omd.get_match('<<one(arg1="val1")>>')
    assert match is not None
    assert exec == False

    match, exec = omd.get_match("<<one()>>")
    assert match is not None
    assert exec == False

    match, exec = omd.get_match("<<one()>>asdf<<two()>>")
    assert match is not None
    assert exec == False

    match, exec = omd.get_match("asdf<<one()>>asdf")
    assert match is not None
    assert exec == False

    match, exec = omd.get_match("asdf<<one()>asdf")
    assert match is None

    match, exec = omd.get_match("<<one()()>>")
    assert match is not None
    assert exec == True

    match, exec = omd.get_match('<<one(arg1="val1")()>>')
    assert match is not None
    assert exec == True

    match, exec = omd.get_match("<<one()()>>asdf<<two()()>>")
    assert match is not None
    assert exec == True

    match, exec = omd.get_match("asdf<<one()()>>asdf")
    assert match is not None
    assert exec == True

    match, exec = omd.get_match("asdf<<one()()>asdf")
    assert match is None
