#!/bin/bash

args=("$@")
num_args=${#args[@]}
index=0

coverage=false
documentation=false

while [ "$index" -lt "$num_args" ]
do
	case "${args[$index]}" in
		"--with-docs")
			documentation=true
			;;
		"--with-coverage")
			coverage=true
			;;
	esac
let "index = $index + 1"
done

if [ $coverage == true ]; then
	pushd .
	cd tests/testapp
	coverage run manage.py test shop
	coverage html
	x-www-browser htmlcov/index.html
	popd

else

	# the default case...
	pushd .
	cd tests/testapp
	python manage.py test shop
	popd

fi

if [ $documentation == true ]; then
	pushd .
	cd docs/
	make html
	x-www-browser _build/html/index.html
	popd
fi
