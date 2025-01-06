# Shopee_Link_Crawler

## Description
- get the momo price of a shopee item
- get the corressponded momo link

## Table of Contents
- [Shopee\_Link\_Crawler](#shopee_link_crawler)
  - [Description](#description)
  - [Table of Contents](#table-of-contents)
  - [Performance](#performance)
  - [Files](#files)
  - [getprice.py](#getpricepy)
    - [Input](#input)
    - [Output](#output)
  - [getlink.py](#getlinkpy)
    - [Input](#input-1)
    - [Output](#output-1)
  - [Credits](#credits)


## Performance
- 7 min for 30 item names, avg 14 sec for 1 item name, roughly 4hr for 1,000 items


## Files
1. **getprice.py:**  
 Literally, aiming to get the momo prices

2. **getlink.py:**  
 Aiming to get the momo links. It gets the corresponded momo price, cheering, at the same time.

3. **same_prouct_or_not.py:**  
containing the supporting function "same_product_or_not"  used in getlink.py. The function utilized OPENAI_API in judging whether crawled momo product is the same with our shopee one.  
For instance, whether 
    - 技嘉AORUS16XASG電競筆電i7-14650X/RTX4070/165z/32G/1TBSSD
    - 【GIGABYTE】16吋i7 RTX4070黑神話悟空適用電競筆電(AORUS 16X ASG-53TWC64SH/i7-14650HX/32G/1T/W11)  

    are the same (the answer is yes).


## getprice.py
### Input
A csv file having below fields

| Item ID | Momo Link |
| -| - |
| XXX | XXX |

### Output
A csv file having below fields
| Item ID | Momo Link | Momo Price |
| -| - | - |
| XXX | XXX |XXX|


## getlink.py
### Input
A csv file having below fields

Item Name|
|-|
|XXX| 

### Output
A csv file having below fields

Item ID| Item Name |Shopee Price| Momo Link | Momo Price
|-| -|-|-|-|
|XXX| XXX|XXX|XXX|XXX|


## Credits
All codes were developed by Bryant-Liu 劉子揚

Github profile (https://github.com/Bryant-Liu-TzuYang)
