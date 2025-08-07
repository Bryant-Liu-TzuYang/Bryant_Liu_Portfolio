// 開啟 Google Sheets 檔案
const 帳本 = SpreadsheetApp.openByUrl("alink");
const 隊服訂購 = SpreadsheetApp.openByUrl("alink");
const 寒訓出遊 = SpreadsheetApp.openByUrl("alink");
const 通訊錄有場時段待辦事項 = SpreadsheetApp.openByUrl("alink");

// 從不同檔案中取得指定的工作表
const 試算 = 帳本.getSheetByName("每人隊費、球衣、寒訓費用試算");
const 練球確認表 = 寒訓出遊.getSheetByName("練球、住宿確認表");
const 搭車確認表 = 寒訓出遊.getSheetByName("搭車確認表");
const 隊服訂購名單 = 隊服訂購.getSheetByName("訂購名單");
const 通訊錄 = 通訊錄有場時段待辦事項.getSheetByName("通訊錄");

// 取得工作表數據
const 搭車確認表數據 = 搭車確認表.getDataRange().getValues();
const 練球確認表數據 = 練球確認表.getDataRange().getValues();
const 隊服訂購名單數據 = 隊服訂購名單.getDataRange().getValues();
const 通訊錄數據 = 通訊錄.getDataRange().getValues();


// <basic functions>
function getname(sheet) {
  // 取得人名
  var 人名 = sheet.getRange(4,1).getValue();
  return 人名;
}


function getnamerow(sheet) {
  // 遍歷數據找到匹配的行數
  for (var i = 0; i < sheet.length; i++) {
    //[列][行]
    if (sheet[i][0] == 人名) {
      // 找到匹配的人名，輸出行數
      return i
    }
  }
}


// <car model>
function car() {
  // 判斷有沒有搭車並輸出給出搭車費用
  var 人名所在列數 = getnamerow(搭車確認表數據)
  if (人名所在列數 == null) {
    return 0
  }
  
  var sum_car = 0
  if (搭車確認表數據[人名所在列數][1] == true) {
    sum_car += 140
  }

  if (搭車確認表數據[人名所在列數][2] == true) {
    sum_car += 140
  }

  return sum_car
}



// <training_hotel model>
function training_hotel() {
// 開始算隊費
  var 人名所在列數 = getnamerow(練球確認表數據)
  
  if (人名所在列數 == null) {
    return 0
  }
  
  var sum_training_hotel = 0
  if (練球確認表數據[人名所在列數][1] == true) {
    sum_training_hotel += 200
  }
  if (練球確認表數據[人名所在列數][2] == true) {
    sum_training_hotel += 683
  }
  if (練球確認表數據[人名所在列數][3] == true) {
    sum_training_hotel += 143
  }
  if (練球確認表數據[人名所在列數][4] == true) {
    sum_training_hotel += 69
  }
  if (練球確認表數據[人名所在列數][5] == true) {
    sum_training_hotel += 700
  }
  if (練球確認表數據[人名所在列數][6] == true) {
    sum_training_hotel += 120
  }
  if (練球確認表數據[人名所在列數][7] == true) {
    sum_training_hotel += 75
  }
  if (練球確認表數據[人名所在列數][8] == true) {
    sum_training_hotel += 1200
  }
  return sum_training_hotel
}



// <cloth module>
function cloth() {
  var 人名所在列數 = getnamerow(隊服訂購名單數據)
  if (人名所在列數 != null) {
    return 700
  }
  else {
    return 0
  }
}



// <team fee>
function team_fee() {
  var 人名所在列數 = getnamerow(通訊錄數據)
  if (人名所在列數 != null) {
    return 500
  }
  else {
    return 0
  }
}



// <main> fee
var 人名 = getname(試算)

function fee_v1() {
  var result = 0
  result = car() + training_hotel() + cloth() + team_fee()

  if (result == 0) {
    result = "恭喜不用繳錢！"
  }

  試算.getRange(4,4).setValue(result)
}
