#!/bin/bash

pushd .
cd tests
python testapp/manage.py test shop

popd
