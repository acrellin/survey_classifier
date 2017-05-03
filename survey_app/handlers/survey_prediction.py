from .base import AccessError
from .general_prediction import GeneralPredictionHandler
from ..models import Prediction, Dataset, Project
from ..config import cfg
from .. import util

import tornado.gen

import cesium
import uuid
import datetime
import tempfile
import requests
import json
import pandas as pd


class SurveyPredictionHandler(GeneralPredictionHandler):
    """Handler for performing survey predictions."""
    @tornado.gen.coroutine
    def _await_prediction(self, prediction, cesium_app_prediction_id):
        try:
            while True:
                pred_info = requests.get('{}/predictions/{}'.format(
                    cfg['cesium_app']['url'],
                    cesium_app_prediction_id)).json()['data']
                if pred_info['finished']:
                    prediction.task_id = None
                    prediction.finished = datetime.datetime.now()
                    prediction.model_type = pred_info['model_type']
                    prediction.model_name = pred_info['model_name']
                    prediction.results = json.dumps(pred_info['results'])
                    prediction.isProbabilistic = pred_info['isProbabilistic']
                    prediction.file_path = pred_info['file']
                    prediction.dataset_name = pred_info['dataset_name']
                    prediction.save()
                    break
                else:
                    yield tornado.gen.sleep(1)

            self.action('survey_app/SHOW_NOTIFICATION',
                        payload={
                            "note": "Prediction '{}/{}' completed".format(
                                pred_info['dataset_name'],
                                pred_info['model_name'])
                            })

        except Exception as e:
            prediction.delete_instance()
            self.action('survey_app/SHOW_NOTIFICATION',
                        payload={
                            "note": "Prediction failed "
                            "with error {}. Please try again.".format(e),
                            "type": "error"})

        self.action('survey_app/FETCH_PREDICTIONS')
        self.action('survey_app/DO_SCIENCE_PREDICTIONS',
                    payload={'prediction_id': prediction.id})

    @tornado.gen.coroutine
    def post(self):
        data = self.get_json()

        dataset_id = data['datasetID']
        model_id = data['modelID']

        username = self.get_username()

        dataset = Dataset.get(Dataset.id == dataset_id)
        cesium_dataset_id = Dataset.get(Dataset.id == dataset_id).cesium_app_id

        data = {'datasetID': cesium_dataset_id,
                'modelID': model_id}
        # POST prediction to cesium_web
        r = requests.post('{}/predictions'.format(cfg['cesium_app']['url']),
                          data=json.dumps(data)).json()
        if r['status'] != 'success':
            return self.error('An error occurred while processing the request'
                              'to cesium_web: {}'.format(r['message']))

        prediction = Prediction.create(dataset=dataset, project=dataset.project,
                                       model_id=model_id)

        prediction.task_id = str(uuid.uuid4())
        prediction.cesium_app_id = r['data']['id']
        prediction.model_type = r['data']['model_type']
        prediction.model_name = r['data']['model_name']
        prediction.dataset_name = r['data']['dataset_name']
        prediction.save()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_prediction, prediction, r['data']['id'])

        return self.success(prediction, 'survey_app/FETCH_PREDICTIONS')

    def get(self, prediction_id=None, action=None):
        if action == 'download':
            pred_path = self._get_prediction(prediction_id).file_path
            try:
                fset, data = cesium.featurize.load_featureset(pred_path)
            except OSError:
                return self.error('The requested file could not be found. '
                                  'The cesium_web app must be running on the '
                                  'same machine to download prediction results.')
            result = pd.DataFrame({'ts_name': fset.index,
                                   'label': data['labels'],
                                   'prediction': data['preds']},
                                  columns=['ts_name', 'label', 'prediction'])
            if len(data.get('pred_probs', [])) > 0:
                result['probability'] = data['pred_probs'].max(axis=1).values
            self.set_header("Content-Type", 'text/csv; charset="utf-8"')
            self.set_header("Content-Disposition", "attachment; "
                            "filename=cesium_prediction_results.csv")
            self.write(result.to_csv(index=False))
