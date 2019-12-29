
# -*- coding: utf-8 -*-
from flask import current_app
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import os
import time
from configparser import ConfigParser
import requests
from bs4 import BeautifulSoup
import urllib
from functions import STOCK_DATA_PATH


class StockClass():
    """[summary]

    Returns:
        [type] -- [description]
    """

    def __init__(self):

        self.db_path = "G:/google_sync/mobile/stock"
        self.yaer_eps_path = "{}/year_eps".format(self.db_path)
        self.dividend_eps_path = "{}/year_dividend".format(self.db_path)
        self.senson_eps_path = "{}/season_eps".format(self.db_path)
        self.ma_path = "{}/ma".format(self.db_path)
        self.net_buy_path = "{}/Net_Buy".format(self.db_path)
        self.month_income_path = "{}/month_income".format(self.db_path)
        self.shareholder_week_path = "{}/shareholders".format(STOCK_DATA_PATH)
        self.MACD_path = "{}/MACD".format(self.db_path)
        self.summary_path = "{}/summary".format(self.db_path)
        self.price_path = "{}/price".format(STOCK_DATA_PATH)
        self.goodinfo_url = 'https://goodinfo.tw/StockInfo/StockList.asp?'
        self.today_price_tmp = pd.DataFrame()

    def replace_index(self, df, title):
        df.index = df[title].values.tolist()
        return df

    def get_data(self, url):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        # url = 'https://kenpom.com/index.php?y=2014'
        df = pd.DataFrame()
        if url:
        #     for i in range(5):
            try:
                print("start to download usr {}".format(url))
                res = requests.get(url,headers=headers)
                res.encoding = 'utf-8'
                html_table = res.text
                soup = BeautifulSoup(html_table, "html.parser")
                # warn! id ratings-table is your page specific
                # print((soup.select('#divStockList table')))
                for table in soup.select('#divStockList table'):
                # for table in soup.findChildren(attrs={'id': 'ratings-table'}):
                    for c in table.children:
                        if c.name in ['tbody', 'thead']:
                            c.unwrap()
                df = pd.read_html(str(soup.select('#divStockList table')), flavor="bs4")
                df = df[0]
                final_df = pd.DataFrame(data = df[df[0] != "排名"].values, columns=df.iloc[0])
                return final_df
            except Exception as e:
                print ("Error {}".format(e))
                return df


    def url_choose(self, option):
        """
        暫時用途不大
        option has -> SHEET, MARKET_CAT, INDUSTRY_CAT, RANK, RPT_TIME, should be diction
        SHEET-主選單
        SHEET2-副選單(如果有)
        MARKET_CAT-複選單
        INDUSTRY_CAT-細項分類
        RANK-頁數,以熱門排行的方法尋找大多為6頁
        RPT_TIME-年度, EX:2017,最新資料
        """
        url = self.goodinfo_url +"SHEET={}&MARKET_CAT={}&INDUSTRY_CAT={}&RANK={}&RPT_TIME={}".format(option.get('SHEET'),                                                                                                     option.get('MARKET_CAT'),                                                                                                     option.get('INDUSTRY_CAT'),                                                                                                     option.get('RANK'),                                                                                                     option.get('RPT_TIME'))
        if option.get('SHEET2'):
            url = "{}&SHEET2={}".format(url, option.get('SHEET2'))
        return url

    def get_date(self, days=0, months=0, years=0):
        """[summary]
        Get now date
        Returns:
            [str] -- [year, month, day]
        """
        now_year, now_month, now_day, now_day_week = (datetime.now() - relativedelta(days=days,months=months, years=years)).strftime("%Y %m %d %w").split(" ")
        return now_year, now_month, now_day, now_day_week

    def get_csv_in_path(self, path):
        """[summary]
        Return all file in path
        Arguments:
            path {[str]} -- [path ]

        Returns:
            [list] -- [file name]
        """
        files = os.listdir((path))
        return files

    def check_duplicated_data(self, path, target):
        """[summary]
        Check the file is duplicated
        Arguments:
            path {[str]} -- [file path]
            target {[str]} -- [file name]

        Returns:
            [type] -- [description]
        """
        files_in_path = [file for file in self.get_csv_in_path(path)]
        print("check duplicated for file {} in path {} , files".format(target, path))
        if target in files_in_path:
            print('The {} is already exist'.format(target))
            return True
        return False

    def get_newest_time_df(self, path, name_form):
        day_count = 0
        df = pd.DataFrame()
        while 1:
            try:
                today = date.today()
                target_date = (today-timedelta(days=day_count)).strftime("%Y-%m-%d").split("-")

                print(name_form.format(path, target_date[0], target_date[1], target_date[2]))

                df = pd.read_csv(name_form.format(path, target_date[0], target_date[1], target_date[2]))
                return df, target_date
            except Exception as e:
                day_count += 1
                print(e)
                if day_count > 10:
                    break
        return df, target_date

    def check_webdata_newer(self, df, new_df, option):
        new_df_na = new_df[option].isna().sum()
        df_na = df[option].isna().sum()
        print("new df nan num {}, old df nan num {}".format(new_df_na, df_na))
        if new_df_na < df_na:
            print("data need to update")
            return True
        else:
            print("don't need update")
            return False

    def check_dataframe_valid(self, df, option):
        """[summary]
        Check the dataframe is vaild or not
        Arguments:
            df {[dataframe]} -- [download data]
            option {[str]} -- [option]

        Returns:
            [Bool] -- [vaild or invaild]
        """
        # display(df)
        if df[option].isna().sum() > df.shape[0]/2:
            print("invalid data")
            return False
        else:
            print("valid data")
            return True


    def my_choose_data_1(self, year_range=5):
        """
        (有季考慮棄用)
        下載資料1
        EPS > 0, 年增率累計>0 (到目前時間為止)
        成交 漲跌價 漲跌幅 財報年度 營收(億) 營收成長(%) 毛利(億) 毛利成長(%) 淨利(億) 淨利成長(%) 毛利(%) 毛率增減 淨利(%) 淨率增減 ROA(%) ROA增減
        ROE(%) ROE增減 EPS(元) EPS增減(元) 財報分數
        """
        urls = []

        df_dict = {}
        now_year, now_month, now_day, now_day_week = self.get_date()
        for year in range(int(now_year), int(now_year) - year_range, -1):
            target_name = '{}.csv'.format(year)
            if int(now_year) -1 > year:
                if self.check_duplicated_data(self.yaer_eps_path, target_name):
                    #倒數的因此如果已經有重複就不繼續做
                    break

            df_list = []
            for i in range(6):
                option1={"SHEET":"年獲利能力", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "年度EPS最高"}
                option1["RANK"] = i
                option1["RPT_TIME"] = year
                url = self.url_choose(option1)
                df_list.append(self.get_data(url))
                time.sleep(2)

            # try:
            #     old_df = pd.read_csv("./{}/{}", self.yaer_eps_path, target_name)

            if df_list:
                df = pd.concat(df_list, axis=0)
                # if there is new data, update the csv file, if is the first time
                # the old_df is empty will get except and restore the df_list
                try:
                    old_df = pd.read_csv('./{}/{}'.format(self.yaer_eps_path, target_name))
                    if self.check_webdata_newer(old_df, df, 'EPS(元)'):
                        df.to_csv('./{}/{}'.format(self.yaer_eps_path, target_name))
                except Exception as e:
                    print("don't have old_df, {}".format(e))


                if self.check_dataframe_valid(df, 'EPS(元)') :
                    df.to_csv('./{}/{}'.format(self.yaer_eps_path, target_name))

        return None

    def my_choose_data_2(self, year_range=5):
        """
        下載資料2
        股利 > 0, 年增率累計>0 (到目前時間為止)

        """
        urls = []

        df_dict = {}
        now_year, now_month, now_day, now_day_week = self.get_date()

        # check for data is
        for year in range(int(now_year) , int(now_year) - year_range , -1):
            df_list = []
            target_name = '{}.csv'.format(year)
            if int(now_year) -1 > year:
                if self.check_duplicated_data(self.dividend_eps_path, target_name):
                    #倒數的因此如果已經有重複就不繼續做
                    break

            for i in range(6):
                option1={"SHEET":"股利政策", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利"}
                option1["RANK"] = i
                option1["RPT_TIME"] = year
                url = self.url_choose(option1)
                print('url = {}'.format(url))
                df = self.get_data(url)
                if not df.empty:
                    df_list.append(df)
                else:
                    break
                time.sleep(2)

            if df_list:
                df = pd.concat(df_list, axis=0)
                try:
                    old_df = pd.read_csv('./{}/{}'.format(self.yaer_eps_path, target_name))
                    if self.check_webdata_newer(old_df, df, '現金股利'):
                        df.to_csv('./{}/{}'.format(self.dividend_eps_path, target_name))
                except Exception as e:
                    print("don't have old_df, {}".format(e))

                if self.check_dataframe_valid(df, '現金股利'):
                    df.to_csv('./{}/{}'.format(self.dividend_eps_path, target_name))

        return None
        #         print(self.url_choose(option1))

    def my_choose_data_3(self, year_range=5):
        """
        資料下載3
        EPS 每季的資料
        自動更新如果已有就不下載

        """
        urls = []
        df_dict = {}
        now_year, now_month, now_day, now_day_week = self.get_date()
        for year in range(int(now_year), int(now_year)  - year_range, -1):
            for season in range(4, 0, -1):
                df_list = []
                target_season = "{}".format((year)*10+season)
                target_name = '{}.csv'.format(target_season)
                # if the file exist, don't download again
                if int(now_year) > year:
                    if self.check_duplicated_data(self.senson_eps_path, target_name):
                        #倒數的因此如果已經有重複就不繼續做
                        break
                for i in range(6):

                    option1={"SHEET":"季獲利能力", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利", "SHEET2":"獲利能力 (季增減統計)"}
                    option1["RANK"] = i
                    option1["RPT_TIME"] = target_season
                    url = self.url_choose(option1)
                    df = self.get_data(url)
                    # display(df)
                    if not df.empty:
                        df_list.append(df)
                    else:
                        break
                    time.sleep(2)
                if df_list:
                    df = pd.concat(df_list, axis=0)
                    try:
                        old_df = pd.read_csv('./{}/{}'.format(self.senson_eps_path, target_name))
                        if self.check_webdata_newer(old_df, df, 'EPS(元)'):
                            df.to_csv('./{}/{}'.format(self.senson_eps_path, target_name))
                    except Exception as e:
                        print("don't have old_df, {}".format(e))

                    if self.check_dataframe_valid(df, "EPS(元)"):
                        df.to_csv('./{}/{}'.format(self.senson_eps_path, target_name))
                    else:
                        print('data not vaild')
                        continue

#             df_dict.update({(int(now_year) - year -1):df})

        return True

    def my_choose_data_4(self):
        """
        資料下載4  下載當天的移動均線
        EPS 每季的資料
        不下載 六日的資料
        """
        urls = []
        df_dict = {}
        now_year, now_month, now_day, now_day_week = self.get_date()
        # print(now_day_week)
        days_count = 0
        # now_day
        #     target_date = (datetime.now() - relativedelta(days=days_count)).strftime("%Y%m")
        # files_in_path =[file for file in self.get_csv_in_path(ma_path)]
        df_list = []
        df=""
        # Continue when data is duplicate and
        while 1:
            now_year, now_month, now_day, now_day_week = self.get_date()
            now_day = str(int(now_day)-1)
            today_data = '{}_{}_{}.csv'.format(now_year, now_month, now_day)

            if self.check_duplicated_data(self.ma_path, today_data) or now_day_week in ['0', '6']:
                break

            for i in range(6):
                option1={"SHEET":"移動均線", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利"}
                option1["RANK"] = i
    #             option1["RPT_TIME"] = target_season
                url = self.url_choose(option1)
                df = self.get_data(url)
                if not df.empty:
                    df_list.append(df)
                else:
                    break
                time.sleep(2)

            if df_list:
                years_count = 0
                while 1:
                    target_date = (datetime.now() - relativedelta(years=years_count)).strftime("%Y")
                    try:
                        df_eps = pd.read_csv("./year_eps/{}.csv".format(target_date))
                        break
                    except:
                        print("read error {}".format(target_date))
                        years_count = years_count + 1
                        if(years_count >20):
                            break

                df = pd.concat(df_list, axis=0)
                df.to_csv('{}/{}'.format(self.ma_path, today_data))
            # days_count = days_count + 1
    #             df_dict.update({(int(now_year) - year -1):df})

        return df

    # def my_choose_data_5(self):
    #     """
    #     下載資料5  最新的股利資料
    #     主要需要 殖利率

    #     """
    #     urls = []
    #     file_in_path = self.get_csv_in_path(self.dividend_eps_path)
    #     df_list = []

    #     for i in range(6):
    #         option1={"SHEET":"股利政策", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利"}
    #         option1["RANK"] = i
    #         option1["RPT_TIME"] = "最新資料"
    #         url = self.url_choose(option1)
    #         df = self.get_data(url)

    #         if not df.empty:
    #             df_list.append(df)
    #         else:
    #             break
    #         time.sleep(2)

    #         if df_list:
    #             df = pd.concat(df_list, axis=0)
    #             df.to_csv('./{}/Dividend_DATA_Newest.csv'.format(self.dividend_eps_path))

    def my_choose_data_6(self):
        """
        下載資料6  月營收

        """

        df_list = []
        month_count = 1

        while month_count < 36:
            df_list = []
            target_date = (datetime.now() - relativedelta(months=month_count)).strftime("%Y%m")
            target_name = "{}.csv".format(target_date)
            if month_count > 2:
                if self.check_duplicated_data(self.month_income_path, target_name):
                    # 倒數的因此如果已經有重複就不繼續做
                    break
            month_count += 1
            for i in range(6):
                option1={"SHEET": "營收狀況", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利", "SHEET2":"月營收狀況"}
                option1["RANK"] = i
                option1["RPT_TIME"] = target_date
                url = self.url_choose(option1)
                df = self.get_data(url)
                if not df.empty:
                    df_list.append(df)
                else:
                    break
                time.sleep(2)

            if df_list:
                df = pd.concat(df_list, axis=0)
                try:
                    old_df = pd.read_csv('./{}/{}'.format(self.month_income_path, target_name))
                    if self.check_webdata_newer(old_df, df, '單月營收(億)'):
                        df.to_csv('./{}/{}'.format(self.month_income_path, target_name))
                except Exception as e:
                    print("don't have old_df, {}".format(e))

                df.to_csv('{}/{}'.format(self.month_income_path, target_name))

    def my_choose_data_7(self):
        """
        下載資料7  股東持股分級
        """

        df_list = []

        df_list = []
        target_name = "shareholder_week.csv"

        for i in range(6):
            option1 = {"SHEET": "股東持股分級_週統計", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利", "SHEET2":"持股比例(%)–持股分級高向低累計"}
            option1["RANK"] = i
            option1["RPT_TIME"] = ""
            url = self.url_choose(option1)
            df = self.get_data(url)
            if not df.empty:
                df_list.append(df)
            else:
                break
            time.sleep(2)

        if df_list:
            df = pd.concat(df_list, axis=0)
            print(df_list[0]["持股資料週別"][0])
            df.to_csv('{}/shareholder_week_{}.csv'.format(self.shareholder_week_path, df_list[0]["持股資料週別"][0]))
            df.to_csv('{}/shareholder_week.csv'.format(self.shareholder_week_path))

    def my_choose_data_8(self, weeks=1):
        """
        下載資料7  股東持股分級 各種張數的持股變化
        """
        urls = []
        file_in_path = self.get_csv_in_path(self.shareholder_week_path)
        df_list = []
        df_count = 0
        week_count = 0
        target_file = "{}_{}.csv".format(datetime.now().strftime("%Y"), datetime.now().isocalendar()[1])
        print(file_in_path)
        while (df_count < weeks):
            if target_file in file_in_path:
                break
            for i in range(6):
                option1 = {"SHEET": "股東持股分級_週統計", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利", "SHEET2":"持股人數(人)–依持股分級個別顯示"}
                option1["RANK"] = i
                option1["RPT_TIME"] = ""
                url = self.url_choose(option1)
                df = self.get_data(url)
                if not df.empty:
                    if not self.check_dataframe_valid(df, '成交'):
                        break
                    df_list.append(df)
                    df_count += 1
                else:
                    break
                time.sleep(2)

            if df_list:
                df = pd.concat(df_list, axis=0)
                df.to_csv('{}/{}'.format(self.shareholder_week_path, target_file))
                # df.to_csv('{}/shareholder_month.csv'.format(self.shareholder_week_path))

    def my_choose_data_9(self):
        """
        下載資料9  MACD
        """

        df_list = []
        target_date = (datetime.now()).strftime("%Y%m%d")
        target_name = "{}.csv".format(target_date)
        if self.check_duplicated_data(self.month_income_path, target_name):
            return
        for i in range(6):
            option1 = {"SHEET": "MACD", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利", "SHEET2":"日/週/月"}
            option1["RANK"] = i
            option1["RPT_TIME"] = ""
            url = self.url_choose(option1)
            df = self.get_data(url)
            if not df.empty:
                if not self.check_dataframe_valid(df, '成交'):
                    break
                df_list.append(df)
            else:
                break
            time.sleep(2)

        if df_list:
            df = pd.concat(df_list, axis=0)
            df.to_csv('{}/MACD_{}'.format(self.MACD_path, target_name))

    def my_choose_data_10(self, days=1):

        df_list = []
        days_count = 0
        df_count = 0
        file_in_path = self.get_csv_in_path(self.price_path)
        print("------------")

        while(df_count < days):
            try:
                target_file = "{}.csv".format((datetime.now() - relativedelta(days=days_count)).strftime("%Y_%m_%d"))
                if target_file in file_in_path:
                    break
                for i in range(7):
                    option1 = {"SHEET": "交易狀況", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "成交價 (高→低)@@成交價@@由高→低", "SHEET2":"日" }
                    option1["RANK"] = i
                    option1["RPT_TIME"] = (datetime.now() - relativedelta(days=days_count)).strftime("%Y/%m/%d")
                    url = self.url_choose(option1)
                    df = self.get_data(url)
                    if not df.empty:
                        if not self.check_dataframe_valid(df, '成交'):
                            break
                        df_list.append(df)
                    else:
                        break
                    time.sleep(1)
                # display((df.loc[:, ["成交"]]).T)

                if df_list:
                    df = pd.concat(df_list, axis=0)
                    df.to_csv('{}/{}'.format(self.price_path, target_file))
                    df_count += 1

            except Exception as e:
                print(e)
                pass
            days_count += 1

    def get_stock_price(self, stock_list):
        dict = {}

        try:
            # path = "{}/{}.csv".format(self.price_path, date)
            if self.today_price_tmp.empty:
                df, target_date = self.get_newest_time_df(self.price_path, "{}/{}_{}_{}.csv")
                if not df.empty:
                    self.today_price_tmp = df
        except Exception as e:
            print(e)
            return dict

        if not self.today_price_tmp.empty:
            for stock in stock_list:
                # print(df[df['代號'] == stock]["昨收"].values[0])
                dict.update({stock: self.today_price_tmp[self.today_price_tmp['代號'] == stock]["成交"].values[0]})
            dict.update({"data_time": self.today_price_tmp["股價日期"][0]})
        else:
            dict.update({"data_time": "no data"})

        # print("dict = {}".format(dict))
        return dict

    def test(self, days=5):
        """
        下載資料9  收盤價 開盤 最高 最低
        """
        urls = []
        file_in_path = self.get_csv_in_path(self.shareholder_week_path)
        df_list = []
        days_count = 0
        successful_times = 0
        print("------------")
        while(successful_times < days):
            try:
                target_date = (datetime.now() - relativedelta(days=days_count)).strftime("%Y_%m_%d")
                if self.check_duplicated_data(self.price_path, "{}.csv".format(target_date)):
                    days_count += 1
                    continue
                for i in range(7):
                    option1 = {"SHEET": "交易狀況", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "成交價 (高→低)@@成交價@@由高→低", "SHEET2":"日" }
                    option1["RANK"] = i
                    option1["RPT_TIME"] = (datetime.now() - relativedelta(days=days_count)).strftime("%Y/%m/%d")
                    url = self.url_choose(option1)
                    df = self.get_data(url)
                    if not df.empty:
                        if not self.check_dataframe_valid(df, '成交'):
                            break
                        df_list.append(df)
                    else:
                        break
                    time.sleep(1)
                # display((df.loc[:, ["成交"]]).T)

                if df_list:
                    df = pd.concat(df_list, axis=0)
                    print(target_date)
                    print(days_count)
                    successful_times += 1
                    df.to_csv('{}/{}.csv'.format(self.price_path, target_date))

            except Exception as e:
                print(e)
                pass
            days_count += 1

    def replace_nan_to_other(self, df, replace):
        # Replace all nan to specify value
        df.fillna(replace, inplace=True)

    def data_updater(self):
        # 進行每日資料更新
        # self.my_choose_data_1()
        # self.my_choose_data_2()
        # self.my_choose_data_3()
        # self.my_choose_data_4()
        # self.my_choose_data_5()
        # self.my_choose_data_6()
        # self.my_choose_data_7()
        self.my_choose_data_8()
        # self.my_choose_data_9()
        self.my_choose_data_10()

    def get_stocks_info(self):
        dict = {}
        df, target_date = self.get_newest_time_df(self.price_path, "{}/{}_{}_{}.csv")
        if not df.empty:
            dict = {"stock_name": df["名稱"].tolist(),
                    "stock_number": df["代號"].tolist()
                    }
        return dict

    def get_dividends(self, stock_list, start_date=None, end_date=None):
        """[summary]
        Get dat from start date to end date
        no interval, return all times
        Keyword Arguments:
            start_date {[str]} -- [start date, format(2018)] (default: {None})
            end_date {[type]} -- [end date, format(2019)] (default: {None})
        """
        df_dict = {}
        df_list = []
        file_in_path = [year.replace(".csv", "") for year in self.get_csv_in_path(self.dividend_eps_path)]
        if not start_date:
            start_date = file_in_path[0]
        if not end_date:
            end_date = file_in_path[-1]
        if start_date > end_date:
            return df_dict
        for year in range(int(start_date), int(end_date)+1):
            target_path = "{}/{}.csv".format(self.dividend_eps_path, year)
            df = pd.read_csv(target_path, index_col="名稱")
            self.replace_nan_to_other(df, "")
            for stock in stock_list:
                pd_index = df.index.to_list()
                old_list = []
                if stock in pd_index:
                    data = df.loc[stock]

                    # print("日期 = {}".format(data.get("除息交易日")))
                    if df_dict.get(stock):
                        old_list = df_dict.get(stock)

                    # check data is available
                    dict = {}
                    if data.get("現金股利") != "":
                        dict.update({"除息交易日": "{}{}".format(year, data.get("除息交易日").split("'")[1].replace("/", "")) if data.get('除息交易日') else "",
                                     "現金股利":  data.get("現金股利"),
                                     })
                    if data.get("股票股利") != "":
                        dict.update({"除權交易日": "{}{}".format(year, data.get("除權交易日").split("'")[1].replace("/", "")) if data.get('除權交易日') else "",
                                     "股票股利":  data.get("股票股利"),
                                     })
                    if dict:
                        old_list.append(dict)
                        df_dict.update({stock: old_list})

        return df_dict

if __name__ == "__main__":
    stock = StockClass()
    stock.data_updater()
    # stock_list = ["全國", '英業達']
    # df_list = stock.get_dividends(stock_list)
    # print(df_list)
    # print(df_list.get('2015').index.to_list())
    # pd_index = df_list.get('2015').index.to_list()
    # df_dict = {}
    # for stock in stock_list:
    #     if stock in pd_index:
    #         print(df_list.get('2015').loc[stock]['現金股利'])
    #         df_dict.update(
    #         {
    #             stock: {"股利年份": "{}{}".format(2015, df_list.get('2015').loc[stock]["除息交易日"].split("'")[1].replace("/", "")) if float(df_list.get('2015').loc[stock]['現金股利']) > 0  else "",
    #                     "股息年份": "{}{}".format(2015, df_list.get('2015').loc[stock]["除權交易日"].split("'")[1].replace("/", ""))if float(df_list.get('2015').loc[stock]['股票股利']) > 0 else "",
    #                     "現金股利": df_list.get('2015').loc[stock]["現金股利"],
    #                     "股票股利": df_list.get('2015').loc[stock]["股票股利"]
    #                     }
    #         }
    #         )
    # df = df_list.get('2015').loc[stock_list]['股利發放年度']


    # stock.data_updater()
    # stock.test(3)


    # print(stock.check_duplicated_data('./month_income', "201811.csv"))
    # target_date = (datetime.now() - relativedelta(days=1)).strftime("%Y %m %d %w")
    # print(stock.get_date(days=2, months=2))
    # print("測試")

