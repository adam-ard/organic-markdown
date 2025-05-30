#!/bin/bash

cd lit
omd tangle

# fix whitespace problems
../whitespace-cleanup.sh omd

omd run all_tests

cp omd ../omd

cd ..

cp omd omd.py
pytest-3
rm omd.py


cd torture_tests
./tests.sh
cd ..

echo "diff old omd with new one"
git diff omd

git restore omd
