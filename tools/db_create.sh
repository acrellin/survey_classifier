#!/usr/bin/env bash

id -u postgres

if [[ $? == 0 ]]; then
    echo "Configuring Linux postgres"
    sudo -u postgres psql -c 'CREATE DATABASE survey_app;'
    sudo -u postgres psql -c 'CREATE DATABASE survey_app_test;'
    sudo -u postgres psql -c 'CREATE USER survey_app;'
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE survey_app to survey_app;'
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE survey_app_test to survey_app;'
else
    echo "Configuring OSX postgres"
    createdb -w survey_app
    createdb -w survey_app_test
    createuser survey_app
    psql -U survey_app -c 'GRANT ALL PRIVILEGES ON DATABASE survey_app to survey_app;'
    psql -U survey_app -c 'GRANT ALL PRIVILEGES ON DATABASE survey_app_test to survey_app;'
fi

python -c  'from survey_app.models import create_tables; create_tables()'
