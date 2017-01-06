from .base import BaseHandler, AccessError
from ..models import Prediction, Project
from ..config import cfg
from .. import util

import cesium
import tempfile
import requests


class GeneralPredictionHandler(BaseHandler):
    """Handler for fetching and deleting predictions."""
    def _get_prediction(self, prediction_id):
        try:
            d = Prediction.get(Prediction.id == prediction_id)
        except Prediction.DoesNotExist:
            raise AccessError('No such dataset')

        if not d.is_owned_by(self.get_username()):
            raise AccessError('No such dataset')

        return d

    def get(self, prediction_id=None):
        if prediction_id is None:
            predictions = [prediction
                           for project in Project.all(self.get_username())
                           for prediction in project.predictions]
            prediction_info = [p.display_info() for p in predictions]
        else:
            prediction = self._get_prediction(prediction_id)
            prediction_info = prediction.display_info()

        return self.success(prediction_info)

    def delete(self, prediction_id):
        prediction = self._get_prediction(prediction_id)
        # Make request to delete prediction in cesium_web
        r = requests.delete('{}/predictions/{}'.format(
            cfg['cesium_app']['url'], prediction.cesium_app_id)).json()
        prediction.delete_instance()
        return self.success(action='survey_app/FETCH_PREDICTIONS')
