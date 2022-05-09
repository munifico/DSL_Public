import os
import time
import win32com.client
from CybosPlus import CybosPlus
from datetime import datetime, timedelta


class DataCollection:
    def __init__(self, stockName, startDay=19000101, endDay=20210101, storePath=None):
        self.StockChart = win32com.client.Dispatch("CpSysDib.StockChart")
        self.CpStockCode = win32com.client.Dispatch("CpUtil.CpStockCode")

        self.stockName = stockName
        self.stockCode = self.CpStockCode.NameToCode(stockName)
        self.startDay = startDay
        self.endDay = endDay

        if not os.path.isdir(storePath): os.mkdir(storePath)
        self.StoreLocation = os.path.join(storePath, '{}.csv')

    def CollectMinute(self, StockName, StockCode, timeperiod=5):
        self.StockChart.SetInputValue(0, StockCode)
        self.StockChart.SetInputValue(1, ord('2'))                  # 개수로 요청
        self.StockChart.SetInputValue(4, 2000)                      # 몇개의 데이터를 수신할 지
        self.StockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])     # 어떤 데이터를 받을 지
        self.StockChart.SetInputValue(6, ord('m'))                  # 차트 종류
        self.StockChart.SetInputValue(7, timeperiod)                # 몇 분봉으로 받을지
        self.StockChart.SetInputValue(9, ord('1'))                  # 수정주가 사용

        self.StockChart.BlockRequest()                              # 데이터 요청
        time.sleep(0.3)

        receive = self.StockChart.GetHeaderValue(3)
        with open(self.StoreLocation.format(StockName + '_' + str(timeperiod) + '분봉'), 'w') as f:
            f.write("StockName,StockCode,Date,Time,Open,High,Low,Close,Volume\n")
            for i in range(receive ):
                t = self.StockChart.GetDataValue(0, i)
                if (self.startDay <= t) and (t <= self.endDay):
                    f.write("{},{},{},{},{},{},{},{},{}\n".format(
                        StockName, StockCode,
                        self.StockChart.GetDataValue(0, i),
                        self.StockChart.GetDataValue(1, i),
                        self.StockChart.GetDataValue(2, i),
                        self.StockChart.GetDataValue(3, i),
                        self.StockChart.GetDataValue(4, i),
                        self.StockChart.GetDataValue(5, i),
                        self.StockChart.GetDataValue(6, i)
                    ))

            finish = False

            while self.StockChart.Continue:
                self.StockChart.BlockRequest() # 데이터 요청
                time.sleep(0.3)
                receive = self.StockChart.GetHeaderValue(3) # 총 수신 개수

                for i in range(receive):
                    t = self.StockChart.GetDataValue(0, i)
                    if (self.startDay <= t) and (t <= self.endDay):
                        f.write("{},{},{},{},{},{},{},{},{}\n".format(
                            StockName, StockCode,
                            self.StockChart.GetDataValue(0, i),
                            self.StockChart.GetDataValue(1, i),
                            self.StockChart.GetDataValue(2, i),
                            self.StockChart.GetDataValue(3, i),
                            self.StockChart.GetDataValue(4, i),
                            self.StockChart.GetDataValue(5, i),
                            self.StockChart.GetDataValue(6, i)))
                    elif t < self.endDay:
                        finish = True
                        break
                if finish: break

    def CollectDay(self, StockName, StockCode):
        self.StockChart.SetInputValue(0, StockCode)
        self.StockChart.SetInputValue(1, ord('1'))  # 기간으로 요청
        self.StockChart.SetInputValue(2, self.endDay)  # 기간으로 요청
        self.StockChart.SetInputValue(3, self.startDay)  # 기간으로 요청
        self.StockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 어떤 데이터를 받을 지
        self.StockChart.SetInputValue(6, ord('D'))  # 차트 종류
        self.StockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        self.StockChart.BlockRequest()
        time.sleep(0.3)

        receive = self.StockChart.GetHeaderValue(3)

        with open(self.StoreLocation.format(StockName), 'w') as f:
            f.write("Date,Open,High,Low,Close,Adj Close,Volume\n")
            for i in range(receive - 1, 0, -1):
                date = str(self.StockChart.GetDataValue(0, i))
                f.write("{},{},{},{},{},{},{}\n".format(
                    date[:4] + "-" + date[4:6] + "-" + date[6:],
                    self.StockChart.GetDataValue(1, i),
                    self.StockChart.GetDataValue(2, i),
                    self.StockChart.GetDataValue(3, i),
                    self.StockChart.GetDataValue(4, i),
                    0,
                    self.StockChart.GetDataValue(5, i)))

    def run(self, collect_type='일봉', period=None):
        if not CybosPlus.CpCybos.IsConnect:
            print("사이보스 혹은 크레온 Plus가 연결되지 않았습니다...")
            return

        if collect_type == '일봉':
            self.CollectDay(self.stockName, self.stockCode)
        elif collect_type == '분봉':
            if period == None: raise Exception("분봉을 수집하기 위해 기간을 설정해야합니다. (ex. 5분봉시 period = 5)")
            else: self.CollectMinute(self.stockName, self.stockCode, period)

if __name__=='__main__':
    """
        store_path  : 데이터를 저장하기 위한 디렉토리 path
        stockName   : 수집하기 위한 종목 이름
        ------------------------------------------------------
        DataCollection class 
        
        init function
        
        stockName       : 종목이름      (type: string, ex. '삼성전자')
        startDay        : 수집 시작 일자 (type: int, ex. 20200101) (조건 : startDay < endDay)
        endDay          : 수집 종료 일자 (type: int, ex. 20200201) (조건 : startDay < endDay)
        StoreLocation   : 데이터 저장 디렉토리 (ex) './data/')
        -------------------------------------------------------
        run function
        
        collect_type    : 수집하고자 하는 봉 종류(일봉, 분봉) (type: string, ex) '일봉')
        period          : collect_type이 분봉인 경우 사용하며 분봉 간격을 의미 (type: int, ex) 5분봉 -> period = 5)
        -------------------------------------------------------
        사용 예시
        
        store_path = './data/'
        stockName = "컴투스"
        DataCollection("삼성전자", 20210101, 20220101, store_path).run('일봉')
    """

    trade_signal = True

    store_path = r'C:\Users\kimsangho\Desktop\shared\data\KOSPI'

    date = int((datetime.now() + timedelta(days=2)).strftime("%Y%m%d"))
    kospi_200 = open(r"C:\Users\kimsangho\Desktop\shared\kospi200.csv", "r")
    for index, stockInfo in enumerate(kospi_200):
        if index == 0: continue
        stockName = stockInfo.rstrip("\n").split(",")[1][1:-1]
        try: DataCollection(stockName, 20120101, date, store_path).run('일봉')
        except: continue

    add_stock = ["KODEX 레버리지", "KODEX 200선물인버스2X", "KODEX 200", "KODEX 인버스"]
    for stockName in add_stock:
        DataCollection(stockName, 20120101, date, store_path).run('일봉')