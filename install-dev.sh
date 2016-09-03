#!/usr/bin/env bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_NAME=`basename "$BASE_DIR"`

if [ `uname` == 'Darwin' ]; then
	dstFolder=~/"Library/Application Support/Sublime Text 3/Packages/$BASE_NAME"
	if ! [ -d "$dstFolder" ]; then
		mkdir "$dstFolder"
	fi
	cp -r "$BASE_DIR"/* "$dstFolder"
else
	echo "Support macOS only"
fi
