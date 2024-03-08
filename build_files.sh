#!/bin/bash

echo "BUILD START"
source /opt/render/project/src/Scripts/activate
python3 manage.py collectstatic --noinput --clear
python3 -m pip install -r requirements.txt
echo "BUILD END"
