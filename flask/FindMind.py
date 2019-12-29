
import requests
import pandas as pd
import json
import datetime


class FindMindClient(object):

    def __init__(self):
        self.url = "http://finmindapi.servebeer.com/api/data"


    def get_price(self, stock_list, date):
        """[summary]
        Get price - open/max/min/
        Arguments:
            stock_list {[type]} -- [description]
            date {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        dict = {}
        for stock in stock_list:
            # print("stock_list = {}, {}".format(stock, date))
            parameter = {
                        'dataset': "TaiwanStockPrice",
                        'stock_id': stock,
                        'date': date
                        }
            res = requests.post(self.url, verify=True, data=parameter)
            data = res.json()
            if data.get('status') == 200 and data.get('data'):
                dict.update({stock: data.get('data')})


        return dict


