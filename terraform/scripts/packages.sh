#!/bin/bash

build_dir=$1
packages_dir=$2
filename=$3

mkdir -p ${build_dir}/python
cp -r ${packages_dir}/* ${build_dir}/python
cd ${build_dir}/python
find -type d -name __pycache__ -exec rm -rf {} \;
find -type d -name _pytest -exec rm -rf {} \;
chmod -R 644 $(find . -type f)
chmod -R 755 $(find . -type d)
cd ..
zip -r ../${filename} * -x *.zip
cd ..
rm -rf ${build_dir}
