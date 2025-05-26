#!/bin/bash

cd lit
omd tangle

# fix whitespace problems
../whitespace-cleanup.sh omd.py

omd run all_tests

cp omd.py ../omd.py

cd ..

pytest-3

cd torture_tests
./tests.sh
cd ..

echo "diff old omd.py with new one"
git diff omd.py

git restore omd.py
