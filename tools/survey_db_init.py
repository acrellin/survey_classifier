'''To be run from top-level cesium_web directory, which is assumed to alongside
both survey_classifier and survey_classifier_data.'''

from cesium_app import models as m
from cesium_app.config import cfg
from cesium.data_management import parse_and_store_ts_data
from cesium.features import CADENCE_FEATS, LOMB_SCARGLE_FEATS, GENERAL_FEATS
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

    # Add datasets
    for dataset_name, ts_data_dir in [
            ['Survey Light Curve Data',
             os.path.join( '..', 'survey_classifier_data/data/lightcurves')]]:

        ts_paths = []
        # As these are only ever accessed to determine meta features, only
        # copy first ten (arbitrary) TS
        for src in glob.glob(os.path.join(ts_data_dir, '*.nc'))[:10]:
            # Add the path to the copied file in cesium data directory
            ts_paths.append(shutil.copy(src, cfg['paths']['ts_data_folder']))
        meta_features = list(cesium.time_series.from_netcdf(ts_paths[0])
                             .meta_features.keys())
        file_names = [os.path.basename(ts_path).split('.nc')[0] for ts_path in ts_paths]
        dataset = m.Dataset.add(name=dataset_name, project=proj, file_names=file_names,
                                file_uris=ts_paths, meta_features=meta_features)
        print('\nAdded dataset:\n', dataset)

    # Add featuresets
    fset_dict = {}
    for fset_name, orig_fset_path, features_list in [
            ['Survey LC Cadence/Error Features',
             '../survey_classifier_data/data/survey_lc_features.nc',
             CADENCE_FEATS]]:
        fset_path = shutil.copy(orig_fset_path, cfg['paths']['features_folder'])
        fset = m.Featureset.create(name=fset_name,
                                   file=m.File.create(uri=fset_path),
                                   project=proj,
                                   features_list=features_list,
                                   custom_features_script=None)
        fset.task_id = None
        fset.finished = datetime.datetime.now()
        fset.save()
        fset_dict[fset_name] = fset
        print('\nAdded featureset:\n', fset)

    # Add models
    for model_name, orig_model_path, model_type, params, fset_name in [
            ['Survey LCs RFC',
             os.path.join('..', 'survey_classifier_data/data/survey_classifier.pkl'),
             'RandomForestClassifier', {}, 'Survey LC Cadence/Error Features']]:
        model_path = shutil.copy(orig_model_path, cfg['paths']['models_folder'])
        model_file = m.File.create(uri=model_path)
        model = m.Model.create(name=model_name, file=model_file,
                               featureset=fset_dict[fset_name], project=proj,
                               params=params, type=model_type)
        model.task_id = None
        model.finished = datetime.datetime.now()
        model.save()
        print('\nAdded model:\n', model)


if __name__ == '__main__':
    setup_survey_db()
