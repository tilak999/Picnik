#!/bin/bash

python -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools
pip install poetry

poetry install

echo "===>> Run 'source .venv/bin/activate'"