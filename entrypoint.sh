#!/bin/sh

if [ "$DATABASE" = "postgresql" ]
then
    echo "Waiting for PostgreSQL ..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

echo "Apply DB migrations"
python3 manage.py migrate
python3 manage.py createsuperifnone

exec "$@"