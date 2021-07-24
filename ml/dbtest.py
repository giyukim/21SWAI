import FinanceDataReader as fdr
import pandas as pd

dataframe = fdr.DataReader("005930", "2015-01-01", exchange = "KRX")
del dataframe["Change"]
del dataframe["Date"]
dataframe = dataframe[['Open', 'High', 'Low', 'Volume', 'Close']]

dataframe