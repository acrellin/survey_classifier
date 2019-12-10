import datetime
import inspect
import os
import sys
import time
import json
import pandas as pd

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from baselayer.app.models import (init_db, join_model, Base, DBSession, User)


def is_owned_by(self, user):
    if hasattr(self, 'users'):
        return (user in self.users)
    elif hasattr(self, 'project'):
        return (user in self.project.users)
    else:
        raise NotImplementedError(f"{type(self).__name__} object has no owner")
Base.is_owned_by = is_owned_by


class Project(Base):
    name = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.String())
    created = sa.Column(sa.DateTime(), default=datetime.datetime.now)
    cesium_app_id = sa.Column(sa.String())
    users = relationship('User', secondary='user_projects',
                         back_populates='projects')
    datasets = relationship('Dataset', back_populates='project',
                            cascade='all')
    predictions = relationship('Prediction', back_populates='project',
                               cascade='all')


user_projects = join_model('user_projects', User, Project)
User.projects = relationship('Project', secondary='user_projects',
                             back_populates='users', cascade='all')


class Dataset(Base):
    name = sa.Column(sa.String(), nullable=False)
    project_id = sa.Column(sa.ForeignKey('projects.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    project = relationship('Project', back_populates='datasets')
    file_names = sa.Column(sa.ARRAY(sa.VARCHAR()), nullable=False, index=True)
    meta_features = sa.Column(sa.ARRAY(sa.VARCHAR()), nullable=False, index=True)
    created = sa.Column(sa.DateTime(), default=datetime.datetime.now)
    cesium_app_id = sa.Column(sa.String())
    cesium_app_project_id = sa.Column(sa.String())


class Prediction(Base):
    """ORM model of the Prediction table"""
    project = relationship('Project', back_populates='predictions')
    project_id = sa.Column(sa.ForeignKey('projects.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    dataset_id = sa.Column(sa.ForeignKey('datasets.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    dataset = relationship('Dataset')
    model_id = sa.Column(sa.String())
    created = sa.Column(sa.DateTime(), default=datetime.datetime.now)
    task_id = sa.Column(sa.String())
    science_preds_task_id = sa.Column(sa.String())
    cesium_app_sci_pred_ids = sa.Column(sa.ARRAY(sa.VARCHAR()), index=True)
    cesium_app_id = sa.Column(sa.String())
    cesium_app_project_id = sa.Column(sa.String())
    finished = sa.Column(sa.DateTime())
    science_preds_finished = sa.Column(sa.DateTime())
    model_type = sa.Column(sa.String())
    model_name = sa.Column(sa.String())
    results = sa.Column(sa.LargeBinary())
    science_results = sa.Column(sa.LargeBinary())
    isProbabilistic = sa.Column(sa.Boolean())
    file_path = sa.Column(sa.String(), nullable=True, index=True)
    dataset_name = sa.Column(sa.String(), nullable=False)

    def display_info(self):
        info = self.to_dict()
        info['results'] = (json.loads(self.results.decode())
                           if self.results else None)
        info['science_results'] = (json.loads(self.science_results.decode())
                                   if self.science_results else None)
        return info
