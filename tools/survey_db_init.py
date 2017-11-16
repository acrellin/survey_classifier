import baselayer
from baselayer.app.models import init_db
from baselayer.app.model_util import status, create_tables, drop_tables
from baselayer.app.env import load_env
from cesium_app import models
from cesium.data_management import parse_and_store_ts_data
from cesium.features import CADENCE_FEATS, LOMB_SCARGLE_FEATS, GENERAL_FEATS
from cesium.time_series import load as load_ts
import cesium

import shutil
import datetime
import glob
import os


def setup_survey_db():
    # if os.getcwd().endswith('survey_app'):
    #     os.chdir('./cesium_web')
    env, cfg = load_env()
    for data_dir in cfg['paths'].values():
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)


    db_session = init_db(**baselayer.app.config.load_config()['database'])
    # Drop & create tables
    with status('Dropping and re-creating tables'):
        drop_tables()
        create_tables()

    # Add testuser
    with status('Adding testuser'):
        u = models.User(username='testuser@cesium-ml.org')
        models.DBSession().add(u)
        models.DBSession().commit()

    # Add project
    with status('Adding project'):
        p = models.Project(name='Survey Classifier', users=[u])
        models.DBSession().add(p)
        models.DBSession().commit()

    # Add datasets
    with status('Adding datasets'):
        for dataset_name, ts_data_dir in [
                ['Survey Light Curve Data',
                 'survey_classifier_data/data/lightcurves'],
                ['ASAS',
                 'survey_classifier_data/data/ASAS_lcs'],
                ['Noisified to CoRoT',
                 'survey_classifier_data/data/noisified_CoRoT_lcs'],
                ['Noisified to HATNet',
                 'survey_classifier_data/data/noisified_HATNet_lcs'],
                ['Noisified to Hipparcos',
                 'survey_classifier_data/data/noisified_Hipparcos_lcs'],
                ['Noisified to KELT',
                 'survey_classifier_data/data/noisified_KELT_lcs'],
                ['Noisified to Kepler',
                 'survey_classifier_data/data/noisified_Kepler_lcs'],
                ['Noisified to LINEAR',
                 'survey_classifier_data/data/noisified_LINEAR_lcs'],
                ['Noisified to OGLE-III',
                 'survey_classifier_data/data/noisified_OGLE-III_lcs'],
                ['Noisified to SuperWASP',
                 'survey_classifier_data/data/noisified_SuperWASP_lcs'],
                ['Noisified to TrES',
                 'survey_classifier_data/data/noisified_TrES_lcs']]:

            ts_paths = []
            # As these are only ever accessed to determine meta features, only
            # copy first ten (arbitrary) TS
            for src in glob.glob(os.path.join(os.path.abspath(ts_data_dir),
                                              '*.npz'))[:10]:
                # Add the path to the copied file in cesium data directory
                ts_paths.append(os.path.abspath(shutil.copy(
                    os.path.abspath(src), cfg['paths']['ts_data_folder'])))
            try:
                meta_features = list(load_ts(ts_paths[0])
                                     .meta_features.keys())
            except IndexError: # No TS data on disk
                meta_features = None
            files = [models.DatasetFile(uri=ts_path) for ts_path in ts_paths]
            dataset = models.Dataset(name=dataset_name, project=p, files=files,
                                     meta_features=meta_features)
            models.DBSession().add_all(files + [dataset])
            models.DBSession().commit()
            print(f'Added dataset {dataset.id}')

    # Add featuresets
    fset_dict = {}
    for fset_name, orig_fset_path, features_list in [
            ['Survey LC Cadence/Error Features',
             './survey_classifier_data/data/survey_lc_features.npz',
             CADENCE_FEATS],
            ['ASAS',
             './survey_classifier_data/data/ASAS_features.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS],
            ['CoRoT',
             './survey_classifier_data/data/noisified_CoRoT_features_100.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS],
            ['HATNet',
             './survey_classifier_data/data/noisified_HATNet_features_100.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS],
            ['Hipparcos',
             './survey_classifier_data/data/noisified_Hipparcos_features_100.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS],
            ['KELT',
             './survey_classifier_data/data/noisified_KELT_features_100.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS],
            ['Kepler',
             './survey_classifier_data/data/noisified_Kepler_features_100.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS],
            ['LINEAR',
             './survey_classifier_data/data/noisified_LINEAR_features_100.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS],
            ['OGLE-III',
             './survey_classifier_data/data/noisified_OGLE-III_features_100.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS],
            ['SuperWASP',
             './survey_classifier_data/data/noisified_SuperWASP_features_100.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS],
            ['TrES',
             './survey_classifier_data/data/noisified_TrES_features_100.npz',
             GENERAL_FEATS + LOMB_SCARGLE_FEATS]]:
        fset_path = os.path.abspath(
            shutil.copy(os.path.abspath(orig_fset_path),
                        cfg['paths']['features_folder']))
        fset = models.Featureset(name=fset_name, file_uri=fset_path,
                                 project=p, features_list=features_list,
                                 task_id=None, finished=datetime.datetime.now())
        models.DBSession().add(fset)
        models.DBSession().commit()
        # fset.task_id = None
        # fset.finished = datetime.datetime.now()
        # fset.save()
        fset_dict[fset_name] = fset
        print(f'Added featureset {fset.id}')

    # Add models
    # TODO: Add actual model params
    for model_name, orig_model_path, model_type, params, fset_name in [
            ['Survey LCs RFC',
             os.path.abspath('./survey_classifier_data/data/survey_classifier.pkl'),
             'RandomForestClassifier', {}, 'Survey LC Cadence/Error Features'],
            ['ASAS',
             os.path.abspath('./survey_classifier_data/data/ASAS_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'ASAS'],
            ['CoRoT',
             os.path.abspath('./survey_classifier_data/data/noisified_CoRoT_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'CoRoT'],
            ['HATNet',
             os.path.abspath('./survey_classifier_data/data/noisified_HATNet_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'HATNet'],
            ['Hipparcos',
             os.path.abspath('./survey_classifier_data/data/noisified_Hipparcos_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'Hipparcos'],
            ['KELT',
             os.path.abspath('./survey_classifier_data/data/noisified_KELT_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'KELT'],
            ['Kepler',
             os.path.abspath('./survey_classifier_data/data/noisified_Kepler_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'Kepler'],
            ['LINEAR',
             os.path.abspath('./survey_classifier_data/data/noisified_LINEAR_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'LINEAR'],
            ['OGLE-III',
             os.path.abspath('./survey_classifier_data/data/noisified_OGLE-III_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'OGLE-III'],
            ['SuperWASP',
             os.path.abspath('./survey_classifier_data/data/noisified_SuperWASP_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'SuperWASP'],
            ['TrES',
             os.path.abspath('./survey_classifier_data/data/noisified_TrES_model_compressed.pkl'),
             'RandomForestClassifier', {}, 'TrES']]:
        model_path = os.path.abspath(
            shutil.copy(orig_model_path, cfg['paths']['models_folder']))
        model = models.Model(name=model_name, file_uri=model_path,
                             featureset_id=fset_dict[fset_name].id, project=p,
                             project_id=p.id,
                             params=params, type=model_type, task_id=None,
                             finished=datetime.datetime.now())
        models.DBSession().add(model)
        models.DBSession().commit()
        # model.task_id = None
        # model.finished = datetime.datetime.now()
        # model.save()
        print(f'Added model {model.id}')
    print(cfg)


if __name__ == '__main__':
    setup_survey_db()
