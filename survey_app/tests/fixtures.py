'''Assortment of fixtures for use in test modules.'''

import uuid
import os
from os.path import join as pjoin
from contextlib import contextmanager
from survey_app import models as m
from cesium import predict
from cesium import data_management
from cesium.features import CADENCE_FEATS
from cesium.tests import fixtures as cesium_fixtures
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
def create_test_dataset(project):
    """Create and yield test labeled dataset, then delete.

    Params
    ------
    project : `models.Project` instance
        The project under which to create test dataset.

    """
    header = pjoin(os.path.dirname(__file__),
                   'data', 'asas_training_subset_classes.dat')
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
