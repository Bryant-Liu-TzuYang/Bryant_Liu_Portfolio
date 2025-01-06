# -*- coding:utf-8 -*-

def same_product_or_not(prd1, prd2, client):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "請幫我判斷底下兩個產品名稱指的是不是同一個產品。如果是請輸出 1，反之則輸出 0。請不要有任合文字敘述，輸出只會是 1 或是 0。"},
        {"role": "user", "content": prd1},
        {"role": "user", "content": prd2}
        ],
        stream=True,
    )

    # message = response.choices[0].message.content

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            temp = chunk.choices[0].delta.content 
    
    return int(temp)
