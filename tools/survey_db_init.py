'''To be run from top-level cesium_web directory, which is assumed to be in the
top-level survey classifier directory and alongside survey_classifier_data.'''

from cesium_app import models as m
from cesium_app.config import cfg
from cesium.data_management import parse_and_store_ts_data
from cesium.features import CADENCE_FEATS
import cesium

import shutil
import datetime
import glob
import os


def setup_survey_db():
    # Drop & create tables
    m.drop_tables()
    m.create_tables()

    # Add project
    proj = m.Project.add_by('Survey Classifier', '', 'testuser@gmail.com')
    assert proj.id == 1
    print('\nAdded project:\n', proj)

    # Add dataset
    dataset_name = 'Survey Light Curve Data'

    ts_paths = []
    for src in glob.glob(os.path.join(
            '..', 'survey_classifier_data/data/lightcurves/*.nc')):
        ts_paths.append(shutil.copy(src, cfg['paths']['ts_data_folder']))
    meta_features = list(cesium.time_series.from_netcdf(ts_paths[0])
                         .meta_features.keys())
    file_names = [os.path.basename(ts_path).split('.nc')[0] for ts_path in ts_paths]
    dataset = m.Dataset.add(name=dataset_name, project=proj, file_names=file_names,
                            file_uris=ts_paths, meta_features=meta_features)
    print('\nAdded dataset:\n', dataset)

    # Add featureset
    fset_path = shutil.copy(
        '../survey_classifier_data/data/survey_lc_features.nc',
        cfg['paths']['features_folder'])
    fset = m.Featureset.create(name='Survey LC Cadence/Error Features',
                               file=m.File.create(uri=fset_path),
                               project=proj,
                               features_list=CADENCE_FEATS,
                               custom_features_script=None)
    fset.task_id = None
    fset.finished = datetime.datetime.now()
    fset.save()
    print('\nAdded featureset:\n', fset)

    # Add model
    model_path = shutil.copy(
        '../survey_classifier_data/data/survey_classifier.pkl',
        cfg['paths']['models_folder'])
    model_file = m.File.create(uri=model_path)
    model = m.Model.create(name='Survey LCs RFC', file=model_file,
                           featureset=fset, project=proj,
                           params={}, type='RandomForestClassifier')
    model.task_id = None
    model.finished = datetime.datetime.now()
    model.save()
    print('\nAdded model:\n', model)


if __name__ == '__main__':
    setup_survey_db()
