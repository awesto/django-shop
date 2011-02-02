#!/bin/bash

pushd .
cd tests/testapp
python manage.py test shop

popd
