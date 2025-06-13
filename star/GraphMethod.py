import os
import pandas as pd
import Setting as st
from collections import defaultdict
from PySide6.QtCore import QDate
from utils import format_month, format_day, term0, generate_daily_labels, term0_pre, to_between


def format_day(day: int) -> str:
    return str(day) if day > 9 else '0' + str(day)

def format_month(month: int) -> str:
    return str(month) if month > 9 else '0' + str(month)

def leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def get_days_in_month(month: int, year: int) -> int:
    if month == 2:
        return 29 if leap_year(year) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31

def generate_daily_labels(year: int, month: int) -> list:
    days = get_days_in_month(month, year)
    month_str = format_month(month)
    return [f"{month_str}-{format_day(day)}" for day in range(1, days + 1)]

def term0_pre(key):
    yy, mm, dd = key.split('-')
    yy = int(yy)
    mm = int(mm)
    dd = int(dd)

    if dd == 1:
        if mm == 1:
            yy -= 1
            mm = 12
            dd = 31
        elif mm == 3:
            mm = 2
            dd = 29 if leap_year(yy) else 28
        elif mm in [5, 7, 8, 10, 12]:
            mm -= 1
            dd = 30
        else:
            mm -= 1
            dd = 31
    else:
        dd -= 1

    return f"{yy}-{format_month(mm)}-{format_day(dd)}"

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

# CSV 파일 처리 관련 함수들
def get_csv_path(date):
    """날짜를 기반으로 CSV 파일 경로 생성"""
    year = str(date.year())
    month = format_month(date.month())
    return os.path.join(st.Fdata_path, year + '-' + month + '.csv')

def read_sales_data(path):
    """판매 데이터 CSV 파일 읽기"""
    return pd.read_csv(path, usecols=[0, 2, 3, 4])

def read_sales_data_for_amount(path):
    """판매 데이터 CSV 파일에서 필요한 컬럼만 읽기"""
    usecol = [0, 4, 7]
    df = pd.read_csv(path, usecols=usecol)
    return df[['판매일시', '합계가격']]

def get_unique_product_names(df):
    """데이터프레임에서 중복 없는 상품명 리스트 추출"""
    return df['상품명'].drop_duplicates().tolist()

def filter_dataframe_by_date_range(df, date):
    """일자별 데이터 필터링"""
    df['판매일시'] = pd.to_datetime(df['판매일시'])
    
    fl = term0(date)
    f_day = pd.to_datetime(fl[0], format='%Y-%m-%d %H:%M:%S')
    l_day = pd.to_datetime(fl[1], format='%Y-%m-%d %H:%M:%S')
    
    return df[df['판매일시'].between(f_day, l_day)]

def get_yearly_data(year):
    """연도별 모든 CSV 파일 데이터 통합"""
    df_list = []
    for filename in os.listdir(st.Fdata_path):
        if filename.startswith(year):
            file_path = os.path.join(st.Fdata_path, filename)
            df = read_sales_data(file_path)
            df_list.append(df)
    
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        return df.drop_duplicates()
    return pd.DataFrame()

# item_name 관련 함수들
def process_daily_data(date):
    """일자별 데이터 처리"""
    path = get_csv_path(date)
    df = read_sales_data(path)
    df = filter_dataframe_by_date_range(df, date)
    name = get_unique_product_names(df)
    return name, df

def process_monthly_data(date):
    """월별 데이터 처리"""
    path = get_csv_path(date)
    df = read_sales_data(path)
    name = get_unique_product_names(df)
    return name, df

def process_yearly_data(date):
    """연도별 데이터 처리"""
    year = str(date.year())
    df = get_yearly_data(year)
    name = get_unique_product_names(df)
    return name, df

def item_name(term, date):  # term =(0 : day) (1 : month) (2 : year)
    """
    기간별 상품명 목록과 데이터프레임 반환
    
    Args:
        term (int): 0=일자별, 1=월별, 2=연도별
        date: 날짜 객체
    
    Returns:
        tuple: (상품명 리스트, 데이터프레임)
    """
    if term == 0:
        return process_daily_data(date)
    elif term == 1:
        return process_monthly_data(date)
    else:
        return process_yearly_data(date)

# get_dt 함수
def get_dt(term, date):
    data_name = []

    year = str(date.year())
    month_int = date.month()
    month = format_month(month_int)

    if term == 0:
        # 현재 월 데이터
        data_name.extend(generate_daily_labels(date.year(), month_int))

        # 다음 달 1일 추가
        next_month = month_int + 1
        if next_month > 12:
            data_name.append("01-01")
        else:
            data_name.append(f"{format_month(next_month)}-01")

    elif term == 1:
        # 월별 데이터
        data_name = [f"{year}-{format_month(m)}" for m in range(1, 13)]

    else:
        # 연도별 데이터
        for i in os.listdir(st.Fdata_path):
            year_prefix = i[:4]
            if year_prefix not in data_name:
                data_name.append(year_prefix)

    return data_name

# count_item 관련 함수들
def filter_count_data_by_date(df, date):
    """count_item용 날짜별 데이터 필터링"""
    fl = term0(date)
    f_day = pd.to_datetime(fl[0], format='%Y-%m-%d %H:%M:%S')
    l_day = pd.to_datetime(fl[1], format='%Y-%m-%d %H:%M:%S')
    
    return df[df['판매일시'].between(f_day, l_day)]

def prepare_count_dataframe(df, cs):
    """count_item용 데이터프레임 준비"""
    column_name = '판매개수' if cs == 0 else '합계가격'
    return df[['판매일시', '상품명', column_name]]

def accumulate_product_data(df, data):
    """상품별 데이터 누적"""
    product_names = df.iloc[:, 1]  # 상품명 컬럼
    values = df.iloc[:, 2]  # 판매개수 또는 합계가격 컬럼
    
    for product_name, value in zip(product_names, values):
        data[product_name] += int(value)

def process_daily_count_data(df, date, data):
    """일자별 count 데이터 처리"""
    filtered_df = filter_count_data_by_date(df, date)
    accumulate_product_data(filtered_df, data)

def process_general_count_data(df, data):
    """일반 count 데이터 처리 (월별, 연도별)"""
    accumulate_product_data(df, data)

def count_item(term, date, data, cs, df):
    """
    :param df: dataframe made item_name
    :param term: int
    :param date: Qdate, ex) 2023-10-13 11:15
    :param data: dic, already keys in data
    :param cs: int : count -> 0 or sale -> 1
    :return: dic, finished data
    """
    df = prepare_count_dataframe(df, cs)

    if term == 0:
        process_daily_count_data(df, date, data)
    else:
        process_general_count_data(df, data)

    return data

# getSale 관련 함수들
def process_daily_sales_data(df, data):
    """일자별 판매 데이터 처리"""
    df['판매일시'] = pd.to_datetime(df['판매일시'], format='%Y-%m-%d %H:%M:%S')
    df = df.sort_values(by='판매일시', ascending=False)
    
    for i in range(len(df)):
        sale_datetime = df.iloc[i, 0]
        sale_amount = int(df.iloc[i, 1])
        
        data_name = str(sale_datetime)[5:10]
        pre_name = term0_pre(str(sale_datetime)[:10])[5:10]
        
        if to_between(sale_datetime):
            data[data_name] += sale_amount
        else:
            data[pre_name] += sale_amount

def process_monthly_sales_data(year, data):
    """월별 판매 데이터 처리"""
    for filename in os.listdir(st.Fdata_path):
        if filename.startswith(year):
            file_path = os.path.join(st.Fdata_path, filename)
            df = read_sales_data_for_amount(file_path)
            
            month_key = filename[:7]  # YYYY-MM 형태
            for row in df.itertuples():
                data[month_key] += int(row[2])

def process_yearly_sales_data(data):
    """연도별 판매 데이터 처리"""
    df_list = []
    
    # 모든 CSV 파일 읽어서 통합
    for filename in os.listdir(st.Fdata_path):
        file_path = os.path.join(st.Fdata_path, filename)
        df = read_sales_data_for_amount(file_path)
        df_list.append(df)
    
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        df = df.drop_duplicates()
        
        for row in df.itertuples():
            year_key = str(row[1][:4])  # 연도 추출
            data[year_key] += int(row[2])

def process_daily_sale(date, data):
    """일자별 판매 데이터 처리 메인 함수"""
    path = get_csv_path(date)
    df = read_sales_data_for_amount(path)
    print('data')
    print(data)
    process_daily_sales_data(df, data)

def process_monthly_sale(date, data):
    """월별 판매 데이터 처리 메인 함수"""
    year = str(date.year())
    process_monthly_sales_data(year, data)

def process_yearly_sale(data):
    """연도별 판매 데이터 처리 메인 함수"""
    process_yearly_sales_data(data)

def getSale(term, date, data):
    """
    기간별 판매 데이터 집계
    
    Args:
        term (int): 0=일자별, 1=월별, 2=연도별
        date: 날짜 객체
        data (dict): 집계 결과를 저장할 딕셔너리
    
    Returns:
        dict: 업데이트된 판매 데이터 딕셔너리
    """
    if term == 0:
        process_daily_sale(date, data)
    elif term == 1:
        process_monthly_sale(date, data)
    else:
        process_yearly_sale(data)
    
    return data

def Color(count):
    count = len(count)
    base_colors = ['#669909', '#FFAA00', '#00FF00', '#FF6969', '#6868FC']
    repeat_times = count // len(base_colors)
    remainder = count % len(base_colors)

    return base_colors * repeat_times + base_colors[:remainder]

def delete_data(data):
    max_value = max(data.values())
    threshold = max_value * 0.05

    removed_total = sum(value for key, value in data.items() if value < threshold)
    data = {key: value for key, value in data.items() if value >= threshold}

    data['기타'] = removed_total
    return data