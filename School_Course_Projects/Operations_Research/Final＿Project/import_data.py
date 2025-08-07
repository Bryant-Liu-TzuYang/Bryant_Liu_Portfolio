def load_file(file_path: str) -> dict:
    """
    從劉子揚生成的各種 instance 檔案中讀取資料 \\
    param: file_path: 檔案路徑，直接放例如 "instance0_v1.xlsx" 就可以了 \\
    return: 讀取的資料
    """

    import pandas as pd
    import numpy as np  

    ### 從 Excel檔案讀取資料存成 dataframe ###
    df_basic = pd.read_excel(file_path, sheet_name='Basic', index_col=0, header=0)

    df_hotel_time = pd.read_excel(file_path, sheet_name='Hotel_Time', index_col=0, header=0)
    df_hotel_cost = pd.read_excel(file_path, sheet_name='Hotel_Cost', index_col=0, header=0)

    df_attraction_cost = pd.read_excel(file_path, sheet_name='Attraction_Cost', index_col=0, header=0)
    df_attrcation_open = pd.read_excel(file_path, sheet_name='Attraction_Open', index_col=0, header=0)
    df_attrcation_close = pd.read_excel(file_path, sheet_name='Attraction_Close', index_col=0, header=0)

    df_walk_time = pd.read_excel(file_path, sheet_name='Walk_Time', index_col=0, header=0)
    df_train_time = pd.read_excel(file_path, sheet_name='Train_Time', index_col=0, header=0)
    df_car_time = pd.read_excel(file_path, sheet_name='Car_Time', index_col=0, header=0)

    df_train_cost = pd.read_excel(file_path, sheet_name='Train_Cost', index_col=0, header=0)
    df_car_cost = pd.read_excel(file_path, sheet_name='Car_Cost', index_col=0, header=0)

    df_stay_happy = pd.read_excel(file_path, sheet_name='Stay_Happy', index_col=0, header=0)
    

    # BUDGET
    BUDGET = int(df_basic.iloc[0, 0])
    # M = len(Set of hotels and airpots)
    M = int(df_basic.iloc[1, 0])
    I = int(df_basic.iloc[2, 0])
    P = int(df_basic.iloc[3, 0])
    D = int(df_basic.iloc[4, 0])
    K = int(df_basic.iloc[5, 0])

    # 第一天抵達的時間
    # 在這個 instance0 中值是 540 = 540 / 60 = 早上 9:00
    Day1Arrival = df_basic.iloc[6, 0]
    print(Day1Arrival)

    LH = df_hotel_time.iloc[0:df_hotel_time.shape[0], 0]
    RH = df_hotel_time.iloc[0:df_hotel_time.shape[0], 1]
    

    STAY = df_stay_happy.iloc[0:df_stay_happy.shape[0], 0]  # stay time
    HAPPINESS = df_stay_happy.iloc[0:df_stay_happy.shape[0], 1]  # happiness

    ### 接下來會把不同交通方式所需的時間矩陣存到一個字典 DURATION 中 ###
    # 設一個變數存取不同地點到不同地點走路所需的時間矩陣
    walk_time = np.zeros((df_walk_time.shape[0], df_walk_time.shape[1]))
    for i in range(df_walk_time.shape[0]):
        for j in range(df_walk_time.shape[1]):
            walk_time[i][j] = df_walk_time.iloc[i, j]
    
    # 設一個變數存取不同地點到不同地點搭火車所需的時間矩陣
    train_time = np.zeros((df_train_time.shape[0], df_train_time.shape[1]))
    for i in range(df_train_time.shape[0]):
        for j in range(df_train_time.shape[1]):
            train_time[i][j] = df_train_time.iloc[i, j]
    
    # 設一個變數存取不同地點到不同地點搭計程車所需的時間矩陣
    car_time = np.zeros((df_car_time.shape[0], df_car_time.shape[1]))
    for i in range(df_car_time.shape[0]):
        for j in range(df_car_time.shape[1]):
            car_time[i][j] = df_car_time.iloc[i, j]

    DURATION = {
        'Walk': walk_time,
        'Train': train_time,
        'Car': car_time
    }

    ### 接下來會把不同交通方式所需的費用矩陣存到一個字典 C_TRAVEL 中 ###
    # 設一個變數存取不同地點到不同地點搭火車所需的花費矩陣
    walk_cost = np.zeros((df_train_cost.shape[0], df_train_cost.shape[1]))
    train_cost = np.zeros((df_train_cost.shape[0], df_train_cost.shape[1]))
    for i in range(df_train_cost.shape[0]):
        for j in range(df_train_cost.shape[1]):
            train_cost[i][j] = df_train_cost.iloc[i, j]

    # 設一個變數存取不同地點到不同地點搭計程車所需的花費矩陣
    car_cost = np.zeros((df_car_cost.shape[0], df_car_cost.shape[1]))
    for i in range(df_car_cost.shape[0]):
        for j in range(df_car_cost.shape[1]):
            car_cost[i][j] = df_car_cost.iloc[i, j]

    # 把兩種交通方式的花費矩陣包裝到一個字典中
    C_TRAVEL = {
        'Walk':walk_cost,
        'Train': train_cost,
        'Car': car_cost
    }


    C_HOTEL = np.zeros((df_hotel_cost.shape[0], df_hotel_cost.shape[1]))
    for i in range(df_hotel_cost.shape[0]):
        for j in range(df_hotel_cost.shape[1]):
            C_HOTEL[i][j] = df_hotel_cost.iloc[i, j]

    C_ATTRACTION = np.zeros(df_attraction_cost.shape[0])
    for i in range(df_attraction_cost.shape[0]):
            C_ATTRACTION[i] = df_attraction_cost.iloc[i]
            
    ATTRACTION_OPEN = np.zeros((df_attrcation_close.shape[0], df_attrcation_close.shape[1]))
    for i in range(df_attrcation_open.shape[0]):
        for j in range(df_attrcation_open.shape[1]):
            ATTRACTION_OPEN[i][j] = df_attrcation_open.iloc[i, j]

    ATTRACTION_CLOSE = np.zeros((df_attrcation_close.shape[0], df_attrcation_close.shape[1]))
    for i in range(df_attrcation_close.shape[0]):
        for j in range(df_attrcation_close.shape[1]):
            ATTRACTION_CLOSE[i][j] = df_attrcation_close.iloc[i, j]

    # 把參數包裝到一個字典中傳回
    results = {
        'BUDGET': BUDGET,
        'M': M,
        'I': I,
        'P': P,
        'D': D,
        'K': K,
        'LH': LH,
        'RH': RH,
        'Day1Arrival': Day1Arrival,
        'STAY': STAY,
        'HAPPINESS': HAPPINESS,
        'DURATION': DURATION,
        'C_TRAVEL': C_TRAVEL,
        'C_HOTEL': C_HOTEL,
        'C_ATTRACTION': C_ATTRACTION,
        'ATTRACTION_OPEN': ATTRACTION_OPEN,
        'ATTRACTION_CLOSE': ATTRACTION_CLOSE
    }
    
    return results