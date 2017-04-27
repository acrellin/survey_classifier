'''To be run from top-level cesium_web directory, which is assumed to be
alongside both survey_classifier and survey_classifier_data.'''

from cesium_app import model_util
from cesium_app import models
from cesium_app.app_server import load_config
from cesium.data_management import parse_and_store_ts_data
from cesium.features import CADENCE_FEATS, LOMB_SCARGLE_FEATS, GENERAL_FEATS
from cesium.time_series import load as load_ts
import cesium

import shutil
import datetime
import glob
import os


def setup_survey_db():
    cfg = load_config()

    # Drop & create tables
    models.db.init('cesium', user='cesium')
    model_util.drop_tables()
    model_util.create_tables()

    # Add testuser
    models.User.create(username='testuser@gmail.com', email='testuser@gmail.com')

    # Add project
    proj = models.Project.add_by('Survey Classifier', '', 'testuser@gmail.com')
    assert proj.id == 1
    print('\nAdded project:\n', proj)

    # Add datasets
    for dataset_name, ts_data_dir in [
            ['Survey Light Curve Data',
             os.path.join( '..', 'survey_classifier_data/data/lightcurves')],
            ['ASAS',
             os.path.join( '..', 'survey_classifier_data/data/ASAS_lcs')],
            ['Noisified to CoRoT',
             os.path.join( '..', 'survey_classifier_data/data/noisified_CoRoT_lcs')],
            ['Noisified to HATNet',
             os.path.join( '..', 'survey_classifier_data/data/noisified_HATNet_lcs')],
            ['Noisified to Hipparcos',
             os.path.join( '..', 'survey_classifier_data/data/noisified_Hipparcos_lcs')],
            ['Noisified to KELT',
             os.path.join( '..', 'survey_classifier_data/data/noisified_KELT_lcs')],
            ['Noisified to Kepler',
             os.path.join( '..', 'survey_classifier_data/data/noisified_Kepler_lcs')],
            ['Noisified to LINEAR',
             os.path.join( '..', 'survey_classifier_data/data/noisified_LINEAR_lcs')],
            ['Noisified to OGLE-III',
             os.path.join( '..', 'survey_classifier_data/data/noisified_OGLE-III_lcs')],
            ['Noisified to SuperWASP',
             os.path.join( '..', 'survey_classifier_data/data/noisified_SuperWASP_lcs')],
            ['Noisified to TrES',
             os.path.join( '..', 'survey_classifier_data/data/noisified_TrES_lcs')]]:

        ts_paths = []
        # As these are only ever accessed to determine meta features, only
        # copy first ten (arbitrary) TS
        for src in glob.glob(os.path.join(ts_data_dir, '*.npz'))[:10]:
            # Add the path to the copied file in cesium data directory
            ts_paths.append(shutil.copy(src, cfg['paths']['ts_data_folder']))
        meta_features = list(load_ts(ts_paths[0])
                             .meta_features.keys())
        file_names = [os.path.basename(ts_path).split('.npz')[0] for ts_path in ts_paths]
        dataset = models.Dataset.add(name=dataset_name, project=proj, file_names=file_names,
                                file_uris=ts_paths, meta_features=meta_features)
        print('\nAdded dataset:\n', dataset)

    # Add featuresets
    fset_dict = {}
    for fset_name, orig_fset_path, features_list in [
            ['Survey LC Cadence/Error Features',
             '../survey_classifier_data/data/survey_lc_features.npz',
             CADENCE_FEATS],
            ['ASAS',
             '../survey_classifier_data/data/ASAS_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS],
            ['CoRoT',
             '../survey_classifier_data/data/noisified_CoRoT_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS],
            ['HATNet',
             '../survey_classifier_data/data/noisified_HATNet_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS],
            ['Hipparcos',
             '../survey_classifier_data/data/noisified_Hipparcos_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS],
            ['KELT',
             '../survey_classifier_data/data/noisified_KELT_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS],
            ['Kepler',
             '../survey_classifier_data/data/noisified_Kepler_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS],
            ['LINEAR',
             '../survey_classifier_data/data/noisified_LINEAR_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS],
            ['OGLE-III',
             '../survey_classifier_data/data/noisified_OGLE-III_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS],
            ['SuperWASP',
             '../survey_classifier_data/data/noisified_SuperWASP_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS],
            ['TrES',
             '../survey_classifier_data/data/noisified_TrES_features.npz',
             LOMB_SCARGLE_FEATS + GENERAL_FEATS]]:
        fset_path = shutil.copy(orig_fset_path, cfg['paths']['features_folder'])
        fset = models.Featureset.create(name=fset_name,
                                   file=models.File.create(uri=fset_path),
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
             'RandomForestClassifier', {}, 'Survey LC Cadence/Error Features'],
            ['ASAS',
             os.path.join(
                 '..', 'survey_classifier_data/data/ASAS_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'ASAS'],
            ['CoRoT',
             os.path.join(
                 '..', 'survey_classifier_data/data/noisified_CoRoT_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'CoRoT'],
            ['HATNet',
             os.path.join(
                 '..', 'survey_classifier_data/data/noisified_HATNet_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'HATNet'],
            ['Hipparcos',
             os.path.join(
                 '..', 'survey_classifier_data/data/noisified_Hipparcos_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'Hipparcos'],
            ['KELT',
             os.path.join(
                 '..', 'survey_classifier_data/data/noisified_KELT_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'KELT'],
            ['Kepler',
             os.path.join(
                 '..', 'survey_classifier_data/data/noisified_Kepler_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'Kepler'],
            ['LINEAR',
             os.path.join(
                 '..', 'survey_classifier_data/data/noisified_LINEAR_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'LINEAR'],
            ['OGLE-III',
             os.path.join(
                 '..', 'survey_classifier_data/data/noisified_OGLE-III_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'OGLE-III'],
            ['SuperWASP',
             os.path.join(
                 '..', 'survey_classifier_data/data/noisified_SuperWASP_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'SuperWASP'],
            ['TrES',
             os.path.join(
                 '..', 'survey_classifier_data/data/noisified_TrES_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'TrES']]:
        model_path = shutil.copy(orig_model_path, cfg['paths']['models_folder'])
        model_file = models.File.create(uri=model_path)
        model = models.Model.create(name=model_name, file=model_file,
                               featureset=fset_dict[fset_name], project=proj,
                               params=params, type=model_type)
        model.task_id = None
        model.finished = datetime.datetime.now()
        model.save()
        print('\nAdded model:\n', model)


if __name__ == '__main__':
    setup_survey_db()
