#!/bin/bash

APP_REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp ./tools/survey_db_init.py ../cesium_web
cd ../cesium_web
make paths
make db_init
PYTHONPATH=.. python survey_db_init.py
rm survey_db_init.py
make log &
make &
sleep 3
PYTHONPATH=.. python cesium_web_login.py
cd $APP_REPO_DIR
