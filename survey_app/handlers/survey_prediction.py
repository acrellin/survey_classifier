from baselayer.app.custom_exceptions import AccessError
from .general_prediction import GeneralPredictionHandler
from ..models import Prediction, Dataset, Project, DBSession

import tornado.gen

import cesium
import cesium.featurize
import uuid
import datetime
import tempfile
import requests
import json
import pandas as pd


class SurveyPredictionHandler(GeneralPredictionHandler):
    """Handler for performing survey predictions."""
    @tornado.gen.coroutine
    def _await_prediction(self, prediction):
        try:
            while True:
                pred_info = requests.get(
                    '{}/predictions/{}'.format(self.cfg['cesium_app:url'],
                                               prediction.cesium_app_id),
                    cookies=self.get_cesium_auth_cookie()).json()['data']
                if pred_info['finished']:
                    prediction.task_id = None
                    prediction.finished = datetime.datetime.now()
                    prediction.model_type = pred_info['model_type']
                    prediction.model_name = pred_info['model_name']
                    prediction.results = bytes(json.dumps(pred_info['results']),
                                               encoding='utf-8')
                    prediction.isProbabilistic = pred_info['isProbabilistic']
                    prediction.file_path = pred_info['file_uri']
                    prediction.dataset_name = pred_info['dataset_name']
                    DBSession().add(prediction)
                    DBSession().commit()
                    break
                else:
                    yield tornado.gen.sleep(1)

            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={
                            "note": "Prediction '{}/{}' completed".format(
                                pred_info['dataset_name'],
                                pred_info['model_name'])
                            })

        except Exception as e:
            prediction.delete_instance()
            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={
                            "note": "Prediction failed "
                            "with error {}. Please try again.".format(e),
                            "type": "error"})

        self.action('survey_app/FETCH_PREDICTIONS')
        self.action('survey_app/DO_SCIENCE_PREDICTIONS',
                    payload={'prediction_id': prediction.id})

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        data = self.get_json()

        dataset_id = data['datasetID']
        model_id = data['modelID']

        dataset = Dataset.get_if_owned_by(dataset_id, self.current_user)
        cesium_dataset_id = dataset.cesium_app_id

        data = {'datasetID': cesium_dataset_id,
                'modelID': model_id}
        # POST prediction to cesium_web
        r = requests.post('{}/predictions'.format(self.cfg['cesium_app:url']),
                          data=json.dumps(data),
                          cookies=self.get_cesium_auth_cookie()).json()
        if r['status'] != 'success':
            return self.error('An error occurred while processing the request '
                              'to cesium_web: {}'.format(r['message']))

        prediction = Prediction(dataset=dataset, project=dataset.project,
                                model_id=model_id)

        prediction.task_id = str(uuid.uuid4())
        prediction.cesium_app_id = r['data']['id']
        prediction.model_type = r['data']['model_type']
        prediction.model_name = r['data']['model_name']
        prediction.dataset_name = r['data']['dataset_name']
        DBSession().add(prediction)
        DBSession().commit()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_prediction, prediction)

        return self.success(prediction, 'survey_app/FETCH_PREDICTIONS')

    @tornado.web.authenticated
    def get(self, prediction_id=None, action=None):
        if action == 'download':
            pred_path = Prediction.get_if_owned_by(prediction_id,
                                                   self.current_user).file_path
            try:
                fset, data = cesium.featurize.load_featureset(pred_path)
            except OSError:
                return self.error('The requested file could not be found. '
                                  'The cesium_web app must be running on the '
                                  'same machine to download prediction results.')
            result = pd.DataFrame(({'label': data['labels']}
                                   if len(data['labels']) > 0 else None),
                                  index=fset.index)
            if len(data.get('pred_probs', [])) > 0:
                result = pd.concat((result, data['pred_probs']), axis=1)
            else:
                result['prediction'] = data['preds']
            result.index.name = 'ts_name'
            self.set_header("Content-Type", 'text/csv; charset="utf-8"')
            self.set_header("Content-Disposition", "attachment; "
                            "filename=survey_app_prediction_results.csv")
            self.write(result.to_csv(index=True))
