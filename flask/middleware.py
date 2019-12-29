import traceback
from functions import Functions as func


class Middleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        print('get request')
        try:
            return self.app(environ, start_response)
        except Exception as e:
            # print(traceback.print_exc())
            func().set_log(traceback.format_exc())