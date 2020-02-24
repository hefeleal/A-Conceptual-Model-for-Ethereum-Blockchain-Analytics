#!/bin/bash

if [ "$#" -lt 1 ]; then
  echo "Please specify the database user"
  exit 1
fi
if [ "$#" -lt 2 ]; then
  echo "Please specify the database password"
  exit 1
fi

DB_USER=$1
DB_PASSWORD=$2

for dirname in ../multi_compile_contracts/openzeppelin/safemath/*/; do
	if [[ "$dirname" =~ safemath\/(.*)\/ ]]; then
		VERSION=$(echo "${BASH_REMATCH[1]}" | sed -e "s/-/./g")
		python3 contract_analysis/extract_library_functions.py --dirname "${dirname}" --libversion "${VERSION}" --libname SafeMath --mysql-user "$DB_USER" --mysql-password "$DB_PASSWORD"
	fi
done
