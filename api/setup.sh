#!/bin/bash

# In this setup script, we do migrations that have not applied yet and create Django super user.

apply_migrations() {
    python manage.py makemigrations
    # Apply migrations
    python manage.py migrate
}

create_superuser() {
    if [[ -n "$ENV_PRODUCTION" ]]
    then
        # If running on production environment
        echo "initializing production environment..."
        NAME=$DJANGO_PROD_NAME
        EMAIL=$DJANGO_PROD_EMAIL
        PASSWORD=$DJANGO_PROD_PASSWORD
    else
        # If running on development environment
        echo "initializing develop environment..."
        NAME=$DJANGO_DEV_NAME
        EMAIL=$DJANGO_DEV_EMAIL
        PASSWORD=$DJANGO_DEV_PASSWORD
    fi

    python manage.py create_superuser_with_password --username "$NAME" --email "$EMAIL" --password "$PASSWORD"
}

# If some migration tasks are left; then
if ! python manage.py makemigrations | grep 'No changes detected' >/dev/null
then
    # Apply migriations
    apply_migrations

    # Create Django superuser with given name / email / password
    create_superuser

    echo "initiaslizing done"
else
    echo "already initialized"
fi

# Run startup command given by docker-compose.yml or so on.
exec "$@"