## 解釋各 instance 的功能
### Group 1: easy case
0. 用來確認我們的 model 跑的動，但資料是假的 <br>
   _real：把 instance0 中的資料換成真實世界的數據
1. 將所有景點的 happiness 設成 0，理論上 output 會是 0
2. 將所有 cost 設成 0
3. 將所有交通方式所需時間設定成 10 hr = 600 min
4. 將 RH 跟 LH 設成只差 1 分鐘

### Group 2: mid case
0. _real 用大一點且為真實世界的 instance
1. 將所有景點的 happiness 設成 0，理論上 output 會是 0
2. 將所有 cost 設成 0
3. 將所有交通方式所需時間設定成 5 hr = 300 min
4. 將 RH 跟 LH 設成只差 1 分鐘
5. 故意給他多一點預算看會不會換飯店，也故意把第一天住的飯店的價格故意調高
6. 給他一堆錢跟天數
7. 當天數超過景點數
8. 只給他三天