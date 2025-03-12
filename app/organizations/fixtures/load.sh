#!/bin/sh

python manage.py loaddata organization.json
python manage.py loaddata building.json
python manage.py loaddata department.json
python manage.py loaddata room.json
