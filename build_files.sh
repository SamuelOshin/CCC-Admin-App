#!/bin/bash

echo "BUILD START"
source Scripts/activate
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
echo "BUILD END"
