# Light Curve Survey Classification Web App

## About

A light curve survey classification web app built on
[`cesium`](https://github.com/cesium-ml/cesium),
[`cesium-web`](https://github.com/cesium-ml/cesium_web), and
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
3. Run `make` to start the server, and navigate to `localhost:7000`.

## Dev Tips
Debugging:

- Run `make log` to watch log output
- Run `make debug` to start webserver in debug mode
- Run `make attach` to attach to output of webserver, e.g. for use with `pdb.set_trace()`
