import os
import requests
from bs4 import BeautifulSoup

# URL of the category page
url = 'https://www.trustpilot.com/categories/atm'

# Send a request to the webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all company listings
companies = soup.find_all('div', class_='styles_main__XgQiuO')

for company in companies:
    name = company.find('p', class_='typography_heading-xs__jSwUz typography_appearance-default__AAY17').text
    domain = company.find('p', class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_websiteUrlDisplayed__QqkCT').text
    reviews = company.find('span', class_='styles_separator__TG_uV')
    trustscore = company.find('div', class_='styles_rating__1x9gC').text

    print(f"Company: {name}")
    print(f"Domain: {domain}")
    print(f"Number of Reviews: {reviews}")
    print(f"Trustscore: {trustscore}")

    url = os.path.join('https://www.trustpilot.com/review/', domain)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    reviews_classes = soup.find_all('div', class_='styles_row__wvn4i')

    for reviews_class in reviews_classes:
        
        if reviews_class['data-star-rating'] == 'five':
            class5_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text
        
        if reviews_class['data-star-rating'] == 'four':
            class4_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text

        if reviews_class['data-star-rating'] == 'three':
            class3_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text

        if reviews_class['data-star-rating'] == 'two':
            class2_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text

        if reviews_class['data-star-rating'] == 'one':
            class1_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text

    print(f"5 stars reviews percentage: {class5_reviews_perc}")
    print(f"4 stars reviews percentage: {class4_reviews_perc}")
    print(f"3 stars reviews percentage: {class3_reviews_perc}")
    print(f"2 stars reviews percentage: {class2_reviews_perc}")
    print(f"1 stars reviews percentage: {class1_reviews_perc}")