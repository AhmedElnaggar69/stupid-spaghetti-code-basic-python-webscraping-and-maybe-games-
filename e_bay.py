import requests
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl
laptop_dic = {
    'name' :[],
    'price' :[],
    'state' :[],
    'seller and rate': [],
    'product link' :[],
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

page_no=1
while True:


    url = f'https://www.ebay.com/sch/i.html?_dcat=177&_fsrp=1&rt=nc&_from=R40&_nkw=laptop&_sacat=0&RAM%2520Size=32%2520GB&SSD%2520Capacity=1%2520TB&_pgn={page_no}'

    response = requests.get(url, headers=headers)
    if response.status_code!=200:
        continue
    soup = BeautifulSoup(response.text, 'html.parser')
    laptops = soup.find_all('div', class_='s-item__info')

    for lap in laptops[2:]:
        ## link , name , price , seller name and rate , state
        name = lap.find('span', attrs={'role': 'heading'})
        starting_price = lap.find('span', attrs={'class': 's-item__price'})
        saler_name_and_pers = lap.find('span', attrs={'class': 's-item__seller-info'})
        product_state = lap.find('span', attrs={'class': 'SECONDARY_INFO'})
        link_tag = lap.find('a', class_='s-item__link')  # Get the link tag

        if name and starting_price and link_tag:
            name_text = name.text.strip()
            laptop_dic['name'].append(name_text)
            price_text = starting_price.text.strip()
            laptop_dic['price'].append(price_text)
            seller_text = saler_name_and_pers.text.strip() if saler_name_and_pers else "N/A"
            laptop_dic['seller and rate'].append(seller_text)
            product_state_text = product_state.text.strip() if product_state else "N/A"
            laptop_dic['state'].append(product_state_text)
            product_link = link_tag['href'].strip()  # Extract the href attribute
            laptop_dic['product link'].append(product_link)
    next_page = soup.find('button' , class_='pagination__next')
    if next_page is not None:
        break

    page_no+=1


df=pd.DataFrame(laptop_dic)
df.to_excel('laptops.xlsx')