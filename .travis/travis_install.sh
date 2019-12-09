#!/bin/bash

set -ex

section "install.base.requirements"
# Install v1.7 or newer of nginx to support 'if' statement for logging
sudo apt-add-repository -y ppa:nginx/stable
sudo apt update
sudo apt install -y nginx firefox

nginx -v
firefox --version

pip install --upgrade pip
hash -d pip  # find upgraded pip
section_end "install.base.requirements"

section "install.baselayer.requirements"
npm -g install npm@next
npm --version
node --version

# TODO replace w/ baselayer dependent build info
if [[ -n ${TRIGGERED_FROM_REPO} ]]; then
    mkdir cesium-clone
    cd cesium-clone
    git init
    git remote add origin git://github.com/${TRIGGERED_FROM_REPO}
    git fetch --depth=1 origin ${TRIGGERED_FROM_BRANCH}
    git checkout -b ${TRIGGERED_FROM_BRANCH} ${TRIGGERED_FROM_SHA}
    pip install .
    cd ..
fi

pip list --format=columns
section_end "install.baselayer.requirements"


section "install.python.requirements"
pip install --retries 3 -r requirements.txt
section_end "install.python.requirements"


section "init.db"
make db_init
section_end "init.db"


# section "install.yarn"
# curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
# echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
# sudo apt-get update && sudo apt-get install -y yarn
# section_end "install.yarn"

# section "install.npm.requirements.with.yarn"
# yarn --version
# yarn --ignore-engines
# section_end "install.npm.requirements.with.yarn"


section "install.geckodriver.and.selenium"
GECKO_VER=0.24.0
wget https://github.com/mozilla/geckodriver/releases/download/v${GECKO_VER}/geckodriver-v${GECKO_VER}-linux64.tar.gz
sudo tar -xzf geckodriver-v${GECKO_VER}-linux64.tar.gz -C /usr/local/bin
rm geckodriver-v${GECKO_VER}-linux64.tar.gz
which geckodriver
geckodriver --version
pip install --upgrade selenium
python -c "import selenium; print(f'Selenium {selenium.__version__}')"
section_end "install.geckodriver.and.selenium"


section "init.submodules"
make baselayer/README.md
section_end "init.submodules"


section "ls.submod.dirs"
ls survey_classifier_data
ls survey_classifier_data/data
ls cesium_web
section_end "ls.submod.dirs"


section "install.cesium_web.requirements"
make install_cesium_web
section_end "install.cesium_web.requirements"


section "initialize.cesium_web"
make cesium_web_init
section_end "initialize.cesium_web"


section "install.deps"
make dependencies
pip list --format=columns
nginx -v
section_end "install.deps"
