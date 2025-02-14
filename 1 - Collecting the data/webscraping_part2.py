import requests
from bs4 import BeautifulSoup

pageNumber = 0
url = 'https://www.trustpilot.com/review/gohenry.com'
response = requests.get(url)

while response.status_code == 200:
    pageNumber += 1
    url = url + '?page=' + str(pageNumber)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    reviews = soup.find_all('div', class_='styles_reviewCardInner__UZk1x')

    for review in reviews:
        stars = review.find('div', class_='star-rating_starRating__sdbkn star-rating_medium__Oj7C9').find('img')['alt'][6]
        if (review.find('p', class_='typography_body-l__v5JLj typography_appearance-default__t8iAq typography_color-black__wpn7m')):
            comment = review.find('p', class_='typography_body-l__v5JLj typography_appearance-default__t8iAq typography_color-black__wpn7m').text
        else:
            comment = ""
        response = review.find('p', class_='typography_body-m__k2UI7 typography_appearance-default__t8iAq styles_message____SVk')

        print("Stars: ", stars)
        print("Comment: ", comment)

        if int(stars) <= 2:
            if response:
                print("Company has responded to this review.")
            else:
                print("Company has NOT responded to this review.")