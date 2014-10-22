#!/bin/bash

for d in *_git; do
		cd ./"$d"/ &&
		git log > ../"$d".log ;
		cd ..
done
