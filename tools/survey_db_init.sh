#!/bin/bash

pwd
make -C ../cesium_web baselayer/README.md
make -C ../cesium_web db_init
PYTHONPATH=../cesium_web python ./tools/survey_db_init.py
PYTHONPATH=../cesium_web python ./tools/generate_token.py survey_app_bot
make -C ../cesium_web log &
make -C ../cesium_web &
sleep 3
