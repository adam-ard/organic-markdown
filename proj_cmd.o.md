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

To see the difference between the new script and the old one:

```bash {name=diff menu=true}
diff omd lit/omd
```

Release the new `omd` script, run the following. Make sure you don't have anything else staged, or it will come along for the ride.

```bash {name=diff menu=true}
cp lit/omd omd
git add omd
git commit -m "Release new omd script"
git push origin main
```
