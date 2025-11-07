#!/bin/bash

python manage.py collectstatic --noinput
gunicorn base.asgi:application -c gunicorn.conf.py