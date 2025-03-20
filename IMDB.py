from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import pandas as pd
import openpyxl

all_data = {
    'Movie Name': [],
    'Year': [],
    'Rating': [],
    'Dirctors_Creators': [],  # Changed to single list
    'Top actors': []  # Changed to single list
}

# Set up WebDriver options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

driver.get("https://www.imdb.com/")
sleep(2)

# Click the search button
search_button = driver.find_element(By.CLASS_NAME, 'searchform__submit')
search_button.click()
sleep(2)

# Wait for "Movies, TV & more" section and click it
wait = WebDriverWait(driver, 10)
movie = wait.until(EC.presence_of_element_located((By.XPATH, "//a[.//span[text()='Movies, TV & more']]")))
movie.click()
sleep(2)

# Get options
options = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                     "section.ipc-page-section.ipc-page-section--base.ipc-page-section--tp-none.ipc-page-section--bp-none.sc-bb21426f-1.fjEPfy")))
print(options.text)

# User chooses a category
choice = input("What's your choice? (copy-paste the exact name) ")
get_choice = wait.until(EC.presence_of_element_located((By.XPATH, f"//button[.//span[text()='{choice}']]")))
print("You selected:", get_choice.text)
get_choice.click()

# Genre selection
genre = driver.find_element(By.ID, 'genreAccordion')
print(genre.text)
genre_choice = input("What's your genre choice? ")
button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-testid="test-chip-id-{genre_choice}"]')))
driver.execute_script("arguments[0].scrollIntoView();", button)
sleep(1)
driver.execute_script("arguments[0].click();", button)


def scrap_page():
    try:
        # Movie Title
        main = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="hero__pageTitle"]')))
        name_of_movie = main.find_element(By.CLASS_NAME, 'hero__primary-text')
        print("Movie:", name_of_movie.text)
        all_data['Movie Name'].append(name_of_movie.text)

        # Year
        try:
            year_element = main.find_element(By.XPATH, './following-sibling::ul/li/a')
            year = year_element.text
            print("Year:", year)
            all_data['Year'].append(year)
        except:
            print("Year: Not found")
            all_data['Year'].append("N/A")

        # Rating
        rating_element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="hero-rating-bar__aggregate-rating__score"]')))
        rating = rating_element.find_element(By.TAG_NAME, 'span')
        print("Rating:", rating.text)
        all_data['Rating'].append(rating.text)

        # Directors/Creators
        directors_list = []
        dirctor_creator_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="title-pc-principal-credit"]')))
        dirctor_creator = dirctor_creator_element.find_elements(By.CLASS_NAME,
                                                                'ipc-metadata-list-item__list-content-item.ipc-metadata-list-item__list-content-item--link')
        for i in dirctor_creator:
            print("Director/Creator:", i.text)
            directors_list.append(i.text)
        all_data['Dirctors_Creators'].append(directors_list)

        # Top Actors
        actors_list = []
        top_cast_element_main = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="title-cast"]')))
        top_cast_elements = top_cast_element_main.find_elements(By.CSS_SELECTOR, '[data-testid="title-cast-item"]')
        for cast_item in top_cast_elements:
            try:
                actor_name = cast_item.find_element(By.CSS_SELECTOR, '[data-testid="title-cast-item__actor"]').text
                print("Actor:", actor_name)
                actors_list.append(actor_name)
            except:
                continue
        all_data['Top actors'].append(actors_list)

    except Exception as e:
        print(f"An error occurred in scrap_page: {e}")
        all_data['Movie Name'].append("N/A")
        all_data['Year'].append("N/A")
        all_data['Rating'].append("N/A")
        all_data['Dirctors_Creators'].append([])
        all_data['Top actors'].append([])


try:
    actions = ActionChains(driver)
    res = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="adv-search-get-results"]')))

    # Click awards section
    clickme = wait.until(EC.presence_of_element_located((By.XPATH, '//div[text()="Awards & recognition"]')))
    actions.move_to_element(clickme).click().perform()

    # Get award options
    click_award = driver.find_element(By.ID, 'accordion-item-awardsAccordion')
    award = click_award.find_element(By.TAG_NAME, 'section')
    all_buttons = award.find_elements(By.CLASS_NAME, 'ipc-chip__text')

    print("Available award options:")
    for button in all_buttons:
        print(button.get_attribute('innerHTML'))

    # Get and process user input
    award_choice = input("Choose your award filter: ").strip()
    if 'top' in award_choice.lower() or 'bottom' in award_choice.lower():
        award_choice = award_choice[5:]
    if 'Emmy Award-Nominated' in award_choice:
        award_choice = 'emmy-nominated'
    if 'Emmy Award-Winning' in award_choice:
        award_choice = 'emmy-winning'
    award_choice = award_choice.replace(' ', '-').lower()

    selector = f'[data-testid="test-chip-id-{award_choice}"]'
    chose_button = award.find_element(By.CSS_SELECTOR, selector)
    actions.move_to_element(chose_button).click().perform()

    actions.move_to_element(res).click().perform()
    sleep(2)

    # Collect all movie links
    movie_links = []
    while True:
        all_movies = driver.find_elements(By.CLASS_NAME, 'ipc-metadata-list-summary-item')
        for movie in all_movies:
            try:
                link = movie.find_element(By.CLASS_NAME, 'ipc-title-link-wrapper').get_attribute('href')
                if link not in movie_links:
                    movie_links.append(link)
            except:
                continue

        try:
            more_button = driver.find_element(By.CLASS_NAME, 'ipc-see-more__button')
            actions.move_to_element(more_button).click().perform()
            sleep(2)
        except:
            break

    # Visit each movie and scrape data
    for link in movie_links:
        try:
            driver.get(link)
            scrap_page()
            sleep(5)
            driver.back()
            sleep(2)
        except Exception as e:
            print(f"Error visiting {link}: {e}")
            continue

    # Print all collected data
    print("\nFinal collected data:")
    for key, value in all_data.items():
        print(f"{key}: {value}")

    # Save to Excel using pandas
    df = pd.DataFrame(all_data)
    # Join lists into strings for Excel compatibility
    df['Dirctors_Creators'] = df['Dirctors_Creators'].apply(lambda x: ', '.join(x) if x else 'N/A')
    df['Top actors'] = df['Top actors'].apply(lambda x: ', '.join(x) if x else 'N/A')
    df.to_excel('data_from_IMDB.xlsx', index=False)
    print("Data saved to 'data_from_IMDB.xlsx'")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()