#!/usr/bin/env python

import argparse
import uuid
import jwt
import os

from baselayer.app.config import load_config
from baselayer.app.models import init_db
from cesium_app import models


cfg = load_config([os.path.join(os.path.dirname(__file__),
                                '../../survey_app/config.yaml.example'),
                   os.path.join(os.path.dirname(__file__),
                                '../config.yaml.example')])

conn = init_db(**cfg['database'])


def generate_token(bot_name):
    raw_token = str(uuid.uuid4())
    encoded_token = jwt.encode({'bot_name': bot_name,
                                'token': raw_token},
                               cfg['app:secret-key']).decode()

    return encoded_token, raw_token


def add_token_to_db(bot_name, raw_token):
    u = models.User(username=raw_token)
    p = models.Project.query.get(cfg['cesium_app:survey_classifier_project_id'])
    u.projects.append(p)
    models.DBSession().add(u)
    models.DBSession().commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bot_name')
    args = parser.parse_args()

    encoded_token, raw_token = generate_token(args.bot_name)

    add_token_to_db(args.bot_name, raw_token)

    with open((os.path.abspath(os.path.join(
            '../survey_app/', cfg['paths:cesium_web_login_cookie_folder'],
            'cesium_web_token'))), 'w') as f:
        f.write(encoded_token)

    print('Successfully generated token, added to DB and stored to disk')
    print(encoded_token)
