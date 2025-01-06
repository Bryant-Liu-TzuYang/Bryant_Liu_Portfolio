import csv
import csvsorter
import os
import pandas as pd

# 讀入原始資料
fn_org_data = "TEJ Data/上市櫃調整股價日-除權息調整.csv"
fh_data = open(fn_org_data, 'r', encoding= 'cp950', newline='')
reader1 = csv.reader(fh_data, delimiter=',')

# 設定暫存資料位置並準備將原始資料內容寫入
stockfn_tmp1 = "TEJ Data/stockfn_tmp1.csv"
stockfh_tmp1 = open(stockfn_tmp1, 'w', encoding='utf-8', newline='')
writer3 = csv.writer(stockfh_tmp1)  # 寫出新的 csv 資料 

for rows in reader1:
    arow = map(lambda x: x.strip(), rows)
    writer3.writerow(arow)

# 將初步轉換好的資料（暫存資料），進一步切出公司名稱跟代碼
df = pd.read_csv(stockfn_tmp1)
df[["證券代碼", "公司名稱"]] = df["證券代碼"].str.split(" ", expand=True)

# 切出來後公司名稱會跑到最後面，把它移到前面
company_name = df["公司名稱"]
df = df.drop(columns=["公司名稱"])
df.insert(loc=1, column="公司名稱", value=company_name)

df.to_csv("TEJ Data/fn_data2.csv", index=False)

stockfn_sorted = "TEJ Data/stockfn_sorted.csv"
csvsorter.csvsort(stockfn_tmp1, [0,2], output_filename=stockfn_sorted, has_header=True)

fh_data.close()
stockfh_tmp1.close()

'''原始資料整理完畢'''
