#!/bin/bash

APP_REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp ./tools/survey_db_init.py ../cesium_web
cp ./tools/generate_token.py ../cesium_web/tools
cd ../cesium_web
make paths
make dependencies
make db_init
PYTHONPATH=.. python survey_db_init.py
PYTHONPATH=. python tools/generate_token.py survey_app_bot
rm survey_db_init.py
rm tools/generate_token.py
make log &
make &
sleep 3
cd $APP_REPO_DIR/..
