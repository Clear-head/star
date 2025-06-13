from collections import defaultdict
from utils import term0_pre, to_between
import os
import pandas as pd
from Setting import Fdata_path

"""
    rankform 관련 함수
"""

def count_frequency(series):
    freq = defaultdict(int)
    for value in series:
        freq[value] += 1
    return freq

def accumulate_sales(df, name_col, value_col):
    sales = defaultdict(int)
    for name, value in zip(df[name_col], df[value_col]):
        sales[name] += value
    return sales

def process_time_orders(df, time_col):
    time_freq = defaultdict(int)
    for timestamp in df[time_col]:
        date_str = str(timestamp)[:11]
        prev_day = term0_pre(date_str)

        key = date_str if to_between(timestamp) else prev_day
        time_freq[key] += 1
    return time_freq

def process_date_sales(df, time_col, value_col):
    result = defaultdict(int)
    df[time_col] = pd.to_datetime(df[time_col], format='%Y-%m-%d %H:%M:%S')

    for timestamp, value in zip(df[time_col], df[value_col]):
        date_key = str(timestamp)[:10]
        prev_key = term0_pre(date_key)[5:10]

        key = date_key if to_between(timestamp) else prev_key
        result[key] += value

    return result

def sort_and_rank(d):
    return sorted(d.items(), key=lambda x: (-x[1], x[0]))

def ranking(text, rank):
    path = os.path.join(Fdata_path, text)
    df = pd.read_csv(path)
    df = df[df['상품분류'] != '프린트']

    sit = count_frequency(df['PC번호'])
    pay = count_frequency(df['결제수단'])
    name = count_frequency(df['고객명(ID)'])
    cate = count_frequency(df['상품분류'])
    sale = accumulate_sales(df, '상품명', '합계가격')
    time = process_time_orders(df, '판매일시')
    result = process_date_sales(df[['판매일시', '합계가격']].copy(), '판매일시', '합계가격')

    # 예외 처리
    sit.pop(0, None)
    name.pop('-(-)', None)
    sale.pop('주차비용', None)

    sit = sort_and_rank(sit)
    pay = sort_and_rank(pay)
    name = sort_and_rank(name)
    cate = sort_and_rank(cate)
    sale = sort_and_rank(sale)
    time = sort_and_rank(time)
    result = sort_and_rank(result)

    return (
        sit[rank][0], sit[rank][1],
        pay[rank][0], pay[rank][1],
        name[rank][0], name[rank][1],
        cate[rank][0], cate[rank][1],
        sale[rank][0], sale[rank][1],
        time[rank][0], time[rank][1],
        result[rank][0], result[rank][1]
    )

def catesaleRanke(text):
    path = os.path.join(Fdata_path, text)
    df = pd.read_csv(path)
    df = df[df['상품분류'] != '프린트']

    catesale = defaultdict(lambda: defaultdict(int))

    for _, row in df.iterrows():
        category = row['상품분류']
        item = row['상품명']
        price = int(row['합계가격'])
        catesale[category][item] += price

    catesale_sorted = {}
    for cat, items in catesale.items():
        catesale_sorted[cat] = sorted(items.items(), key=lambda x: x[1], reverse=True)

    return catesale_sorted, list(catesale_sorted.keys())