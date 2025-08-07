# -*- coding:utf-8 -*-

def same_product_or_not(prd1, prd2, client):
    if "福利品" in prd2:  # prd2 = momo product name
        return 0

    try:
        response = client.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:personal:test:Bj22Z51T",
            messages=[
            {"role": "system", "content": "You are an expert in computer, communication, and consumer electronics products."},
            {"role": "user", "content": "請幫我判斷底下兩個產品名稱指的是不是同一個產品。如果是請輸出 1，反之則輸出 0。請不要有任合文字敘述，輸出只會是 1 或是 0。"},
            {"role": "user", "content": prd1},
            {"role": "user", "content": prd2}
            ],
            stream=True,
        )
    except Exception as e:
        mes = f"same_product_or_not| {e}"
        raise Exception(mes)

    # message = response.choices[0].message.content

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            temp = chunk.choices[0].delta.content 
    
    return int(temp)
