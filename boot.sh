#!/bin/sh
# this script is used to boot a Docker container
pipenv shell

exec gunicorn -b :5000 --access-logfile - --error-logfile - philetag:app
