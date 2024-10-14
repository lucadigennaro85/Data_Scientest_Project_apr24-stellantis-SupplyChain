import requests
from bs4 import BeautifulSoup

pageNumber = 0
url = 'https://www.trustpilot.com/review/gohenry.com'
response = requests.get(url)

# URL of the company page
while response.status_code == 200:
    pageNumber += 1
    url = url + '?page=' + str(pageNumber)

    # Send a request to the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    # Find all reviews
    reviews = soup.find_all('div', class_='styles_reviewCardInner__EwDq2')

    for review in reviews:
        stars = review.find('div', class_='star-rating_starRating__4rrcf star-rating_medium__iN6Ty').find('img')['alt'][6]
        if (review.find('p', class_='typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn')):
            comment = review.find('p', class_='typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn').text
        else:
            comment = ""
        response = review.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_message__shHhX')

        print("Stars: ", stars)
        print("Comment: ", comment)

        if int(stars) <= 2:
            if response:
                print("Company has responded to this review.")
            else:
                print("Company has NOT responded to this review.")