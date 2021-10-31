#!/bin/bash
pip install --upgrade pip
pip install -r ./thx_bot/requirements/requirements.txt -r ./thx_bot/requirements/dev-requirements.txt
python3 main.py