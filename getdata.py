import numpy as np


# 日付から配列内に格納されている日付の順番を得る自作関数searchの定義
# def search(list_1, date_selected, default=False):
#    if date_selected in list_1:
#        value_1 = list_1.index(date_selected)
#        return value_1
#    else:
#        return default
# 自作関数searchの定義終了


# csvファイルから特定の行のデータを得るための自作関数getdataの定義
def getdata(i, j):
    data = np.loadtxt(
        fname=r"2020process.csv",
        dtype="float",
        encoding='shift_jis',
        delimiter=",",
        skiprows=10 + i * 24 + j,
        max_rows=1,
        usecols=(2, 7)
    )
    data = data / 100
    return data
# 自作関数getdataの定義終了


# 実際にデータがとれているかの実験
# date_list = ["2020/04/07", "2020/04/17", "2020/06/03", "2020/06/07", "2020/08/09", "2020/10/03", "2021/01/07", "2021/03/15"]

# date_select = "2021/01/07"
# date_value = search(date_list, date_select)
date_value = 0
hour_value = 2
print(f'{getdata(i = date_value, j = hour_value)}')
# date_selectに日付を入れることによって、リスト内の何番目にその日付があるかを自作関数searchで探索可能。
# pygameより、直接日付が何番目にあるかのデータをdate_valueに代入することで、自作関数searchの部分は省略可能。
# hour_valueに0時から23時までの数字を指定可能。
