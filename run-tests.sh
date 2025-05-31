#!/bin/bash

cd lit
omd tangle

# run linter
black omd

omd run all_tests

cp omd ../omd

cd ../torture_tests
./tests.sh
cd ..

echo "diff old omd with new one"
git diff omd

git restore omd
