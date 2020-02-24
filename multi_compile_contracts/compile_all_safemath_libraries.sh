#!/bin/bash

for filename in openzeppelin/safemath/*.sol; do
	if [[ "$filename" =~ Math-(.*)\.sol ]]; then
		node index.js "$filename" "openzeppelin/safemath/${BASH_REMATCH[1]}"
	fi
done
