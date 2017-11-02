.DEFAULT_GOAL := run

baselayer/README.md:
	git submodule update --init --remote
	$(MAKE) baselayer-update

.PHONY: baselayer-update run log
baselayer-update:
	./baselayer/tools/submodule_update.sh

log:
	make -C baselayer log

run:
	make -C baselayer run

run_testing:
	make -C baselayer run_testing

run_production:
	make -C baselayer run_production

test:
	make -C baselayer test

test_headless:
	make -C baselayer test_headless

db_init:
	make -C baselayer db_init

db_clear:
	make -C baselayer db_clear

attach:
	make -C baselayer attach

clean:
	make -C baselayer clean

-include "baselayer/README.md"  # always clone baselayer if it doesn't exist

download_data:
	git clone https://github.com/acrellin/survey_classifier_data.git ../survey_classifier_data || echo 'Data has already been downloaded.'

install_cesium_web:
	git clone https://github.com/acrellin/cesium_web.git ../cesium_web
	pip install -r ../cesium_web/requirements.txt

cesium_web_init: download_data
	@PYTHONPATH=. ./tools/survey_db_init.sh
