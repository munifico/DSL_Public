from datetime import datetime, timedelta
from CybosPlus import CybosPlus as Cybos


class CybosTrade:
    def __init__(self, accNum):
        self.TradingInit()
        self.account = Cybos.CpTdUtil.AccountNumber     # 계좌 번호 튜플
        try: self.acc = self.account.index(accNum)
        except: raise Exception("해당 계좌 번호가 존재하지 않습니다. 다시 확인해주세요!!")

        self.acc_flag = Cybos.CpTdUtil.GoodsList(self.account[self.acc], 1)  # 상품 구분

        self.SIRL_data, self.HDRL_data = self.TradeSignalInfo()  # 매매 신호

        self.TotalTradeStockNum = len(self.SIRL_data)
        print("TotalTradeStockNum: ", self.TotalTradeStockNum)

        self.code_6033 = {'Y': "신용융자/유통융자", 'D': "신용대주/유통대주", 'B': "담보대출", 'M': "매입담보대출",
                          'P': "플러스론대출", 'I': "자기융자/유통융자", " ": " "}

        # 장부가    : (매수 금액 + 수수료(0.015%)) / 수량
        # 손익 단가 : {(장부가 * 수량) + (매도 수수료(0.015%) + 제세금(0.25%))} / 수량
        # 수익률    : (현재가 - 손익단가) / 손익단가 * 100

    def TradeSignalInfo(self):
        SIRL_data = []; HDRL_data = []
        trade_signal_data = open(r"C:\Users\kimsangho\Desktop\shared\trade_signal.csv", 'r')
        for data in trade_signal_data:
            data = data.rstrip("\n")
            if data.split(",")[0] != datetime.now().strftime("%Y-%m-%d"): continue
            if data.split(",")[1] == "SIRL": SIRL_data.append(data.split(","))
            elif data.split(",")[1] == "HDRL": HDRL_data.append(data.split(","))
        return SIRL_data, HDRL_data

    def TradingInit(self):
        return Cybos.CpTdUtil.TradeInit(0) # 계좌 초기화

    def DetermineTradingVolume(self, BuySellCode, StockName, Volume=0):
        TotalBalance, *_, AmountAvailableSell, TotalBuyPrice = self.TotalAccountBalance()

        data = open(r"C:\Users\kimsangho\Desktop\shared\data\KOSPI\{}.csv".format(StockName), "r")
        data = [i.rstrip("\n").split(",") for i in data][-1][-3]

        Volume = 3 if int(data) < 30000 else 2 if int(data) < 60000 else 1

        if BuySellCode == '2':  # 매수인 경우
            if StockName not in AmountAvailableSell.keys():
                Volume = 3 if int(data) < 30000 else 2 if int(data) < 60000 else 1
            else:
                if (TotalBalance / self.TotalTradeStockNum) < TotalBuyPrice[StockName]: Volume = 0
                else:
                    diff = (TotalBalance / self.TotalTradeStockNum) - TotalBuyPrice[StockName]
                    Volume = min(int(diff // (TotalBuyPrice[StockName] / AmountAvailableSell[StockName])), Volume)
        elif BuySellCode == '1':  # 매도인 경우
            if StockName not in AmountAvailableSell.keys(): Volume = 0
            else: Volume = min(AmountAvailableSell[StockName], 3 if int(data) < 30000 else 2 if int(data) < 60000 else 1)
        return Volume

    def BuySellOrder(self, BuySellCode, StockName, Volume, Price=None, Quotes='03'):
        Cybos.CpTd0311.SetInputValue(0, str(BuySellCode))                           # 1: 매도, 2: 매수
        Cybos.CpTd0311.SetInputValue(1, self.account[self.acc])                     # 계좌 번호
        Cybos.CpTd0311.SetInputValue(2, self.acc_flag[0])                           # 상품 구분
        Cybos.CpTd0311.SetInputValue(3, Cybos.CpStockCode.NameToCode(StockName))    # 종목 코드
        Cybos.CpTd0311.SetInputValue(4, Volume)                                     # 주문 수량
        if Quotes != "03": Cybos.CpTd0311.SetInputValue(5, Price)                   # 주문 가격
        Cybos.CpTd0311.SetInputValue(7, "0")                                        # 0: 기본, 1: IOC, 2: FOK
        Cybos.CpTd0311.SetInputValue(8, Quotes)                                     # 주문 호가 구분 코드: 01(보통), 03(시장가), 05(조건부 시장가)
                                                                                    #                   12(최유리 지정가), 13(최우선 지정가)
        Cybos.CpTd0311.BlockRequest()

        # 0: (string)주문종류코드, 1: (string)계좌정보, 2: (string)상품관리구분코드, 3: (string)종목코드
        # 4: (long)주문수량, 5: (long)주문단가, 8: (long)주문번호, 9: (string)계좌명, 10: (string)종목명
        # 12: (string)주문조건구분코드
        result_info = [1, 3, 4, 5, 8, 9, 10]
        return result_info, {str(i): Cybos.CpTd0311.GetHeaderValue(i) for i in result_info}

    def ClosePriceOrder(self, BuySellCode, StockName):
        Volume = self.DetermineTradingVolume(BuySellCode, StockName)
        print(BuySellCode, StockName, Volume)

        Cybos.CpTd0322.SetInputValue(0, str(BuySellCode))                           # 1: 매도, 2: 매수
        Cybos.CpTd0322.SetInputValue(1, self.account[self.acc])                     # 계좌 번호
        Cybos.CpTd0322.SetInputValue(2, self.acc_flag[0])                           # 상품 구분
        Cybos.CpTd0322.SetInputValue(3, Cybos.CpStockCode.NameToCode(StockName))    # 종목 코드
        Cybos.CpTd0322.SetInputValue(4, Volume)                                     # 주문 수량

        Cybos.CpTd0322.BlockRequest()

        return [Cybos.CpTd0322.GetHeaderValue(i) for i in range(8)]

    def ClosePriceCancelOrder(self, OrderNum, StockName, CancelVolume=0):
        # CpTd0326
        Cybos.CpTd0326.SetInputValue(1, OrderNum)
        Cybos.CpTd0322.SetInputValue(2, self.account[self.acc])
        Cybos.CpTd0326.SetInputValue(3, self.acc_flag[0])
        Cybos.CpTd0326.SetInputValue(4, Cybos.CpStockCode.NameToCode(StockName))
        Cybos.CpTd0326.SetInputValue(5, CancelVolume)

        Cybos.CpTd0326.BlockRequest()

        return [Cybos.CpTd0326.GetHeaderValue(i) for i in range(1, 9)]

    def AfterHoursTrading(self, BuySellCode, StockName, Price):
        Volume = self.DetermineTradingVolume(BuySellCode, StockName)

        Cybos.CpTd0386.SetInputValue(0, str(BuySellCode))
        Cybos.CpTd0386.SetInputValue(1, self.account[self.acc])
        Cybos.CpTd0386.SetInputValue(2, self.acc_flag[0])
        Cybos.CpTd0386.SetInputValue(3, Cybos.CpStockCode.NameToCode(StockName))
        Cybos.CpTd0386.SetInputValue(4, Volume)
        Cybos.CpTd0386.SetInputValue(5, Price)

        Cybos.CpTd0386.BlockRequest()

        return [Cybos.CpTd0386.GetHeaderValue(i) for i in range(9)]

    def AfterHourCancelTrading(self, OrderNum, StockName, Volume):
        Cybos.CpTd0387.SetInputValue(1, OrderNum)
        Cybos.CpTd0387.SetInputValue(2, self.account[self.acc])
        Cybos.CpTd0387.SetInputValue(3, self.acc_flag[0])
        Cybos.CpTd0387.SetInputValue(4, Cybos.CpStockCode.NameToCode(StockName))
        Cybos.CpTd0387.SetInputValue(5, Volume)

        Cybos.CpTd0387.BlockRequest()

        return [Cybos.CpTd0387.GetHeaderValue(i) for i in range(1, 9)]

    def AfterHourModifyTrading(self, OrderNum, StockName, Volume, Price):
        Cybos.CpTd0389.SetInputValue(1, OrderNum)
        Cybos.CpTd0389.SetInputValue(2, self.account[self.acc])
        Cybos.CpTd0389.SetInputValue(3, self.acc_flag[0])
        Cybos.CpTd0389.SetInputValue(4, Cybos.CpStockCode.NameToCode(StockName))
        Cybos.CpTd0389.SetInputValue(5, Volume)
        Cybos.CpTd0389.SetInputValue(6, Price)

        Cybos.CpTd0389.BlockRequest()

        return [Cybos.CpTd0389.GetHeaderValue(i) for i in range(1, 9)]

    def TodayTradingProfitLoss(self):
        Cybos.CpTd6032.SetInputValue(0, self.account[self.acc])
        Cybos.CpTd6032.SetInputValue(1, self.acc_flag[0])

        Cybos.CpTd6032.BlockRequest()

        with open(r"C:\Users\kimsangho\Desktop\shared\log\TodayTradingProfitLoss\{}_{}.csv".format(
                datetime.now().strftime("%Y%m%d"), self.account[self.acc]), "w") as f:
            f.write("종목명,신용일자,전일잔고,금일매수수량,금일매도수량,금일잔고,평균매입단가,평균매도단가,현재가,잔량평가손익,매도실현손익,수익률\n")
            for i in range(Cybos.CpTd6032.GetHeaderValue(0)):
                StockName = Cybos.CpTd6032.GetDataValue(0, i)
                Credit = Cybos.CpTd6032.GetDataValue(1, i)
                PrevBalance = Cybos.CpTd6032.GetDataValue(2, i)
                TodayBuyAmount = Cybos.CpTd6032.GetDataValue(3, i)
                TodaySellAmount = Cybos.CpTd6032.GetDataValue(4, i)
                TodayBalance = Cybos.CpTd6032.GetDataValue(5, i)
                AvgBuyPrice = Cybos.CpTd6032.GetDataValue(6, i)
                AvgSellPrice = Cybos.CpTd6032.GetDataValue(7, i)
                CurrPrice = Cybos.CpTd6032.GetDataValue(8, i)
                RestEvalProfit = Cybos.CpTd6032.GetDataValue(9, i)
                TakeSellProfit = (int(AvgSellPrice) - int(AvgBuyPrice)) * int(TodaySellAmount)
                RateOfReturn = Cybos.CpTd6032.GetDataValue(11, i)

                f.write("{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                    StockName, Credit, PrevBalance, TodayBuyAmount, TodaySellAmount, TodayBalance, AvgBuyPrice,
                    AvgSellPrice, CurrPrice, RestEvalProfit, TakeSellProfit, RateOfReturn))

    def TotalAccountBalance(self):
        Cybos.CpTd6033.SetInputValue(0, self.account[self.acc])             # 계좌 번호
        Cybos.CpTd6033.SetInputValue(1, self.acc_flag[0])                   # 상품 구분
        Cybos.CpTd6033.BlockRequest()

        TotalBalance = Cybos.CpTd6033.GetHeaderValue(3)
        AveragePrice = {Cybos.CpTd6033.GetDataValue(0, i): Cybos.CpTd6033.GetDataValue(18, i) for i in
                        range(Cybos.CpTd6033.GetHeaderValue(7))}
        TotalAmount = {Cybos.CpTd6033.GetDataValue(0, i): Cybos.CpTd6033.GetDataValue(7, i) for i in
                       range(Cybos.CpTd6033.GetHeaderValue(7))}
        AmountAvailableSell = {Cybos.CpTd6033.GetDataValue(0, i): Cybos.CpTd6033.GetDataValue(15, i) for i in
                               range(Cybos.CpTd6033.GetHeaderValue(7))}
        # 총 매입 금액
        TotalBuyPrice = {
            Cybos.CpTd6033.GetDataValue(0, i): Cybos.CpTd6033.GetDataValue(17, i) * Cybos.CpTd6033.GetDataValue(15, i)
            for i in range(Cybos.CpTd6033.GetHeaderValue(7))}

        with open(r"C:\Users\kimsangho\Desktop\shared\log\AccountInfo\{}_{}.csv".format(
                datetime.now().strftime("%Y%m%d"), self.account[self.acc]), "w") as f:
            f.write("종목명,종목코드,신용구분,대출일,결제잔고수량,결제장부단가,전일체결수량,금일체결수량,체결잔고수량,평가금액,평가손익,"
                    "수익률,주문구분,매도가능수량,만기일,체결장부단가,손익단가\n")
            for i in range(Cybos.CpTd6033.GetHeaderValue(7)):
                StockName = Cybos.CpTd6033.GetDataValue(0, i)               # 종목명
                CreditClassification = Cybos.CpTd6033.GetDataValue(1, i)    # 신용구분
                LoanDate = Cybos.CpTd6033.GetDataValue(2, i)                # 대출일
                PaymentBalance = Cybos.CpTd6033.GetDataValue(3, i)          # 결제잔고수량
                PaymentBookPrice = Cybos.CpTd6033.GetDataValue(4, i)        # 결제장부단가
                PrevDayExecAmount = Cybos.CpTd6033.GetDataValue(5, i)       # 전일체결수량
                TodayExecAmount = Cybos.CpTd6033.GetDataValue(6, i)         # 금일체결수량
                ExecBalanceAmount = Cybos.CpTd6033.GetDataValue(7, i)       # 체결잔고수량
                PortfolioValue = Cybos.CpTd6033.GetDataValue(9, i)          # 평가금액(단위:원) - 천원미만은내림
                PortfolioProfitLoss = Cybos.CpTd6033.GetDataValue(10, i)    # 평가손익(단위:원) - 천원미만은내림
                ReturnOfRate = Cybos.CpTd6033.GetDataValue(11, i)           # 수익률
                StockCode = Cybos.CpTd6033.GetDataValue(12, i)              # 종목코드
                OrderClassification = Cybos.CpTd6033.GetDataValue(13, i)    # 주문구분
                PossibleSellOrder = Cybos.CpTd6033.GetDatavalue(15, i)      # 매도가능수량
                LoanDueDate = Cybos.CpTd6033.GetDataValue(16, i)            # 만기일
                ExecBookAvgPrice = Cybos.CpTd6033.GetDataValue(17, i)       # 체결장부단가
                ProfitLossPrice = Cybos.CpTd6033.GetDataValue(18, i)        # 손익단가

                f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                    StockName, StockCode, self.code_6033[chr(CreditClassification)], LoanDate, PaymentBalance,
                    PaymentBookPrice, PrevDayExecAmount, TodayExecAmount, ExecBalanceAmount, PortfolioValue,
                    PortfolioProfitLoss, ReturnOfRate, chr(OrderClassification), PossibleSellOrder, LoanDueDate,
                    ExecBookAvgPrice, ProfitLossPrice))

        return TotalBalance, AveragePrice, TotalAmount, AmountAvailableSell, TotalBuyPrice

    def TradeHistory(self, model, close_price):
        today = datetime.now().strftime("%Y%m%d")
        TotalProfit, AveragePrice, TotalAmount, *_ = self.TotalAccountBalance()
        self.TodayTradingProfitLoss()

        Cybos.CpTd5341.SetInputValue(0, self.account[self.acc])
        Cybos.CpTd5341.SetInputValue(1, self.acc_flag[0])

        Cybos.CpTd5341.BlockRequest()

        cnt = Cybos.CpTd5341.GetHeaderValue(6)
        with open(r"C:\Users\kimsangho\Desktop\shared\log\{}_{}_{}.csv".format(model, today, TotalProfit), "w") as f:
            f.write("계좌번호,종목이름,주문호가,주문수량,주문단가,체결수량,체결단가,체결잔고수량,손익단가,종가,매매구분\n")

            for i in range(cnt):
                StockName = Cybos.CpTd5341.GetDataValue(4, i)
                OrderBook = Cybos.CpTd5341.GetDataValue(6, i)
                OrderAmount = Cybos.CpTd5341.GetDataValue(7, i)
                OrderPrice = Cybos.CpTd5341.GetDataValue(8, i)
                TradeAmount = Cybos.CpTd5341.GetDataValue(10, i)
                TradePrice = Cybos.CpTd5341.GetDataValue(11, i)
                AccountNum = Cybos.CpTd5341.GetDataValue(21, i)
                BuySell = Cybos.CpTd5341.GetDataValue(24, i)

                if TradeAmount == 0: continue
                try:
                    f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(
                        self.account[self.acc], StockName, OrderBook, OrderAmount, OrderPrice, TradeAmount, TradePrice,
                        TotalAmount[StockName], AveragePrice[StockName], close_price[StockName][4], BuySell))
                except:
                    f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(
                        self.account[self.acc], StockName, OrderBook, OrderAmount, OrderPrice, TradeAmount, TradePrice,
                        0, 0, close_price[StockName][4],
                        BuySell if TradeAmount == OrderAmount else "보유"))

            tradedStock = [Cybos.CpTd5341.GetDataValue(4, i) for i in range(cnt)]
            for StockName in AveragePrice.keys():
                if StockName in tradedStock: continue

                f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(
                   self.account[self.acc], StockName, 0, 0, 0, 0, 0, TotalAmount[StockName],
                   AveragePrice[StockName], close_price[StockName][4], "보유"))


if __name__=="__main__":
    a = CybosTrade('782653948')
    a.BuySellOrder("1", "KODEX 200", 1)
    #a.TotalAccountBalance()

