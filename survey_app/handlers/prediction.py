from .base import BaseHandler, AccessError
from ..models import Prediction, Dataset, Project
from ..config import cfg
from .. import util

import tornado.gen
from tornado.escape import json_decode

import cesium
from os.path import join as pjoin
import uuid
import datetime
import os
import tempfile
import requests
import traceback
import json


class SurveyPredictionHandler(BaseHandler):
    def _get_prediction(self, prediction_id):
        try:
            d = Prediction.get(Prediction.id == prediction_id)
        except Prediction.DoesNotExist:
            raise AccessError('No such dataset')

        if not d.is_owned_by(self.get_username()):
            raise AccessError('No such dataset')

        return d

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
            try:
                prediction = cesium.featureset.from_netcdf(
                    self._get_prediction(prediction_id).file_path)
            except OSError:
                return self.error('The requested file could not be found. '
                                  'The cesium_web app must be running on the '
                                  'same machine to download prediction results.')
            with tempfile.NamedTemporaryFile() as tf:
                util.prediction_to_csv(prediction, tf.name)
                with open(tf.name) as f:
                    self.set_header("Content-Type", 'text/csv; charset="utf-8"')
                    self.set_header("Content-Disposition",
                                    "attachment; filename=survey_app_prediction_results.csv")
                    self.write(f.read())
        else:
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


class SciencePredictionHandler(BaseHandler):
    def _get_prediction(self, prediction_id):
        try:
            d = Prediction.get(Prediction.id == prediction_id)
        except Prediction.DoesNotExist:
            raise AccessError('No such dataset')

        if not d.is_owned_by(self.get_username()):
            raise AccessError('No such dataset')

        return d

    @tornado.gen.coroutine
    def _await_science_predictions(self, prediction, science_model_ids_and_probs):
        try:
            while True:
                preds_info = [
                    requests.get('{}/predictions/{}'.format(
                        cfg['cesium_app']['url'],
                        cesium_app_prediction_id)).json()['data']
                    for cesium_app_prediction_id in
                    prediction.cesium_app_sci_pred_ids]
                if all([pred_info['finished'] for pred_info in preds_info]):
                    prediction.science_preds_task_id = None
                    prediction.science_preds_finished = datetime.datetime.now()
                    sci_pred_results = {pred_info['model']: pred_info['results']
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
            r = requests.post('{}/predictions'.format(cfg['cesium_app']['url']),
                              data=json.dumps(data)).json()
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

    def get(self, prediction_id=None, action=None):
        if action == 'download':
            try:
                prediction = cesium.featureset.from_netcdf(
                    self._get_prediction(prediction_id).file_path)
            except OSError:
                return self.error('The requested file could not be found. '
                                  'The cesium_web app must be running on the '
                                  'same machine to download prediction results.')
            with tempfile.NamedTemporaryFile() as tf:
                util.prediction_to_csv(prediction, tf.name)
                with open(tf.name) as f:
                    self.set_header("Content-Type", 'text/csv; charset="utf-8"')
                    self.set_header("Content-Disposition",
                                    "attachment; filename=survey_app_prediction_results.csv")
                    self.write(f.read())
        else:
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
