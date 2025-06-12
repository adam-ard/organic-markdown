# Build

To build a new `omd` script, run the following. Don't run `omd tangle` because that will also tangle the stuff in `e2e-tests/`, which should be tested using the new `lit/omd` file. Here we get around that by just tangling `omd_file` and nothing else.

```bash {name=build-omd menu=true}
rm -f lit/omd
omd tangle omd_file
black lit/omd
chmod u+x lit/omd
```

# Unit Tests
To test the new `omd` script, run the following:

```bash
omd run all_tests
```

# e2e tests

To e2e test the new `omd` script, run the following:

```bash
omd run e2e-tests
```

# Diff

To see the difference between the built script and the system on:

```bash {name=diff menu=true}
diff lit/omd `which omd`
```

# Release

To do an official release.

- Update the version in the file: `lit\version.o.md`.
- Run `build-omd`
- Run `all_tests`
- Run `e2e-tests`
- If all pass, create a commit with the version update and push.
- Create a new release on the right of the github project page (make sure create a tag with the version as well)
- Attach the `lit/omd` file to the release.
