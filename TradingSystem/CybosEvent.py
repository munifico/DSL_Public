import win32com.client
from pywinauto import application
from CybosPlus import CybosPlus as Cybos


class CybosEvent:
    def set_params(self, client, name, memory):
        self.client = client  # CP 실시간 통신 object
        self.name = name  # 서비스가 다른 이벤트를 구분하기 위한 이름
        self.memory = memory

    # PLUS 로 부터 실제로 시세를 수신 받는 이벤트 핸들러
    def OnReceived(self):
        if self.name == "StockCur":
            # 현재가 체결 데이터 실시간 업데이트
            self.memory.exFlag = self.client.GetHeaderValue(19)  # 예상체결 플래그
            code = self.client.GetHeaderValue(0)
            diff = self.client.GetHeaderValue(2)
            cur = self.client.GetHeaderValue(13)  # 현재가
            vol = self.client.GetHeaderValue(9)  # 거래량
            timess = self.client.GetHeaderValue(18)

        elif self.name == "StockUniJpBid":
            self.memory.StockCode = self.client.GetHeaderValue(0)
            self.memory.Time = self.client.GetHeaderValue(1)
            self.memory.Volume = self.client.GetHeaderValue(2)

            BidIndex = [3, 7, 11, 15, 19]
            for i in range(5):
                self.memory.ATBidPrice[i] = self.client.GetHeaderValue(BidIndex[i])
                self.memory.ATAskPrice[i] = self.client.GetHeaderValue(BidIndex[i] + 1)
                self.memory.ATBidPriceAmount[i] = self.client.GetHeaderValue(BidIndex[i] + 2)
                self.memory.ATAskPriceAmount[i] = self.client.GetHeaderValue(BidIndex[i] + 3)

            self.memory.ATTotalBidPriceAmount = self.client.GetHeaderValue(23)
            self.memory.ATTotalAskPriceAmount = self.client.GetHeaderValue(24)

            print(self.memory.Time)
            print(self.memory.ATBidPrice, self.memory.ATBidPriceAmount)
            print(self.memory.ATAskPrice, self.memory.ATAskPriceAmount)
            print()

        elif self.name == "StockJpBid":
            self.memory.StockCode = self.client.GetHeaderValue(0)
            self.memory.Time = self.client.GetHeaderValue(1)
            self.memory.Volume = self.client.GetHeaderValue(2)

            BidIndex = [3, 7, 11, 15, 19, 27, 31, 35, 39, 43]
            for i in range(10):
                self.memory.StockBidPrice[i] = self.client.GetHeaderValue(BidIndex[i])
                self.memory.StockAskPrice[i] = self.client.GetHeaderValue(BidIndex[i] + 1)
                self.memory.StockBidPriceAmount[i] = self.client.GetHeaderValue(BidIndex[i] + 2)
                self.memory.StockAskPriceAmount[i] = self.client.GetHeaderValue(BidIndex[i] + 3)

            self.memory.StockTotalBidPriceAmount = self.client.GetHeaderValue(23)
            self.memory.StockTotalAskPriceAmount = self.client.GetHeaderValue(24)

            print(self.memory.Time)
            print(self.memory.StockBidPrice, self.memory.StockBidPriceAmount)
            print(self.memory.StockAskPrice, self.memory.StockAskPriceAmount)
            print()


class CybosPublish:
    def __init__(self, name, serviceID):
        self.name = name
        self.obj = win32com.client.Dispatch(serviceID)
        self.bIsSB = False

    def Subscribe(self, StockName, memory):
        if self.bIsSB:
            self.Unsubscribe()

        self.obj.SetInputValue(0, Cybos.CpStockCode.NameToCode(StockName))

        handler = win32com.client.WithEvents(self.obj, CybosEvent)
        handler.set_params(self.obj, self.name, memory)
        self.obj.Subscribe()
        self.bIsSB = True

    def Unsubscribe(self):
        if self.bIsSB:
            self.obj.Unsubscribe()
        self.bIsSB = False
