#!/usr/bin/env bash

export ENV_NAME="venv"

source "${ENV_NAME}/bin/activate"
python3 monitor.py \
    --input_dirs "/mnt/data_1/1c_tj/" \
    --delay 3600
deactivate
