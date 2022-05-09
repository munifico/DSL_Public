from datetime import datetime
from CybosTrade import CybosTrade
from CybosPrice import CybosPrice


class CybosMainForTrade(CybosTrade):
    def __init__(self, model, accNum):
        super(CybosMainForTrade, self).__init__(accNum=accNum)
        self.model = model
        self.cPrice = CybosPrice()
        self.DictTrade = {0: "2", 1: "1"}
        self.dictTrade = {0: "매수", 1: "매도", 2: "보유"}

    def SIRL_Trade(self):
        #print(self.SIRL_data)
        for _, _, stock1, _, action, _, confidence, _, _ in self.SIRL_data:
            if int(action) == 2: continue
            stock_trade_result = self.ClosePriceOrder(self.DictTrade[int(action)], stock1)

    def HDRL_Trade(self):
        # SIRL model 매매
        for _, _, stock1, stock2, action, stoploss, confidence, hedge_ratio, _ in self.HDRL_data:
            if int(action) == 2: continue

            if stoploss is False:
                if int(action) == 0:
                    self.ClosePriceOrder(self.DictTrade[1], stock1)
                    self.ClosePriceOrder(self.DictTrade[0], stock2)
                elif int(action) == 1:
                    self.ClosePriceOrder(self.DictTrade[0], stock1)
                    self.ClosePriceOrder(self.DictTrade[1], stock2)
            else:
                self.ClosePriceOrder(self.DictTrade[1], stock1)
                self.ClosePriceOrder(self.DictTrade[1], stock2)

    def run(self):
        if self.model == "SIRL":
            self.SIRL_Trade()
        elif self.model == "HDRL":
            self.HDRL_Trade()

if __name__ == "__main__":
    today = datetime.now()

    if today.weekday() <= 4: # 주말이 아닌 경우에만 실행
        SIRL_Trader = CybosMainForTrade("SIRL", '782648241')    # 주 계좌
        SIRL_Trader.run()

        # HDRL_Trader = CybosMainForTrade("HDRL", '782653948') # 위임 계좌1
        # HDRL_Trader.run()
    else: print("오늘은 개장일이 아닙니다!!!")
