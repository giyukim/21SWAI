from re import I
from flask import Flask, request, Response, jsonify
from flask_restx import Resource, Api
import pymysql
import os
import datetime
import random
import hashlib

api_version = "V1"

db = pymysql.connect(
    user = "swaiapiv1",
    passwd = "swaiapiv1_password",
    host = "127.0.0.1",
    db = "swai01",
    charset = "utf8mb4"
)
cursor = db.cursor()

app = Flask(__name__)
api = Api(app)

@api.route("/" + api_version + "/users?username=<str:username>&password=<str:password>&passwordconfirm=<str:password2")
class Users(Resource):
    def get(self, username, password):
        if username != "" and password != "":
            sql = "SELECT EXISTS (SELECT id FROM users WHERE username=\"" + username + "\")"
            cursor.execute(sql)
            result_data_exist = cursor.fetchall()[0][0]
            if result_data_exist == 0:
                return_json = {
                    "msg": "User not exists"
                }
                return Response(status = 404)
            elif result_data_exist == 1:
                sql = "SELECT password FROM users WHERE username = \"" + username + "\""
                cursor.execute(sql)
                result_data_password = cursor.fetchall()[0][0]
                if result_data_password == password:
                    sql = "SELECT id FROM users WHERE username = \"" + username + "\""
                    cursor.execute(sql)
                    result_data_id = cursor.fetchall()[0][0]
                    sql = "SELECT token FROM users WHERE id = \"" + result_data_id + "\""
                    cursor.execute(sql)
                    result_data_usertoken = cursor.fetchall()[0][0]
                    return_json = {
                        "id" : result_data_id,
                        "username" : username,
                        "token" : result_data_usertoken
                    }
                    return Response(response = jsonify(return_json), status = 200)
                elif result_data_password != password:
                    return_json = {
                        "msg": "Password incorrect"
                    }
                    return Response(status = 404)
        else:
            return_json = {
                "msg": "parameter(s) have(has) NULL data"
            }
            return Response(response = jsonify(return_json), status = 400)


    def post(self, username, password, password2):
        if username != "" and password != "" and password2 != "":
            if password != password2:
                return_json = {
                    "msg": "password and password confirm is not coincident"
                }
                return Response(repsonse = jsonify(return_json), status = 400)
            sql = "SELECT EXISTS (SELECT id FROM users WHERE username = \"" + username + "\")"
            cursor.execute(sql)
            result_data_userexist = cursor.fetchall()[0][0]
            if result_data_userexist == 1:
                return_json = {
                    "msg": "User already exists"
                }
                return Response(response = jsonify(return_json), status = 404)
            else:
                usertoken = (hashlib.sha256((str(username) + str(password)).encode())).hexdigest()
                sql = "INSERT INTO users(username, token, password) VALUES(\"" + str(username) + "\", \"" + str(usertoken) + "\", \"" + str(password) + "\")"
                cursor.execute(sql)
                db.commit()
                return Response(status = 201)
        else:
            return_json = {
                "msg": "parameter(s) have(has) NULL data"
            }
            return Response(response = jsonify(return_json), status = 400)

@api.route("/" + api_version + "/users/<int:userid>?token=<str:usertoken>&username=<str:username>&password=<str:password>&passwordtoken=<str:password2>")
class Userssim(Resource):
    def get(self, userid, usertoken):
        if userid != "" and usertoken != "":
            sql = "SELECT EXISTS (SELECT token FROM users WHERE id = \"" + int(userid) + "\")"
            cursor.execute(sql)
            result_data_userexist = cursor.fetchall()[0][0]
            if result_data_userexist == 1:
                sql = "SELECT token FROM users WHERE id = \"" + int(userid) + "\")"
                cursor.execute(sql)
                result_data_usertoken = cursor.fetchall()[0][0]
                if result_data_usertoken == usertoken:
                    sql = "SELECT username FROM users WHERE id = \"" + userid + "\""
                    cursor.execute(sql)
                    result_data_username = cursor.fetchall()[0][0]
                    sql = "SELECT token FROM users WHERE id = \"" + userid + "\""
                    cursor.execute(sql)
                    result_data_token = cursor.fetchall()[0][0]
                    sql = "SELECT stocklist FROM users WHERE id = \"" + userid + "\""
                    cursor.execute(sql)
                    result_data_stocklist = list(cursor.fetchall()[0][0].split("|"))
                    
                    return_json = {
                        "id": int(userid),
                        "username": str(result_data_username),
                        "token": str(result_data_token),
                        "stocklist": result_data_stocklist
                    }
                    return Response(response = jsonify(return_json), status = 200)
                else:
                    return_json = {
                        "msg": "User token incorrect with userid"
                    }
                    return Response(response = jsonify(return_json), status = 400)
            else:
                return_json = {
                    "msg": "User not exists"
                }
                return Response(response = jsonify(return_json), status = 404)
        else:
            return_json = {
                "msg": "parameter(s) have(has) NULL data"
            }
            return Response(response = jsonify(return_json), status = 400)

    def put(self, userid, usertoken, username, password, password2):
        if userid != "" and usertoken != "" and username != "" and password != "" and password2 != "":
            sql = "SELECT EXISTS (SELECT username FROM users WHERE id = \"" + int(userid) + "\")"
            cursor.execute(sql)
            result_data_userexist = cursor.fetchall()[0][0]
            if result_data_userexist == 1:
                sql = "SELECT token FROM users WHERE id = \"" + userid + "\""
                cursor.execute(sql)
                result_data_dbusertoken = cursor.fetchall()[0][0]
                if usertoken == result_data_dbusertoken:
                    new_usertoken = (hashlib.sha256((str(username) + str(password)).encode())).hexdigest()
                    sql = "UPDATE users SET username = \"" + username + "\", token = \"" + new_usertoken + "\", password = \"" + password + " WHERE id = \"" + userid + "\""
                    cursor.execute(sql)
                    db.commit()
                    return Response(status = 204)
                else:
                    return_json = {
                        "msg": "Token error"
                    }
                    return Response(response = jsonify(return_json), status = 400)
            else:
                return Response(status = 404)
        else:
            return_json = {
                "msg": "parameter(s) have(has) NULL data"
            }
            return Response(response = jsonify(return_json), status = 400)
        
    def patch(self, userid, usertoken, username, password, password2):
        if userid != "" and usertoken != "":
            sql = "SELECT EXISTS (SELECT username FROM users WHERE id = \"" + int(userid) + "\")"
            cursor.execute(sql)
            result_data_userexist = cursor.fetchall()[0][0]
            if result_data_userexist == 1:
                sql = "SELECT token FROM users WHERE id = \"" + userid + "\""
                cursor.execute(sql)
                result_data_dbusertoken = cursor.fetchall()[0][0]
                if usertoken == result_data_dbusertoken:
                    if password != "" and password != "":
                        if password == password2:
                            new_usertoken = (hashlib.sha256((str(username) + str(password)).encode())).hexdigest()
                            sql = "UPDATE users SET password = \"" + password + "\", token = \"" + new_usertoken + "\" WHERE id = \"" + userid + "\""
                            cursor.execute(sql)
                            db.commit()
                        else:
                            return_json = {
                                "msg": "password and password confirm incorrect"
                            }
                            return Response(response = return_json, status = 400)
                    elif password != "" and password2 == "":
                        return_json = {
                                "msg": "password parameter is blank"
                        }
                        return Response(response = return_json, status = 400)
                    elif password == "" and password2 != "":
                        return_json = {
                                "msg": "password confirm parameter is blank"
                        }
                        return Response(response = return_json, status = 400)
                    if username != "":
                        new_usertoken = (hashlib.sha256((str(username) + str(password)).encode())).hexdigest()
                        sql = "UPDATE users SET username = \"" + username + "\", token = \"" + new_usertoken + "\" WHERE id = \"" + userid + "\""
                        cursor.execute(sql)
                        db.commit()
                    return Response(status = 204)
                else:
                    return_json = {
                        "msg": "Token error"
                    }
                    return Response(response = jsonify(return_json), status = 400)
            else:
                return Response(status = 404)
        else:
            return_json = {
                "msg": "parameter(s) have(has) NULL data"
            }
            return Response(response = jsonify(return_json), status = 400)

    def delete(self, userid, usertoken): 
        if userid != "" and usertoken != "":
            
        else:
            
    


if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 5000) 