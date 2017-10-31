#!/bin/bash

set -ex


section "install.base.requirements"
# Install v1.7 or newer of nginx to support 'if' statement for logging
sudo apt-add-repository -y ppa:nginx/development
sudo apt update
sudo apt install -y nginx

pip install --upgrade pip
hash -d pip  # find upgraded pip
pip install --retries 3 -q requests
section_end "install.base.requirements"


section "install.python.requirements"
pip install --retries 3 -r requirements.txt
section_end "install.python.requirements"


# section "install.yarn"
# curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
# echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
# sudo apt-get update && sudo apt-get install -y yarn
# section_end "install.yarn"

# section "install.npm.requirements.with.yarn"
# yarn --version
# yarn --ignore-engines
# section_end "install.npm.requirements.with.yarn"


section "install.npm.reqs"
npm -g install npm@latest
npm --version
node --version
pip list --format=columns
section_end "install.npm.reqs"


section "init.survey_app"
make db_init
section_end "init.survey_app"


section "install.chromedriver"
wget https://chromedriver.storage.googleapis.com/2.33/chromedriver_linux64.zip
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
