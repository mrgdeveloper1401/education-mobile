#!/bin/bash

python manage.py collectstatic --noinput
gunicorn base.asgi:application -c /home/app/scripts/gunicorn.conf.py