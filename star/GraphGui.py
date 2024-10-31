import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtCore import QLocale, QDate
from PySide6.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import ForExcel as fe
import GraphMethod as gm

matplotlib.rcParams['font.family'] = 'AppleGothic'  # 윈도우로 넘길 때 나눔 고딕으로 바꿔야함 NanumGothic
matplotlib.rcParams.update({'font.size': 6})  # 윈도우로 넘길 때 사이즈 조절 해야함
plt.rcParams['axes.unicode_minus'] = False

"""
    Radio Structure
    
    shape : bar, pie
    
    x : item,                   sale
    y : item count, item sales, sale term
    
    term : day, month, year
    
    set default : bar, item, count item, month
"""


class pastSaleForm(QWidget):  # 이전 매출
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.date = QDate()
        self.isC = None
        self.mainWindow = None

        #   groupboxShape
        groupboxShape = QGroupBox('모양')

        self.radio_bar = QRadioButton('막대')
        self.radio_pie = QRadioButton('원')

        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.radio_bar)
        vbox1.addWidget(self.radio_pie)

        vbox1.addStretch(1)
        groupboxShape.setLayout(vbox1)

        #   set x
        groupboxX = QGroupBox('X축 설정')
        self.radio_item = QRadioButton('상품')
        self.radio_sale = QRadioButton('기간')

        # self.radio_item.clicked.connect(self.change())
        # self.radio_sale.clicked.connect(self.change())

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.radio_item)
        vbox2.addWidget(self.radio_sale)

        vbox2.addStretch(1)
        groupboxX.setLayout(vbox2)

        #   set y
        groupboxY = QGroupBox('Y축 설정')
        self.radio_itemCnt = QRadioButton('상품 판매 갯수 : 상품 버튼만')
        self.radio_itemSale = QRadioButton('상품 판매 매출 : 상품 버튼만')
        self.radio_term = QRadioButton('매출 : 기간 버튼만')

        vbox3 = QVBoxLayout()
        vbox3.addWidget(self.radio_itemCnt)
        vbox3.addWidget(self.radio_itemSale)
        vbox3.addWidget(self.radio_term)

        vbox3.addStretch(1)
        groupboxY.setLayout(vbox3)

        #   set term
        groupboxTerm = QGroupBox('기간 설정')
        self.radio_day = QRadioButton('일')
        self.radio_month = QRadioButton('월')
        self.radio_year = QRadioButton('년')

        vbox4 = QVBoxLayout()
        vbox4.addWidget(self.radio_day)
        vbox4.addWidget(self.radio_month)
        vbox4.addWidget(self.radio_year)

        vbox4.addStretch(1)
        groupboxTerm.setLayout(vbox4)

        #   set calender
        groupboxCal = QGroupBox()
        self.calendar = QCalendarWidget()
        self.calendar.setLocale(QLocale("ko_KR_seoul"))

        last_Fdata = list(fe.Fdata_list.keys())[-1]
        Last_date = QDate(int(last_Fdata[:4]), int(last_Fdata[5:7]),
                          30 if int(last_Fdata[5:7]) in [2, 4, 6, 9, 11] else 31)

        self.calendar.setMaximumDate(Last_date)  # 데이터화 된 파일의 제일 최근 날짜
        self.calendar.setMinimumDate(QDate(2022, 2, 1))
        self.calendar.setGridVisible(True)

        self.calendar.selectionChanged.connect(self.calendarSelectionChanged)

        self.btn = QPushButton('이전 화면')
        self.selectAll = QPushButton('그래프 보기')
        self.warning = QLabel('')

        self.btn.clicked.connect(self.return_window)
        self.selectAll.clicked.connect(lambda: self.is_checked(self.ax, self.date))

        vbox5 = QVBoxLayout()
        vbox5.addWidget(self.calendar)
        vbox5.addWidget(self.btn)
        vbox5.addWidget(self.selectAll)
        vbox5.addWidget(self.warning)

        groupboxCal.setLayout(vbox5)

        #   canvasbox1
        canvasbox1 = QGroupBox()

        canvas = FigureCanvas(Figure((10, 8), 100))
        self.toolbar = NavigationToolbar(canvas, self)

        self.ax = canvas.figure.subplots(1, 1)

        vbox6 = QVBoxLayout()
        vbox6.addWidget(self.toolbar)
        vbox6.addWidget(canvas)

        vbox6.addStretch(1)
        canvasbox1.setLayout(vbox6)

        #   set form
        gridlayout = QGridLayout()
        gridlayout.addWidget(groupboxShape, 0, 5)
        gridlayout.addWidget(groupboxX, 1, 5)
        gridlayout.addWidget(groupboxY, 2, 5)
        gridlayout.addWidget(groupboxTerm, 3, 5)
        gridlayout.addWidget(groupboxCal, 4, 5)
        gridlayout.addWidget(canvasbox1, 0, 0, 5, 4)

        self.setLayout(gridlayout)
        self.setGeometry(0, 0, 1200, 500)
        self.show()

    def calendarSelectionChanged(self):
        self.date = self.calendar.selectedDate()

    def is_checked(self, ax, date):
        is_shape = [self.radio_pie.isChecked(), self.radio_bar.isChecked()]
        is_xlabel = [self.radio_item.isChecked(), self.radio_sale.isChecked()]
        is_ylabel = [self.radio_itemCnt.isChecked(), self.radio_itemSale.isChecked(), self.radio_term.isChecked()]
        is_term = [self.radio_day.isChecked(), self.radio_month.isChecked(), self.radio_year.isChecked()]

        shape = 0 if is_shape[0] else 1
        xlabel = 0 if is_xlabel[0] else 1

        if is_ylabel[0]:
            ylabel = 0
        elif is_ylabel[1]:
            ylabel = 1
        else:
            ylabel = 2

        if is_term[0]:
            term = 0
        elif is_term[1]:
            term = 1
        else:
            term = 2
        self.isC = [shape, xlabel, ylabel, term]
        self.draw_graph(ax, self.isC, date)
        self.warning.setText('')

    def draw_graph(self, ax, isC, date):
        global df
        self.ax.clear()

        shape = isC[0]
        xlabel = isC[1]
        ylabel = isC[2]
        term = isC[3]

        data = {}

        if xlabel == 0:  # item is checked
            data_name, df = gm.item_name(term, date)

        else:  # sale is checked
            data_name = gm.get_dt(term, date)

        for i in data_name:
            data[i] = 0
        try:
            if ylabel == 0:  # item count
                data = gm.count_item(term, date, data, ylabel, df)
                data = gm.delete_data(data)

            elif ylabel == 1:  # item sales
                data = gm.count_item(term, date, data, ylabel, df)
                data = gm.delete_data(data)

            else:  # how many sales
                data = gm.getSale(term, date, data)
        except(Exception,):
            self.warning.setText('기간 버튼은 매출 버튼, 상품 버튼은 상품~~버튼만 선택')

        for i, j in list(data.items()):
            if j == 0:
                data.pop(i)
                data_name.remove(i)

        if shape == 0:  # pie
            explode = [0.13 for i in range(len(data.keys()))]
            ax.pie(data.values(), labels=data.keys(), colors=gm.Color(data_name), explode=explode, autopct='%.1f%%')

        else:  # bar
            data_name = np.array(data_name)
            ax.bar(data.keys(), data.values(), color=gm.Color(data_name))
            ax.set_yticks([i for i in range(min(data.values()), max(data.values()), (max(data.values())//10))])

            x_labels = ax.get_xticklabels()
            y_labels = ax.get_yticklabels()

            asd = list(data.values())

            for i in range(len(data)):
                ax.text(i, asd[i], str(asd[i]), ha='center', rotation=90)

            plt.setp(x_labels, rotation=45, horizontalalignment='right')
            plt.setp(y_labels, rotation=45, horizontalalignment='right')

        ax.figure.canvas.draw()

    def return_window(self):
        from justGui import mainWindow
        self.hide()
        self.mainWindow = mainWindow()
        self.mainWindow.show()


class calculateForm(QWidget):  # 미래 매출
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.mainWindow = None
        self.btn = QPushButton('이전 화면', self)
        self.btn.clicked.connect(self.return_window)

        layout = QHBoxLayout()
        layout.addWidget(self.btn)

        self.setLayout(layout)

    def return_window(self):
        from justGui import mainWindow
        self.hide()
        self.mainWindow = mainWindow()
        self.mainWindow.show()


class rankingForm(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.mainWindow = None
        self.warn = QLabel('주의! 파일 단위 결과만 보여짐, 서비스 제외')

        self.btn = QPushButton('이전 화면', self)
        self.btn.clicked.connect(self.return_window)

        self.cb = QComboBox()
        kea = []

        for i in fe.Fdata_list.keys():
            kea.append(i[:7] + '월')

        self.cb.addItems(kea)

        self.btn2 = QPushButton('선택')
        self.btn2.clicked.connect(self.select_excel)

        #   1위
        self.label = QLabel("음식 주문 좌석 1위, 카운터 제외")
        self.label2 = QLabel("결제수단 1위, 서비스 제외")
        self.label3 = QLabel("주문 많은 손님 1위, 카운터 제외")
        self.label4 = QLabel('카테고리 1위, 서비스 제외')
        self.label5 = QLabel('전체 메뉴 1위, 서비스 제외')
        self.label6 = QLabel('주문 많은 날짜 1위, 서비스 제외')
        self.label7 = QLabel('매출 높은 날짜 1위, 서비스 제외')

        #   2위
        self.label8 = QLabel("음식 주문 좌석 2위, 카운터 제외")
        self.label9 = QLabel("결제수단 2위, 서비스 제외")
        self.label10 = QLabel("주문 많은 손님 2위, 카운터 제외")
        self.label11 = QLabel('카테고리 2위, 서비스 제외')
        self.label12 = QLabel('전제 메뉴 2위, 서비스 제외')
        self.label13 = QLabel('주문 많은 날짜 2위, 서비스 제외')
        self.label14 = QLabel('매출 높은 날짜 2위, 서비스 제외')

        #   3위
        self.label15 = QLabel("음식 주문 좌석 3위, 카운터 제외")
        self.label16 = QLabel("결제수단 3위, 서비스 제외")
        self.label17 = QLabel("주문 많은 손님 3위, 카운터 제외")
        self.label18 = QLabel('카테고리 3위, 서비스 제외')
        self.label19 = QLabel('전체 메뉴 3위, 서비스 제외')
        self.label20 = QLabel('주문 많은 날짜 3위, 서비스 제외')
        self.label21 = QLabel('매출 높은 날짜 3위, 서비스 제외')

        #   카테고리별 상품
        self.clabel = QLabel('카테고리별 1위')
        self.clabel2 = QLabel('카테고리별 1위')
        self.clabel3 = QLabel('카테고리별 1위')
        self.clabel4 = QLabel('카테고리별 1위')

        self.clabel5 = QLabel('카테고리별 1위')
        self.clabel6 = QLabel('카테고리별 1위')
        self.clabel7 = QLabel('카테고리별 1위')
        self.clabel8 = QLabel('카테고리별 1위')

        self.clabel9 = QLabel('카테고리별 1위')
        self.clabel10 = QLabel('카테고리별 1위')
        self.clabel11 = QLabel('카테고리별 1위')
        self.clabel12 = QLabel('카테고리별 1위')

        layout = QHBoxLayout()
        grlay = QGridLayout()
        mainlay = QVBoxLayout()

        layout.addWidget(self.btn)
        layout.addWidget(self.cb)
        layout.addWidget(self.btn2)

        # 1위
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.label)
        vbox1.addWidget(self.label2)
        vbox1.addWidget(self.label3)
        vbox1.addWidget(self.label4)
        vbox1.addWidget(self.label5)
        vbox1.addWidget(self.label6)
        vbox1.addWidget(self.label7)

        groupbox1 = QGroupBox('Rank 1')
        groupbox1.setLayout(vbox1)

        # 2위
        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.label8)
        vbox2.addWidget(self.label9)
        vbox2.addWidget(self.label10)
        vbox2.addWidget(self.label11)
        vbox2.addWidget(self.label12)
        vbox2.addWidget(self.label13)
        vbox2.addWidget(self.label14)

        groupbox2 = QGroupBox('Rank 2')
        groupbox2.setLayout(vbox2)

        # 3위
        vbox3 = QVBoxLayout()
        vbox3.addWidget(self.label15)
        vbox3.addWidget(self.label16)
        vbox3.addWidget(self.label17)
        vbox3.addWidget(self.label18)
        vbox3.addWidget(self.label19)
        vbox3.addWidget(self.label20)
        vbox3.addWidget(self.label21)

        groupbox3 = QGroupBox('Rank 3')
        groupbox3.setLayout(vbox3)

        # 카테고리별 상품
        vbox4 = QVBoxLayout()
        vbox4.addWidget(self.clabel)
        vbox4.addWidget(self.clabel2)
        vbox4.addWidget(self.clabel3)
        vbox4.addWidget(self.clabel4)

        groupbox4 = QGroupBox('카테고리별 1위')
        groupbox4.setLayout(vbox4)

        vbox5 = QVBoxLayout()
        vbox5.addWidget(self.clabel5)
        vbox5.addWidget(self.clabel6)
        vbox5.addWidget(self.clabel7)
        vbox5.addWidget(self.clabel8)

        groupbox5 = QGroupBox('카테고리별 1위')
        groupbox5.setLayout(vbox5)

        vbox6 = QVBoxLayout()
        vbox6.addWidget(self.clabel9)
        vbox6.addWidget(self.clabel10)
        vbox6.addWidget(self.clabel11)
        vbox6.addWidget(self.clabel12)

        groupbox6 = QGroupBox('카테고리별 1위')
        groupbox6.setLayout(vbox6)

        grlay.addWidget(groupbox1, 0, 0)
        grlay.addWidget(groupbox2, 0, 1)
        grlay.addWidget(groupbox3, 0, 2)
        grlay.addWidget(groupbox4, 1, 0)
        grlay.addWidget(groupbox5, 1, 1)
        grlay.addWidget(groupbox6, 1, 2)

        mainlay.addWidget(self.warn)
        mainlay.addLayout(layout)
        mainlay.addLayout(grlay)

        self.setLayout(mainlay)

    def select_excel(self):
        self.label.clear()
        curtxt = self.cb.currentText()[:-1] + '.csv'

        (sit,  # 음식 주문 좌석
         cnt,
         pay,  # 결제수단
         payCnt,
         name,  # 주문 많은 손님
         nameCnt,
         cate,  # 카테고리
         cateCnt,
         sale,  # 메뉴
         saleCnt,
         time,  # 주문 많은 날짜
         timeCnt,
         result,  # 매출 높은 날짜
         resultCnt) = gm.ranking(curtxt, 0)

        self.label.setText("음식 주문 좌석 1위" + ' : ' + str(sit) + '번, ' + str(cnt) + '회')
        self.label2.setText("결제수단 1위" + ' : ' + pay + ', ' + str(payCnt) + '회')
        self.label3.setText("주문 많은 손님 1위" + ' : ' + name + ', ' + str(nameCnt) + '회')
        self.label4.setText("카테고리 1위" + ' : ' + cate + ', ' + str(cateCnt) + '회')
        self.label5.setText("메뉴 1위" + ' : ' + sale + ', ' + str(saleCnt) + '회')
        self.label6.setText("주문 많은 날짜 1위" + ' : ' + time + ', ' + str(timeCnt) + '회')
        self.label7.setText("매출 높은 날짜 1위" + ' : ' + result + ', ' + str(resultCnt) + '원')

        # 2위
        (sit,
         cnt,
         pay,
         payCnt,
         name,
         nameCnt,
         cate,
         cateCnt,
         sale,
         saleCnt,
         time,
         timeCnt,
         result,
         resultCnt) = gm.ranking(curtxt, 1)
        self.label8.setText("음식 주문 좌석 2위" + ' : ' + str(sit) + '번, ' + str(cnt) + '회')
        self.label9.setText("결제수단 2위" + ' : ' + pay + ', ' + str(payCnt) + '회')
        self.label10.setText("주문 많은 손님 2위" + ' : ' + name + ', ' + str(nameCnt) + '회')
        self.label11.setText("카테고리 2위" + ' : ' + cate + ', ' + str(cateCnt) + '회')
        self.label12.setText("메뉴 2위" + ' : ' + sale + ', ' + str(saleCnt) + '회')
        self.label13.setText("주문 많은 날짜 2위" + ' : ' + time + ', ' + str(timeCnt) + '회')
        self.label14.setText("매출 높은 날짜 2위" + ' : ' + result + ', ' + str(resultCnt) + '원')

        # 3위
        (sit,
         cnt,
         pay,
         payCnt,
         name,
         nameCnt,
         cate,
         cateCnt,
         sale,
         saleCnt,
         time,
         timeCnt,
         result,
         resultCnt) = gm.ranking(curtxt, 2)
        self.label15.setText("음식 주문 좌석 3위" + ' : ' + str(sit) + '번, ' + str(cnt) + '회')
        self.label16.setText("결제수단 3위" + ' : ' + pay + ', ' + str(payCnt) + '회')
        self.label17.setText("주문 많은 손님 3위" + ' : ' + name + ', ' + str(nameCnt) + '회')
        self.label18.setText("카테고리 3위" + ' : ' + cate + ', ' + str(cateCnt) + '회')
        self.label19.setText("메뉴 3위" + ' : ' + sale + ', ' + str(saleCnt) + '회')
        self.label20.setText("주문 많은 날짜 3위" + ' : ' + time + ', ' + str(timeCnt) + '회')
        self.label21.setText("매출 높은 날짜 3위" + ' : ' + result + ', ' + str(resultCnt) + '원')

        # category
        temp = []
        catesale, key = gm.catesaleRanke(curtxt)
        for i in range(len(key)):
            temp.append(catesale[key[i]])

        self.clabel.setText(key[0] + ' : ' + temp[0][0][0] + ' ' + str(temp[0][0][1]) + '회')
        self.clabel2.setText(key[1] + ' : ' + temp[1][0][0] + ' ' + str(temp[1][0][1]) + '회')
        self.clabel3.setText(key[2] + ' : ' + temp[2][0][0] + ' ' + str(temp[2][0][1]) + '회')
        self.clabel4.setText(key[3] + ' : ' + temp[3][0][0] + ' ' + str(temp[3][0][1]) + '회')
        self.clabel5.setText(key[4] + ' : ' + temp[4][0][0] + ' ' + str(temp[4][0][1]) + '회')
        self.clabel6.setText(key[5] + ' : ' + temp[5][0][0] + ' ' + str(temp[5][0][1]) + '회')
        self.clabel7.setText(key[6] + ' : ' + temp[6][0][0] + ' ' + str(temp[6][0][1]) + '회')
        self.clabel8.setText(key[7] + ' : ' + temp[7][0][0] + ' ' + str(temp[7][0][1]) + '회')
        self.clabel9.setText(key[8] + ' : ' + temp[8][0][0] + ' ' + str(temp[8][0][1]) + '회')
        self.clabel10.setText(key[9] + ' : ' + temp[9][0][0] + ' ' + str(temp[9][0][1]) + '회')
        self.clabel11.setText(key[10] + ' : ' + temp[10][0][0] + ' ' + str(temp[10][0][1]) + '회')
        try:
            self.clabel12.setText(key[11] + ':' + temp[11][0][0] + ' ' + str(temp[11][0][1]) + '회')
        except(Exception,):
            pass

    def return_window(self):
        from justGui import mainWindow
        self.hide()
        self.mainWindow = mainWindow()
        self.mainWindow.show()
