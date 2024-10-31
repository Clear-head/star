import os
import pandas as pd
import Setting as st
from PySide6.QtCore import QDate


def term0_pre(key):
    """
    :param key: string ex) yyyy-mm-dd
    :return: yy-mm-(dd-1)

    """
    yy, mm, dd = key.split('-')

    if dd == '01':

        if mm == '01':
            yy = str(int(yy) - 1)
            mm = '12'
            dd = '31'

        elif mm == '03':
            if leap_year(int(yy)):
                dd = '29'
                mm = '02'
            else:
                mm = '02'
                dd = '28'

        elif mm in ['05', '07', '08', '10', '12']:
            dd = '30'
            mm = str(int(mm) - 1) if int(mm) - 1 > 9 else '0' + str(int(mm) - 1)

        else:
            dd = '31'
            mm = str(int(mm) - 1) if int(mm) - 1 > 9 else '0' + str(int(mm) - 1)
    else:
        dd = str(int(dd) - 1) if int(dd) - 1 > 9 else '0' + str(int(dd) - 1)

    return yy + '-' + mm + '-' + dd

"""
        item_name   :       상품명 가져오는 함수
        get_dt :            term 에 비례하여 x축에 둘 것 리턴 : 일, 월, 년
        count_item  :       count or sale 에 따라 data.value 채워서 리턴
"""


def item_name(term, date):  # term =(0 : day) (1 : month) (2 : year)
    year = str(date.year())
    month = str(date.month()) if date.month() > 9 else '0' + str(date.month())
    name = []
    path = os.path.join(st.Fdata_path, year + '-' + month + '.csv')

    if term == 0:
        df = pd.read_csv(path, usecols=[0, 2, 3, 4])
        df['판매일시'] = pd.to_datetime(df['판매일시'])

        fl = term0(date)
        f_day = pd.to_datetime(fl[0], format='%Y-%m-%d %H:%M:%S')
        l_day = pd.to_datetime(fl[1], format='%Y-%m-%d %H:%M:%S')

        df = df[(df['판매일시'].between(f_day, l_day))]

        for i in df['상품명']:
            if i not in name:
                name.append(i)

    elif term == 1:
        df = pd.read_csv(path, usecols=[0, 2, 3, 4])
        for i in df['상품명']:
            if i not in name:
                name.append(i)

    else:
        df_list = []
        for i in os.listdir(st.Fdata_path):
            if i.startswith(year):
                df = pd.read_csv(os.path.join(st.Fdata_path, i), usecols=[0, 2, 3, 4])
                df_list.append(df)
        df = pd.concat(df_list, ignore_index=True)
        df = df.drop_duplicates()

        for i in df['상품명']:
            if i not in name:
                name.append(i)
    return name, df


def get_dt(term, date):
    data_name = []

    year = str(date.year())
    month = str(date.month()) if date.month() > 9 else '0' + str(date.month())

    if term == 0:
        if date.month() in [2, 4, 6, 9, 11]:
            for i in range(1, 31):
                data_name.append(month + '-' + (str(i) if i > 9 else '0' + str(i)))
            month = str(int(month) + 1) if int(month) + 1 > 9 else '0' + str(int(month) + 1)
            data_name.append(month + '-' + '01')

        elif date.month() in [1, 3, 5, 7, 8, 10]:
            for i in range(1, 32):
                day = str(i) if i > 9 else '0' + str(i)
                data_name.append(month + '-' + day)
            month = str(int(month) + 1) if int(month) + 1 > 9 else '0' + str(int(month) + 1)
            data_name.append(month + '-' + '01')

        else:  # 12
            for i in range(1, 32):
                data_name.append(month + '-' + (str(i) if i > 9 else '0' + str(i)))
            data_name.append('01-01')

    elif term == 1:
        for i in range(1, 13):
            data_name.append(year + '-' + (str(i) if i > 9 else '0' + str(i)))

    else:
        for i in os.listdir(st.Fdata_path):

            if i[:4] not in data_name:  # i[:4] = year
                data_name.append(i[:4])  # if under 5

    return data_name


def count_item(term, date, data, cs, df):
    """
    :param df: dataframe made item_name
    :param term: int
    :param date: Qdate, ex) 2023-10-13 11:15
    :param data: dic, already keys in data
    :param cs: int : count -> 0 or sale -> 1
    :return: dic, finished data
    """
    df = df[['판매일시', '상품명', '판매개수' if cs == 0 else '합계가격']]

    if term == 0:
        fl = term0(date)
        f_day = pd.to_datetime(fl[0], format='%Y-%m-%d %H:%M:%S')
        l_day = pd.to_datetime(fl[1], format='%Y-%m-%d %H:%M:%S')

        df = df[df['판매일시'].between(f_day, l_day)]

        for i in range(len(df)):
            data[df.iloc[:, 1].tolist()[i]] += int(df.iloc[:, 2].tolist()[i])

    else:
        for i in range(len(df)):
            data[df.iloc[:, 1].tolist()[i]] += int(df.iloc[:, 2].tolist()[i])

    return data


def getSale(term, date, data):
    usecol = [0, 4, 7]
    year = str(date.year())
    month = str(date.month()) if date.month() > 9 else '0' + str(date.month())
    path = os.path.join(st.Fdata_path, year + '-' + month + '.csv')

    if term == 0:
        df = pd.read_csv(path, usecols=usecol)
        df = df[['판매일시', '합계가격']]
        df['판매일시'] = pd.to_datetime(df['판매일시'], format='%Y-%m-%d %H:%M:%S')
        df = df.sort_values(by='판매일시', ascending=False)
        print('data')
        print(data)

        for i in range(len(df)):  # 2023-10-18 09:00:00
            data_name = str(df.iloc[i, 0])[5:10]
            pre_name = term0_pre(str(df.iloc[i, 0])[:10])[5:10]

            if to_between(df.iloc[i, 0]):
                data[data_name] += int(df.iloc[i, 1])
            else:
                data[pre_name] += int(df.iloc[i, 1])

    elif term == 1:
        for i in os.listdir(st.Fdata_path):
            if i.startswith(year):
                df = pd.read_csv(os.path.join(st.Fdata_path, i), usecols=usecol)
                df = df[['판매일시', '합계가격']]

                for j in df.itertuples():
                    data[i[:7]] += int(j[2])

    else:
        df_list = []
        for i in os.listdir(st.Fdata_path):
            df = pd.read_csv(os.path.join(st.Fdata_path, i), usecols=usecol)
            df = df[['판매일시', '합계가격']]
            df_list.append(df)

        df = pd.concat(df_list, ignore_index=True)
        df = df.drop_duplicates()

        for i in df.itertuples():
            data[str(i[1][:4])] += int(i[2])

    return data


def term0(date):
    """
    :param date: Qdate or pd.datetime
    :return: list(f_day, l_day)
    :for to_datetime format
    :f_day ex) 2023-10-18 09:00:00
    :l_day ex) 2023-10-19 08:59:59
    """

    global year, month, day

    if isinstance(date, QDate):
        year = str(date.year())
        month = str(date.month()) if date.month() > 9 else '0' + str(date.month())
        day = str(date.day()) if date.day() > 9 else '0' + str(date.day())

    elif isinstance(date, pd.Timestamp):
        year = str(date.year)
        month = str(date.month) if date.month > 9 else '0' + str(date.month)
        day = str(date.day) if date.day > 9 else '0' + str(date.day)

    f_day = year + '-' + month + '-' + day + ' 09:00:00'
    l_day = None

    if month in ['04', '06', '09', '11'] and day == '30':
        month = str(int(month) + 1) if int(month) + 1 > 9 else '0' + str(int(month) + 1)
        l_day = year + '-' + month + '-01' + ' 08:59:59'

    elif month in ['01', '03', '05', '07', '08', '10'] and day == '31':
        month = str(int(month) + 1) if int(month) + 1 > 9 else '0' + str(int(month) + 1)
        l_day = year + '-' + month + '-01' + ' 08:59:59'

    elif month == '02':
        month = str(int(month) + 1) if int(month) + 1 > 9 else '0' + str(int(month) + 1)

        if leap_year(int(year)) and day == '29':
            l_day = year + '-' + month + '-01' + ' 08:59:59'

        elif not leap_year(int(year)) and day == '28':
            l_day = year + '-' + month + '-01' + ' 08:59:59'

    elif month == '12' and day == '31':
        l_day = str(int(year) + 1) + '-01-01' + ' 08:59:59'

    else:
        day = str(int(day) + 1) if (int(day) + 1) > 9 else '0' + str(int(day) + 1)
        l_day = year + '-' + month + '-' + day + ' 08:59:59'

    return [f_day, l_day]


def to_between(i):
    """
    :param i: dataframe's one row ex) 2023-10-18 09:00:00
    :return: key, pre_key, between day, standard day
    """

    i = pd.to_datetime(i, format='%Y-%m-%d %H:%M:%S')
    fl = term0(i)

    f_day = pd.to_datetime(fl[0], format='%Y-%m-%d %H:%M:%S')
    l_day = pd.to_datetime(fl[1], format='%Y-%m-%d %H:%M:%S')

    fl = pd.Series([f_day, l_day])
    sei = pd.Series([i])

    if sei.between(fl[0], fl[1]).bool():
        return True
    else:
        return False


def leap_year(year):
    if year % 4 == 0 and year % 100 != 0:
        return True

    elif year % 400 == 0:
        return True

    else:
        return False


# 색 무작위 설정

def Color(count):
    count = len(count)
    color = ['#669909', '#FFAA00', '#00FF00', '#FF6969', '#6868FC']
    for_re = []
    for i in range(count // len(color)):
        for j in color:
            for_re.append(j)

    if count // len(color) != 0:
        for i in range(count % len(color)):
            for_re.append(color[i])

    return for_re


def delete_data(data):
    max_value = max(data.values())
    temp = 0
    delkey = []
    for (key, value) in data.items():
        if value < max_value * 0.05:
            delkey.append(key)
            temp += value

    for i in delkey:
        del data[i]

    data['기타'] = temp

    return data


"""
        이 밑으로는 rankform 관련 함수
"""


def ranking(text, rank):
    sit = {}
    pay = {}
    name = {}
    cate = {}
    sale = {}
    time = {}
    result = {}

    path = os.path.join(st.Fdata_path, text)
    df = pd.read_csv(path)  # 판매일시, 상품분류, 상품명, 합계가격, PC번호, 고객명, 결재수단
    df = df[(df['상품분류'] != '프린트')]

    for i in df['PC번호']:  # 주문 많은 PC
        if i not in sit:
            sit[i] = 1
        else:
            sit[i] += 1

    for i in df['결제수단']:  # 결제 수단
        if i not in pay:
            pay[i] = 1
        else:
            pay[i] += 1

    for i in df['고객명(ID)']:  # 주문 많은 손님
        if i not in name:
            name[i] = 1
        else:
            name[i] += 1

    for i in df['상품분류']:  # 주문 많은 카테고리
        if i not in cate:
            cate[i] = 1
        else:
            cate[i] += 1

    for k in range(len(df['상품명'])):  # 매뉴 판매 갯수
        i = df.iloc[k, 2]
        j = df.iloc[k, 3]

        if i not in sale:
            sale[i] = j
        else:
            sale[i] += j

    for i in df['판매일시']:  # 주문 많은 날 갯수
        # 2022-06-01 07:12
        a = str(i)[:11]
        b = term0_pre(a)
        if to_between(i):
            if a not in time:
                time[a] = 1
            else:
                time[a] += 1
        else:
            if b not in time:
                time[b] = 1
            else:
                time[b] += 1

    df = df.loc[:, ['판매일시', '합계가격']].reset_index()  # 매출 높은 날짜
    df['판매일시'] = pd.to_datetime(df['판매일시'], format='%Y-%m-%d %H:%M:%S')

    for i in range(len(df)):
        data_name = str(df['판매일시'][i])[:10]
        pre_name = term0_pre(data_name)[5:10]

        if to_between(df['판매일시'][i]):
            if data_name not in result:
                result[data_name] = df['합계가격'][i]
            else:
                result[data_name] += df['합계가격'][i]

        # 09:00:00 미만
        else:
            if pre_name not in result:
                result[pre_name] = df['합계가격'][i]

            else:
                result[pre_name] += df['합계가격'][i]

    del sit[0]
    del name['-(-)']
    if '주차비용' in sale.keys():
        del sale['주차비용']

    sit = sorted(sit.items(), key=lambda x: (-x[1], x[0]))
    pay = sorted(pay.items(), key=lambda x: (-x[1], x[0]))
    name = sorted(name.items(), key=lambda x: (-x[1], x[0]))
    cate = sorted(cate.items(), key=lambda x: (-x[1], x[0]))
    sale = sorted(sale.items(), key=lambda x: (-x[1], x[0]))
    time = sorted(time.items(), key=lambda x: (-x[1], x[0]))
    result = sorted(result.items(), key=lambda x: (-x[1], x[0]))

    return (sit[rank][0], sit[rank][1],
            pay[rank][0], pay[rank][1],
            name[rank][0], name[rank][1],
            cate[rank][0], cate[rank][1],
            sale[rank][0], sale[rank][1],
            time[rank][0], time[rank][1],
            result[rank][0], result[rank][1]
            )


def catesaleRanke(text):
    path = os.path.join(st.Fdata_path, text)
    df = pd.read_csv(path)
    catesale = {}

    df = df[(df['상품분류'] != '프린트')]
    for q in range(len(df)):  # 카테고리 별 상품 순위
        c = df.iloc[q, 1]
        i = df.iloc[q, 2]
        j = int(df.iloc[q, 3])
        # structure
        # catesale = {'상품분류' : {'상품명' : 1}, }
        if c not in catesale:
            catesale[c] = {}
            catesale[c][i] = j
        elif c in catesale and i not in catesale[c]:
            catesale[c][i] = j
        else:
            catesale[c][i] += j

    catesale_key = []  # '상품분류' list
    for i in catesale:
        catesale_key.append(i)
    for i in catesale_key:
        catesale[i] = sorted(catesale[i].items(), key=lambda x: x[1], reverse=True)

    return catesale, catesale_key
