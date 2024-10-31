import json
import requests
import Setting as st
import os

url = "http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList"
EncodeKey = "7Gp0N%2Fx4rJeOMwrauxl2%2BZqjmeyCxyKCBl9vIyR2GX%2BQbTv6BXg26tj%2BeV%2BZmmxu98AMhkmj8AAOKlVmgAkg1w%3D%3D"
DecodeKey = "7Gp0N/x4rJeOMwrauxl2+ZqjmeyCxyKCBl9vIyR2GX+QbTv6BXg26tj+eV+Zmmxu98AMhkmj8AAOKlVmgAkg1w=="


def para(F_date, L_date, key):  # key == decodekey
    a = 0
    a += 31 if L_date[6:8] == '31' else 30

    para = {'serviceKey': key,
            "numOfRows": a,
            "pageNo": 1,
            "dataType": "JSON",
            "dataCd": "ASOS",
            "dateCd": "DAY",
            "startDt": F_date,
            "endDt": L_date,
            "stnIds": 119}

    return para


def take_json(url, para):  # api 에서 받아 오기
    data_key = ["tm", "avgTa", "minTa", "minTaHrmt", "maxTa", "maxTaHrmt", "sumRnDur", "sumRn"]
    # trans_key = ["time", "average temperature", "minimum temperature", "minimum temperature time",
    #              "maximum temperature", "maximum temperature time", "sumRnDur", "sumRn"]
    trans_key = ['시간', '평균 기온(°C)', '최저 기온(°C)', '최저 기온 시각(hhmi)'
        , '최고 기온(°C)', '최고 기온 시각(hhmi)', '강수 계속시간(hr)', '일강수량(mm)']

    data_value = []
    return_value = []
    res = requests.get(url, params=para)
    parse_json = json.loads(res.text)
    j_data = parse_json["response"]["body"]["items"]["item"]

    for i in range(len(j_data)):
        data_dict = j_data[i]
        for j in range(len(data_key)):
            s = data_dict[data_key[j]]
            data_value.append(s)

    return_value.append(trans_key)
    return_value.append(data_value)

    return return_value


def j_to_c(data_name, data):  # 존재하는 날짜의 파일을 안만들게 하는 부분도 추가 해야함
    name = data[0][:4] + '-' + data[0][5:7]
    path = os.path.join(st.AIdata_path, "weather_data_" + name + ".csv")

    with open(path, "w") as f:
        for i in data_name:
            if not i == "sumRn":
                f.write(i + ", ")
            else:
                f.write(i)
        f.write("\n")
        cnt = 0

        for i in data:
            if i == '':
                i = '0'

            cnt += 1

            if not cnt % 8 == 0:
                f.write(i + ", ")
            else:
                f.write(i)
                f.write("\n")

# 실험
# a, b = fe.find_m(fg.folder_path,'2022-05.xls')
# para1 = para(a, b, DecodeKey)
# data_name, data2 = take_json(url, para1)
# j_to_c(data_name, data2)

# 만약 사용 하게 된다면
# for i in fe.excel_list:
#     a, b = fe.find_m(i)
#     para1 = para(a, b, DecodeKey)
#     data_name, data = take_json(url, para1)
#     j_to_c(data_name, data)
# 이런 식 으로 사용 하게 될 것 같음
