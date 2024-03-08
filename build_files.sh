#!/bin/bash

echo "BUILD START"
python3 manage.py collectstatic --noinput --clear
python3 -m pip install -r requirements.txt
echo "BUILD END"
