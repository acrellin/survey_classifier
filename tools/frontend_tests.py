#!/usr/bin/env python

import sys
import os
import pathlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
from os.path import join as pjoin
import time
import socket
from baselayer.tools.supervisor_status import supervisor_status
try:
    import http.client as http
except ImportError:
    import httplib as http

from baselayer.app.model_util import clear_tables
from survey_app import models

try:
    import pytest_randomly
    RAND_ARGS = '--randomly-seed=1'
except ImportError:
    RAND_ARGS = ''

TEST_CONFIG = '_test_config.yaml'


base_dir = os.path.abspath(pjoin(os.path.dirname(__file__), '..'))
if len(sys.argv) > 1:
    test_spec = sys.argv[1]
else:
    test_spec = pjoin(base_dir, 'survey_app', 'tests')

print('test_spec:', test_spec)
print('rand_args:', RAND_ARGS)

def add_test_yaml():
    print(f'Creating {TEST_CONFIG}')

    from textwrap import dedent
    with open(TEST_CONFIG, 'w') as f:
        f.write(dedent('''
            database:
                database: survey_app_test
                user: survey_app
                host: localhost
                port: 5432
                password:

            server:
                url: http://localhost:7000
                multi_user: True
                auth:
                  debug_login: True
                  google_oauth2_key:
                  google_oauth2_secret:

            cesium_app:
                url: http://localhost:5000
                survey_classifier_project_id: 1
                survey_classifier_featureset_id: 1
                survey_classifier_model_id: 1
        '''))


def delete_test_yaml():
    os.remove(TEST_CONFIG)


if __name__ == '__main__':
    add_test_yaml()

    # Initialize the test database connection
    from survey_app.models import init_db
    from survey_app.app_server import load_config
    basedir = pathlib.Path(os.path.dirname(__file__))/'..'
    cfg = load_config([basedir/'config.yaml.example',
                       basedir/TEST_CONFIG])
    init_db(**cfg['database'])

    clear_tables()

    web_client = subprocess.Popen(['make', 'testrun'], cwd=base_dir)

    print('[test_frontend] Waiting for supervisord to launch all server processes...')

    try:
        timeout = 0
        while ((timeout < 30) and
               (not all([b'RUNNING' in line for line in supervisor_status()]))):
            time.sleep(1)
            timeout += 1

        if timeout == 10:
            print('[test_frontend] Could not launch server processes; terminating')
            sys.exit(-1)

        for timeout in range(10):
            conn = http.HTTPConnection("localhost", 7000)
            try:
                conn.request('HEAD', '/')
                status = conn.getresponse().status
                if status == 200:
                    break
            except socket.error:
                pass
            time.sleep(1)
        else:
            raise socket.error("Could not connect to localhost:7000.")

        if status != 200:
            print('[test_frontend] Server status is {} instead of 200'.format(
                status))
            sys.exit(-1)
        else:
            print('[test_frontend] Verified server availability')

        print('[test_frontend] Launching pytest on {}...'.format(test_spec))
        print('cwd:', os.getcwd())
        status = subprocess.run(f'python -m pytest -v {test_spec} {RAND_ARGS}',
                                shell=True, check=True)
    except:
        raise
    finally:
        print('[test_frontend] Terminating supervisord...')
        web_client.terminate()
        delete_test_yaml()
