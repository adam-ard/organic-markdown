# OMD batch execution

This fixture verifies the public batch syntax through the generated `lit/omd` executable. The `batch-e2e` block invokes two ordinary named commands in order. Neither helper is exposed in the command menu because they exist only to make the batch behavior observable.

```bash {name=batch-e2e-first}
printf "batch first\n"
```

```bash {name=batch-e2e-second}
printf "batch second\n"
```

```omd {name=batch-e2e}
run batch-e2e-first
run batch-e2e-second
```

The co-located test is pulled into the project end-to-end runner with a literate reference. It checks the terminal-facing `omd run <name>` entry point and the ordered output from both commands.

```bash {name=batch_feature_e2e_test}
expected_output="batch first
batch second"
@<CMP_OMD_CMD(exp="$expected_output" got="run batch-e2e")@>
```
