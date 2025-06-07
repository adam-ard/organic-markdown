# Build

To build a new `omd` script, run the following in the `lit` directory:

```bash {name=build-omd dir=lit menu=true}
omd tangle
black omd
chmod u+x omd
```

# Unit Tests
To test the new `omd` script, run the following in the `lit` directory:

```bash {name=test-omd dir=lit menu=true}
omd run all_tests
```

# e2e tests

To e2e test the new `omd` script, run the following in the `e2e-tests` directory:

```bash {name=e2e-tests-omd dir=e2e-tests menu=true}
./tests.sh
```

# Diff

To see the difference between the built script and the system on:

```bash {name=diff menu=true}
diff lit/omd `which omd`
```

# Release

To do an official release.

- Update the version in the file: `lit\version.o.md`.
- Run `omd-build`
- Run `test-omd`
- Run `e2e-tests-omd`
- Create a new release on the right of the github project page (make sure create a tag with the version as well)
- Attach the `lit/omd` file to the release.
