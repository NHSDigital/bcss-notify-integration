#!/bin/bash

lambda_name=$1

build_dir=build/${lambda_name}

mkdir -p ${build_dir}
cp ../../../${lambda_name}/*.py ${build_dir}
cp ../../../shared/*.py ${build_dir}
cd ${build_dir}
zip -r ../../${lambda_name}.zip *.py
cd ../..
rm -rf build
