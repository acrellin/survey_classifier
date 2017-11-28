.DEFAULT_GOAL := run

-include baselayer/Makefile

baselayer/README.md:
	git submodule update --init --remote
	$(MAKE) baselayer-update

.PHONY: baselayer-update run log
baselayer-update:
	./baselayer/tools/submodule_update.sh

install_cesium_web:
	pip install -r ./cesium_web/requirements.txt

cesium_web_init:
	@PYTHONPATH=. ./tools/survey_db_init.sh
