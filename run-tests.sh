#!/bin/bash

pytest-3

cd torture_tests
./tests.sh
cd ..

cd lit
omd tangle

# fix whitespace problems
../whitespace-cleanup.sh omd.py

omd run all_tests

echo "diff old omd.py with new one"
diff ../omd.py omd.py

