from flask import Flask, Response, jsonify
from flask_restx import Resource, Api
import pymysql
import os
import datetime
import random
import hashlib

from werkzeug.datastructures import ResponseCacheControl

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
            sql = "SELECT EXISTS (SELECT id FROM users WHERE username=\"" + str(username) + "\")"
            cursor.execute(sql)
            result_data_exist = cursor.fetchall()[0][0]
            if int(result_data_exist) == 0:
                return_json = {
                    "msg": "User not exists"
                }
                return Response(status = 404)
            else:
                sql = "SELECT password FROM users WHERE username = \"" + str(username) + "\""
                cursor.execute(sql)
                result_data_password = cursor.fetchall()[0][0]
                if result_data_password == password:
                    sql = "SELECT id FROM users WHERE username = \"" + str(username) + "\""
                    cursor.execute(sql)
                    result_data_id = cursor.fetchall()[0][0]
                    return_json = {
                        "id" : result_data_id,
                        "username" : username
                    }
                    return Response(response = jsonify(return_json), status = 200)
                elif result_data_password != password:
                    return_json = {
                        "msg": "Password incorrect"
                    }
                    return Response(status = 404)
        else:
            return_json = {
                "msg": "Parameter Error"
            }
            return Response(response = jsonify(return_json), status = 400)


    def post(self, username, password, password2):
        if username != "" and password != "" and password2 != "":
            if password != password2:
                return_json = {
                    "msg": "password and password confirm is not coincident"
                }
                return Response(repsonse = jsonify(return_json), status = 400)
            sql = "SELECT EXISTS (SELECT id FROM users WHERE username = \"" + str(username) + "\")"
            cursor.execute(sql)
            result_data_userexist = cursor.fetchall()[0][0]
            if result_data_userexist == 1:
                return_json = {
                    "msg": "User already exists"
                }
                return Response(response = jsonify(return_json), status = 404)
            else:
                sql = "INSERT INTO users(username, password) VALUES(\"" + str(username) + "\", \"" + str(password) + "\")"
                cursor.execute(sql)
                db.commit()
                return Response(status = 201)
        else:
            return_json = {
                "msg": "Parameter Error"
            }
            return Response(response = jsonify(return_json), status = 400)

@api.route("/" + api_version + "/users/<int:userid>?username=<str:username>&password=<str:password>&passwordconfirm=<str:password2>")
class Usersid(Resource):
    def get(self, userid):
        sql = "SELECT EXISTS (SELECT username FROM users WHERE id = " + str(userid) + ")"
        cursor.execute(sql)
        result_data_userexist = cursor.fetchall()[0][0]
        if result_data_userexist == 1:
            sql = "SELECT username FROM users WHERE id = " + str(userid)
            cursor.execute(sql)
            result_data_username = cursor.fetchall()[0][0]
            sql = "SELECT stocklist FROM users WHERE id = " + str(userid)
            cursor.execute(sql)
            result_data_stocklist = list(cursor.fetchall()[0][0].split("|"))
            stock_data = []
            for stockcode in result_data_stocklist:
                stock_data.append(str(stockcode))
            return_json = {
                "id": int(userid),
                "username": str(result_data_username),
                "stocklist": stock_data
            }
            return Response(response = jsonify(return_json), status = 200)
        else:
            return_json = {
                "msg": "User not exists"
            }
            return Response(response = jsonify(return_json), status = 404)

    def put(self, userid, username, password, password2):
        if username != "" and password != "" and password2 != "":
            sql = "SELECT EXISTS (SELECT username FROM users WHERE id = " + str(userid) + ")"
            cursor.execute(sql)
            result_data_userexist = cursor.fetchall()[0][0]
            if result_data_userexist == 1:
                sql = "UPDATE users SET username = \"" + str(username) + "\", password = \"" + str(password) + " WHERE id = " + str(userid)
                cursor.execute(sql)
                db.commit()
                return Response(status = 204)
            else:
                return Response(status = 404)
        else:
            return_json = {
                "msg": "Parameter Error"
            }
            return Response(response = jsonify(return_json), status = 400)
        
    def patch(self, userid, username, password, password2):
        sql = "SELECT EXISTS (SELECT username FROM users WHERE id = " + str(userid) + ")"
        cursor.execute(sql)
        result_data_userexist = cursor.fetchall()[0][0]
        if result_data_userexist == 1:
            if password != "" and password2 != "":
                if password == password2:
                    sql = "UPDATE users SET password = \"" + str(password) + "\" WHERE id = " + str(userid)
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
                sql = "UPDATE users SET username = \"" + str(username) + "\" WHERE id = " + str(userid)
                cursor.execute(sql)
                db.commit()
            return Response(status = 204)
        else:
            return Response(status = 404)

    def delete(self, userid): 
        sql = "SELECT EXISTS (SELECT username FROM users WHERE id = " + str(userid) + ")"
        cursor.execute(sql)
        result_data_userexist = cursor.fetchall()[0][0]
        if result_data_userexist == 1:
            sql = "DELETE FROM users WHERE id = " + str(userid)
            cursor.execute(sql)
            db.commit()
            return Response(status = 204)
        else:
            return Response(status = 404)

@api.route("/" + api_version + "/users/<int:userid>/stocks")
class Usersstocks(Resource):
    def get(self, userid):
        sql = "SELECT EXISTS (SELECT username FROM users WHERE id = " + str(userid) + ")"
        cursor.execute(sql)
        result_data_userexist = cursor.fetchall()[0][0]
        if int(result_data_userexist) == 1:
            sql = "SELECT stocklist FROM users WHERE id = " + int(userid) + ")"
            cursor.execute(sql)
            return_data_stocklist = str(cursor.fetchall()[0][0]).split("[|]")
            return_json = {
                "stocklist": return_data_stocklist
            }
            return Response(response = jsonify(return_json), status = 200)
        else:
            return Response(status = 404)

    def delete(self, userid):
        sql = "SELECT EXISTS (SELECT username FROM users WHERE id = " + str(userid) + ")"
        cursor.execute(sql)
        result_data_userexist = cursor.fetchall()[0][0]
        if int(result_data_userexist) == 1:
            sql = "UPDATE users SET stocklist = NULL WHERE id = " + str(userid)
            cursor.execute(sql)
            db.commit()
        else:
            return Response(status = 404)

@api.route("/" + api_version +  "/users/<int:userid>/stocks/<str:stockcode>")
class Usersuseridstocksstockcode(Resource):
    def patch(self, userid, stockcode):
        if stockcode != "":
            sql = "SELECT EXISTS (SELECT username FROM users WHERE id = " + str(userid) + ")"
            cursor.execute(sql)
            result_data_userexist = cursor.fetchall()[0][0]
            if result_data_userexist == 1:
                sql = "SELECT stocklist FROM users WHERE id = " + str(userid) + ")"
                cursor.execute(sql)
                result_data_stocklist = str(cursor.fetchall()[0][0])
                stocklist_listed = result_data_stocklist.split("[|]")
                if str(stockcode) in stocklist_listed:
                    return_json = {
                        "msg": "Stock code exist"
                    }
                    return Response(response = jsonify(return_json), status = 400)
                else:
                    result_data_stocklist = result_data_stocklist + "[|]" + str(stockcode)
                    sql = "UPDATE uers SET stocklist = \"" + result_data_stocklist + "\" WHERE id = " + str(userid)
                    cursor.execute(sql)
                    db.commit()
                    return Response(status = 204)
            else:
                return Response(status = 404)
        else:
            return_json = {
                "msg": "Parameter Error"
            }
            return Response(response = jsonify(return_json), status = 400)

    def delete(self, userid, stockcode):
        if stockcode != "":
            sql = "SELECT EXISTS (SELECT username FROM users WHERE id = " + str(userid) + ")"
            cursor.execute(sql)
            result_data_userexist = cursor.fetchall()[0][0]
            if result_data_userexist == 1:
                sql = "SELECT stocklist FROM users WHERE id = " + str(userid) + ")"
                cursor.execute(sql)
                result_data_stocklist = str(cursor.fetchall()[0][0])
                stocklist_listed = result_data_stocklist.split("[|]")
                if str(stockcode) in stocklist_listed:
                    stocklist_deleted = result_data_stocklist.replace("[|]" + str(stockcode) + "[|]", "[|]")
                    sql = "UPDATE uers SET stocklist = \"" + str(stocklist_deleted) + "\" WHERE id = " + str(userid)
                    return Response(status = 204)
                else:
                    return Response(status = 404)
            else:
                return Response(status = 404)
        else:
            return_json = {
                "msg": "Parameter Error"
            }
            return Response(response = jsonify(return_json), status = 400)

@api.route("/" + api_version + "/stocks")
class Stocks(Resource): 
    def get(self):
        sql = "SELECT stockcode FROM stock_data"
        cursor.execute(sql)
        result_data_stockcodelist = cursor.fetchall()
        # stockcodelist
        # if no stockcode in table
        # return 204
        return_json = {

        }
        return Response(response = jsonify(return_json), status = 200)

@api.route("/" + api_version + "/stocks/<str:stockcode>?ml=<int:d_ml>&nlp=<int:d_nlp>&ma520=<float:d_ma520>&ma2060=<float:d_ma2060>&macd12269=<float:d_macd12269>&stcstc93=<float:d_stcstc93>&rsi14=<float:d_rsi14>&bb202=<float:d_bb202>&evlp2065=<float:d_evlp2065>&cci14=<float:d_cci14>&dmi14=<float:d_dmi14>&obv14=<float:d_obv14>&opinion=<int:d_opinion>")
class Stockstockcode(Resource):
    def get(self, stockcode):
        sql = "SELECT * FROM stock_data WHERE stockcode = \"" + str(stockcode) + "\""
        cursor.execute(sql)
        result_data_stockdata = cursor.fetchall()
        # stock data anayze
        # if no opinion in table
        # return 204
        return_json = {

        }
        return Response(resonpse = jsonify(return_json), status = 200)

    def post(self, stockcode):
        sql = "SELECT EXISTS (SELECT id FROM stock_data WHERE stockcode = \"" + str(stockcode) + "\")"
        cursor.execute(sql)
        result_data_stockexist = cursor.fetchall()[0][0]
        if int(result_data_stockexist) == 1:
            sql = "INSERT INTO stock_data(stockcode, opinion) VALUES(\"" + str(stockcode) + "\", " + 0 + ")"
            cursor.execute(sql)
            db.commit()
            return Response(status = 201)
        else:
            return_json = {
                "msg": "Stock code already exists"
            }
            return Response(respones = jsonify(return_json), status = 400)

    def put(self, stockcode, d_ml, d_nlp, d_ma520, d_ma2060, d_macd12269, d_stcstc93, d_rsi14, d_evlp2065, d_cci14, d_dmi14, d_obv14, d_opinion):
        sql = "SELECT EXISTS (SELECT id FROM stock_data WHERE = \"" + stockcode + "\")"
        cursor.execute(sql)
        result_data_stockexist = cursor.fetchall()[0][0]
        if result_data_stockexist == 1:
            sql = "UPDATE users SET "
            if d_ml != None: 
                sql = sql + "ml = " + str(d_ml) + " "
            else:
                sql = sql + "ml = NULL "
            if d_nlp != None:
                sql = sql + "ma520 = " + str(d_ma520) + " "
            else:
                sql = sql + "ma520 = NULL "
            if d_ma2060 != None:
                sql = sql + "ma2060 = " = str(d_ma2060) + " "
            else:
                sql = sql + "ma2060 = NULL "
            if d_macd12269 != None:
                sql = sql + "macd12269 = " = str(d_macd12269) + " "
            else:
                sql = sql + "macd12269 = NULL "
            if d_stcstc93 != None:
                sql = sql + "stcstc93 = " = str(d_stcstc93) + " "
            else:
                sql = sql + "stcstc93 = NULL "
            if d_rsi14 != None:
                sql = sql + "rsi14 = " = str(d_rsi14) + " "
            else:
                sql = sql + "rsi14 = NULL "
            if d_evlp2065 != None:
                sql = sql + "evlp2065 = " = str(d_evlp2065) + " "
            else:
                sql = sql + "evlp2065 = NULL "
            if d_cci14 != None:
                sql = sql + "cci14 = " = str(d_cci14) + " "
            else:
                sql = sql + "cci14 = NULL "
            if d_dmi14 != None:
                sql = sql + "dmi14 = " = str(d_dmi14) + " "
            else:
                sql = sql + "dmi14 = NULL "
            if d_obv14 != None:
                sql = sql + "obv14 = " = str(d_obv14) + " "
            else:
                sql = sql + "obv14 = NULL "
            if d_opinion != None:
                sql = sql + "opinion = " = str(d_opinion) + " "
            else:
                sql = sql + "opinion = NULL "
            sql += "WHERE stockcode = \"" + str(stockcode) + "\""
            cursor.execute(sql)
            db.commit()
            return Response(status = 204)
        else:
            return Response(status = 404)

    def patch(self, stockcode, d_ml, d_nlp, d_ma520, d_ma2060, d_macd12269, d_stcstc93, d_rsi14, d_evlp2065, d_cci14, d_dmi14, d_obv14, d_opinion):
        sql = "SELECT EXISTS (SELECT id FROM stock_data WHERE = \"" + stockcode + "\")"
        cursor.execute(sql)
        result_data_stockexist = cursor.fetchall()[0][0]
        if result_data_stockexist == 1:
            sql = "UPDATE users SET "
            if d_ml != None: 
                sql = sql + "ml = " + str(d_ml) + " "
            if d_nlp != None:
                sql = sql + "ma520 = " + str(d_ma520) + " "
            if d_ma2060 != None:
                sql = sql + "ma2060 = " = str(d_ma2060) + " "
            if d_macd12269 != None:
                sql = sql + "macd12269 = " = str(d_macd12269) + " "
            if d_stcstc93 != None:
                sql = sql + "stcstc93 = " = str(d_stcstc93) + " "
            if d_rsi14 != None:
                sql = sql + "rsi14 = " = str(d_rsi14) + " "
            if d_evlp2065 != None:
                sql = sql + "evlp2065 = " = str(d_evlp2065) + " "
            if d_cci14 != None:
                sql = sql + "cci14 = " = str(d_cci14) + " "
            if d_dmi14 != None:
                sql = sql + "dmi14 = " = str(d_dmi14) + " "
            if d_obv14 != None:
                sql = sql + "obv14 = " = str(d_obv14) + " "
            if d_opinion != None:
                sql = sql + "opinion = " = str(d_opinion) + " "
            sql += "WHERE stockcode = \"" + str(stockcode) + "\""
            cursor.execute(sql)
            db.commit()
            return Response(status = 204)
        else:
            return Response(status = 404)
 
    def delete(self, stockcode):
        sql = "SELECT EXISTS (SELECT id FROM stock_data WHERE = \"" + str(stockcode) + "\""
        cursor.execute(sql)
        result_data_stockexist = cursor.fetchall()[0][0]
        if result_data_stockexist == 1:
            sql = "DELETE FROM stock_data WHERE stockcode = \"" + str(stockcode) + "\"" 
            cursor.execute(sql)
            db.commit()
            return Response(status = 204)
        else:
            return Response(status = 404)

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 5000)