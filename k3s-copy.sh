#!/usr/bin/env bash


# StackOverflow: https://stackoverflow.com/questions/8880603/loop-through-an-array-of-strings-in-bash
images=( "your-dl-server")
tags=( "1.0" )

# get length of an array
arraylength=${#images[@]}

# use for loop to read all values and indexes
for (( i=0; i<${arraylength}; i++ ));
do
	podman save --output "${images[$i]}.tar" "${images[$i]}:${tags[$i]}"
	sudo k3s ctr image import "${images[$i]}.tar"
	rm "${images[$i]}.tar"
	echo "index: $i, value: ${images[$i]}:${tags[$i]}"
done
