#!/bin/bash

APP_REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp ./tools/survey_db_init.py ../cesium_web
cd ../cesium_web
make paths
make db_init
python survey_db_init.py
rm survey_db_init.py
make log &
make debug &
sleep 3
cd $APP_REPO_DIR
