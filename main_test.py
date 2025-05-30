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

# dup
def test_split_lines():
    res = omd.split_lines("test")
    assert res == ["test"]

    res = omd.split_lines("test\ntest")
    assert res == ["test", "test"]

    res = omd.split_lines("A@<B(a=1\nb=2)@>\nC\nD")
    assert res == ["A@<B(a=1\nb=2)@>", "C", "D"]

# dup
def test_parse_block():
    cb = omd.CodeBlock()
    cb.parse(code_block)

    assert cb.name == "build_project"
    assert cb.code == "gcc --version"
    assert cb.lang == "bash"
    assert cb.cwd == "@<project_name@>"
    assert cb.tangle_file == "@<project_name@>/main.c"
    assert cb.in_menu == True
    assert cb.docker_container == "@<docker_container_name@>"
    assert cb.ssh_host == "aard@localhost.com"


# dup
def test_parse_block_alt_syntax():
    cb = omd.CodeBlock()
    cb.parse(code_block_alt_syntax)

    assert cb.name == "build_project"
    assert cb.code == "gcc --version"
    assert cb.lang == "python"
    assert cb.cwd == "@<project_name@>"
    assert cb.tangle_file == "@<project_name@>/main.c"
    assert cb.in_menu == True
    assert cb.docker_container == "@<docker_container_name@>"
    assert cb.ssh_host == "aard@localhost.com"

    cb = omd.CodeBlock()
    cb.parse(code_block_alt_syntax2)

    assert cb.name == "build_project"
    assert cb.code == "gcc --version"
    assert cb.lang == "bash"
    assert cb.cwd == "@<project_name@>"
    assert cb.tangle_file == "@<project_name@>/main.c"
    assert cb.in_menu == True
    assert cb.docker_container == "@<docker_container_name@>"
    assert cb.ssh_host == "aard@localhost.com"

    cb = omd.CodeBlock()
    cb.parse(code_block_alt_syntax3)

    assert cb.name == "build_project"
    assert cb.code == "gcc --version"
    assert cb.lang == None
    assert cb.cwd == "@<project_name@>"
    assert cb.tangle_file == "@<project_name@>/main.c"
    assert cb.in_menu == True
    assert cb.docker_container == "@<docker_container_name@>"
    assert cb.ssh_host == "aard@localhost.com"

def test_parse_menu():
    assert omd.parse_menu_attrib("true") == True
    assert omd.parse_menu_attrib("True") == True
    assert omd.parse_menu_attrib("1") == True
    assert omd.parse_menu_attrib(1) == True
    assert omd.parse_menu_attrib(True) == True
    assert omd.parse_menu_attrib("asdf") == True

    assert omd.parse_menu_attrib("false") == False
    assert omd.parse_menu_attrib("False") == False
    assert omd.parse_menu_attrib("FaLse") == False
    assert omd.parse_menu_attrib("0") == False
    assert omd.parse_menu_attrib("") == False
    assert omd.parse_menu_attrib(None) == False
    assert omd.parse_menu_attrib(0) == False
    assert omd.parse_menu_attrib(False) == False

# dup
def test_eat_ws():
    assert omd.eat_ws("   ") == ""
    assert omd.eat_ws("   \t   ") == ""
    assert omd.eat_ws("   \n\t   ") == ""

# dup
def test_eat_eq():
    assert omd.eat_eq("=asdfasdf") == "asdfasdf"
    assert omd.eat_eq("=\"") == "\""
    assert omd.eat_eq("") == None
    assert omd.eat_eq(" = ") == None   # the whitespace should get eaten in the calling function
    assert omd.eat_eq("asdf") == None

def test_parse_arg_value():
    value, txt = omd.parse_arg_value("")
    assert value == None

    value, txt = omd.parse_arg_value("  ")
    assert value == None

    value, txt = omd.parse_arg_value("val1")
    assert value == "val1"
    assert txt == ""

    value, txt = omd.parse_arg_value("val1 name2=val2")
    assert value == "val1"
    assert txt == " name2=val2"

    value, txt = omd.parse_arg_value('"val1 val2" name2=val2')
    assert value == "val1 val2"
    assert txt == " name2=val2"

    value, txt = omd.parse_arg_value('"val1 val2"name2=val2')
    assert value == "val1 val2"
    assert txt == "name2=val2"

    value, txt = omd.parse_arg_value('@<one@> name2=val2')
    assert value == "@<one@>"
    assert txt == " name2=val2"

    value, txt = omd.parse_arg_value('@<one(two="frog toads")@> name2=val2')
    assert value == '@<one(two="frog toads")@>'
    assert txt == " name2=val2"

    value, txt = omd.parse_arg_value('"@<one(two="frog toads")@> @<three@>" name2=val2')
    assert value == '@<one(two="frog toads")@> @<three@>'
    assert txt == " name2=val2"

    value, txt = omd.parse_arg_value("val1\\@< name2=val2")
    assert value == "val1@<"
    assert txt == " name2=val2"

    value, txt = omd.parse_arg_value('val1\" name2=val2')
    assert value == 'val1"'
    assert txt == " name2=val2"

    value, txt = omd.parse_arg_value('val1\\@> name2=val2')
    assert value == 'val1@>'
    assert txt == " name2=val2"

# dup
def test_parse_arg_name():
    name, txt = omd.parse_arg_name("")
    assert name == None

    name, txt = omd.parse_arg_name("name=value")
    assert name == "name"
    assert txt == "=value"

    name, txt = omd.parse_arg_name("name  ")
    assert name == "name"
    assert txt == "  "

    name, txt = omd.parse_arg_name("name=")
    assert name == "name"
    assert txt == "="

    name, txt = omd.parse_arg_name(" stuff")
    assert name == None

    name, txt = omd.parse_arg_name("name1=value1")
    assert name == "name1"
    assert txt == "=value1"

    name, txt = omd.parse_arg_name("name1 = value1")
    assert name == "name1"
    assert txt == " = value1"

    name, txt = omd.parse_arg_name("name1 \t = value1")
    assert name == "name1"
    assert txt == " \t = value1"

def test_parse_arg_name_value():
    name, value, txt = omd.parse_arg_name_value("name=val1")
    assert name == "name"
    assert value == "val1"
    assert txt == ""

    name, value, txt = omd.parse_arg_name_value("name=val1 name2=asdf")
    assert name == "name"
    assert value == "val1"
    assert txt == " name2=asdf"

    name, value, txt = omd.parse_arg_name_value("name = val1")
    assert name == "name"
    assert value == "val1"
    assert txt == ""

    name, value, txt = omd.parse_arg_name_value("name \t = \t val1")
    assert name == "name"
    assert value == "val1"
    assert txt == ""

    name, value, txt = omd.parse_arg_name_value('name = "val1 val2"')
    assert name == "name"
    assert value == "val1 val2"
    assert txt == ""

    name, value, txt = omd.parse_arg_name_value('name = "@<one(two = "blah blah")@> @<three@>" name2=asdf')
    assert name == "name"
    assert value == '@<one(two = "blah blah")@> @<three@>'
    assert txt == " name2=asdf"

def test_parse_args():
    assert omd.parse_args('') == {}
    assert omd.parse_args('a1=v1 a2=v2') == {"a1": "v1", "a2": "v2"}
    assert omd.parse_args(' a1 = v1 a2 = v2 ') == {"a1": "v1", "a2": "v2"}

    assert omd.parse_args('a1="v1" a2="v2"') == {"a1": "v1", "a2": "v2"}
    assert omd.parse_args('arg1="val1" arg2="val2"') == {"arg1": "val1", "arg2": "val2"}
    assert omd.parse_args('arg1="val1" arg2="val2"') == {"arg1": "val1", "arg2": "val2"}
    assert omd.parse_args('arg1="val1"   arg2="val2"') == {"arg1": "val1", "arg2": "val2"}
    assert omd.parse_args('arg1  =   "val1" arg2  =   "val2"') == {"arg1": "val1", "arg2": "val2"}
    assert omd.parse_args('arg1="" arg2=""') == {"arg1": "", "arg2": ""}
    assert omd.parse_args('arg1=" " arg2=" "') == {"arg1": " ", "arg2": " "}
    assert omd.parse_args('arg1="val one"   arg2="val one"') == {"arg1": "val one", "arg2": "val one"}
    assert omd.parse_args('   arg1  =  " val1 "   arg2  =  " val2 "') == {"arg1": " val1 ", "arg2": " val2 "}

    txt = 'ret_name="parsed_bool" ret="bool value, float one" name="myFunc" args="char *filename, float two"'
    assert omd.parse_args(txt) == {"ret_name": "parsed_bool",
                                      "ret": "bool value, float one",
                                      "name": "myFunc",
                                      "args": "char *filename, float two"}

def test_get_match():
    test_data = [
        ['', False, '', False, '', ''],
        ['@<one()[]@>', False, '', False, '', ''],
        ['@<one()(@>', False, '', False, '', ''],
        ['@<one(){@>', False, '', False, '', ''],
        ['@<one)(@>', False, '', False, '', ''],
        ['@<one(@>', False, '', False, '', ''],
        ['@<one@>', True, 'one', False, '', ''],
        ['@<one@>', True, 'one', False, '', ''],
        ['@<one*@>', True, 'one', True, '', ''],
        ['@<one(arg1="val1")@>', True, 'one', False, 'arg1="val1"', ''],
        ['@<one*(arg1="val1")@>', True, 'one', True, 'arg1="val1"', ''],
        ['@<one(){1}@>', True, 'one', False, '', '1'],
        ['@<one*(){1}@>', True, 'one', True, '', '1'],
        ['@<one*(){lots of stuff}@>', True, 'one', True, '', 'lots of stuff'],
        ['@<one*(){@<two(){5}@>}@>', True, 'one', True, '', '@<two(){5}@>'],
        ['@<one*(two="@<two(){5}@>")@>', True, 'one', True, 'two="@<two(){5}@>"', ''],
        ['@<two_sentences(one="@<three_lines@>")@>', True, 'two_sentences', False, 'one="@<three_lines@>"', ''],
        ['@<one*(two="@<three*@>")@>', True, 'one', True, 'two="@<three*@>"', ''],
    ]
    for test_datum in test_data:
        match = omd.get_match(test_datum[0])
        if test_datum[1] == False:
            assert match is None
        else:
            assert match is not None
            assert match["start"] == 0
            assert match["end"] == len(test_datum[0])
            assert match["full"] == test_datum[0]
            assert match["name"] == test_datum[2]
            assert match["exec"] == test_datum[3]
            assert match["args"] == test_datum[4]
            assert match["default"] == test_datum[5]

    match = omd.get_match("@<one@>asdf@<two@>")
    assert match is not None
    assert match["start"] == 0
    assert match["end"] == len('@<one@>')
    assert match["full"] == '@<one@>'
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == ''

    match = omd.get_match("asdf@<one@>asdf")
    assert match is not None
    assert match["start"] == 4
    assert match["end"] == 4 + len('@<one@>')
    assert match["full"] == '@<one@>'
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == ''

    match = omd.get_match("asdf@<one()>asdf")
    assert match is None

    match = omd.get_match("@<one*@>asdf@<two*@>")
    assert match is not None
    assert match["start"] == 0
    assert match["end"] == len('@<one*@>')
    assert match["full"] == '@<one*@>'
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == ''

    match = omd.get_match("asdf@<one*@>asdf")
    assert match is not None
    assert match["start"] == 4
    assert match["end"] == 4 + len('@<one*@>')
    assert match["full"] == '@<one*@>'
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == ''

    match = omd.get_match("asdf@<one*()>asdf")
    assert match is None

    match = omd.get_match("asdf@<asdf() asdf() asdf@>asdf@<asdf@>asdf")
    assert match is not None
    assert match["start"] == 30
    assert match["end"] == 30 + len('@<asdf@>')
    assert match["full"] == '@<asdf@>'
    assert match["name"] == 'asdf'
    assert match["exec"] == False
    assert match["args"] == ''

# dup
def test_parse_name():
    name, txt = omd.parse_name("one")
    assert name == "one"
    assert txt == ""

    name, txt = omd.parse_name("one'")
    assert name == "one'"
    assert txt == ""

    name, txt = omd.parse_name("one*")
    assert name == "one*"
    assert txt == ""

    name, txt = omd.parse_name("one_two")
    assert name == "one_two"
    assert txt == ""

    name, txt = omd.parse_name("one_two(){}")
    assert name == "one_two"
    assert txt == "(){}"

    name, txt = omd.parse_name("one_two(){}")
    assert name == "one_two"
    assert txt == "(){}"

    name, txt = omd.parse_name("one_two()")
    assert name == "one_two"
    assert txt == "()"

    name, txt = omd.parse_name("one_two{}")
    assert name == "one_two"
    assert txt == "{}"

    name, txt = omd.parse_name("one_two)")
    assert name == "one_two)"
    assert txt == ""

    name, txt = omd.parse_name("one_two}")
    assert name == "one_two}"
    assert txt == ""

    name, txt = omd.parse_name("one}_two")
    assert name == "one}_two"
    assert txt == ""

    name, txt = omd.parse_name("one<_two")
    assert name == "one<_two"
    assert txt == ""

    name, txt = omd.parse_name("one>_two")
    assert name == "one>_two"
    assert txt == ""

    name, txt = omd.parse_name("one=_two")
    assert name == "one=_two"
    assert txt == ""

    name, txt = omd.parse_name('one"_two')
    assert name == 'one"_two'
    assert txt == ""

    name, txt = omd.parse_name('one two')
    assert name == 'one two'
    assert txt == ""

    name, txt = omd.parse_name('one\\()()')
    assert name == 'one\\()'
    assert txt == "()"

    name, txt = omd.parse_name('one\\{}()')
    assert name == 'one\\{}'
    assert txt == "()"

# dup
def test_parse_exec():
    name, exec, success = omd.parse_exec("")
    assert success == False

    name, exec, success = omd.parse_exec("*")
    assert success == False

    name, exec, success = omd.parse_exec("one")
    assert name == "one"
    assert exec == False
    assert success == True

    name, exec, success = omd.parse_exec("one*")
    assert name == "one"
    assert exec == True
    assert success == True

    name, exec, success = omd.parse_exec("a*")
    assert name == "a"
    assert exec == True
    assert success == True

# dup
def test_parse_args_str():
    args, txt = omd.parse_args_str("")
    assert args == ""
    assert txt == ""

    args, txt = omd.parse_args_str("{}")
    assert args == ""
    assert txt == "{}"

    args, txt = omd.parse_args_str("aa")
    assert args == None

    args, txt = omd.parse_args_str("()")
    assert args == ""
    assert txt == ""

    args, txt = omd.parse_args_str('(a=5 b=6)')
    assert args == "a=5 b=6"
    assert txt == ""

    args, txt = omd.parse_args_str('(a=5 b=6)asdf')
    assert args == "a=5 b=6"
    assert txt == "asdf"

    args, txt = omd.parse_args_str('(a="5" b="6")')
    assert args == 'a="5" b="6"'
    assert txt == ""

    args, txt = omd.parse_args_str('(aasfd')
    assert args == None

    args, txt = omd.parse_args_str('(a=5 b=@<six@>)')
    assert args == "a=5 b=@<six@>"
    assert txt == ""

    args, txt = omd.parse_args_str('(((())))')
    assert args == "((()))"
    assert txt == ""

def test_parse_default():
    default, txt= omd.parse_default("")
    assert default == ""
    assert txt == ""

    default, txt= omd.parse_default("()")
    assert default == None

    default, txt= omd.parse_default("aa")
    assert default == None

    default, txt= omd.parse_default("{}")
    assert default == ""
    assert txt == ""

    default, txt= omd.parse_default("{a}")
    assert default == "a"
    assert txt == ""

    default, txt= omd.parse_default("{@<a@>}")
    assert default == "@<a@>"
    assert txt == ""

    default, txt= omd.parse_default('{aasfd')
    assert default == None

    default, txt= omd.parse_default("{@<a{5}@>}")
    assert default == "@<a{5}@>"
    assert txt == ""

    default, txt= omd.parse_default('{{{{{{}}}}}}')
    assert default == "{{{{{}}}}}"
    assert txt == ""

def test_parse_match():
    match = omd.parse_match('')
    assert match is None

    txt="one"
    match = omd.parse_match(txt)
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == ""
    assert match["default"] == ""

    match = omd.parse_match('one(')
    assert match is None

    match = omd.parse_match('one)(')
    assert match is None

    match = omd.parse_match('one()(')
    assert match is None

    match = omd.parse_match('one(){}')
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == ""
    assert match["default"] == ""

    match = omd.parse_match("one*(){}")
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == ""
    assert match["default"] == ""

    match = omd.parse_match('one(){1}')
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == ''
    assert match["default"] == "1"

    match = omd.parse_match("one*(){1}")
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == ''
    assert match["default"] == "1"

    match = omd.parse_match('one(){"1"}')
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == ''
    assert match["default"] == '1'

    match = omd.parse_match("one*(){lots of stuff}")
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == ''
    assert match["default"] == "lots of stuff"

    match = omd.parse_match("one*(a=5 b=6){lots of stuff}")
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == 'a=5 b=6'
    assert match["default"] == "lots of stuff"

    match = omd.parse_match('one(){@<two(){5}@>}')
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == ''
    assert match["default"] == "@<two(){5}@>"

    match = omd.parse_match('one(two="@<two(){5}@>")')
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == 'two="@<two(){5}@>"'
    assert match["default"] == ""

    match = omd.parse_match('two_sentences(one="@<three_lines@>")')
    assert match is not None
    assert match["name"] == 'two_sentences'
    assert match["exec"] == False
    assert match["args"] == 'one="@<three_lines@>"'
    assert match["default"] == ""

    match = omd.parse_match('two_sentences*(one="@<three_lines@>")')
    assert match is not None
    assert match["name"] == 'two_sentences'
    assert match["exec"] == True
    assert match["args"] == 'one="@<three_lines@>"'
    assert match["default"] == ""

    match = omd.parse_match('one(arg1="val1")')
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == 'arg1="val1"'
    assert match["default"] == ""

    match = omd.parse_match("one()")
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == ''
    assert match["default"] == ""

    match = omd.parse_match("one")
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == False
    assert match["args"] == ''
    assert match["default"] == ""

    match = omd.parse_match("one*")
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == ''
    assert match["default"] == ""

    match = omd.parse_match("one*()")
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == ''
    assert match["default"] == ""

    match = omd.parse_match('one*(two="@<three*@>")')
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == 'two="@<three*@>"'
    assert match["default"] == ""

    match = omd.parse_match('one*(arg1="val1")')
    assert match is not None
    assert match["name"] == 'one'
    assert match["exec"] == True
    assert match["args"] == 'arg1="val1"'
    assert match["default"] == ""
