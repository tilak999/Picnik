#!/bin/bash

python -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools poetry

poetry install
prisma migrate deploy
prisma generate

echo "===>> Run 'source .venv/bin/activate'"