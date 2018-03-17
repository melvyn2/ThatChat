#!/usr/bin/env bash
if [[ $0 != "-bash" ]]
then
	echo "You mush run this with source"
	echo "Like so: source extend_path.sh"
	exit 0
fi
SCRIPTPATH="$( cd "$(dirname "$1")" ; pwd -P )"
export PYTHONPATH="$SCRIPTPATH/Cryptography:$PYTHONPATH"
echo "$PYTHONPATH"