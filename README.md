# Light Curve Survey Classification Web App

[![Build Status](https://travis-ci.org/acrellin/survey_classifier_app.svg?branch=master)](https://travis-ci.org/acrellin/survey_classifier_app)

## About

A light curve survey classification web app built on
[`cesium`](https://github.com/cesium-ml/cesium),
[`cesium_web`](https://github.com/cesium-ml/cesium_web), and
[`baselayer`](https://github.com/cesium-ml/baselayer).

## Running the app locally
1. Install the following dependencies:

- supervisor
- nginx
- npm

### MacOS
Using [Homebrew](http://brew.sh/):

`brew install supervisor nginx node`

### Linux
On Debian or Ubuntu:
```
sudo apt-get install nginx supervisor npm nodejs-legacy
```

2. Install Python and npm dependencies: `make dependencies`
3. Download `cesium_web` and install dependencies: `make install_cesium_web`
4. Download data, initialize `cesium_web` database and start `cesium_web`:
`make cesium_web_init`
5. Initialize database with `make db_init`.
6. Run `make` to start the server, and navigate to `localhost:7000` to start using the app.

## Dev Tips
Debugging:

- Run `make log` to watch log output
- Run `make debug` to start webserver in debug mode
- Run `make attach` to attach to output of webserver, e.g. for use with `pdb.set_trace()`
