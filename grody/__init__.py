from flask import Flask, request
from flask_restful import reqparse, Resource, Api
from flask_cors import CORS
import types
import epics
import json

app = Flask(__name__)
api = Api(app)
CORS(app)

# utility to allow route decorator on flask_restful Resource
def api_route(self, *args, **kwargs):
    def wrapper(cls):
        self.add_resource(cls, *args, **kwargs)
        return cls
    return wrapper
api.route = types.MethodType(api_route, api)

parser = reqparse.RequestParser()
parser.add_argument('value')

@api.route("/pv/<name>")
class ChannelAccess(Resource):

    def get(self, name):
        pv = epics.PV(name, auto_monitor=False)
        pv.wait_for_connection()
        if pv.connected is False:
            return ("PV not found.", 404)
        pv.get()
        info = pv._args
        del info["chid"] # sometimes this is filled with a clong which is not serializable
        pv.disconnect()
        return (info, 200)

    def post(self, name):
        # print("Somebody is trying to PUT to name")
        try:
            # data = request.text
            data = request.get_json()
            epics.caput(name, data["value"])
            return (data, 200)
        except ValueError:
            return ("Value is not valid.", 404)
        return ("okay", 200)
        # try:
        #     epics.caput(name, value)
        # except Exception as e:
        #     return ("PV name not valid.", 404)
