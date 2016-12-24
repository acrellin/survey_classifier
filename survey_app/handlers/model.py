'''Handler for '/models' route.'''

from .base import BaseHandler
from ..config import cfg

import requests


class ModelHandler(BaseHandler):
    def get(self, model_id=None):
        if model_id is not None:
            model_info = requests.get('{}/models/{}'.format(
                cfg['cesium_app']['url'], model_id)).json()['data']
        else:
            model_info = [model for model in requests.get('{}/models'.format(
                cfg['cesium_app']['url'])).json()['data'] if model['project'] ==
                          cfg['cesium_app']['survey_classifier_project_id']]

        return self.success(model_info)
