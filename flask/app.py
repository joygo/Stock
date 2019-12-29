from flask import Flask, request, render_template, Response, url_for
# from stock import StockClass
from config_parser import ConfigParserFuntion
from pd_functions import StockClass
import json
import os
import subprocess
import shlex
import pandas as pd
from middleware import Middleware
from functions import ROOT_PATH, STOCK_DATA_PATH, CONFIG_PATH, Functions

func = Functions()
# class print_hello(Resource):
#     def get(self):
#         return {
#             'message': 'Hello World'
#         }, 200


# class user (Resource):
#     def get(self):
#         # return render_template('index.html')
#         pass

#     def post(self):
#         print(request.form.post)
#         pass

#     def put(self):
#         pass

#     def delete(self):
#         pass

app = Flask(__name__)
app.config.from_object('config')



@app.route("/", methods=["GET"])
def index():
    return render_template('index.html', user_test="joy")


@app.route("/test", methods=["GET"])
def test():
    print(os.getcwd())
    (ConfigParserFuntion('test').init_dir())
    return render_template('test.html')


@app.route("/api/add_info", methods=["GET", "POST", "DELETE"])
def add_info():
    if request.method == "GET":
        # user = request.json.get('user')
        # print(StockClass().get_stock_info())
        return response_format("200", "0", "", StockClass().get_stocks_info())

        # ConfigParserFuntion(user)
    if request.method == "POST":
        error_code = "0"
        des = ""
        if request.json:
            user = request.json.get('user')
            action = request.json.get('action')
            if action == "buy":
                stock_name = request.json.get('stock_name')
                stock_count = request.json.get('stock_count')
                stock_price = request.json.get('stock_price')
                stock_number = request.json.get('stock_number')
                date = request.json.get('date')
                print(stock_name, stock_count, stock_price, date)
                ConfigParserFuntion(user).add_stock(stock_name, stock_number, int(stock_count), float(stock_price), date)
                print("action = {}".format(action))
            elif action == "sell":
                stock_name = request.json.get('stock_name')
                stock_count = request.json.get('stock_count')
                stock_price = request.json.get('stock_price')
                stock_number = request.json.get('stock_number')
                date = request.json.get('date')
                print(stock_name, stock_count, stock_price, date)
                ret, des = ConfigParserFuntion(user).sell_stock(stock_name, stock_number, int(stock_count), float(stock_price), date)


            elif action == "dividend":
                print("action = {}".format(action))

            # ConfigParserFuntion.
            return response_format("200", error_code, des, "")
    elif request.method == "DELETE":
        if request.json:
            user = request.json.get('user')
            datas = request.json.get('data')
            for data in datas:
                target = data.get('target')
                stock_name = data.get('stock_name')
                date = data.get('date')
                if ConfigParserFuntion(user).del_stock(target, stock_name, date):
                    return response_format("200", "0", "", "")
                else:
                    return response_format("200", "1", "", "")


@app.route("/api/update_db", methods=["GET"])
def update_db():
    if request.method == "GET":
        cmd = "python {}/pd_functions.py".format(os.getcwd()).replace("\\", "/")
        subprocess.Popen(shlex.split(cmd), stdin=None, stdout=None, stderr=None)
        return response_format("200", "0", "", "")

        # StockClass().data_updater()



@app.route("/api/get_info", methods=["GET", "POST"])
def get_info():
    if request.method == "GET":
        user = request.args.get('user')
        start_date = request.args.get('start_date') if request.args.get('start_date') else None
        end_date = request.args.get('end_date') if request.args.get('end_date') else None
        if user:
            return response_format("200", "0", "", ConfigParserFuntion(user).read_user_info(start_date, end_date))
        else:
            return response_format("200", "1", "", "使用者不存在")


@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "GET":
        user = request.args.get('user')
        password = request.args.get('password')
        if user:
            if ConfigParserFuntion(user).user_exists():
                return response_format("200", "0", "", {"user": user})
            else:
                return response_format("200", "1", "使用者不存在", "")
    elif request.method == "POST":
        # register the user
        user = request.json.get("user_name")
        password = request.json.get("password")
        if user and password:
            config_object = ConfigParserFuntion(user)
            if config_object.user_exists():
                return response_format("200", "1", "使用者已存在", "")
            else:
                if config_object.add_account(password):
                    return response_format("200", "0", "", "")
                else:
                    return response_format("200", "1", "註冊失敗", "")
        else:
            return response_format("200", "1", "輸入資料錯誤", "")


@app.route("/user", methods=["GET", "POST"])
def user():
    if request.method == "GET":
        # user = request.args.get('user')
        # start_date = request.args.get('start_date') if request.args.get('start_date') else None
        # end_date = request.args.get('end_date') if request.args.get('end_date') else None
        # if user:
        #     return response_format("200", "0", "", ConfigParserFuntion(user).read_user_info(start_date, end_date))
        # else:
        #     return response_format("200", "1", "", "使用者不存在")
        return render_template('user_info.html')
    elif request.method == "POST":
        # return render_template('index.html', user_test="joy")
        if request.json:
            user = request.json.get('user')
            data = request.json.get('data')
            print(json.dumps(data))
            # start_date = request.json.get('start_date') if request.json.get('start_date') else None
            # end_date = request.json.get('end_date') if request.json.get('end_date') else None
            ConfigParserFuntion(user).set_user_config(data)
        return response_format("200", "0", "", "")
        # return request.values['username']

@app.route("/api/polling", methods=["GET"])
def polling_function():
    if request.method == "GET":
        stock_class = StockClass()
        df, target_date = stock_class.get_newest_time_df(stock_class.price_path, "{}/{}_{}_{}.csv")
        print(target_date)
        data = {"update_db_date":"{}/{}/{}".format(target_date[0], target_date[1], target_date[2])}
        return response_format("200", "0", "", data)



def response_format(status, error_code, des, data):
    """[summary]

    Arguments:
        status {[str]} -- [http response]
        error_code {[str]} -- [error code]
        des {[str]} -- [description]
        data {[str]} -- [return data]

    Returns:
        [json] -- [description]
    """
    res = {"status": status, "error": error_code, "data": data, "des": des}
    return Response(json.dumps(res), mimetype='application/json')


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))


def init_dir():
    if not os.path.isdir(ROOT_PATH):
        os.makedirs(ROOT_PATH)

    if not os.path.isdir(STOCK_DATA_PATH):
        os.makedirs(STOCK_DATA_PATH)

    if not os.path.isdir("{}/{}".format(STOCK_DATA_PATH, "price")):
        os.makedirs("{}/{}".format(STOCK_DATA_PATH, "price"))
        func.set_log("[APP] download newest price for init")
        cmd = "python {}/pd_functions.py".format(os.getcwd()).replace("\\", "/")
        subprocess.Popen(shlex.split(cmd), stdin=None, stdout=None, stderr=None)

    if not os.path.isdir("{}/{}".format(STOCK_DATA_PATH, "shareholders")):
        os.makedirs("{}/{}".format(STOCK_DATA_PATH, "shareholders"))

    if not os.path.isdir(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)




# @app.route("/test")
# def test():
#     return "Hello test!"

if __name__ == "__main__":

    # print(ConfigParserFuntion("joylin").add_account("12345678"))
    # pretty(ConfigParserFuntion("joylin").read_user_info())
    # app.config.from_object('config.InitializedConfig')
    init_dir()
    app.wsgi_app = Middleware(app.wsgi_app)
    app.run(debug=True)
