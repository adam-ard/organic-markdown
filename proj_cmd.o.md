# Project Commands

To build a new omd script, run:

```bash {name=build-omd dir=lit menu=true}
omd tangle
black omd
chmod u+x omd
```

To test the new omd script, run:

```bash {name=test-omd dir=lit menu=true}
omd run all_tests
```

To torture test the new omd script, run:

```bash {name=torture-test-omd dir=torture_tests menu=true}
./tests.sh
```

To see the difference between the new script and the old one:

```bash {name=diff menu=true}
diff omd lit/omd
```

