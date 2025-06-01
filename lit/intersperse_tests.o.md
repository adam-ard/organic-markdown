Here are a few tests to confirm that the intersperse functionality is working correctly:


```python {tangle=tests/intersperse.py}
#!/usr/bin/env python3

@<get_max_lines@>
@<intersperse@>
@<omd_assert@>

omd_assert(intersperse([]), "")
omd_assert(intersperse(["a", "b"]), "ab")
omd_assert(intersperse(["a\nb", "c\nd"]), "ac\nbd")
omd_assert(intersperse(["a\nb\nc", "d\ne"]), "ad\nbe\nce")
omd_assert(intersperse(["a\nb\nc\nd", "e\nf"]), "ae\nbf\ncf\ndf")
omd_assert(intersperse(["e\nf", "a\nb\nc\nd"]), "ea\nfb\nfc\nfd")
omd_assert(intersperse(["e\nf", ":", "a\nb\nc\nd", ":"]), "e:a:\nf:b:\nf:c:\nf:d:")

@<test_passed(name="intersperse")@>
```

To run the intersperse test:

```bash {name=intersperse_tests menu=true}
tests/intersperse.py
```

[source code](intersperse.o.md)
