SHELL = /bin/bash
APP_NAME = survey_app
SUPERVISORD=FLAGS=$$FLAGS supervisord -c baselayer/conf/supervisor/supervisor.conf
SUPERVISORCTL=FLAGS=$$FLAGS supervisorctl -c baselayer/conf/supervisor/supervisor.conf

.DEFAULT_GOAL := run

bundle = ./static/build/bundle.js
webpack = ./node_modules/.bin/webpack --display-error-details

baselayer/README.md:
	git submodule update --init --remote
	$(MAKE) baselayer-update

.PHONY: baselayer-update
baselayer-update:
	./baselayer/tools/submodule_update.sh

fill_conf_values:
	PYTHONPATH=. ./baselayer/tools/fill_conf_values.py

dependencies: baselayer/README.md
	@./baselayer/tools/silent_monitor.py pip install -r baselayer/requirements.txt
	@./baselayer/tools/silent_monitor.py pip install -r requirements.txt
	@./baselayer/tools/silent_monitor.py ./baselayer/tools/check_js_deps.sh

db_init:
	@PYTHONPATH=. ./baselayer/tools/silent_monitor.py ./baselayer/tools/db_init.py

db_clear:
	PYTHONPATH=. ./baselayer/tools/db_init.py -f

db_test_data:
	@PYTHONPATH=. python ./survey_app/models.py

download_data:
	git clone https://github.com/acrellin/survey_classifier_data.git ../survey_classifier_data || echo 'Data has already been downloaded.'

install_cesium_web:
	git clone https://github.com/cesium-ml/cesium_web.git ../cesium_web
	pip install -r ../cesium_web/requirements.txt

cesium_web_init: download_data
	@PYTHONPATH=. ./tools/survey_db_init.sh

$(bundle): webpack.config.js package.json
	$(webpack)

bundle: $(bundle)

bundle-watch:
	$(webpack) -w

paths:
	mkdir -p log run tmp
	mkdir -p log/sv_child
	mkdir -p ~/.local/$(APP_NAME)/logs

log: paths
	./baselayer/tools/watch_logs.py

run: paths dependencies fill_conf_values
	@echo "Supervisor will now fire up various micro-services."
	@echo
	@echo " - Please run \`make log\` in another terminal to view logs"
	@echo " - Press Ctrl-C to abort the server"
	@echo " - Run \`make monitor\` in another terminal to restart services"
	@echo
	$(SUPERVISORD)

debug: fill_conf_values
	@echo "Starting web service in debug mode"
	@echo "Press Ctrl-D to stop"
	@echo
	@export FLAGS="--debug" && $(SUPERVISORD) &
	@sleep 1 && $(SUPERVISORCTL) -i status
	@$(SUPERVISORCTL) shutdown

# Attach to terminal of running webserver; useful to, e.g., use pdb
attach:
	$(SUPERVISORCTL) fg app

testrun: paths dependencies fill_conf_values
	export FLAGS="--config _test_config.yaml" && $(SUPERVISORD)

clean:
	rm $(bundle)

test_headless: paths dependencies fill_conf_values
	PYTHONPATH='.' xvfb-run ./tools/frontend_tests.py

test: paths dependencies fill_conf_values
	PYTHONPATH='.' ./tools/frontend_tests.py

stop:
	$(SUPERVISORCTL) stop all

status:
	PYTHONPATH='.' ./baselayer/tools/supervisor_status.py

# Call this target to see which Javascript dependencies are not up to date
check-js-updates:
	./baselayer/tools/check_js_updates.sh
