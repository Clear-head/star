import os
import pandas as pd
import Setting as st
import re

"""

    엑셀 읽고 정리

"""


excel_list = []
weather_list = []
AIdata_list = []
Fdata_list = {}

data_name = []


def find_m(path, excel_name):
    """
    엑셀의 날짜 찾는 함수

    :param path: file path
    :param excel_name: file name
    :return: string ex) 2022-01
    """
    file_path = os.path.join(path, excel_name)
    col = [0]

    if excel_name.endswith('.xls'):
        df = pd.read_excel(file_path, usecols=col, engine='xlrd')
    else:
        df = pd.read_csv(file_path, usecols=col)

    start_day = re.sub(r'[^0-9]', '', str(df.iloc[0]))
    end_day = re.sub(r'[^0-9]', '', str(df.iloc[-1]))

    return start_day[:8], end_day[:8]


def to_AIdata(path, excel_name):
    import GraphMethod as gm

    start_day, _ = find_m(path, excel_name)
    month_str = f"{start_day[:4]}-{start_day[4:6]}"
    file_path = os.path.join(path, excel_name)

    df = pd.read_csv(file_path, usecols=[0, 4])

    for i in range(len(df)):
        raw_date = str(df.iloc[i, 0])
        df.iloc[i, 0] = gm.term0_pre(raw_date[:10]) if not gm.to_between(raw_date) else raw_date[:10]

    sales_summary = {}

    for date_str, price in zip(df.iloc[:, 0], df.iloc[:, 1]):
        sales_summary[date_str] = sales_summary.get(date_str, 0) + int(price)

    sale_df = pd.DataFrame({
        '판매일시': pd.to_datetime(list(sales_summary.keys()), format='%Y-%m-%d'),
        '합계가격': list(sales_summary.values())
    }).sort_values(by='판매일시', ascending=False)

    output_file = os.path.join(st.AIdata_path, f"{month_str}_data.csv")
    sale_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    st.add_AIdata_list(f"{month_str}_data.csv")


def to_Fdata():
    global fdataf, start_date

    col = [1, 2, 3, 4, 6, 7, 8, 9]
    df_list = []

    for file in os.listdir(st.folder_path):
        if file.endswith('.xls') and file not in excel_list:
            df_list.append(pd.read_excel(os.path.join(st.folder_path, file), usecols=col, engine='xlrd'))

    if not df_list:
        return

    df = pd.concat(df_list, ignore_index=True)
    df = df[(df['합계가격'] != 0) & (df['결제수단'] != '서비스')].drop_duplicates().reset_index(drop=True)

    df['판매일시'] = df['판매일시'].apply(lambda x: '20' + x.replace('/', '-'))
    df['판매일시'] = pd.to_datetime(df['판매일시'], format='%Y-%m-%d %H:%M:%S')
    df.sort_values(by='판매일시', ascending=False, inplace=True)

    while not df.empty:
        df.reset_index(drop=True, inplace=True)

        start_dt = df['판매일시'].iloc[-1]
        start_str = f"{start_dt.year}-{start_dt.month:02d}-01 09:00:00"
        end_str = (
            f"{start_dt.year + 1}-01-01 08:59:59" if start_dt.month == 12
            else f"{start_dt.year}-{start_dt.month + 1:02d}-01 08:59:59"
        )

        start_date = pd.to_datetime(start_str, format='%Y-%m-%d %H:%M:%S')
        last_date = pd.to_datetime(end_str, format='%Y-%m-%d %H:%M:%S')

        monthly_df = df[df["판매일시"].between(start_date, last_date)]

        output_file = os.path.join(st.Fdata_path, f"{str(start_date)[:7]}.csv")
        monthly_df.to_csv(output_file, index=False, encoding="utf-8-sig")
        st.add_fdata_list(f"{str(start_date)[:7]}.csv", 'True')

        df.drop(monthly_df.index, inplace=True)
