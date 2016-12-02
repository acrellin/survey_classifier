'''Assortment of fixtures for use in test modules.'''

import uuid
import os
from os.path import join as pjoin
from contextlib import contextmanager
from survey_app import models as m
from cesium import predict
from cesium import data_management
from survey_app.config import cfg
import shutil
import peewee
import datetime
import joblib


@contextmanager
def create_test_project():
    """Create and yield test project, then delete."""
    p = m.Project.add_by('test_proj', 'test_desc', 2, 'testuser1@gmail.com')
    p.save()
    try:
        yield p
    finally:
        p.delete_instance()


@contextmanager
def create_test_dataset(project, label_type='class'):
    """Create and yield test labeled dataset, then delete.

    Params
    ------
    project : `models.Project` instance
        The project under which to create test dataset.
    label_type  : str
        String indicating whether data labels are class names ('class')
        for classification, or numerical values for regression (anything other
        than 'class'). Defaults to 'class'.

    """
    if label_type == 'class':
        header = pjoin(os.path.dirname(__file__),
                       'data', 'asas_training_subset_classes.dat')
    elif label_type == 'regr':
        header = pjoin(os.path.dirname(__file__),
                       'data', 'asas_training_subset_targets.dat')
    tarball = pjoin(os.path.dirname(__file__),
                    'data', 'asas_training_subset.tar.gz')
    header = shutil.copy2(header, cfg['paths']['upload_folder'])
    tarball = shutil.copy2(tarball, cfg['paths']['upload_folder'])
    d = m.Dataset.add('test_ds', project, 3, 3, file_names=[])
    d.save()
    try:
        yield d
    finally:
        d.delete_instance()


@contextmanager
def create_test_prediction(dataset, model):
    """Create and yield test prediction, then delete.

    Params
    ------
    dataset : `models.Dataset` instance
        The dataset on which prediction will be performed.
    model  : `models.Model` instance
        The model to use to create prediction.

    """
    with featureset.from_netcdf(model.featureset.file.uri, engine=cfg['xr_engine']) as fset_data:
        model_data = joblib.load(model.file.uri)
        pred_data = predict.model_predictions(fset_data.load(), model_data)
    pred_path = pjoin(cfg['paths']['predictions_folder'],
                      '{}.nc'.format(str(uuid.uuid4())))
    pred_data.to_netcdf(pred_path, engine=cfg['xr_engine'])
    f, created = m.File.create_or_get(uri=pred_path)
    pred = m.Prediction.create(file=f, dataset=dataset, project=dataset.project,
                               model=model, finished=datetime.datetime.now())
    pred.save()
    try:
        yield pred
    finally:
        pred.delete_instance()
