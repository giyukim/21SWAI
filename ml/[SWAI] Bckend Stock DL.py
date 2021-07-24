#This Project doesn't support python Version under 3.6 (Recommended: 3.8.10)

import numpy as np
import pandas as pd
import FinanceDataReader as fdr
import sklearn.preprocessing as skl
import tensorflow as tf
import pymysql
import typing as tpy
import os
import datetime as dt

# Settings
data_directory_path:str = "./SWAIMLDATA"

mysql_host:str = "api.swai.jgamgyul.kr"
mysql_user:str = "swaiapiv1"
mysql_password:str = "swaiapiv1_password"
mysql_db:str = "swai01"
mysql_table:str = "stock_data"

stock_exchange:str = "KRX"
stock_crawling_start_date:str = "2010-01-01"

rnn_m1_seq_length:int = 7
rnn_m1_learning_rate = 0.001
rnn_m1_epoch:int = 10000
rnn_m1_datacolsize:int = 5
rnn_m1_trainsize = 0.8

def logging(msg):
    print("[LOG] {}".format(msg))

# Driectory: MainDirectoryName/Date/Stockcode
def make_directory(secondary_directory:tpy.Union[str, bool] = False, tertiary_directory:tpy.Union[str, bool] = False, path_return:bool = False):
    path:str = "{}".format(data_directory_path)
    if secondary_directory == True:
        secondary_directory_edited:str = "{}".format(secondary_directory)
        secondary_directory_edited_next:str = "{}1".format(secondary_directory)
        count:int = 1
        while os.path.isdir("{}/{}".format(data_directory_path, secondary_directory_edited_next)):
            secondary_directory_edited = "{}".format(secondary_directory_edited_next)
            count += 1
            secondary_directory_edited_next = "{}{}".format(secondary_directory, str(count))
        path += "/{}".format(secondary_directory_edited)
    elif not secondary_directory == False and not secondary_directory == True:
        secondary_directory_edited:str = "{}".format(secondary_directory)
        count:int = 0
        while os.path.isdir("{}/{}".format(data_directory_path, secondary_directory_edited)):
            count += 1
            secondary_directory_edited = "{}{}".format(secondary_directory, str(count))
        path += "/{}".format(secondary_directory_edited)
    if not tertiary_directory == False and not secondary_directory == False:
        path += "/{}".format(tertiary_directory)
    os.makedirs(path, exist_ok = True)
    logging("Make Directory \"{}\"".format(path))
    if path_return == True:
        return path

def mysql_connect():
    logging("Connect DB")
    global db
    global cursor
    db = pymysql.connect(
        user = mysql_user,
        passwd = mysql_password,
        host = mysql_host,
        db = mysql_db,
        charset = 'utf8mb4'
    )
    cursor = db.cursor()

def mysql_disconnect():
    logging("Disconnect DB")
    db.close()

# Option '0':Read, '1':Write
def mysql_sql(sql:str, option:int = 0):
    logging("Call Query \"{}\" ({})".format(sql, option))
    if option == 0:
        cursor.execute(sql)
        return cursor.fetchall()
    elif option == 1:
        cursor.execute(sql)
        db.commit()

def data_get(stock_symbol:str, save_path:str, statistics:bool = False):
    logging("Get Stock Data: {}{}".format(stock_exchange, stock_symbol))
    dataframe = fdr.DataReader(stock_symbol, stock_crawling_start_date, exchange = stock_exchange)
    dataframe_col:list = dataframe.columns
    dataframe.to_csv("{}/dataframe.csv".format(save_path))
    if statistics == False:
        return dataframe, dataframe_col
    elif statistics == True:
        dataframe_statistics, dataframe_statistics_col = data_statistics(dataframe)
        dataframe_statistics.to_csv("{}/dataframe_statistics.csv".format(save_path))
        return dataframe, dataframe_col, dataframe_statistics, dataframe_statistics_col

def data_statistics(dataframe):
    logging("Stock Data Analyzing Statistics")
    dataframe_statistics = dataframe
    dataframe_statistics.insert(len(dataframe.columns), "Mid", (dataframe["High"] + dataframe["Low"]) / 2)
    dataframe_statistics.insert(len(dataframe.columns), "MA5", dataframe["Close"].rolling(window = 5).mean())
    dataframe_statistics.insert(len(dataframe.columns), "MA20", dataframe["Close"].rolling(window = 20).mean())
    dataframe_statistics.insert(len(dataframe.columns), "MA60", dataframe["Close"].rolling(window = 60).mean())
    dataframe_statistics.insert(len(dataframe.columns), "MA120", dataframe["Close"].rolling(window = 120).mean())
    dataframe_statistics.insert(len(dataframe.columns), "Tomorrow Close", dataframe["Close"].shift(-1))
    dataframe_statistics.insert(len(dataframe.columns), "Fluctuation", dataframe["Tomorrow Close"] - dataframe["Close"])
    dataframe_statistics.insert(len(dataframe.columns), "Fluctuation Rate", dataframe["Fluctuation"] / dataframe["Close"])
    dataframe_statistics_col:list = dataframe_statistics.columns
    return dataframe_statistics, dataframe_statistics_col

def data_generalization(dataframe, dataframe_col:list, save_path:str):
    logging("Data Generalization")
    MinMax_Scaler = skl.MinMaxScaler()
    MinMax_Scaler.fit(dataframe)
    dataframe_gen = MinMax_Scaler.transform(dataframe)
    dataframe_gen = pd.DataFrame(dataframe_gen, columns = dataframe_col[1:])
    dataframe_gen_col:list = dataframe_gen.columns
    dataframe_gen.to_csv("{}/dataframe_generalization.csv".format(save_path))
    return dataframe_gen, dataframe_gen_col
    
def rnn_m1_build_dataset(dataframe):
    logging("Build DataSet (rnn m1)")
    dataX = []
    dataY = []
    for i in range(0, len(dataframe) - rnn_m1_seq_length):
        x = dataframe[i:i + rnn_m1_seq_length, :]
        y = dataframe[i + rnn_m1_seq_length, [-1]]
        dataX.append(x)
        dataY.append(y)
    return np.array(dataX), np.array(dataY)

def rnn_m1_dataset_distribution(dataframe):
    logging("Distribute DataSet (rnn m1)")
    del dataframe["Change"]
    del dataframe["Date"]
    dataframe = dataframe[['Open', 'High', 'Low', 'Volume', 'Close']]
    dataframe_np = dataframe.to_numpy()
    dataframe_np = dataframe_np[::-1]
    train_size = int(len(dataframe_np) * rnn_m1_trainsize)
    trainX, trainY = rnn_m1_build_dataset(dataframe_np[0:train_size])
    testX, testY = rnn_m1_build_dataset(dataframe_np[train_size - rnn_m1_seq_length:])
    predictionX = [dataframe[rnn_m1_seq_length * -1:]]
    return trainX, trainY, testX, testY, predictionX

def rnn_m1_learning_prediction(trainX, trainY, testX, testY, predict_x, save_path:str):
    logging("Learning and Making Prediction rnn m1 model")
    rnn_m1_model = tf.keras.Sequential()
    rnn_m1_model.add(tf.keras.layers.LSTM(units = 1, kernel_regularizer = tf.keras.regularizers.l2(0.001), input_shape = (rnn_m1_seq_length, rnn_m1_datacolsize)))
    rnn_m1_model.add(tf.keras.layers.Dropout(0.2))
    rnn_m1_model.add(tf.keras.layers.Dense(units = 1, activation = "tanh"))
    rnn_m1_model.summary()
    rnn_m1_model.compile(loss='binary_crossentropy', metrics=['accuracy', 'mean_squared_error', 'binary_crossentropy'], optimizer = tf.keras.optimizers.Adam)
    rnn_m1_model.fit(trainX, trainY, epochs = rnn_m1_epoch, validation_data = (testX, testY), verbose = 2)
    rnn_m1_model.save("{}/rnn_m1_model".format(save_path))
    prediction = rnn_m1_model.predict(predict_x)
    del rnn_m1_model
    return prediction

def rnn_m1_get_opinion(dataframe, prediction, save_path:str):
    logging("Save Opinion")
    with_compare = dataframe["Close"][-1]
    opinion = (with_compare <= prediction)
    with open("{}/rnnm1_opinion.txt".format(save_path), "w") as file:
        file.write(opinion)
    return opinion

def main():
    logging("Start Session")
    today_date:str = dt.date.today().strftime("%Y%m%d")
    make_directory(today_date)
    mysql_connect()
    sql_stocklist = mysql_sql("SELECT stockcode FROM {}".format(mysql_table))
    mysql_disconnect()
    stock_list = []
    for i in sql_stocklist:
        stock_list.append(i[0])
    stock_opinion:dict = {}
    for stock_symbol in stock_list:
        data_path = make_directory(True, str(stock_symbol), True)
        dataframe, dataframe_col = data_get(stock_symbol, data_path)
        dataframe, dataframe_col = data_generalization(dataframe, dataframe_col, data_path)
        trainX, trainY, testX, testY, predictionX = rnn_m1_dataset_distribution(dataframe)
        prediction = rnn_m1_learning_prediction(trainX, trainY, testX, testY, predictionX, data_path)
        opinion = rnn_m1_get_opinion(dataframe, prediction, data_path)
        if opinion == True:
            opinion:int = 1
        elif opinion == False:
            opinion:int = 0
        stock_opinion[stock_symbol] = opinion
    mysql_connect()
    stock_opinion_keys = list(stock_opinion.keys())
    for key in stock_opinion_keys:
        mysql_sql("UPDATE {} SET opinion = {} WHERE stockcode = \"{}\"".format(mysql_table, int(stock_opinion[key]), str(key)))
    mysql_disconnect()
    logging("End Session")

if __name__ == "__main__":
    main()