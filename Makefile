SHELL = /bin/bash
APP_NAME = survey_app
SUPERVISORD=supervisord

.DEFAULT_GOAL := run

bundle = ./public/build/bundle.js
webpack = ./node_modules/.bin/webpack

dependencies:
	@./tools/install_deps.py requirements.txt
	@./tools/install_npm_deps.py package.json

db_init:
	./tools/db_create.sh

db_drop:
	PYTHONPATH=. ./tools/db_drop.py

db_test_data:
	PYTHONPATH=. python ./survey_app/models.py

download_data:
	git clone https://github.com/acrellin/survey_classifier_data.git ../survey_classifier_data

install_cesium_web:
	git clone https://github.com/cesium-ml/cesium_web.git ../cesium_web
	pip install -r ../cesium_web/requirements.txt

cesium_web_init: download_data
	./tools/init_cesium_web_db.sh

$(bundle): webpack.config.js
	$(webpack)

bundle: $(bundle)

bundle-watch:
	$(webpack) -w

paths:
	mkdir -p log run tmp
	mkdir -p log/sv_child
	mkdir -p ~/.local/$(APP_NAME)/logs

log: paths
	./tools/watch_logs.py

run: paths dependencies
	$(SUPERVISORD) -c conf/supervisord.conf

debug:
	$(SUPERVISORD) -c conf/supervisord_debug.conf

# Attach to terminal of running webserver; useful to, e.g., use pdb
attach:
	supervisorctl -c conf/supervisord_common.conf fg app

clean:
	rm $(bundle)

test_headless: paths dependencies
	PYTHONPATH='.' xvfb-run ./tools/frontend_tests.py

test: paths dependencies
	PYTHONPATH='.' ./tools/frontend_tests.py

status:
	PYTHONPATH='.' ./tools/supervisor_status.py
