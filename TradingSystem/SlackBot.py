import os
import time
import requests
from glob import glob
from datetime import datetime
from CybosPrice import CybosPrice
from CybosTrade import CybosTrade
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

executers = {
    'default' : ThreadPoolExecutor(90),
    'processpool' : ProcessPoolExecutor(20)}
sched = BackgroundScheduler(executers=executers)

class SlackBot:
    def __init__(self):
        self.base_log_path = r"C:\Users\kimsangho\Desktop\shared\log"
        self.kospi200_signal_file = os.path.join(r"C:\Users\kimsangho\Desktop\shared\etf_signal.csv")
        self.init_balance = {"SIRL": 1000000, "HDRL": 1000000}

    def TodayStockList(self):
        StockList = []
        trade_signal_data = open(r"C:\Users\kimsangho\Desktop\shared\trade_signal.csv", 'r')
        trade_signal_columns = trade_signal_data.readline()
        for data in trade_signal_data:
            data = data.rstrip("\n")
            if data.split(",")[0] != datetime.now().strftime("%Y-%m-%d"): continue
            StockList.append(data.split(",")[2])
            if data.split(",")[3] != "None": StockList.append(data.split(",")[3])
        return list(set(StockList))

    def post_message(self, token, channel, text):
        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers={"Authorization": "Bearer " + token},
                                 data={"channel": channel, "text": text})
        print(response)

    def DataPreprocessing(self, data):
        pass

    def CreateMessage(self, model_list):
        text = "{} 매매 결과\n".format(datetime.now().strftime("%Y/%m/%d"))
        for model in model_list:
            model_trade_result = glob(
                os.path.join(self.base_log_path, "{}_{}*".format(model, datetime.now().strftime("%Y%m%d"))))
            if len(model_trade_result) == 0: continue

            text += "=============================== {}-Trader ===============================\n".format(model)
            trade_log = open(model_trade_result[0])
            column = trade_log.readline()
            for i in trade_log:
                # log_data columns: 계좌번호, 종목이름, 주문호가, 주문수량, 주문단가, 체결수량, 체결단가, 체결잔고수량, 손익단가, 종가, 매매구분
                log_data = i.rstrip("\n").split(",")
                stock_profit = (int(log_data[9]) - int(log_data[8])) * 100 / int(log_data[9])  # 종목 수익률 계산
                if log_data[10] == "보유":
                    text += "{}을(를) 보유 -> 종가: {:,}원, 종목 수익률: {:.3f}%\n".format(log_data[1], int(log_data[9]), stock_profit)
                else:
                    if int(log_data[6]) == 0: slippage = 0
                    else: slippage = (int(log_data[9]) - int(log_data[6])) * 100 / int(log_data[6])  # 슬리피지 계산
                    #if int(log_data[3]) != int(log_data[5]): continue

                    if log_data[10] == "매도": stock_profit = 0
                    text += "{}을(를) {}로 {:,}원에 {}주 {} -> 종가: {:,}원, 슬리피지: {:.2f}%, 종목 수익률: {:.3f}%\n".format(
                        log_data[1], log_data[2], int(log_data[6]), log_data[5], log_data[10],
                        int(log_data[9]), slippage, stock_profit)
            text += "-----------------------------------------------------------------" \
                    "-----------------------------------------------\n"

            total_balance = model_trade_result[0].split("_")[-1].split(".")[0]
            total_profit = (int(total_balance) - self.init_balance[model]) * 100 / self.init_balance[model]
            text += "{}-Trader 종합 잔고: {:,}, 종합 수익률: {:.3f}%\n".format(model, int(total_balance), total_profit)
            text += "========================================================================\n\n\n\n\n\n"

        return text

    def SendMessageToSlack(self, workspace, model_list):
        test_Token = "xoxb-3199102464134-3229520889024-ebonsfUhg2BuO8OYww6BKq0K"
        DSL_Token = "xoxb-2887210581458-3218431013681-8H9SAjTJlTVuPqiAFYeuZ7Kq"
        Home_Toekn = "xoxb-3225249208097-3236466448112-IQ7XIi1qSRsePS7MoB4jDLCe"

        text = self.CreateMessage(model_list)

        if workspace == "test":
            self.post_message(test_Token, "#주식", text)
        elif workspace == "DSL":
            self.post_message(DSL_Token, "#매매기록", text)
        elif workspace == "Home":
            self.post_message(Home_Toekn, "#stock", text)

        print("Message transfer completed to ", workspace)

if __name__=="__main__":
    today = datetime.now()
    print(today)
    if today.weekday() <= 4:  # 주말이 아닌 경우에만 실행
        slack = SlackBot()

        StockClosingPrice = CybosPrice().TodayClosePrice(slack.TodayStockList())
        CybosTrade("782648241").TradeHistory("SIRL", StockClosingPrice)
        try: CybosTrade("782653948").TradeHistory("HDRL", StockClosingPrice)
        except: pass

        modelForSending = ["SIRL"]

        time.sleep(5)
        slack.SendMessageToSlack('test', modelForSending)
        #slack.SendMessageToSlack("DSL")
        slack.SendMessageToSlack("Home", modelForSending)
    else:
        print("Today is not open!!!")

# @sched.scheduled_job('cron', hour='18', minute='50', id='SlackBot')
# def job():
#     today = datetime.now()
#     if today.weekday() <= 4:  # 주말이 아닌 경우에만 실행
#         slack = SlackBot()
#
#         StockClosingPrice = CybosPrice().TodayClosePrice(slack.TodayStockList())
#         CybosTrade("782648241").TradeHistory("SIRL", StockClosingPrice)
#         try: CybosTrade("782653948").TradeHistory("HDRL", StockClosingPrice)
#         except: pass
#
#         modelForSending = ["SIRL"]
#
#         time.sleep(5)
#         slack.SendMessageToSlack('test', modelForSending)
#         # slack.SendMessageToSlack("DSL")
#         slack.SendMessageToSlack("Home", modelForSending)
#     else:
#         print("Today is not open!!!")
#
# while True:
#     time.sleep(20)