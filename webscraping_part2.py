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
    stars = review.find('img', class_='star-rating_starRating__4rrcf star-rating_medium__iN6Ty')['alt'][7]
    comment = review.find('p', class_='typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn').text
    response = review.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_message__shHhX')

    print(f"Stars: {stars}")
    print(f"Comment: {comment}")

    if int(stars) <= 2:
        if response:
            print("Company has responded to this review.")
        else:
            print("Company has NOT responded to this review.")
        print("\n")