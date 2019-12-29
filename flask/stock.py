
# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pandas
import pandas as pd
import numpy as np
import os
import time
from configparser import ConfigParser
import requests
from bs4 import BeautifulSoup
import urllib

class StockClass():
    """[summary]

    Returns:
        [type] -- [description]
    """

    def __init__(self):
        self.yaer_eps_path = "G:/google_sync/mobile/stock/year_eps"
        self.dividend_eps_path = "G:/google_sync/mobile/stock/year_dividend"
        self.senson_eps_path = "season_eps"
        self.ma_path = "G:/google_sync/mobile/stock/ma"
        self.net_buy_path = "G:/google_sync/mobile/stock/Net_Buy"
        self.month_income_path = "G:/google_sync/mobile/stock/month_income"
        self.shareholder_week_path = "G:/google_sync/mobile/stock/shareholder_week"
        self.MACD_path = "G:/google_sync/mobile/stock/MACD"
        self.summary_path = "G:/google_sync/mobile/stock/summary"
        self.price_path = "G:/google_sync/mobile/stock/price"
        self.goodinfo_url = 'https://goodinfo.tw/StockInfo/StockList.asp?'

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
        files = os.listdir(path)
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
                    old_df = pd.read_csv('{}/{}'.format(self.yaer_eps_path, target_name))
                    if self.check_webdata_newer(old_df, df, 'EPS(元)'):
                        df.to_csv('{}/{}'.format(self.yaer_eps_path, target_name))
                except Exception as e:
                    print("don't have old_df, {}".format(e))

                if self.check_dataframe_valid(df, 'EPS(元)'):
                    df.to_csv('{}/{}'.format(self.yaer_eps_path, target_name))

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
                    old_df = pd.read_csv('{}/{}'.format(self.yaer_eps_path, target_name))
                    if self.check_webdata_newer(old_df, df, '現金股利'):
                        df.to_csv('{}/{}'.format(self.dividend_eps_path, target_name))
                except Exception as e:
                    print("don't have old_df, {}".format(e))

                if self.check_dataframe_valid(df, '現金股利'):
                    df.to_csv('{}/{}'.format(self.dividend_eps_path, target_name))

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
                        old_df = pd.read_csv('{}/{}'.format(self.senson_eps_path, target_name))
                        if self.check_webdata_newer(old_df, df, 'EPS(元)'):
                            df.to_csv('{}/{}'.format(self.senson_eps_path, target_name))
                    except Exception as e:
                        print("don't have old_df, {}".format(e))

                    if self.check_dataframe_valid(df, "EPS(元)"):
                        df.to_csv('{}/{}'.format(self.senson_eps_path, target_name))
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
                        df_eps = pd.read_csv("year_eps/{}.csv".format(target_date))
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
    #             df.to_csv('{}/Dividend_DATA_Newest.csv'.format(self.dividend_eps_path))

    def my_choose_data_6(self):
        """
        下載資料6  月營收

        """
        urls = []
        file_in_path = self.get_csv_in_path(self.month_income_path)
        df_list = []
        month_count = 1

        while month_count < 36:
            df_list = []
            target_date = (datetime.now() - relativedelta(months=month_count)).strftime("%Y%m")
            target_name = "{}.csv".format(target_date)
            if month_count > 2:
                if self.check_duplicated_data(self.month_income_path, target_name):
                    #倒數的因此如果已經有重複就不繼續做
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
                    old_df = pd.read_csv('{}/{}'.format(self.month_income_path, target_name))
                    if self.check_webdata_newer(old_df, df, '單月營收(億)'):
                        df.to_csv('{}/{}'.format(self.month_income_path, target_name))
                except Exception as e:
                    print("don't have old_df, {}".format(e))

                df.to_csv('{}/{}'.format(self.month_income_path, target_name))

    def my_choose_data_7(self):
        """
        下載資料7  股東持股分級
        """
        urls = []
        file_in_path = self.get_csv_in_path(self.shareholder_week_path)
        df_list = []

        df_list = []
        target_name = "shareholder_week.csv"

        for i in range(6):
            option1={"SHEET": "股東持股分級_週統計", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利", "SHEET2":"持股比例(%)–持股分級高向低累計"}
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

    def my_choose_data_8(self):
        """
        下載資料7  股東持股分級
        """
        urls = []
        file_in_path = self.get_csv_in_path(self.shareholder_week_path)
        df_list = []

        df_list = []
        target_name = "shareholder_week.csv"

        for i in range(6):
            option1={"SHEET": "股東持股分級_月統計", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利", "SHEET2":"持股比例(%)–持股分級高向低累計"}
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
            df.to_csv('{}/shareholder_month_{}.csv'.format(self.shareholder_week_path, df_list[0]["持股資料月份"][0]))
            df.to_csv('{}/shareholder_month.csv'.format(self.shareholder_week_path))


    def my_choose_data_9(self):
        """
        下載資料9  MACD
        """
        urls = []
        file_in_path = self.get_csv_in_path(self.shareholder_week_path)
        df_list = []

        df_list = []
        target_date = (datetime.now()).strftime("%Y%m%d")
        target_name = "{}.csv".format(target_date)
        if self.check_duplicated_data(self.month_income_path, target_name):
            return
        for i in range(6):
            option1={"SHEET": "MACD", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "股票股利", "SHEET2":"日/週/月"}
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
            df.to_csv('{}/MACD_{}'.format(self.MACD_path, target_name))

    def my_choose_data_10(self, days=1):

        urls = []
        file_in_path = self.get_csv_in_path(self.shareholder_week_path)
        df_list = []
        days_count = 0
        print("------------")
        while(len(df_list)<days):
            try:
                target_date = (datetime.now() - relativedelta(days=days_count)).strftime("%Y_%m_%d")
                for i in range(7):
                    option1={"SHEET": "交易狀況", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "成交價 (高→低)@@成交價@@由高→低", "SHEET2":"日" }
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
                    df.to_csv('{}/{}.csv'.format(self.price_path, target_date))

            except Exception as e:
                print(e)
                pass
            days_count += 1

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
                    option1={"SHEET": "交易狀況", "MARKET_CAT": "熱門排行", "INDUSTRY_CAT": "成交價 (高→低)@@成交價@@由高→低", "SHEET2":"日" }
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
                    df_list=[]
                    successful_times += 1
                    df.to_csv('{}/{}.csv'.format(self.price_path, target_date))

            except Exception as e:
                print(e)
                pass
            days_count += 1



    def data_updater(self):
        #進行每日資料更新
        # self.my_choose_data_1()
        # self.my_choose_data_2()
        # self.my_choose_data_3()
        # self.my_choose_data_4()
        # self.my_choose_data_5()
        # self.my_choose_data_6()
        # self.my_choose_data_7()
        # self.my_choose_data_8()
        # self.my_choose_data_9()
        self.my_choose_data_10()

if __name__ == "__main__":
    stock = StockClass()

    stock.data_updater()
    # stock.test(3)


    # print(stock.check_duplicated_data('./month_income', "201811.csv"))
    # target_date = (datetime.now() - relativedelta(days=1)).strftime("%Y %m %d %w")
    # print(stock.get_date(days=2, months=2))
    # print("測試")

