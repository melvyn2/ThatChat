#!/usr/bin/env bash
cd "$(dirname ${BASH_SOURCE[0]})"
echo "Removing .pyc files..."
find *.pyc -exec rm -f {}
echo "done\n"
echo "Cleaning \"dist\" and \"build\" directories..."
rm -rf dist/* build/*
echo "done\n"