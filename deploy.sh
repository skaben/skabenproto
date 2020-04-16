#!/usr/bin/env bash


# linting
#flake8 /skabenproto
# testing
#pytest /skabenproto

version=$(cat ./setup.py |grep version |cut -f2 -d "'")

python ./setup.py build sdist bdist_wheel

# pushing to repo
for entry in $(ls dist | grep $version)
do
    curl -F package=@dist/$entry https://$TOKEN@push.fury.io/zerthmonk
done
