from PySide6.QtWidgets import *
import os
import Setting as st
import ForExcel as fe
import ForWeather as fw
from GraphGui import pastSaleForm, calculateForm, rankingForm

"""
    단순 버튼만 들어가 있는 gui class 모음
    
    GuiForm
    첫 화면에 해당 되는 gui class
"""


class GuiForm(QWidget):
    folder_path = ''
    

    def __init__(self):
        QWidget.__init__(self)
        self.add_window = None
        self.setWindowTitle('Stardom Demo')

        self.line = QLineEdit(self)
        button = QPushButton('Select', self)
        button.clicked.connect(self.select_dir)

        buttonOk = QPushButton('Ok', self)
        buttonOk.clicked.connect(self.next_window)

        layout = QHBoxLayout()
        layout.addWidget(buttonOk)
        layout.addWidget(button)
        layout.addWidget(self.line)

        self.setLayout(layout)

    def select_dir(self):
        select_path = QFileDialog.getExistingDirectory(self, '', "C:\\")
        self.line.setText(select_path)


    def next_window(self):
        self.folder_path = self.line.text()
        self.AIdata_path = os.path.join(self.folder_path, 'AIdata')
        self.set_path = os.path.join(self.folder_path, 'set')
        self.Fdata_path = os.path.join(self.folder_path, 'Fdata')
        if len(self.line.text()) > 0:
            st.create_folder(self.folder_path)
            st.create_folder(self.AIdata_path)
            st.create_folder(self.set_path)
            st.create_folder(self.Fdata_path)

            if not st.is_any_file(st.excel_list_path(self.set_path)):
                st.make_list(st.excel_list_path(self.set_path))
            if not st.is_any_file(st.AIdata_list_path(self.set_path)):
                st.make_list(st.AIdata_list_path(self.set_path))
            if not st.is_any_file(st.Fdata_list_path(self.set_path)):
                st.make_list(st.Fdata_list_path(self.set_path))
            if not st.is_any_file(st.weather_list_path(self.set_path)):
                st.make_list(st.weather_list_path(self.set_path))

            st.read_list(self.set_path)
            fe.to_Fdata(self.folder_path)
            st.add_execl_list(self.folder_path, self.set_path)

            for i in fe.Fdata_list.keys():
                if i not in os.listdir(self.AIdata_path):
                    fe.to_AIdata(self.Fdata_path, i)

            for i in fe.Fdata_list.keys():
                a, b = fe.find_m(self.Fdata_path, i)
                k = a[0:4] + "-" + a[4:6]

                if 'weather_data_' + k + '.csv' in os.listdir(self.AIdata_path):
                    break

                para1 = fw.para(a, b, fw.DecodeKey)

                try:
                    retjas = fw.take_json(fw.url, para1)
                    fw.j_to_c(retjas[0], retjas[1])

                except(Exception,):
                    pass

            st.add_weather_list(self.AIdata_path, self.set_path)
            st.read_list(self.set_path)

            self.hide()
            self.add_window = mainWindow(self.folder_path)
            self.add_window.show()


class mainWindow(QWidget):  # 메인 메뉴 존재, 아마 완성
    """
        mainWindow
        첫 화면에서 폴더 위치 체크후 세팅이나 이것저것 다 된뒤 버튼 2개 들어가 있는 gui class
    """
    def __init__(self, path, parent=None):
        QWidget.__init__(self, parent)
        self.add_window = None

        self.Fdata_path = os.path.join(path, "Fdata")
        self.folder_path = path

        self.widget = self
        self.setWindowTitle('Main')

        self.calculate_next = QPushButton('예측 매출', self)
        self.calculate_next.clicked.connect(self.next_window)

        self.past_sales = QPushButton('지난 매출 그래프', self)
        self.past_sales.clicked.connect(self.next_window2)

        self.rank = QPushButton('Rank', self)
        self.rank.clicked.connect(self.next_window3)

        layout = QVBoxLayout()
        layout.addWidget(self.calculate_next)
        layout.addWidget(self.past_sales)
        layout.addWidget(self.rank)
        self.setLayout(layout)

    def next_window(self):
        self.hide()
        self.add_window = calculateForm(self.folder_path)
        self.add_window.show()

    def next_window2(self):
        self.hide()
        self.add_window = pastSaleForm(self.folder_path)
        self.add_window.show()

    def next_window3(self):
        self.hide()
        self.add_window = rankingForm(self.Fdata_path)
        self.add_window.show()
