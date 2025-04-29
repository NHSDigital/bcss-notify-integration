#!/bin/bash

build_dir=$1
lambda_dir=$2
filename=$3

mkdir -p ${build_dir}
cp ${lambda_dir}/*.py ${build_dir}
cp ${lambda_dir}/../shared/*.py ${build_dir}
cd ${build_dir}
find -type d -name __pycache__ -exec rm -rf {} \;
find -type d -name _pytest -exec rm -rf {} \;
chmod -R 644 $(find . -type f)
chmod -R 755 $(find . -type d)
zip -r ../${filename} * -x *.zip
cd ..
rm -rf ${build_dir}
