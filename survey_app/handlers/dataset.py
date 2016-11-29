from .base import BaseHandler, AccessError
from ..models import Project, Dataset
from ..config import cfg

import os
from os.path import join as pjoin
import uuid
import tempfile
import requests


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

        zipfile = self.request.files['tarFile'][0]

        if zipfile.filename == '':
            return self.error('Empty tar file uploaded')

        dataset_name = self.get_argument('datasetName')
        project_id = self.get_argument('projectID')

        # Header file is optional for unlabled data w/o metafeatures
        if 'headerFile' in self.request.files:
            headerfile = self.request.files['headerFile'][0]
            print(self.request.files['headerFile'])
        else:
            headerfile = None

        with tempfile.TemporaryDirectory() as temp_dir:
            for f in [x for x in (headerfile, zipfile) if x is not None]:
                with open(os.path.join(temp_dir, f.filename), 'wb') as fout:
                    fout.write(f['body'])
                    print(os.path.join(temp_dir, f.filename))

        p = Project.get(Project.id == project_id)
        # TODO this should give unique names to the time series files
        ts_paths = parse_ts_data(
            zipfile_path,
            cfg['paths']['ts_data_folder'],
            headerfile_path)
        meta_features = list(time_series.from_netcdf(ts_paths[0])
                             .meta_features.keys())
        unique_ts_paths = [os.path.join(os.path.dirname(ts_path),
                                        str(uuid.uuid4()) + "_" +
                                        util.secure_filename(ts_path))
                           for ts_path in ts_paths]
        for old_path, new_path in zip(ts_paths, unique_ts_paths):
            os.rename(old_path, new_path)
        file_names = [os.path.basename(ts_path) for ts_path in ts_paths]
        d = Dataset.add(name=dataset_name, project=p, file_names=file_names)

        return self.success(d, 'cesium/FETCH_DATASETS')

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
        d.delete_instance()
        return self.success(action='cesium/FETCH_DATASETS')
