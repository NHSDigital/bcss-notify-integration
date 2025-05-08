#!/bin/bash

mkdir -p build/python
pip install pipenv
pipenv requirements > requirements.txt
pipenv run pip install -r requirements.txt --target build/python/
rm requirements.txt
cd build/python
find -name "tests" -type d | xargs rm -rf
find -name "__pycache__" -type d | xargs rm -rf
find -name "_pytest" -type d | xargs rm -rf
cd ..
zip -r ../packages.zip python/ -x *.zip
cd ..
rm -rf build
