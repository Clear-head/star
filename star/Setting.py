import os
import re

folder_path = '/Users/saseoghun/Desktop/stardom_sales'
AIdata_path = os.path.join(folder_path, 'AIdata')
set_path = os.path.join(folder_path, 'set')
Fdata_path = os.path.join(folder_path, 'Fdata')

excel_list_path = os.path.join(set_path, "excel_list.txt")
weather_list_path = os.path.join(set_path, "weather_list.txt")
AIdata_list_path = os.path.join(set_path, "AIdata_list.txt")
Fdata_list_path = os.path.join(set_path, "Fdata_list.txt")


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def is_any_file(path):
    try:
        return os.path.exists(path)
    except (Exception,):
        print('is_excel_file --> error')


def make_list(path):
    try:
        with open(path, "w") as f:
            f.write("")
    except (Exception,):
        pass


def read_list():
    import ForExcel as fe
    try:
        with open(excel_list_path, "r") as f:
            for i in f.read().split(','):
                fe.excel_list.append(i)
            if fe.excel_list[-1] == '':
                fe.excel_list.pop()
    except (Exception,):
        print('read_list --> excel')

    try:
        with open(weather_list_path, "r") as f:
            for i in f.read().split(','):
                fe.weather_list.append(i)
            if fe.weather_list[-1] == '':
                fe.weather_list.pop()
    except (Exception,):
        print('read_list --> weather')

    with open(AIdata_list_path, "r") as f:
        for i in f.read().split(','):
            fe.AIdata_list.append(i)
        if fe.AIdata_list[-1] == '':
            fe.AIdata_list.pop()

    with open(os.path.join(set_path, "Fdata_list.txt"), "r") as f:
        for i in f.read().split('\n'):
            if len(i) > 1:
                a = i.split('=')
                fe.Fdata_list[a[0]] = a[1]


def add_execl_list():
    from ForExcel import excel_list

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xls') and file_name not in excel_list:
            excel_list.append(file_name)
    try:
        with open(os.path.join(set_path, "excel_list.txt"), "w") as f:
            excel_list = list(set(excel_list))
            excel_list = [re.findall(r"(\d{4})-(\d{2})", date)[0] for date in excel_list]
            excel_list.sort(key=lambda x: (int(x[0]), int(x[1])))
            excel_list = [f"{year}-{month}.xls" for year, month in excel_list]

            for i in excel_list:
                f.write(i + ",")
    except (Exception,):
        print('add_execl_list -- > error')


def add_AIdata_list(name):
    from ForExcel import AIdata_list
    if name in AIdata_list:
        return
    try:
        with open(os.path.join(set_path, 'AIdata_list.txt'), "a") as f:
            f.write(name + ', ')

    except(Exception,):
        print('add_aidata_list -- > error')


def add_weather_list():
    from ForExcel import weather_list

    try:
        for file_name in os.listdir(AIdata_path):
            if file_name.endswith('.csv') and file_name.startswith('weather_data_') and file_name not in weather_list:
                weather_list.append(file_name)

        with open(os.path.join(set_path, "weather_list.txt"), "w") as f:
            weather_list = list(set(weather_list))
            weather_list = [re.findall(r"weather_data_(\d{4})-(\d{2}).csv", date)[0] for date in weather_list]
            weather_list.sort(key=lambda x: (int(x[0]), int(x[1])))
            weather_list = [f"weather_data_{year}-{month}.csv" for year, month in weather_list]
            for i in weather_list:
                f.write(i + ",")
    except (Exception,):
        print('add_weather_list -- > error')


def add_fdata_list(name, tf):
    from ForExcel import Fdata_list
    try:
        Fdata_list[name] = tf
        with open(os.path.join(set_path, 'Fdata_list.txt'), "a") as f:
            f.write(name + '=' + tf + '\n')

    except(Exception,):
        print('add_fdata_list -- > error')
