import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

URL = 'https://books.toscrape.com/'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
}

book_dic = {
    'name': [],
    'price': [],
    'category': [],
    'stars': [],
    'upc': [],
    'stock': [],
    'availability': [],
    'imglink': [],
}

# Initial request with header
response = requests.get(URL, headers=header)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'html.parser')

# Get number of pages
try:
    num_page = int(soup.find('li', attrs={'class': 'current'}).text.strip().split(' ')[-1])
except (AttributeError, ValueError):
    num_page = 1  # Fallback if page count fails

# Iterate through each page
for page in range(1, num_page + 1):
    print(f'This is the page number {page}')
    page_url = f"https://books.toscrape.com/catalogue/page-{page}.html"

    try:
        response = requests.get(page_url, headers=header)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        books = soup.find_all('article', attrs={'class': 'product_pod'})
        for book in books:
            book_url = urljoin(URL, book.find('a')['href'])
            try:
                response = requests.get(book_url, headers=header)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract book details
                div_name = soup.find('div', attrs={'class': 'col-sm-6 product_main'})
                name = div_name.find('h1').text
                book_dic['name'].append(name)

                price = soup.find('p', attrs={'class': 'price_color'}).text
                book_dic['price'].append(price)

                cat = soup.find('ul', class_='breadcrumb').find_all('a')[-1].text.strip()
                book_dic['category'].append(cat)

                star_loc = soup.find('p', attrs={'class': 'star-rating'})
                stars = star_loc['class'][1] if star_loc else 'Not Rated'
                book_dic['stars'].append(stars)

                table = soup.find_all('tr')
                upc = table[0].find('td').text
                book_dic['upc'].append(upc)

                stock_text = table[5].find('td').text
                stock = int(stock_text.split('(')[-1].split(' ')[0])
                book_dic['stock'].append(stock)

                ava_state = stock > 0
                ava_rep = "In stock" if ava_state else "Out of stock"
                book_dic['availability'].append(ava_rep)

                img_loc = soup.find('img')
                img_link = urljoin(URL, img_loc['src'])
                book_dic['imglink'].append(img_link)

            except Exception as e:
                print(f"Failed to scrape book details: {e}")

    except Exception as e:
        print(f"Failed to fetch page {page}: {e}")

# Save data to Excel
df = pd.DataFrame(book_dic)
df.to_excel('book.xlsx', index=False)
print("Data saved to book.xlsx")
