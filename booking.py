import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

hotels = {
    'name': [],
    'price': [],
    'review': [],
    'review_count': [],
    'nights': [],
    'taxes': []
}

base_url = "https://www.booking.com/searchresults.en-gb.html"
params = {
    "ss": "Hurghada, Egypt",
    "checkin": "2025-03-09",
    "checkout": "2025-03-31",
    "group_adults": 2,
    "no_rooms": 1,
    "group_children": 0,
    "offset": 0  # Controls pagination
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept-Encoding": "gzip, deflate"
}

page = 0
total_properties = None  # To store the total count dynamically

while True:
    print(f"\n--- Scraping page {page + 1} ---\n")
    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")
        break

    soup = BeautifulSoup(response.text, 'html.parser')

    # Get total number of properties on the first page only
    if total_properties is None:
        total_tag = soup.find('h1')  # Adjust this if the tag is different
        if total_tag:
            total_text = total_tag.get_text(strip=True)
            print(total_text)  # Debugging line to see what it captures
            import re
            match = re.search(r"(\d+) properties found", total_text)
            if match:
                total_properties = int(match.group(1))
                max_pages = (total_properties // 25) + 1  # Calculate max pages
                print(f"Total properties: {total_properties}, Max pages: {max_pages}")
            else:
                print("Failed to extract total properties.")
                break

    cards = soup.find_all('div', attrs={'data-testid': 'property-card'})
    if not cards:
        print("No more hotel data found.")
        break

    for card in cards:
        title = card.find('div', attrs={'data-testid': 'title'})
        price = card.find('span', attrs={'data-testid': 'price-and-discounted-price'})
        review_score = card.find('div', attrs={'data-testid': 'review-score'})
        nights = card.find('div', attrs={'data-testid': 'price-for-x-nights'})
        taxes = card.find('div', attrs={'data-testid': 'taxes-and-charges'})

        hotels['name'].append(title.get_text(strip=True) if title else None)
        hotels['price'].append(price.get_text(strip=True) if price else None)

        if review_score:
            scored = review_score.find(class_='ac4a7896c7')
            review_ct = review_score.find(class_='abf093bdfe')
            hotels['review'].append(scored.text if scored else None)
            hotels['review_count'].append(review_ct.text if review_ct else None)
        else:
            hotels['review'].append(None)
            hotels['review_count'].append(None)

        hotels['nights'].append(nights.text if nights else None)
        hotels['taxes'].append(taxes.text if taxes else None)

    if page + 1 >= max_pages:
        print("Reached the last page of results.")
        break

    params["offset"] += 25
    page += 1
    time.sleep(2)

# Save to Excel
data = pd.DataFrame(hotels)
data.to_excel("hotels_in_hurghada.xlsx", index=False)
print("Scraping completed and saved to hotels_in_hurghada.xlsx.")
