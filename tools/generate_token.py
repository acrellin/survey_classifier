#!/usr/bin/env python

import argparse
import os

from baselayer.app.config import load_config
from cesium_app.model_util import create_token_user


cfg = load_config([os.path.join(os.path.dirname(__file__),
                                '../../survey_app/config.yaml.example'),
                   os.path.join(os.path.dirname(__file__),
                                '../config.yaml.example')])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bot_name')
    args = parser.parse_args()

    token = create_token_user(args.bot_name,
                              cfg['cesium_app:survey_classifier_project_id'])

    with open((os.path.abspath(os.path.join(
            '../survey_app/', cfg['paths:cesium_web_login_token_folder'],
            'cesium_web_token'))), 'w') as f:
        f.write(token)

    print('Successfully generated token, added to DB and stored to disk')
    print(token)
