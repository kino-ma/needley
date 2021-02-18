#!/bin/bash

# In this setup script, we do migrations that have not applied yet and create Django super user.

wait_for_db() {
    echo -n "waiting for DB"

    until python manage.py inspectdb &>/dev/null
    do
        echo -n '.'
        sleep 1
    done

    echo
    echo "DB is up. start"
}

apply_migrations() {
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

watch_schema() {
    echo "Watching schema..."
    python manage.py graphql_schema --watch
}

wait_for_db

# If some migration tasks are left; then
if [[ 0 < $(python manage.py showmigrations --plan | grep -v '[X]' | wc -l) ]]
then
    # Apply migriations
    apply_migrations

    # Create Django superuser with given name / email / password
    create_superuser

    echo "initiaslizing done"
else
    echo "already initialized"
fi

# Automatically update specs/schema.graphql when files in this project were changed -- non-blocking
watch_schema &

# Run startup command given by docker-compose.yml or so on.
exec "$@"