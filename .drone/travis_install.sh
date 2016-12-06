#!/bin/bash

set -ex


section "install.base.requirements"
pip install --upgrade pip
hash -d pip  # find upgraded pip
pip install --retries 3 -q requests
section_end "install.base.requirements"


section "install.python.requirements"
pip install --retries 3 -r requirements.txt
pip list
section_end "install.python.requirements"


section "install.npm.requirements"
sudo ln -s /usr/bin/nodejs /usr/bin/node
npm --version
node --version
make dependencies
section_end "install.npm.requirements"


section "init.survey_app"
make paths
make db_init
make bundle
section_end "init.survey_app"


section "install.chromedriver"
wget http://chromedriver.storage.googleapis.com/2.23/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip chromedriver -d /usr/local/bin
rm chromedriver_linux64.zip
which chromium-browser
chromium-browser --version
section_end "install.chromedriver"


section "install.cesium_web.and.requirements"
make install_cesium_web
section_end "install.cesium_web.and.requirements"


section "download.data.and.initialize.cesium_web"
make cesium_web_init
section_end "download.data.and.initialize.cesium_web"
