from baselayer.app.handlers.base import BaseHandler
from baselayer.app.custom_exceptions import AccessError
from ..models import DBSession, Project
import tornado.web

import requests
import json


class ProjectHandler(BaseHandler):
    def get(self, project_id=None):
        if project_id is not None:
            proj_info = Project.get_if_owned_by(project_id, self.current_user)
        else:
            proj_info = self.current_user.projects

        return self.success(proj_info)

    def post(self):
        data = self.get_json()
        cesium_app_id = requests.post(
            '{}/project'.format(self.cfg['cesium_app:url']),
            data=json.dumps(data)).json()['data']['id']
        p = Project(name=data['projectName'],
                    description=data.get('projectDescription', ''),
                    cesium_app_id=cesium_app_id,
                    users=[self.current_user])
        DBSession().add(p)
        DBSession().commit()

        return self.success({"id": p.id}, 'survey_app/FETCH_PROJECTS')

    def put(self, project_id):
        data = self.get_json()
        p = Project.get_if_owned_by(project_id, self.current_user)

        p.name = data['projectName']
        p.description = data.get('projectDescription', '')
        DBSession().commit()

        return self.success(action='survey_app/FETCH_PROJECTS')

    def delete(self, project_id):
        p = Project.get_if_owned_by(project_id, self.current_user)

        # Make request to delete project in cesium_web
        r = requests.delete('{}/project/{}'.format(
            self.cfg['cesium_app:url'], p.cesium_app_id)).json()

        DBSession().delete(p)
        DBSession().commit()

        return self.success(action='survey_app/FETCH_PROJECTS')
