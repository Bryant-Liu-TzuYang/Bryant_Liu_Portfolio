# -*- coding:utf-8 -*-

def clean_prd_name(prdname, client):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
            {"role": "system", "content": "你是電腦、通訊和消費性電子產品的專家。"},
            {
                "role": "user", "content": """請幫我清理並輸出乾淨的產品名稱。

                清理規則：
                1. 保留核心資訊：
                - 品牌名稱（如 Apple、Samsung、小米等）
                - 產品系列（如 iPhone、Galaxy、Mi等）
                - 型號（如 15 Pro、S24、13等）
                - 容量規格（如 128GB、256GB、1TB等）
                - 重要規格（如螢幕大小、顏色等）
                - 貨源消息（特別是相機需要確認是「公司貨」還是「平行輸入」）

                2. 刪除冗餘詞彙：
                - 行銷用詞：「全新」、「新機」、「空機」、「熱賣」、「限量」
                - 保證詞彙：「原廠保固」、「正品」、「官方認證」
                - 商家資訊：店家名稱、賣家暱稱（如「Q哥」、「小王手機店」等）
                - 無關描述：「現貨」、「快速出貨」、「免運」等

                3. 統一格式：
                - 容量：統一為「128GB」、「256GB」格式
                - 螢幕：統一為「6.1吋」、「6.7吋」格式
                - 顏色：保留但統一用詞（如「太空灰」、「玫瑰金」）

                範例：
                - 輸入：Apple iPhone 16 128G 全新 6.1吋 新機 空機 原廠保固 公司貨 蘋果 i16 Q哥
                - 輸出：Apple iPhone 16 128GB 6.1吋
                
                請直接輸出清理後的產品名稱，不要包含其他說明文字。"""
            },
            {"role": "user", "content": prdname},
            ],
            stream=True,
        )

    except Exception as e:
        mes = f"clean_prd_name| {e}"
        raise Exception(mes)

    complete_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            complete_response += chunk.choices[0].delta.content 
    
    return str(complete_response)
