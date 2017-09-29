from baselayer.app.custom_exceptions import AccessError
from .general_prediction import GeneralPredictionHandler
from ..models import Prediction, Project, DBSession
from .. import util

import tornado.gen

import cesium
import uuid
import datetime
import tempfile
import requests
import traceback
import json


class SciencePredictionHandler(GeneralPredictionHandler):
    """Handler for performing science predictions."""
    @tornado.gen.coroutine
    def _await_science_predictions(self, prediction, science_model_ids_and_probs):
        try:
            while True:
                preds_info = [
                    requests.get(
                        '{}/predictions/{}'.format(self.cfg['cesium_app:url'],
                                                   cesium_app_prediction_id),
                        cookies=self.get_cesium_auth_cookie()).json()['data']
                    for cesium_app_prediction_id in
                    prediction.cesium_app_sci_pred_ids]
                if all([pred_info['finished'] for pred_info in preds_info]):
                    prediction.science_preds_task_id = None
                    prediction.science_preds_finished = datetime.datetime.now()
                    sci_pred_results = {pred_info['model_id']: pred_info['results']
                                        for pred_info in preds_info}
                    prediction.science_results = json.dumps(
                        util.aggregate_pred_results_by_ts(
                            sci_pred_results, science_model_ids_and_probs))
                    prediction.save()
                    break
                else:
                    yield tornado.gen.sleep(1)

            self.action('survey_app/SHOW_NOTIFICATION',
                        payload={"note": "Science prediction completed."})

        except Exception as e:
            traceback.print_exc()
            prediction.delete_instance()
            self.action('survey_app/SHOW_NOTIFICATION',
                        payload={
                            "note": "Prediction failed "
                            "with error {}. Please try again.".format(e),
                            "type": "error"})

        self.action('survey_app/FETCH_PREDICTIONS')

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        username = self.get_username()
        data = self.get_json()

        prediction_id = data['prediction_id']
        prediction = Prediction.get(Prediction.id == prediction_id)
        dataset = prediction.dataset
        dataset_id = dataset.id
        cesium_dataset_id = dataset.cesium_app_id

        science_model_ids_and_probs = util.determine_model_ids(
            prediction.display_info()['results'])

        cesium_app_pred_ids = []
        for model_id in set([mdl_id for ts_name in science_model_ids_and_probs
                             for mdl_id in
                             science_model_ids_and_probs[ts_name]]):
            data = {'datasetID': cesium_dataset_id,
                    'modelID': model_id,
                    'ts_names': [ts_name for ts_name in science_model_ids_and_probs
                                 if model_id in science_model_ids_and_probs[ts_name]]}
            # POST prediction to cesium_web
            r = requests.post('{}/predictions'.format(self.cfg['cesium_app:url']),
                              data=json.dumps(data),
                              cookies=self.get_cesium_auth_cookie()).json()
            if r['status'] != 'success':
                return self.error('An error occurred while processing the request'
                                  'to cesium_web: {}'.format(r['message']))
            cesium_app_pred_ids.append(r['data']['id'])

        prediction.science_preds_task_id = str(uuid.uuid4())
        prediction.cesium_app_sci_pred_ids = cesium_app_pred_ids
        prediction.save()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_science_predictions, prediction,
                            science_model_ids_and_probs)

        return self.success(prediction.display_info(),
                            'survey_app/FETCH_PREDICTIONS')

    @tornado.web.authenticated
    def get(self, prediction_id=None, action=None):
        if action == 'download':
            try:
                pred = self._get_prediction(prediction_id).display_info()
            except OSError:
                return self.error('The requested file could not be found. '
                                  'The cesium_web app must be running on the '
                                  'same machine to download prediction results.')
            if ('label' in pred['results'][list(pred['results'].keys())[0]] and
                pred['results'][list(pred['results'].keys())[0]]['label'] is not None):
                for ts_name in pred['results'].keys():
                    pred['science_results'][ts_name]['label'] = (
                        pred['results'][ts_name]['label'])
            with tempfile.NamedTemporaryFile() as tf:
                util.pred_results_to_csv(pred['science_results'], tf.name)
                with open(tf.name) as f:
                    self.set_header("Content-Type", 'text/csv; charset="utf-8"')
                    self.set_header("Content-Disposition",
                                    "attachment; filename=survey_app_prediction_results.csv")
                    self.write(f.read())
