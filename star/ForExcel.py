import os
import pandas as pd
import Setting as st
import re

excel_list = []
weather_list = []
AIdata_list = []
Fdata_list = {}

data_name = []


def find_m(path, excel_name):  # 엑셀의 날짜 찾는 함수
    """
    :param path: file path
    :param excel_name: file name
    :return: string ex) 2022-01
    """
    col = [0]
    path = os.path.join(path, excel_name)
    if excel_name.endswith('.xls'):
        df = pd.read_excel(path, usecols=col, engine='xlrd')
    else:
        df = pd.read_csv(path, usecols=col)
    l_day = str(df.iloc[0])
    f_day = str(df.iloc[-1])

    l_day = re.sub(r'[^0-9]', '', l_day)
    f_day = re.sub(r'[^0-9]', '', f_day)

    return f_day[0:8], l_day[0:8]


def to_AIdata(path, excel_name):
    import GraphMethod as gm
    """
    :param path: fdata path
    :param excel_name: fdata name
    :return:
    """
    f, w = find_m(path, excel_name)
    f = f[0:4] + "-" + f[4:6]
    col = [0, 4]

    df = pd.read_csv(os.path.join(path, excel_name), usecols=col)

    for i in range(len(df)):
        a = str(df.iloc[i, 0])
        if gm.to_between(a):
            df.iloc[i, 0] = a[:10]
        else:
            df.iloc[i, 0] = gm.term0_pre(a[:10])
    temp = {}
    for i in range(len(df)):
        a = str(df.iloc[i, 0])
        b = int(df.iloc[i, 1])
        if a not in temp:
            temp[a] = b
        else:
            temp[a] += b

    del df
    sale_df = pd.DataFrame({'판매일시': temp.keys(), '합계가격': temp.values()})
    sale_df['판매일시'] = pd.to_datetime(sale_df['판매일시'], format='%Y-%m-%d')
    sale_df = sale_df.sort_values(by='판매일시', ascending=False)

    sale_df.to_csv(os.path.join(st.AIdata_path, f + "_data.csv"),
                   index=False, columns=['판매일시', '합계가격'],
                   encoding="utf-8-sig")

    st.add_AIdata_list(a + "_data.csv")


def to_Fdata():
    global fdataf, start_date
    df_list = []
    col = [1, 2, 3, 4, 6, 7, 8, 9]

    for i in os.listdir(st.folder_path):
        if i not in excel_list and i.endswith('.xls'):
            fdf = pd.read_excel(os.path.join(st.folder_path, i), usecols=col, engine='xlrd')
            df_list.append(fdf)

    if len(df_list) > 0:
        df = pd.concat(df_list, ignore_index=True)
        df = df[(df['합계가격'] != 0) & (df['결제수단'] != '서비스')]
        df = df.drop_duplicates()
        df = df.reset_index(drop=True)
    else:
        return

    for i in range(len(df['판매일시'])):
        temp = df.at[i, '판매일시']
        temp = list(temp.replace('/', '-'))
        df.at[i, '판매일시'] = '20' + "".join(temp)

    df['판매일시'] = pd.to_datetime(df['판매일시'], format='%Y-%m-%d %H:%M:%S')
    df = df.sort_values(by='판매일시', ascending=False)

    while len(df['판매일시']) > 0:
        df = df.reset_index(drop=True)

        df_time1 = df['판매일시'].iloc[-1]
        p = str(df_time1.year) + '-' + str(df_time1.month) + '-01 09:00:00'

        if str(df_time1.month) == '12':
            q = str(int(df_time1.year) + 1) + '-' + '01-01 08:59:59'
        else:
            q = str(df_time1.year) + '-' + str(int(df_time1.month) + 1) + '-01 08:59:59'

        start_date = pd.to_datetime(p, format='%Y-%m-%d %H:%M:%S')
        last_date = pd.to_datetime(q, format='%Y-%m-%d %H:%M:%S')

        new_df = df.loc[df["판매일시"].between(start_date, last_date)]

        new_df.to_csv(os.path.join(st.Fdata_path, str(start_date)[:7] + '.csv'), index=False, encoding="utf-8-sig")

        st.add_fdata_list(str(start_date)[:7] + '.csv', 'True')

        df.drop(new_df.index, inplace=True)
        if df.index is None:
            break
