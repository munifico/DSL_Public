import os
import time
import pymysql
import logging
from datetime import datetime
from CybosTrade import CybosTrade
from CybosPrice import CybosPrice


class CybosMainForDB:
    def __init__(self, StockNameList):
        self.StockNamelist = StockNameList
        if len(self.StockNamelist) > 50: raise Exception("종목은 최대 50개만 가능합니다.")

        self.cTrade = CybosTrade()
        self.cPrice = CybosPrice()

        curr_time = datetime.now().hour * 100 + datetime.now().minute
        self.MarketOpen = curr_time if curr_time > 900 else 900

        # DB information
        host = "ai-funding.ciuvwkxdrg5s.ap-northeast-2.rds.amazonaws.com"
        user = "admin"
        password = "^iG22j#3i#R5AD6"
        db = "ai_funding"
        char = 'utf8'

        conn = pymysql.connect(host=host, user=user, password=password, db=db, charset=char, autocommit=True)
        self.curs = conn.cursor(pymysql.cursors.DictCursor)

        self.logger = logging.getLogger(__name__)

        if not os.path.isdir("./logs"): os.makedirs("./logs")


    def Log(self):
        formatter = logging.Formatter("[%(asctime)s][%(levelname)s] >> %(message)s")

        fileHandler = logging.FileHandler("./logs/LogFile.log")
        fileHandler.setFormatter(formatter)

        self.logger.addHandler(fileHandler)
        self.logger.setLevel(level=logging.DEBUG)

    def DB_Insert_StockTable(self, StockName, CurrPrice, StockCode):
        time.sleep(1)
        for name, price, code in zip(StockName, CurrPrice, StockCode):
            try: # 새로운 주가 정보를 넣는 경우
                sql = "INSERT INTO stock(item_name, now_price, stock_code) VALUES (%s, %s, %s)"
                self.curs.execute(sql, [name, price, code])
                self.logger.info("{} inserts in the Stock table".format(name))
            except: # 이미 주가 정보가 존재하는 경우 (시간도 같이 업데이트함)
                sql = "UPDATE stock SET create_at=NOW(), now_price=%s WHERE stock_code=%s"
                self.curs.execute(sql, [price, code])
                self.logger.info("{} exists in the Stock table, Update the current price".format(name))

    def DB_Insert_StockPriceByDayTable(self, PrevClosingPrice, StartPrice, StockName):
        sql1 = "SELECT count(*) FROM stock_price_by_day WHERE DATE(create_at)=%s"
        self.curs.execute(sql1, datetime.now().strftime("%Y-%m-%d"))
        if self.curs.fetchall()[0]['count(*)'] > 0:
            self.logger.info("Both start price and previous closing price are already inserted in the StockPriceByDay table")
            return

        # Get Stock id
        StockId = []
        sql2 = "SELECT stock_id FROM stock WHERE item_name=%s"
        for stock_name in StockName:
            self.curs.execute(sql2, stock_name)
            StockId.append(self.curs.fetchall()[0]['stock_id'])

        # Insert stock info
        insert_sql = "INSERT INTO stock_price_by_day(end_price, start_price, stock_id) VALUES (%s, %s, %s)"
        self.curs.executemany(insert_sql, list(zip(PrevClosingPrice, StartPrice, StockId)))
        self.logger.info("StockPriceByDay insert Success!!")

    def DB_Insert_TradingDetailTable(self, signal, price, amount):
        # '00' : 매수, '01' : 매도
        pass

    def run(self):
        self.Log()
        # stock_price_by_day: 전일 종가(end_price), 시가(start_price)
        # Stock : 종목 코드(stock_code), 종목 명(item_name), 현재가(now_price), 생성일자(create_at)
        while datetime.now().hour * 100 + datetime.now().minute < 900: time.sleep(1)  # 개장 전(9:00)전에는 실행하지 않음

        # 현재 가격이랑 전날 종가 불러온 뒤 저장
        StockCode, StockName, CurrPrice, StartPrice, PrevClosingPrice = self.cPrice.PriceInfo(self.StockNamelist)
        self.DB_Insert_StockTable(StockName, CurrPrice, StockCode)
        self.DB_Insert_StockPriceByDayTable(PrevClosingPrice, StartPrice, StockName)

        self.MarketOpen += 1
        while self.MarketOpen <= 1530:
            if self.MarketOpen == datetime.now().hour * 100 + datetime.now().minute:
                self.logger.info("Data Insert start ------------------------------")
                # 1분마다 DB에 현재가 저장
                StockCode, StockName, CurrPrice, _, _ = self.cPrice.PriceInfo(self.StockNamelist)
                self.DB_Insert_StockTable(StockName, CurrPrice, StockCode)
                self.MarketOpen += 1
        self.logger.info("DB Insert Success!!")
        
        # 이쪽에서 서버에서 받은 매매 신호를 이용해 실제 매매를 진행함
        
if __name__ == "__main__":
    a = CybosMainForDB(["카카오뱅크", "SK하이닉스", "카카오", "삼성전자우"])
    a.run()