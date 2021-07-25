#!/usr/bin/env sh

flake8 /app/skabenproto --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place /app/skabenproto --exclude=__init__.py
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 127 --recursive --apply /app/skabenproto

pytest /app/skabenproto
