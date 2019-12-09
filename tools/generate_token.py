#!/usr/bin/env python

import argparse
import uuid
import os

from baselayer.app.config import load_config
from baselayer.app.models import init_db
from cesium_app import model_util

cfg_paths = [os.path.join(os.path.dirname(__file__),
                          '../config.yaml.defaults'),
             os.path.join(os.path.dirname(__file__),
                          '../cesium_web/config.yaml.defaults')]

cfg = load_config(cfg_paths)
conn = init_db(**cfg['database'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bot_name')

    args = parser.parse_args()

    token = model_util.create_token_user(
        args.bot_name, [cfg['cesium_app']['survey_classifier_project_id']])

    token_path = os.path.abspath(os.path.join(
        cfg['paths']['cesium_web_login_token_folder'], 'cesium_web_token'))
    if not os.path.exists(os.path.dirname(token_path)):
        print(f'{os.path.dirname(token_path)} does not exist - creating it now')
        os.makedirs(os.path.dirname(token_path))

    with open(token_path, 'w') as f:
        f.write(token)

    print('Successfully created token user and stored token to disk'
          f' ({token_path})')
    print(token)
