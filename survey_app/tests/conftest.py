'''Test fixture configuration.'''

import pytest
import os
import distutils.spawn
import types
import pathlib
import shutil

from survey_app import models
from survey_app.tests.fixtures import TMP_DIR

from baselayer.app.config import load_config
from baselayer.app.test_util import (driver, MyCustomWebDriver, reset_state,
                                     set_server_url)


print('Loading test configuration from _test_config.yaml')
basedir = pathlib.Path(os.path.dirname(__file__))/'../..'
cfg = load_config([basedir/'test_config.yaml'])
print('\n\n\n', cfg, '\n\n\n')
set_server_url(cfg['server:url'])
print('Setting test database to:', cfg['database'])
print('initing models...')
models.init_db(**cfg['database'])
print('inited models')

@pytest.fixture(scope='session', autouse=True)
def delete_temporary_files(request):
    def teardown():
        shutil.rmtree(TMP_DIR, ignore_errors=True)
    request.addfinalizer(teardown)
