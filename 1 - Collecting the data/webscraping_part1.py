import os
import requests
from bs4 import BeautifulSoup

url = 'https://www.trustpilot.com/categories/atm'

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

companies = soup.find_all('div', class_='styles_businessUnitMain__e_tIa')

for company in companies:
    name = company.find('p', class_='typography_heading-xs__osRhC typography_appearance-default__t8iAq').text
    domain = company.find('p', class_='typography_body-m__k2UI7 typography_appearance-subtle__PYOVM styles_websiteUrlDisplayed__lSw1A').text
    reviews = company.find('p', class_='typography_body-m__k2UI7 typography_appearance-subtle__PYOVM styles_ratingText__A2dmB').text.split("|")[1].split(" ")[0]
    trustscore = company.find('span', class_='typography_body-m__k2UI7 typography_appearance-subtle__PYOVM styles_trustScore__iURkS').text.split(" ")[1]

    print("Company: ", name)
    print("Domain: ", domain)
    print("Number of Reviews: ", reviews)
    print("Trustscore: ", trustscore)

    url = 'https://www.trustpilot.com/review/' + domain

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    reviews_classes = soup.find_all('label', class_='styles_row__4BwV6')

    for reviews_class in reviews_classes:
        
        if reviews_class['data-star-rating'] == 'five':
            class5_reviews_perc = reviews_class.find('p', class_='typography_body-m__k2UI7 typography_appearance-default__t8iAq styles_cell__2f_al styles_percentageCell__AKkqm').text
            print("5 stars reviews percentage: ", class5_reviews_perc)
            
        if reviews_class['data-star-rating'] == 'four':
            class4_reviews_perc = reviews_class.find('p', class_='typography_body-m__k2UI7 typography_appearance-default__t8iAq styles_cell__2f_al styles_percentageCell__AKkqm').text
            print("4 stars reviews percentage: ", class4_reviews_perc)
            
        if reviews_class['data-star-rating'] == 'three':
            class3_reviews_perc = reviews_class.find('p', class_='typography_body-m__k2UI7 typography_appearance-default__t8iAq styles_cell__2f_al styles_percentageCell__AKkqm').text
            print("3 stars reviews percentage: ", class3_reviews_perc)
            
        if reviews_class['data-star-rating'] == 'two':
            class2_reviews_perc = reviews_class.find('p', class_='typography_body-m__k2UI7 typography_appearance-default__t8iAq styles_cell__2f_al styles_percentageCell__AKkqm').text
            print("2 stars reviews percentage: ", class2_reviews_perc)
            
        if reviews_class['data-star-rating'] == 'one':
            class1_reviews_perc = reviews_class.find('p', class_='typography_body-m__k2UI7 typography_appearance-default__t8iAq styles_cell__2f_al styles_percentageCell__AKkqm').text
            print("1 star reviews percentage: ", class1_reviews_perc)