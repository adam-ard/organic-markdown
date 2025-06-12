# Build

To build a new `omd` script, run the following in the `lit` directory. Don't tangle the stuff in `e2e-tests/`. It should stay isolated by tangling specific files.

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

To e2e test the new `omd` script, run the following in the `e2e-tests` directory. I tangle only the `e2e-tests/tests.sh` file, so that the rest of the files can be tangled by the omd that is under test `lit/omd` -- when `e2e-tests/tests.sh` is run it calls `lit/omd` explicitly.

```bash {name=e2e-tests-omd menu=true}
rm -f e2e-tests/tests.sh
omd tangle e2e-tests-script
chmod u+x e2e-tests/tests.sh
cd e2e-tests
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
- Run `all_tests`
- Run `e2e-tests-omd`
- If all pass, create a commit with the version update and push.
- Create a new release on the right of the github project page (make sure create a tag with the version as well)
- Attach the `lit/omd` file to the release.
