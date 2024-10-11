# -- 1

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

url = 'https://www.trustpilot.com/review' + domain



# -- 2

import requests
from bs4 import BeautifulSoup

# URL of the company page
url = 'https://www.trustpilot.com/review/www.showroomprive.com'

# Send a request to the webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all reviews
reviews = soup.find_all('div', class_='styles_cardWrapper__LcCPA styles_show__HUXRb styles_reviewCard__9HxJJ')

for review in reviews:
    stars = review.find('img', class_='star-rating_starRating__4rrcf star-rating_medium__iN6Ty')['alt'][7] # <- typecast to integer
    comment = review.find('p', class_='typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn').text
    response = review.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_message__shHhX')

    print(f"Stars: {stars}")
    print(f"Comment: {comment}")

    if stars <= 2: #negative review
        if response:
            print("Company has responded to this review.")
        else:
            print("Company has NOT responded to this review.")
        print("\n")
    
