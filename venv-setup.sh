#!/usr/bin/env bash

export ENV_NAME="venv"

python3 -m venv "${ENV_NAME}"
source "${ENV_NAME}/bin/activate"
chmod +x "venv-run.sh"
pip install -r "requirements.txt"
deactivate
