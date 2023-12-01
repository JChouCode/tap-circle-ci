#!/usr/bin/env bash

python -m venv venv/tap-circle-ci
source /code/venv/tap-circle-ci/bin/activate

pip install -e .[tests]

echo "source /code/venv/tap-circle-ci/bin/activate" >> ~/.bashrc
echo -e "\n\nINFO: Dev environment ready."

tail -f /dev/null
