import os
from datetime import datetime, timedelta
from CybosPlus import CybosPlus as Cybos

class CybosPrice:
    def __init__(self):
        self.StockCodeInfo = []
        self.StockNameInfo = []
        self.CurrPriceInfo = []
        self.StartPriceInfo = []
        self.SellQuoteInfo = []
        self.BuyQuoteInfo = []
        self.PrevClosingPriceInfo = []

    def PriceInfo(self, StockNameList):
        self.reset()

        StockCodeList = [Cybos.CpStockCode.NameToCode(name) for name in StockNameList]
        Cybos.StockMst2.SetInputValue(0, ",".join(StockCodeList))
        Cybos.StockMst2.BlockRequest()

        for i in range(Cybos.StockMst2.GetHeaderValue(0)):
            self.StockCodeInfo.append(Cybos.StockMst2.GetDataValue(0, i))          # 종목 코드
            self.StockNameInfo.append(Cybos.StockMst2.GetDataValue(1, i))          # 종목 이름
            self.CurrPriceInfo.append(Cybos.StockMst2.GetDataValue(3, i))          # 현재가
            self.StartPriceInfo.append(Cybos.StockMst2.GetDataValue(6, i))         # 시가
            self.SellQuoteInfo.append(Cybos.StockMst2.GetDataValue(9, i))          # 매도 호가
            self.BuyQuoteInfo.append(Cybos.StockMst2.GetDataValue(10, i))          # 매수 호가
            self.PrevClosingPriceInfo.append(Cybos.StockMst2.GetDataValue(19, i))  # 전일 종가

        return self.StockCodeInfo, self.StockNameInfo, self.CurrPriceInfo, self.StartPriceInfo, self.PrevClosingPriceInfo

    def TodayClosePrice(self, stockNameList):
        today = datetime.now()

        ClosePrice = {}
        for stockName in stockNameList:
            Cybos.StockChart.SetInputValue(0, Cybos.CpStockCode.NameToCode(stockName))
            Cybos.StockChart.SetInputValue(1, ord('1'))  # 기간으로 요청
            Cybos.StockChart.SetInputValue(2, int(today.strftime("%Y%m%d")))  # 기간으로 요청
            Cybos.StockChart.SetInputValue(3, int(today.strftime("%Y%m%d")))  # 기간으로 요청
            Cybos.StockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 어떤 데이터를 받을 지
            Cybos.StockChart.SetInputValue(6, ord('D'))  # 차트 종류
            Cybos.StockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

            Cybos.StockChart.BlockRequest()

            date = Cybos.StockChart.GetDataValue(0, 0)
            open = Cybos.StockChart.GetDataValue(1, 0)
            high = Cybos.StockChart.GetDataValue(2, 0)
            low = Cybos.StockChart.GetDataValue(3, 0)
            close = Cybos.StockChart.GetDataValue(4, 0)
            volume = Cybos.StockChart.GetDataValue(5, 0)
            ClosePrice[stockName] = [date, open, high, low, close, volume]

        return ClosePrice


    def reset(self):
        self.StockCodeInfo = []
        self.CurrPriceInfo = []
        self.StartPriceInfo = []
        self.SellQuoteInfo = []
        self.BuyQuoteInfo = []
        self.PrevClosingPriceInfo = []

    def StreamStockPrice(self):
        pass