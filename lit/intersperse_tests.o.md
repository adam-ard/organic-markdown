Here are a few tests to confirm that the intersperse functionality is working correctly:


```python {tangle=tests/intersperse.py}
#!/usr/bin/env python3

@<get_max_lines@>
@<intersperse@>

if intersperse([]) != "":
    @<test_failed(name="intersperse" msg="should return empty string")@>

if intersperse(["a", "b"]) != "ab":
    @<test_failed(name="intersperse" msg="should return 'ab'")@>

if intersperse(["a\nb", "c\nd"]) != "ac\nbd":
    @<test_failed(name="intersperse" msg="should return 'ac\nbd'")@>

if intersperse(["a\nb\nc", "d\ne"]) != "ad\nbe\nce":
    @<test_failed(name="intersperse" msg="should return 'ad\nbe\nce'")@>

if intersperse(["a\nb\nc\nd", "e\nf"]) != "ae\nbf\ncf\ndf":
    @<test_failed(name="intersperse" msg="should return 'ae\nbf\ncf\ndf'")@>

if intersperse(["e\nf", "a\nb\nc\nd"]) != "ea\nfb\nfc\nfd":
    @<test_failed(name="intersperse" msg="should return 'ea\nfb\nfc\nfd'")@>

if intersperse(["e\nf", ":", "a\nb\nc\nd", ":"]) != "e:a:\nf:b:\nf:c:\nf:d:":
    @<test_failed(name="intersperse" msg="should return 'e:a:\nf:b:\nf:c:\nf:d:'")@>

@<test_passed(name="intersperse")@>
```

To run the intersperse test:

```bash {name=intersperse_tests menu=true}
tests/intersperse.py
```

[source code](intersperse.o.md)
