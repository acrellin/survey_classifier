#!/usr/bin/env python

import argparse
import uuid
import jwt
import os

from baselayer.app.config import load_config
from baselayer.app.models import init_db
from cesium_app import model_util

cfg_paths = [os.path.join(os.path.dirname(__file__),
                          '../../survey_app/config.yaml.defaults'),
             os.path.join(os.path.dirname(__file__),
                          '../config.yaml.defaults')]

cfg = load_config(cfg_paths)

conn = init_db(**cfg['database'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bot_name')

    args = parser.parse_args()

    token = model_util.create_token_user(
        args.bot_name, [cfg['cesium_app:survey_classifier_project_id']])

    with open((os.path.abspath(os.path.join(
            '../survey_app/', cfg['paths:cesium_web_login_token_folder'],
            'cesium_web_token'))), 'w') as f:
        f.write(token)

    print('Successfully created token user and stored token to disk')
    print(token)
