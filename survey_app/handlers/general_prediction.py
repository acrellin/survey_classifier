from .base import BaseHandler
from baselayer.app.custom_exceptions import AccessError
from ..models import Prediction, Project, DBSession

import requests
import tornado.web


class GeneralPredictionHandler(BaseHandler):
    """Handler for fetching and deleting predictions."""
    @tornado.web.authenticated
    def get(self, prediction_id=None):
        if prediction_id is None:
            predictions = [prediction
                           for project in self.current_user.projects
                           for prediction in project.predictions]
            prediction_info = [p.display_info() for p in predictions]
        else:
            prediction = Prediction.get_if_owned_by(prediction_id,
                                                    self.current_user)
            prediction_info = prediction.display_info()

        return self.success(prediction_info)

    @tornado.web.authenticated
    def delete(self, prediction_id):
        prediction = Prediction.get_if_owned_by(prediction_id,
                                                self.current_user)
        DBSession().delete(prediction)
        DBSession().commit()
        return self.success(action='survey_app/FETCH_PREDICTIONS')
