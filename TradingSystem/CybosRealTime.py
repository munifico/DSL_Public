import time
from datetime import datetime
from CybosEvent import CybosPublish
from CybosMemory import CybosMemoryForRealTime


class CpPBStockCur(CybosPublish):
    def __init__(self):
        super().__init__("StockCur", "DsCbo1.StockCur")


class CpPBStockUniJpBid(CybosPublish):
    def __init__(self):
        super().__init__("StockUniJpBid", "CpSysDib.StockUniJpBid")


class CpPBStockJpBid(CybosPublish):
    def __init__(self):
        super().__init__("StockJpBid", "Dscbo1.StockJpBid")


class RealTimeMain:
    def __init__(self, object):
        if object == "StockCur":
            self.obj = CpPBStockCur()
        elif object == "StockUniJpBid":
            self.obj = CpPBStockUniJpBid()
        elif object == "StockJpBid":
            self.obj = CpPBStockJpBid()
        else: self.obj = None

        self.memory = CybosMemoryForRealTime()

    def run(self, code):
        self.obj.Unsubscribe()
        self.obj.Subscribe(code, self.memory)

        time.sleep(200)

        self.obj.Unsubscribe()

    def SelectAskBidPrice(self, BuySellCode):
        if BuySellCode == 2:  # 매수
            return self.memory.StockAskPrice[-1]
        elif BuySellCode == 1:  # 매도
            return self.memory.StockBidPrice[-1]

if __name__ == '__main__':
    a = RealTimeMain("StockUniJpBid")
    a.run("KODEX 200")
    print(a.SelectAskBidPrice(1), a.SelectAskBidPrice(2))
