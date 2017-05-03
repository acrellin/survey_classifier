from .base import BaseHandler, AccessError
from ..models import Project, Dataset
from ..config import cfg

import os
from os.path import join as pjoin
import uuid
import tempfile
import requests
import cesium
from cesium.data_management import parse_and_store_ts_data


class DatasetHandler(BaseHandler):
    def _get_dataset(self, dataset_id):
        try:
            d = Dataset.get(Dataset.id == dataset_id)
        except Dataset.DoesNotExist:
            raise AccessError('No such dataset')

        if not d.is_owned_by(self.get_username()):
            raise AccessError('No such dataset')

        return d

    def post(self):
        if not 'tarFile' in self.request.files:
            return self.error('No tar file uploaded')

        tarfile = self.request.files['tarFile'][0]

        if tarfile.filename == '':
            return self.error('Empty tar file uploaded')

        dataset_name = self.get_argument('datasetName')
        project_id = self.get_argument('projectID')
        cesium_app_project_id = Project.get(Project.id == project_id).cesium_app_id

        # Header file is optional for unlabled data w/o metafeatures
        if 'headerFile' in self.request.files:
            headerfile = self.request.files['headerFile'][0]
        else:
            headerfile = None

        data = {'datasetName': dataset_name,
                'projectID': cesium_app_project_id}
        files = {}
        with tempfile.TemporaryDirectory() as temp_dir:
            for posted_file, key in [[f, k] for f, k in [[headerfile, 'headerFile'],
                                     [tarfile, 'tarFile']] if f is not None]:
                tmp_path = os.path.join(temp_dir, posted_file.filename)
                with open(tmp_path, 'wb') as fout:
                    fout.write(posted_file['body'])
                files[key] = open(tmp_path, 'rb')
                if key == 'tarFile':
                    tarfile_path = tmp_path
            # Post to cesium_web
            r = requests.post('{}/dataset'.format(cfg['cesium_app']['url']),
                              files=files, data=data).json()
            if r['status'] != 'success':
                return self.error(r['message'])

            ts_paths = parse_and_store_ts_data(tarfile_path, temp_dir,
                                               cleanup_archive=False)
            file_names = [os.path.basename(ts_path) for ts_path in ts_paths]

        p = Project.get(Project.id == project_id)
        d = Dataset.add(name=dataset_name, project=p, file_names=file_names,
                        meta_features=r['data']['meta_features'],
                        cesium_app_id=r['data']['id'],
                        cesium_app_project_id=r['data']['project'])

        return self.success(d, 'survey_app/FETCH_DATASETS')

    def get(self, dataset_id=None):
        if dataset_id is not None:
            dataset = self._get_dataset(dataset_id)
            dataset_info = dataset.display_info()
        else:
            datasets = [d for p in Project.all(self.get_username())
                            for d in p.datasets]
            dataset_info = [d.display_info() for d in datasets]

        return self.success(dataset_info)

    def delete(self, dataset_id):
        d = self._get_dataset(dataset_id)
        # Make request to delete dataset in cesium_web
        r = requests.delete('{}/dataset/{}'.format(
            cfg['cesium_app']['url'], d.cesium_app_id)).json()
        d.delete_instance()
        return self.success(action='survey_app/FETCH_DATASETS')
