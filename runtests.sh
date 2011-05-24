#!/bin/bash

args=("$@")
num_args=${#args[@]}
index=0

suite='shop addressmodel'
coverage=false
documentation=false
ci=false

while [ "$index" -lt "$num_args" ]
do
	case "${args[$index]}" in
		"--with-docs")
			documentation=true
			;;
		"--with-coverage")
			coverage=true
			;;
		"--ci")
			ci=true
			;;
		*)
			suite="shop.${args[$index]}"
	esac
let "index = $index + 1"
done
if [ $ci == true ]; then
	pushd .
	cd tests/testapp
	coverage run manage.py test $suite
	coverage xml
	popd

elif [ $coverage == true ]; then
	pushd .
	cd tests/testapp
	coverage run manage.py test $suite
	coverage html
	#x-www-browser htmlcov/index.html
	popd

else

	# the default case...
	pushd .
	cd tests/testapp
	python manage.py test $suite
	popd

fi

if [ $documentation == true ]; then
	pushd .
	cd docs/
	make html
	x-www-browser _build/html/index.html
	popd
fi
