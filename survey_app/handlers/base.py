from baselayer.app.handlers.base import BaseHandler as BLBaseHandler


class BaseHandler(BLBaseHandler):
    def get_cesium_auth_cookie(self):
        if not hasattr(self, 'cesium_auth_cookie'):
            with open(f'{self.cfg["paths:cesium_web_login_cookie_folder"]}/login.cookie') as f:
                self.cesium_auth_cookie = {'user_id': f.read().strip()}
        return self.cesium_auth_cookie
