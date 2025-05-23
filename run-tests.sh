#!/bin/bash

pytest-3

cd lit
omd tangle

# fix whitespace problems
../whitespace-cleanup.sh omd.py

omd run all_tests

cd ../torture_tests
./tests.sh

echo "diff old omd.py with new one"
cd ..
diff omd.py lit/omd.py

