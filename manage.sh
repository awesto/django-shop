#!/bin/bash

pushd .
cd tests/testapp
python manage.py $@
popd

