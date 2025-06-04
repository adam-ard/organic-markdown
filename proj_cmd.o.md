# Project Commands

To build a new `omd` script, run the following in the `lit` directory:

```bash {name=build-omd dir=lit menu=true}
omd tangle
black omd
chmod u+x omd
```

To test the new `omd` script, run the following in the `lit` directory:

```bash {name=test-omd dir=lit menu=true}
omd run all_tests
```

To torture test the new `omd` script, run the following in the `torture_tests` directory:

```bash {name=torture-test-omd dir=torture_tests menu=true}
./tests.sh
```

To see the difference between the built script and the system on:

```bash {name=diff menu=true}
diff lit/omd `which omd`
```
