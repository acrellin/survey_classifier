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


section "download.data"
git clone https://github.com/acrellin/survey_classifier_data.git
section_end "download data"


section "initialize.cesium_web"
git clone https://github.com/cesium-ml/cesium_web.git
cd cesium_web
cp ../tools/survey_db_init.py ./
make paths
make db_init
pip install --retries 3 -r requirements.txt
python survey_db_init.py
make debug &
cd ..
section_end "initialize.cesium_web"