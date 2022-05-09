class CybosMemoryForRealTime:
    def __init__(self):
        self.StockCode = None
        self.name = None
        self.Time = None
        self.Volume = 0

        self.ATAskPrice = [0 for _ in range(5)]
        self.ATBidPrice = [0 for _ in range(5)]
        self.ATAskPriceAmount = [0 for _ in range(5)]
        self.ATBidPriceAmount = [0 for _ in range(5)]
        self.ATTotalAskPriceAmount = 0
        self.ATTotalBidPriceAmount = 0

        self.StockAskPrice = [0 for _ in range(10)]
        self.StockBidPrice = [0 for _ in range(10)]
        self.StockAskPriceAmount = [0 for _ in range(10)]
        self.StockBidPriceAmount = [0 for _ in range(10)]
        self.StockTotalAskPriceAmount = 0
        self.StockTotalBidPriceAmount = 0

        self.exFlag = None
        self.CurrPrice = 0
        self.DiffPrice = 0
        self.TempVolume = 0
