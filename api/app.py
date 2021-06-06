from flask import Flask, request, Response, jsonify
from flask_restx import Resource, Api
import pymysql
import os
import datetime
import random

api_version = "V1"

db = pymysql.connect(
    user = "swaiapiv1",
    passwd = "swaiapiv1_password",
    host = "127.0.0.1",
    db = "swai01",
    charset = "utf8mb4"
)
cursor = db.cursor(pymysql.cursors.DictCursor)

app = Flask(__name__)
api = Api(app)

@api.route("/" + api_version + "/users?username=<str:username>&password=<str:password>&passwordconfirm=<str:password2")
class Users(Resource):
    def get(self, username, password):
        sql = "SELECT EXISTS (SELECT id FROM users WHERE username=\"" + username + "\")"
        cursor.execute(sql)
        result_data_exist = cursor.fetchall()[0][0]
        if result_data_exist == 0:
            return Response(status = 404)
        elif result_data_exist == 1:
            sql = "SELECT password FROM users WHERE username = \"" + username + "\""
            cursor.execute(sql)
            result_data_password = cursor.fetchall()[0][0]
            if result_data_password == password:
                sql = "SELECT id FROM users WHERE username = \"" + username + "\""
                cursor.execute(sql)
                result_data_id = cursor.fetchall()[0][0]
                return_data = {
                    "id" : result_data_id,
                    "username" : username
                }
                return jsonify(return_data), 200
            elif result_data_password != password:
                return Response(status = 404)
    def post(self, username, password, password2):
        
            

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 5000)