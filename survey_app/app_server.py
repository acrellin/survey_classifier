import tornado.web

import sys
import os

from . import models

from baselayer.app import model_util

from .handlers import (
    SocketAuthTokenHandler,
    ProjectHandler,
    DatasetHandler,
    ModelHandler,
    GeneralPredictionHandler,
    SurveyPredictionHandler,
    SciencePredictionHandler
    )



def make_app(cfg, baselayer_handlers, baselayer_settings):
    """Create and return a `tornado.web.Application` object with specified
    handlers and settings.

    Parameters
    ----------
    cfg : Config
        Loaded configuration.  Can be specified with '--config'
        (multiple uses allowed).
    baselayer_handlers : list
        Tornado handlers needed for baselayer to function.
    baselayer_settings : cfg
        Settings needed for baselayer to function.

    """
    if baselayer_settings['cookie_secret'] == 'abc01234':
        print('!' * 80)
        print('  Your server is insecure. Please update the secret string ')
        print('  in the configuration file!')
        print('!' * 80)

    for path_name, path in cfg['paths'].items():
        if not os.path.exists(path):
            print("Creating %s" % path)
            try:
                os.makedirs(path)
            except Exception as e:
                print(e)

    handlers = [
        (r'/project(/.*)?', ProjectHandler),
        (r'/dataset(/.*)?', DatasetHandler),
        (r'/models(/.*)?', ModelHandler),
        (r'/predictions(/[0-9]+)?', GeneralPredictionHandler),
        (r'/survey_predictions(/[0-9]+)?', SurveyPredictionHandler),
        (r'/survey_predictions/([0-9]+)/(download)', SurveyPredictionHandler),
        (r'/science_predictions(/[0-9]+)?', SciencePredictionHandler),
        (r'/science_predictions/([0-9]+)/(download)', SciencePredictionHandler),
        (r'/socket_auth_token', SocketAuthTokenHandler),
        (r'/(.*)', tornado.web.StaticFileHandler,
         {'path': 'public/', 'default_filename': 'index.html'})
    ]

    settings = baselayer_settings
    # settings.update({})  # Specify additional settings here

    app = tornado.web.Application(handlers, **settings)
    models.init_db(**cfg['database'])
    model_util.create_tables()

    return app
