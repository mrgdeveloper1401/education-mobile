#!/bin/bash

python manage.py collectstatic --noinput
python manage.py makemigrations
#python manage.py migrate
gunicorn base.asgi:application -c gunicorn.conf.py