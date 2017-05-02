#!/bin/bash

set -ex


section "install.base.requirements"
pip install --upgrade pip
hash -d pip  # find upgraded pip
pip install --retries 3 -q requests
section_end "install.base.requirements"


section "install.python.requirements"
pip install --retries 3 -r requirements.txt
section_end "install.python.requirements"


section "install.yarn"
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt-get update && sudo apt-get install -y yarn
section_end "install.yarn"

section "install.npm.requirements.with.yarn"
yarn --version
yarn
section_end "install.npm.requirements.with.yarn"


section "init.survey_app"
make paths
make db_init
make bundle
section_end "init.survey_app"


section "install.chromedriver"
wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip
sudo unzip chromedriver_linux64.zip chromedriver -d /usr/local/bin
rm chromedriver_linux64.zip
which chromium-browser
chromium-browser --version
section_end "install.chromedriver"


section "download.data"
make download_data
section_end "download.data"


section "install.cesium_web.and.requirements"
make install_cesium_web
section_end "install.cesium_web.and.requirements"


section "initialize.cesium_web"
make cesium_web_init
section_end "initialize.cesium_web"


section "list.packages"
pip list --format=columns
section_end "list.packages"
