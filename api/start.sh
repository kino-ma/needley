#!/bin/sh

if [[ -n "$ENV_PRODUCTION" ]]
then
    NAME=$DJANGO_PROD_NAME
    EMAIL=$DJANGO_PROD_EMAIL
    PASSWORD=$DJANGO_PROD_PASSWORD
else
    NAME=$DJANGO_DEV_NAME
    EMAIL=$DJANGO_DEV_EMAIL
    PASSWORD=$DJANGO_DEV_PASSWORD
fi

python manage.py migrate
python manage.py create_superuser_with_password --username "$NAME" --email "$EMAIL" --password "$PASSWORD"

python manage.py runserver 0.0.0.0:8000