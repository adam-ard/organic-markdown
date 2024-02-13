import xmd

code_block = [["",
               [],
               [["name", "build_project"],
                ["lang", "bash"],
                ["what_is_this", "blah"],
                ["runnable", "true"],
                ["docker", "<<docker_container_name()>>"],
                ["runnable", "true"],
                ["dir", "<<project_name()>>"],
                ["tangle", "<<project_name()>>/main.c"]
                ]],
              "gcc --version"]

code_block_one = [["",
                   [],
                   [["name", "one"],
                    ]],
                  "[This is some text]"]

code_block_two = [["",
                   [],
                   [["name", "two"],
                    ]],
                  "[This is the text from block one:<<one()>>, wasn't that nice?]"]

code_block_three = [["",
                     [],
                     [["name", "three"],
                      ]],
                    "[This is the text from block two:<<two()>>, can you believe it?]"]

full_file = {"blocks": [{"t": "CodeBlock",
                         "c": code_block_one
                         },
                        {"t": "CodeBlock",
                         "c": code_block_two
                         },
                        {"t": "CodeBlock",
                         "c": code_block_three
                         },],
             "pandoc-api-version": [1, 20],
             "meta": {
                 "includes": {
                     "t": "MetaList",
                     "c": [{"t": "MetaInlines", "c": [{"t": "Str", "c": "constants.md"}]},
                           {"t": "MetaInlines", "c": [{"t": "Str", "c": "docker.md"}]}]}}}

def test_expand_from_full_json():
    code_blocks = xmd.CodeBlocks()
    code_blocks.parse(full_file)

    blk = code_blocks.get_code_block("three")
    assert blk != None

    txt = blk.get_expanded_code()
    assert txt == "[This is the text from block two:[This is the text from block one:[This is some text], wasn't that nice?], can you believe it?]"

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
    cb = xmd.CodeBlock()
    assert cb.parse_runnable_attrib("true") == True
    assert cb.parse_runnable_attrib("True") == True
    assert cb.parse_runnable_attrib("1") == True
    assert cb.parse_runnable_attrib(1) == True
    assert cb.parse_runnable_attrib(True) == True
    assert cb.parse_runnable_attrib("asdf") == True

    assert cb.parse_runnable_attrib("false") == False
    assert cb.parse_runnable_attrib("False") == False
    assert cb.parse_runnable_attrib("FaLse") == False
    assert cb.parse_runnable_attrib("0") == False
    assert cb.parse_runnable_attrib("") == False
    assert cb.parse_runnable_attrib(None) == False
    assert cb.parse_runnable_attrib(0) == False
    assert cb.parse_runnable_attrib(False) == False
