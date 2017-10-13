from baselayer.app.handlers.base import BaseHandler as BLBaseHandler


class BaseHandler(BLBaseHandler):
    def get_cesium_auth_cookie(self):
        if not hasattr(self, 'cesium_auth_cookie'):
            with open(os.path.join(self.cfg['paths:cesium_web_login_cookie_folder'],
                                   '/cesium_web_token')) as f:
                self.cesium_auth_cookie = {'token': f.read().strip()}
        return self.cesium_auth_cookie
