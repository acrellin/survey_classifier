import datetime
import inspect
import os
import sys
import time
import json

import peewee as pw
from playhouse.postgres_ext import ArrayField, BinaryJSONField
from playhouse.shortcuts import model_to_dict
from playhouse import signals

from survey_app.json_util import to_json
from survey_app.config import cfg


db = pw.PostgresqlDatabase(autocommit=True, autorollback=True,
                           **cfg['database'])


class BaseModel(signals.Model):
    def __str__(self):
        return to_json(self.__dict__())

    def __dict__(self):
        return model_to_dict(self, recurse=False, backrefs=False)

    class Meta:
        database = db


class Project(BaseModel):
    """ORM model of the Project table"""
    name = pw.CharField()
    description = pw.CharField(null=True)
    created = pw.DateTimeField(default=datetime.datetime.now)
    cesium_app_id = pw.CharField(null=True)

    @staticmethod
    def all(username):
        return (Project
                .select()
                .join(UserProject)
                .where(UserProject.username == username)
                .order_by(Project.created))

    @staticmethod
    def add_by(name, description, cesium_app_id, username):
        with db.atomic():
            p = Project.create(name=name, description=description,
                               cesium_app_id=cesium_app_id)
            UserProject.create(username=username, project=p)
        return p

    def is_owned_by(self, username):
        users = [o.username for o in self.owners]
        return username in users


class UserProject(BaseModel):
    username = pw.CharField()
    project = pw.ForeignKeyField(Project, related_name='owners',
                                 on_delete='CASCADE')

    class Meta:
        indexes = (
            (('username', 'project'), True),
        )


class Dataset(BaseModel):
    """ORM model of the Dataset table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='datasets')
    name = pw.CharField()
    file_names = ArrayField(field_class=pw.CharField)
    meta_features = ArrayField(pw.CharField)
    created = pw.DateTimeField(default=datetime.datetime.now)
    cesium_app_id = pw.IntegerField()
    cesium_app_project_id = pw.IntegerField()

    @staticmethod
    def add(name, project, cesium_app_id, cesium_app_project_id, file_names=[],
            meta_features=[]):
        with db.atomic():
            d = Dataset.create(name=name, project=project,
                               cesium_app_id=cesium_app_id,
                               cesium_app_project_id=cesium_app_project_id,
                               file_names=file_names, meta_features=meta_features)
        return d

    def is_owned_by(self, username):
        return self.project.is_owned_by(username)

    def display_info(self):
        info = self.__dict__()
        return info


class Prediction(BaseModel):
    """ORM model of the Prediction table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='predictions')
    dataset = pw.ForeignKeyField(Dataset, on_delete='CASCADE')
    model_id = pw.CharField(null=True)
    created = pw.DateTimeField(default=datetime.datetime.now)
    task_id = pw.CharField(null=True)
    science_preds_task_id = pw.CharField(null=True)
    cesium_app_sci_pred_ids = ArrayField(pw.IntegerField, null=True)
    cesium_app_id = pw.CharField(null=True)
    cesium_app_project_id = pw.CharField(null=True)
    finished = pw.DateTimeField(null=True)
    science_preds_finished = pw.DateTimeField(null=True)
    model_type = pw.CharField(null=True)
    model_name = pw.CharField(null=True)
    results = pw.BlobField(null=True)
    science_results = pw.BlobField(null=True)
    isProbabilistic = pw.BooleanField(null=True)
    file_path = pw.CharField(null=True)
    dataset_name = pw.CharField(null=True)

    def is_owned_by(self, username):
        return self.project.is_owned_by(username)

    def display_info(self):
        info = self.__dict__()
        info['results'] = (json.loads(self.results.tobytes().decode())
                           if self.results else None)
        info['science_results'] = (json.loads(self.science_results.tobytes().decode())
                                   if self.science_results else None)
        return info


models = [
    obj for (name, obj) in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(obj) and issubclass(obj, pw.Model)
    and not obj == BaseModel
]


def create_tables(retry=5):
    for i in range(1, retry + 1):
        try:
            db.create_tables(models, safe=True)
            return
        except Exception as e:
            if (i == retry):
                raise e
            else:
                print('Could not connect to database...sleeping 5')
                time.sleep(5)

def drop_tables():
    db.drop_tables(models, safe=True, cascade=True)


if __name__ == "__main__":
    print("Dropping all tables...")
    drop_tables()
    print("Creating tables: {}".format([m.__name__ for m in models]))
    create_tables()
