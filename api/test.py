from flask import Flask, request, Response, jsonify
from flask_restx import Resource, Api
import pymysql
import os
import datetime
import random

api_version = "V1"

app = Flask(__name__)
api = Api(app)

@api.route("/" + api_version + "/users?username=<str:username>&password=<str:password>&passwordconfirm=<str:password2")
class Usersclass(Resource):
    def get(self, username, password):
        un = "test"
        if un == username:
            return_data = {
                    "username" : username,
                    "password" : password
                    }
            return jsonify(return_data), 200
        else:
            return 404

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 5000)
