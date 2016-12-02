from .base import BaseHandler, AccessError
from ..models import Project
from ..config import cfg

import requests
import json


class ProjectHandler(BaseHandler):
    def _get_project(self, project_id):
        try:
            p = Project.get(Project.id == project_id)
        except Project.DoesNotExist:
            raise AccessError('No such project')

        if not p.is_owned_by(self.get_username()):
            raise AccessError('No such project')

        return p

    def get(self, project_id=None):
        if project_id is not None:
            proj_info = self._get_project(project_id)
        else:
            proj_info = Project.all(self.get_username())

        return self.success(proj_info)

    def post(self):
        data = self.get_json()
        cesium_app_id = requests.post(
            '{}/project'.format(cfg['cesium_app']['url']),
            data=json.dumps(data)).json()['data']['id']
        p = Project.add_by(data['projectName'],
                           data.get('projectDescription', ''),
                           cesium_app_id,
                           self.get_username())

        return self.success({"id": p.id}, 'survey_app/FETCH_PROJECTS')

    def put(self, project_id):
        # This ensures that the user has access to the project they
        # want to modify
        p = self._get_project(project_id)

        data = self.get_json()
        query = Project.update(
            name=data['projectName'],
            description=data.get('projectDescription', ''),
            ).where(Project.id == project_id)
        query.execute()

        return self.success(action='survey_app/FETCH_PROJECTS')

    def delete(self, project_id):
        p = self._get_project(project_id)
        # Make request to delete project in cesium_web
        r = requests.delete('{}/project/{}'.format(
            cfg['cesium_app']['url'], p.cesium_app_id)).json()
        p.delete_instance()

        return self.success(action='survey_app/FETCH_PROJECTS')
