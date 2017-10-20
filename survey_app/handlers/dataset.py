from .base import BaseHandler
from baselayer.app.custom_exceptions import AccessError
from ..models import Project, Dataset, DBSession

import os
from os.path import join as pjoin
import uuid
import tempfile
import requests
import tornado.web

import cesium
from cesium.data_management import parse_and_store_ts_data


class DatasetHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = self.get_json()
        if not 'tarFile' in data:
            return self.error('No tar file uploaded')

        zipfile = data['tarFile']
        tarball_content_type_str = 'data:application/gzip;base64,'

        if not zipfile['body'].startswith(tarball_content_type_str):
            return self.error('Invalid tar file - please ensure file is gzip '
                              'format.')

        if zipfile['name'] == '':
            return self.error('Empty tar file uploaded')

        dataset_name = data['datasetName']
        project_id = data['projectID']
        cesium_app_project_id = Project.get_if_owned_by(
            project_id, self.current_user).cesium_app_id

        # Header file is optional for unlabled data w/o metafeatures
        if 'headerFile' in data:
            headerfile = data['headerFile']
        else:
            headerfile = None

        json_data = {'datasetName': dataset_name,
                     'projectID': cesium_app_project_id,
                     'headerFile': headerfile,
                     'tarFile': zipfile,
                     'token': self.get_cesium_auth_token()}

        r = requests.post('{}/dataset'.format(self.cfg['cesium_app:url']),
                          json=json_data).json()
        if r['status'] != 'success':
            return self.error(r['message'])

        p = Project.query.filter(Project.id == project_id).one()
        d = Dataset(name=dataset_name, project=p, file_names=r['data']['files'],
                    project_id=p.id, meta_features=r['data']['meta_features'],
                    cesium_app_id=r['data']['id'],
                    cesium_app_project_id=r['data']['project_id'])
        DBSession().add(d)
        DBSession().commit()

        return self.success(d, 'survey_app/FETCH_DATASETS')

    @tornado.web.authenticated
    def get(self, dataset_id=None):
        if dataset_id is not None:
            dataset = Dataset.get_if_owned_by(dataset_id, self.current_user)
            dataset_info = dataset.to_dict()
        else:
            datasets = [d for p in self.current_user.projects
                        for d in p.datasets]
            dataset_info = [d.to_dict() for d in datasets]

        return self.success(dataset_info)

    @tornado.web.authenticated
    def delete(self, dataset_id):
        d = Dataset.get_if_owned_by(dataset_id, self.current_user)
        # Make request to delete dataset in cesium_web
        r = requests.delete(
            '{}/dataset/{}'.format(self.cfg['cesium_app:url'], d.cesium_app_id),
            json={'token': self.get_cesium_auth_token()}).json()
        DBSession().delete(d)
        DBSession().commit()
        return self.success(action='survey_app/FETCH_DATASETS')
