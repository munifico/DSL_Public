import win32com.client


class CybosPlus:
    CpCybos = win32com.client.Dispatch("CpUtil.CpCybos")             # Cybos의 각종 상태를 확인
    CpStockCode = win32com.client.Dispatch("CpUtil.CpStockCode")     # Cybos에서 사용되는 주식 코드조회 작업
    CpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")         # 각종 종목코드 정보 및 코드 리스트

    StockChart = win32com.client.Dispatch("CpSysDib.StockChart")     # 주식, 업종, ELW 차트 데이터를 수신
    MarketEye = win32com.client.Dispatch("CpSysDib.MarketEye")       # 주식,지수,선물/옵션 등의 여러 종목의 필요 항목들을 한번에 수신
    CpSvr7238 = win32com.client.Dispatch("CpSysDib.CpSvr7238")       # 종목별 공매도 추이

    CpTdUtil = win32com.client.Dispatch("CpTrade.CpTdUtil")          # 주문 오브젝트를 사용하기 위해 필요한 초기화 과정을 수행
    CpTd0311 = win32com.client.Dispatch("CpTrade.CpTd0311")          # 현금주문 데이터를 요청하고 수신
    CpTd0313 = win32com.client.Dispatch("CpTrade.CpTd0313")          # 가격정정주문 데이터를 요청하고 수신
    CpTd0314 = win32com.client.Dispatch("CpTrade.CpTd0314")          # 취소주문 데이터를 요청하고 수신
    CpTd0322 = win32com.client.Dispatch("CpTrade.CpTd0322")          # 시간외 종가매매
    CpTd0326 = win32com.client.Dispatch("CpTrade.CpTd0326")          # 시간외 종가 취소 주문
    CpTd0386 = win32com.client.Dispatch("CpTrade.CpTd0386")          # 시간외 단일가 주문
    CpTd0387 = win32com.client.Dispatch("CpTrade.CpTd0387")          # 시간외 단일가 취소 주문
    CpTd0389 = win32com.client.Dispatch("CpTrade.CpTd0389")          # 시간외 단일가 정정 주문
    CpTd5339 = win32com.client.Dispatch("CpTrade.CpTd5339")          # 계좌별 미체결 잔량데이터를 요청하고 수신
    CpTd5341 = win32com.client.Dispatch("CpTrade.CpTd5341")          # 계좌별 미체결 잔량데이터를 요청하고 수신
    CpTd6032 = win32com.client.Dispatch("CpTrade.CpTd6032")          # 체결기준 주식 당일매매손익 데이터를 요청하고 수신
    CpTd6033 = win32com.client.Dispatch("CpTrade.CpTd6033")          # 계좌별 잔고 및 주문체결평가 현황 데이터를 요청하고 수신
    CpTdNew5331A = win32com.client.Dispatch("CpTrade.CpTdNew5331A")  # 계좌별 매수 주문가능금액/수량데이터를 요청하고 수신
    CpTdNew5331B = win32com.client.Dispatch("CpTrade.CpTdNew5331B")  # 계좌별 매도 주문가능수량 데이터를 요청하고 수신

    StockCur = win32com.client.Dispatch("Dscbo1.StockCur")           # 주식/업종/ELW 시세 데이터를 수신
    CpConclusion = win32com.client.Dispatch("Dscbo1.CpConclusion")   # 주식 주문한 것에 대한 체결 내역을 실시간으로 요청하고 수신
    StockJpBid = win32com.client.Dispatch("Dscbo1.StockJpBid")       # 주식/ETF/ELW 종목 매도, 매수에 관란 1~10차호가/LP 호가 및 호가 잔량 수신
    StockJpBid2 = win32com.client.Dispatch("Dscbo1.StockJpBid2")     # 주식 종목에 대해 매도, 매수에 관란 1~10차 호가 및 호가 잔량 수신
    SoptionCur = win32com.client.Dispatch("Dscbo1.SoptionCur")
    StockMst = win32com.client.Dispatch("Dscbo1.StockMst")           # 주식 종목의 현재가에 관련한 데이터
    StockMst2 = win32com.client.Dispatch("Dscbo1.StockMst2")         # 주식 복수 종목에 대해 일괄 조회를 요청하고 수신

    CpSeries = win32com.client.Dispatch("CpIndexes.CpSeries")        # 차트지표계산에 필요한 데이터
    CpIndex = win32com.client.Dispatch("CpIndexes.CpIndex")          # 차트지표계산에 필요한 함수제공