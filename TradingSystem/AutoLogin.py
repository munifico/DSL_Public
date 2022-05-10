from pywinauto import application
from datetime import datetime
import QuantLib as ql
import os
import time

n = datetime.now().year
kr = ql.SouthKorea()
kr_holidayList = kr.holidayList(ql.Date(1, 1, n), ql.Date(31, 12, n))

if not kr.isHoliday(ql.Date(datetime.now().day, datetime.now().month, datetime.now().year)):
    os.system('taskkill /im ncStarter*')
    time.sleep(3)
    os.system('taskkill /im CpStart*')
    time.sleep(3)
    os.system('taskkill /im DibServer*')
    time.sleep(3)
    os.system('taskkill /im coServer.exe')
    time.sleep(3)
    os.system('taskkill /im coMain.exe')

    app = application.Application()
    app.start('C:\Daishin\Starter\\ncStarter.exe /prj:cp /id:{id} /pwd:{pwd} /pwdcert:{pwdc} /autostart'.format(
        id='아이디', pwd='비밀번호', pwdc="공인인증서 비밀번호"))