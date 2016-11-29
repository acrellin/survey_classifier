import tornado.web

import sys


from .handlers import (
    SocketAuthTokenHandler,
    ProjectHandler,
    DatasetHandler,
    PredictionHandler
    )



def make_app():
    """Create and return a `tornado.web.Application` object with specified
    handlers and settings.
    """
    settings = {
        'static_path': '../public',
        'autoreload': '--debug' in sys.argv
        }

    handlers = [
        (r'/project(/.*)?', ProjectHandler),
        (r'/dataset(/.*)?', DatasetHandler),
        (r'/predictions(/[0-9]+)?', PredictionHandler),
        (r'/predictions/([0-9]+)/(download)', PredictionHandler),
        (r'/socket_auth_token', SocketAuthTokenHandler),
        (r'/(.*)', tornado.web.StaticFileHandler,
         {'path': 'public/', 'default_filename': 'index.html'})
    ]

    return tornado.web.Application(handlers, **settings)
