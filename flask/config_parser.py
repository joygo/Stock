from configparser import ConfigParser
import pandas as pd
import numpy as np
import json
import datetime
import time
import copy
import math
import os
from flask import current_app

from pd_functions import StockClass
from functions import CONFIG_PATH, Functions


class SelfConfigParser(ConfigParser):
    def __init__(self, **kwargs):
        super(SelfConfigParser, self).__init__(**kwargs)

    def get_default(self, section, option, default=''):
        if self.has_section(section):
            if self.has_option(section, option):
                return self.get(section, option)
        return default

    def get_total_default(self, section, default=''):
        if self.has_section(section):
            return self.items(section)
        return default


class ConfigParserFuntion():

    def __init__(self, user):
        self.user = user
        self.handling_fee = 0.001425
        self.fee_count = 0.6
        self.g_fee = 0.003
        self.func = Functions()
        self.account_file = "{}\\{}".format(CONFIG_PATH, "account.conf")
        self.setting_path = "{}\\{}".format(CONFIG_PATH, "setting.conf")
        self.buy_account_path = "{}\\{}_buy_account.conf".format(CONFIG_PATH, self.user)
        self.sell_account_path = "{}\\{}_sell_account.conf".format(CONFIG_PATH, self.user)
        self.dividend_account_path = "{}\\{}_dividend.conf".format(CONFIG_PATH, self.user)
        # self.init_dir()
        self.init_fee()
        self.init_setting_config()
        self.stock_data_func = StockClass()



    def init_setting_config(self):
        config = self.read_config_obj(self.setting_path)
        if not config.has_section("System Info"):
            config.add_section("System Info")
            config.set("System Info", "Last Update Time", "")
            config.set("System Info", "Update Status", "0")

        self.write_config(self.setting_path, config)

    def init_fee(self):
        config = self.read_config_obj(self.account_file)
        self.handling_fee = float(config.get_default(self.user, "handling_fee", 0.001425))
        self.fee_count = float(config.get_default(self.user, "fee_count", 0.6))
        self.g_fee = float(config.get_default(self.user, "g_fee", 0.003))

    def get_user_config(self):
        config = self.read_config_obj(self.account_file)
        data = {}
        dividend_price_flag = config.get_default(self.user, "dividend_price", "0")
        dividend_stock_flag = config.get_default(self.user, "dividend_stock", "0")
        handing_fee = config.get_default(self.user, "handing_fee", "0")
        fee_count = config.get_default(self.user, "fee_count", "0")
        data = {"dividend_price": dividend_price_flag,
                "dividend_stock": dividend_stock_flag,
                "handing_fee": handing_fee,
                "fee_count": fee_count
                }
        return data


    def set_user_config(self, data):
        """[summary]
        Set the user config data
        Arguments:
            data {[dict]} -- [setting data]

        Default value
        [div_stock, div_price]
        """
        config = self.read_config_obj(self.account_file)
        for key, value in data.items():
            config.set(self.user, str(key), value)

        self.write_config(self.account_file, config)

    def user_exists(self):
        config = self.read_config_obj(self.account_file)
        if not config.sections:
            return False
        else:
            if config.has_section(self.user):
                return True
            else:
                return False

    def read_config_obj(self, path):
        config = SelfConfigParser()
        config.optionxform = str
        try:
            config.read(path)
        except Exception as e:
            print("read config error {}".format(e))

        return config

    def write_config(self, path, config):
        with open(path, 'w') as fp:
            config.write(fp)

    def date_compare(self, date1, date2):
        """
        [summary]
        compare date , if date1 > date2 return 1, else 0
        Arguments:
            date1 {[str]} -- [description]
            date2 {[str]} -- [description]

        """

        date1_s = datetime.datetime(int(date1[0:4]), int(date1[4:6]), int(date1[6:8])).timestamp()
        date2_s = datetime.datetime(int(date2[0:4]), int(date2[4:6]), int(date2[6:8])).timestamp()
        if date1_s > date2_s:
            return 1
        return 0

    def date_minus(self, date1, date2):
        """[summary]

        Arguments:
            date1 {[str]} -- [format, 20190803]
            date2 {[str]} -- [format, 20190805]

        Returns:
            [int] -- [days]

        it should return 2(int)
        """
        days = 0
        date1_s = datetime.datetime(int(date1[0:4]), int(date1[4:6]), int(date1[6:8])).timestamp()
        date2_s = datetime.datetime(int(date2[0:4]), int(date2[4:6]), int(date2[6:8])).timestamp()
        days = (date2_s-date1_s)/86400
        return days

    def dividend_calculate(self, dividend_dict, stock, income, sell_date, buy_date, stock_count=1):
        if dividend_dict.get(stock):
            for div_index, dividend_data in enumerate(dividend_dict.get(stock)):
                year_price = dividend_data.get('除息交易日')
                div_price = dividend_data.get('現金股利')
                div_stock = dividend_data.get('股票股利')
                # print("stock {}, {}, {}, {}, {}".format(stock, sell_date, buy_date, year_price, div_price))
                if year_price and self.date_compare(year_price, buy_date) and self.date_compare(sell_date, year_price):
                    income += div_price * 1000 * stock_count
                    self.func.set_log('{} 符合股利 {}'.format(stock, income))

                # print(income)
        return income

    def read_user_buy_info(self, start_date=None, end_date=None):
        user = self.user
        buy_dict = {}
        buy_path_with_user = self.buy_account_path.format(user)
        # print("buy = {}".format(buy_path_with_user))
        buy_config = self.read_config_obj(buy_path_with_user)
        for date in buy_config.sections():
            if start_date and self.date_compare(start_date, date):
                continue
            for stock in buy_config.options(date):
                # print(json.loads(buy_config.get(date, stock)))
                stock_data = json.loads(buy_config.get(date, stock))
                # cost = float(stock_data.get("投資成本"))
                if not buy_dict.get(stock):
                    buy_dict.update({stock: {
                        "股票代號": stock_data.get("股票代號"),
                        "購買股價": [float(stock_data.get("股價"))],
                        "購買數量": [int(stock_data.get("數量"))],
                        "投資成本": [int(stock_data.get("投資成本"))],
                        "購買時間": [date]
                    }

                    })
                else:
                    # print(dict.get(stock).get("購買股價").append((stock_data.get("股價"))))
                    # print((dict.get(stock).get("購買股價")))
                    price_list = buy_dict.get(stock).get("購買股價")
                    num_list = buy_dict.get(stock).get("購買數量")
                    cost_list = buy_dict.get(stock).get("投資成本")
                    date_list = buy_dict.get(stock).get("購買時間")
                    for index, data in enumerate(date_list):
                        if self.date_compare(data, date):
                            price_list.insert(index, float(stock_data.get("股價")))
                            num_list.insert(index, int(stock_data.get("數量")))
                            cost_list.insert(index, int(stock_data.get("投資成本")))
                            date_list.insert(index, date)
                            break
                    else:
                        price_list.append(float(stock_data.get("股價")))
                        num_list.append(int(stock_data.get("數量")))
                        cost_list.append(int(stock_data.get("投資成本")))
                        date_list.append(date)

                    # price_list.append(stock_data.get("股價"))
                    # num_list.append(stock_data.get("數量"))
                    # cost_list.append(stock_data.get("投資成本"))
                    # date_list.append(date)
                    # print(list)

                    buy_dict.update({stock: {
                        "股票代號": stock_data.get("股票代號"),
                        "購買股價": price_list,
                        "購買數量": num_list,
                        "投資成本": cost_list,
                        "購買時間": date_list
                        }
                    })
            # print(dict)
        return buy_dict

    def read_user_sell_info(self, start_date=None, end_date=None):
        sell_dict = {}
        sell_path_with_user = self.sell_account_path.format(self.user)
        sell_config = self.read_config_obj(sell_path_with_user)
        for date in sell_config.sections():
            if end_date and self.date_compare(date, end_date):
                continue
            for stock in sell_config.options(date):
                # print(json.loads(buy_config.get(date, stock)))
                stock_data = json.loads(sell_config.get(date, stock))
                # cost = float(stock_data.get("投資成本"))
                if not sell_dict.get(stock):
                    sell_dict.update({stock: {
                        "股票代號": stock_data.get("股票代號"),
                        "賣出股價": [float(stock_data.get("股價"))],
                        "賣出數量": [int(stock_data.get("數量"))],
                        "賣出價格": [int(stock_data.get("賣出價格"))],
                        "賣出時間": [date]
                        }

                    })
                else:
                    # print(dict.get(stock).get("購買股價").append((stock_data.get("股價"))))
                    # print((dict.get(stock).get("購買股價")))
                    price_list = sell_dict.get(stock).get("賣出股價")
                    num_list = sell_dict.get(stock).get("賣出數量")
                    cost_list = sell_dict.get(stock).get("賣出價格")
                    date_list = sell_dict.get(stock).get("賣出時間")
                    for index, data in enumerate(date_list):
                        if self.date_compare(data, date):
                            price_list.insert(index, float(stock_data.get("股價")))
                            num_list.insert(index, int(stock_data.get("數量")))
                            cost_list.insert(index, int(stock_data.get("賣出價格")))
                            date_list.insert(index, date)
                            break
                    else:
                        price_list.append(float(stock_data.get("股價")))
                        num_list.append(int(stock_data.get("數量")))
                        cost_list.append(int(stock_data.get("賣出價格")))
                        date_list.append(date)

                    # price_list.append(stock_data.get("股價"))
                    # num_list.append(stock_data.get("數量"))
                    # cost_list.append(stock_data.get("投資成本"))
                    # date_list.append(date)
                    # print(list)
                    sell_dict.update({stock: {
                        "股票代號": stock_data.get("股票代號"),
                        "賣出股價": price_list,
                        "賣出數量": num_list,
                        "賣出價格": cost_list,
                        "賣出時間": date_list
                        }
                    })
        return sell_dict

    def del_element_from_array_by_index(self, array, indexes):
        return [data for index, data in enumerate(array) if index not in indexes]


    def buy_cost(self, buy_price, count):
        """[summary]
        count the buy cost included fee
        Arguments:
            buy_price {[float]} -- [price]
            count {[float]} -- [stock num]

        Returns:
            [float] -- [cost]
        """
        fee = 20 if math.floor(count*buy_price*1000*self.fee_count*self.handling_fee) <= 20 else math.ceil(count*buy_price*1000*self.fee_count*self.handling_fee)
        return int(buy_price*1000*count+fee)

    def sell_cost(self, sell_price, count):
        """[summary]
        count the sell cost included fee

        Arguments:
            sell_cost {[float]} -- [price]
            count {[float]} -- [stock num]

        Returns:
            [float] -- [cost]
        """

        g_cost = math.floor(self.g_fee * sell_price * 1000 * count)
        handling_cost = math.ceil(self.handling_fee * self.fee_count * sell_price * 1000 * count)
        new_fee = g_cost + handling_cost
        print(sell_price, self.g_fee, self.handling_fee, self.fee_count, new_fee)
        return int(sell_price*1000*count-new_fee)



    def date_sort(self, type, dict, start_date, end_date):
        """[summary]
        return data in start_date -> end_date
        """
        # print("start date = {}, end date = {}".format(start_date, end_date))
        if type == "buy":
            for stock, data in dict.items():
                # if self.date_compare(start_date, data.get("購買時間")) or self.date_compare(data.get("購買時間"), end_date)):
                stock_index = dict.get(stock).get("股票代號")
                price_list = dict.get(stock).get("購買股價")
                num_list = dict.get(stock).get("購買數量")
                cost_list = dict.get(stock).get("投資成本")
                date_list = dict.get(stock).get("購買時間")
                del_indexes = []
                for index, date in enumerate(date_list):
                    # print("Date = {}".format(date))
                    if (start_date and self.date_compare(start_date, date)) or (end_date and self.date_compare(date, end_date)):
                        del_indexes.append(index)
                        # del date_list[index]
                print(del_indexes)
                price_list = self.del_element_from_array_by_index(price_list, del_indexes)
                num_list = self.del_element_from_array_by_index(num_list, del_indexes)
                cost_list = self.del_element_from_array_by_index(cost_list, del_indexes)
                date_list = self.del_element_from_array_by_index(date_list, del_indexes)

                dict.update(
                    {stock: {
                            "股票代號": stock_index,
                            "購買股價": price_list,
                            "購買數量": num_list,
                            "投資成本": cost_list,
                            "購買時間": date_list
                            }
                    })
        elif type == "sell":
            for stock, data in dict.items():
                # if self.date_compare(start_date, data.get("購買時間")) or self.date_compare(data.get("購買時間"), end_date)):
                stock_index = dict.get(stock).get("股票代號")
                price_list = dict.get(stock).get("賣出股價")
                num_list = dict.get(stock).get("賣出數量")
                cost_list = dict.get(stock).get("賣出價格")
                date_list = dict.get(stock).get("賣出時間")
                income_list = dict.get(stock).get("實現損益")
                buycost_list = dict.get(stock).get("購買成本")
                del_indexes = []
                for index, date in enumerate(date_list):
                    if (start_date and self.date_compare(start_date, date)) or (end_date and self.date_compare(date, end_date)):
                        del_indexes.append(index)
                        # del date_list[index]
                print(del_indexes)
                price_list = self.del_element_from_array_by_index(price_list, del_indexes)
                num_list = self.del_element_from_array_by_index(num_list, del_indexes)
                cost_list = self.del_element_from_array_by_index(cost_list, del_indexes)
                date_list = self.del_element_from_array_by_index(date_list, del_indexes)

                dict.update(
                    {stock: {
                            "股票代號": stock_index,
                            "賣出股價": price_list,
                            "賣出數量": num_list,
                            "賣出價格": cost_list,
                            "賣出時間": date_list,
                            "實現損益": income_list,
                            "購買成本": buycost_list
                            }
                    })




    def read_user_info(self, start_date=None, end_date=None):
        """[summary]
        summary = 未實現損益 (時間不看)
        sell = 賣出損益 可輸入時間範圍
        buy = 買入
        Arguments:
            user {[type]} -- [description]

        Keyword Arguments:
            start_date {[str]} -- [start date] (default: {None}) ex:20180915
            end_date {[str]} -- [end start] (default: {None})
        """
        user = self.user
        now_date = time.strftime("%Y%m%d", time.localtime())
        buy_path_with_user = self.buy_account_path.format(user)
        sell_path_with_user = self.sell_account_path.format(user)
        dividend_path_with_user = self.dividend_account_path.format(user)
        buy_config = self.read_config_obj(buy_path_with_user)
        sell_config = self.read_config_obj(sell_path_with_user)
        dividend_config = self.read_config_obj(dividend_path_with_user)
        user_config = self.get_user_config()
        dividend_dict = {}
        dict = {}
        buy_dict = {}
        sell_dict = {}
        stock_info = []
        print(self.get_user_config())
        user_config = self.get_user_config()

        if start_date and end_date and self.date_compare(start_date, end_date):
            return dict

        buy_dict = self.read_user_buy_info()
        sell_dict = self.read_user_sell_info()
        self.date_sort('buy', buy_dict, start_date, end_date)
        self.date_sort('sell', sell_dict, start_date, end_date)
        all_sell_dict = copy.deepcopy(sell_dict)
        dict = copy.deepcopy(buy_dict)




        if user_config.get('dividend_price') == "1":
            dividend_dict = StockClass().get_dividends(sell_dict.keys())
            # print("dividend_dict = {}".format(dividend_dict))

        # pretty(sell_dict)
        # copy for summary dict

        for stock, data in sell_dict.items():

            price_list = dict.get(stock).get("購買股價")
            num_list = dict.get(stock).get("購買數量")
            cost_list = dict.get(stock).get("投資成本")
            date_list = dict.get(stock).get("購買時間")
            sell_count_list = sell_dict.get(stock).get("賣出數量")
            sell_price_list = sell_dict.get(stock).get("賣出股價")
            sell_income_list = sell_dict.get(stock).get("賣出價格")
            sell_date_list = sell_dict.get(stock).get("賣出時間")
            for sell_index, sell_count in enumerate(sell_count_list):
                del_index = []
                dividend_price = 0
                cost = 0
                sell_lefe_count = sell_count
                sell_income = sell_income_list[sell_index]
                # avg_sell_income = sell_income_list[index]/sell_count
                print("sell stock {}".format(stock))
                for index, buy_count in enumerate(num_list):
                    if sell_lefe_count == 0:
                        break
                    if buy_count - sell_lefe_count == 0:
                        # count the dividend
                        dividend_price = self.dividend_calculate(dividend_dict, stock, dividend_price, sell_date_list[sell_index], date_list[index], sell_lefe_count)
                        cost += float(cost_list[index])
                        # income = sell_lefe_count * avg_sell_income
                        sum_price = sell_income - cost
                        # print("-----------------------stock {},{},{},{}, {}".format(stock, sell_income, cost, sell_price_list[index], index))
                        if(not sell_dict[stock].get('實現損益')):
                            sell_dict[stock]['實現損益'] = [sum_price+dividend_price]
                            sell_dict[stock]['購買成本'] = [cost]
                        else:
                            sell_dict[stock]['實現損益'].append(sum_price+dividend_price)
                            sell_dict[stock]['購買成本'].append(cost)
                        # del num_list[index]
                        # del price_list[index]
                        # del cost_list[index]
                        # del date_list[index]
                        del_index.append(index)
                        sell_lefe_count = sell_lefe_count - buy_count
                        break
                    elif buy_count - sell_lefe_count > 0:
                        cost += float(cost_list[index]) / buy_count * sell_lefe_count
                        sum_price = sell_income - cost
                        dividend_price = self.dividend_calculate(dividend_dict, stock, dividend_price, sell_date_list[sell_index], date_list[index], sell_lefe_count)

                        if(not sell_dict[stock].get('實現損益')):
                            sell_dict[stock]['實現損益'] = [sum_price+dividend_price]
                            sell_dict[stock]['購買成本'] = [cost]
                        else:
                            sell_dict[stock]['實現損益'].append(sum_price+dividend_price)
                            sell_dict[stock]['購買成本'].append(cost)
                        num_list[index] = buy_count - sell_lefe_count
                        cost_list[index] = float(cost_list[index]) / buy_count * num_list[index]
                        break
                    elif buy_count - sell_lefe_count < 0:
                        dividend_price = self.dividend_calculate(dividend_dict, stock, dividend_price, sell_date_list[sell_index], date_list[index], sell_lefe_count)
                        cost += float(cost_list[index])
                        sell_lefe_count = sell_lefe_count - num_list[index]
                        del_index.append(index)
                    else:
                        print(" count failed, sell more than buy")


                # remove the already used data in list
                num_list = self.del_element_from_array_by_index(num_list, del_index)
                price_list = self.del_element_from_array_by_index(price_list, del_index)
                cost_list = self.del_element_from_array_by_index(cost_list, del_index)
                date_list = self.del_element_from_array_by_index(date_list, del_index)

            # Update the info
            dict[stock]["購買股價"] = price_list
            dict[stock]["購買數量"] = num_list
            dict[stock]["投資成本"] = cost_list
            dict[stock]["購買時間"] = date_list

        #計算未實現損益
        for stock, data in dict.items():
            number = data.get("股票代號")
            today_price_dict = self.stock_data_func.get_stock_price([number])
            today_close_price = today_price_dict.get(number)
            if today_close_price:
                num_list = dict.get(stock).get("購買數量")
                cost_list = dict.get(stock).get("投資成本")
                all_cost = 0
                all_income = 0
                for index, count in enumerate(num_list):
                    all_cost += float(cost_list[index])
                    all_income += self.sell_cost(today_close_price, count)
                # print("stock {}, all_cost = {}, all_income ={}".format(stock, all_cost, all_income))
                dict.get(stock)["今日股價"] = today_close_price
                dict.get(stock)["未實現損益"] = int(all_income - all_cost)
            else:
                dict.get(stock)["今日股價"] = ""
                dict.get(stock)["未實現損益"] = ""



        income = 0

        #計算股利(還持有的)

        if user_config.get('dividend_price') == "1":
            dividend_dict = StockClass().get_dividends(dict.keys())
            for stock, data in dict.items():
                # print(stock, data)
                num_list = dict.get(stock).get("購買數量")
                date_list = dict.get(stock).get("購買時間")
                cost_list = dict.get(stock).get("投資成本")
                price_list = dict.get(stock).get("購買股價")
                number = dict.get(stock).get("股票代號")

                old_sum_price = float(dict.get(stock).get("實現損益")) if dict.get(stock).get("實現損益") else 0
                # print("old_sum_price = {}".format(old_sum_price))
                for index, date in enumerate(date_list):
                    old_sum_price += self.dividend_calculate(dividend_dict, stock, 0, now_date, date_list[index]) * num_list[index]
                    # income = old_sum_price + income
                    # dict.update({stock: {
                    #                     "股票代號": number,
                    #                     "購買股價": price_list,
                    #                     "購買數量": num_list,
                    #                     "投資成本": cost_list,
                    #                     "實現損益": old_sum_price,
                    #                     "購買時間": date_list,
                    #                     }
                    # })
                    dict.get(stock)["實現損益"] = old_sum_price
                    dict.update({stock: dict.get(stock)})

        all_income = 0
        # count all income in certain stock
        for stock, data in sell_dict.items():
            if(data.get("實現損益")):
                for income in data.get("實現損益"):
                    all_income += income
            dict.get(stock)['實現損益'] = all_income
            all_income = 0

        stock_info.append({'buy': buy_dict})
        stock_info.append({'sell': sell_dict})
        stock_info.append({'summary': dict})
        stock_info.append({'user_config': user_config})
        return stock_info

    # def del_stock(self, stock, date):
        # config = self.read_config_obj(self.)

    def add_stock_dividend(self, date, stock, money_div, stock_div):
        config = self.read_config_obj(self.dividend_account_path)
        if not config.has_section("股利"):
            config.add_section("股利")

        if stock in config.options("股利"):
            old_dict = config.get("股利", stock)
            old_year = old_dict.get("股利年份")
            old_money_div = old_dict.get("現金股利")
            old_stock_div = old_dict.get("股票股利")
            old_year.append(date)
            old_money_div.append(old_money_div)
            old_stock_div.append(old_stock_div)
            dict = {
                    "股利年份": old_year,
                    "現金股利": old_money_div,
                    "股票股利": old_stock_div
                }
        else:
            dict = {
                    "股利年份": [date],
                    "現金股利": [money_div],
                    "股票股利": [stock_div]
                    }

        config.set("股利", stock, json.dumps(dict))
        self.write_config(self.dividend_account_path, config)

    def add_account(self, password):
        config = self.read_config_obj(self.account_file)
        if self.user in config.sections():
            return False
        else:
            config.add_section(self.user)
            config.set(self.user, "password", password)
            config.set(self.user, "dividend_price", "0")
            config.set(self.user, "dividend_stock", "0")
            config.set(self.user, "handling_fee", "0.001425")
            config.set(self.user, "g_fee", "0.003")
            config.set(self.user, "fee_count", "0.6")

        self.write_config(self.account_file, config)
        return True

    def del_stock(self, target, stock, date):
        try:
            if not stock or not date:
                return False
            if target == "buy":
                config = self.read_config_obj(self.buy_account_path)
                config.remove_option(date, stock)
                if not config.options(date):
                    config.remove_section(date)
                self.write_config(self.buy_account_path, config)
            elif target == "sell":
                config = self.read_config_obj(self.sell_account_path)
                config.remove_option(date, stock)
                if not config.options(date):
                    config.remove_section(date)
                self.write_config(self.sell_account_path, config)

        except Exception as e:
            print("error = {}".format(e))
            return False
        return True

    def add_stock(self, stock, number, count, price, date):
        if not stock or not count or not price or not date:
            return False
        exist_stock_info = self.stock_data_func.get_stocks_info()
        if stock not in exist_stock_info.get("stock_name") or number not in exist_stock_info.get("stock_number"):
            return False

        config = self.read_config_obj(self.buy_account_path)
        price = price * 1000
        now_year, now_month, now_day = time.strftime("%Y %m %d", time.localtime()).split(" ")
        fee_cost = 20 if math.floor(count*price*self.fee_count*self.handling_fee) <= 20 else math.ceil(count*price*self.fee_count*self.handling_fee)

        if not config.has_section(date):
            config.add_section(date)
            dict = {
                    "股價": price/1000,
                    "數量": count,
                    "投資成本": str(math.floor(fee_cost + price*count)),
                    "股票代號": number
                    }

            config.set(date, stock, json.dumps(dict))
        else:
            if config.has_option(date, stock):
                old_price = config.get(date, stock).get("股價")
                old_count = config.get(date, stock).get("數量")
                old_cost = config.get(date, stock).get("投資成本")
                price = ((old_count*old_price)+(price/1000)*count)/(old_count+count)

                dict = {
                        "股價": price,
                        "數量": count + old_count,
                        "投資成本": str(int(math.floor(fee_cost + price*count + int(old_cost)))),
                        "股票代號": number
                        }

            else:
                dict = {
                        "股價": price/1000,
                        "數量": count,
                        "投資成本": str(int(math.floor(fee_cost + price*count))),
                        "股票代號": number
                        }

            config.set(date, stock, json.dumps(dict))

        self.write_config(self.buy_account_path, config)

    def sell_stock(self, stock, number, count, price, date):
        if not stock or not count or not price or not date:
            return False
        exist_stock_info = self.stock_data_func.get_stocks_info()
        if stock not in exist_stock_info.get("stock_name") or number not in exist_stock_info.get("stock_number"):
            return False
        buy_dict = self.read_user_buy_info()
        sell_dict = self.read_user_sell_info()
        config = self.read_config_obj(self.sell_account_path)
        all_buy_count = 0
        already_sell_count = 0
        if buy_dict.get(stock):
            for x in buy_dict.get(stock).get("購買數量"):
                all_buy_count += x

        if sell_dict.get(stock):
            for x in sell_dict.get(stock).get("賣出數量"):
                already_sell_count += x
        if all_buy_count - already_sell_count - count < 0:
            print("{} 張數不足".format(stock))
            return False, "{} 張數不足 {}".format(stock,  already_sell_count + count - all_buy_count)

        # price = price * 1000
        if not config.has_section(date):
            config.add_section(date)
        # new_fee = int(price * count * (self.g_fee + self.handling_fee * 0.6)) if self.handling_fee * 0.6 * price > 20 else int(price * count * (self.g_fee) + 20)
        # income = (int(price*count-new_fee))
        income = self.sell_cost(price, count)
        if config.has_option(date, stock):
            old_price = json.loads(config.get(date, stock)).get("股價")
            old_count = json.loads(config.get(date, stock)).get("數量")
            old_income = json.loads(config.get(date, stock)).get("賣出價格")
            price = ((old_count*old_price)+(price)*count)/(old_count+count)

            dict = {
                    "股價": price,
                    "數量": count + old_count,
                    "賣出價格": str(math.floor(income + int(old_income))),
                    "股票代號": number
                    }
        else:
            dict = {
                    "股票代號": number,
                    "股價": price,
                    "數量": count,
                    "賣出價格": str(math.floor(income))
                    }

        config.set(date, stock, json.dumps(dict))
        self.write_config(self.sell_account_path, config)
        return True, ""



if __name__ == '__main__':
    config = ConfigParserFuntion('test')
    print(config.read_user_info())

