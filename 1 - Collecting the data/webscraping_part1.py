import os
import requests
from bs4 import BeautifulSoup

# URL of the category page
url = 'https://www.trustpilot.com/categories/atm'

# Send a request to the webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

# Find all company listings
companies = soup.find_all('div', class_='styles_businessUnitMain__PuwB7')

for company in companies:
    name = company.find('p', class_='typography_heading-xs__jSwUz typography_appearance-default__AAY17').text
    domain = company.find('p', class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_websiteUrlDisplayed__QqkCT').text
    reviews = company.find('p', class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_ratingText__yQ5S7').text.split("|")[1].split(" ")[0]
    trustscore = company.find('span', class_='typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_trustScore__8emxJ').text.split(" ")[1]

    print("Company: ", name)
    print("Domain: ", domain)
    print("Number of Reviews: ", reviews)
    print("Trustscore: ", trustscore)

    url = 'https://www.trustpilot.com/review/' + domain

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    reviews_classes = soup.find_all('label', class_='styles_row__wvn4i')

    for reviews_class in reviews_classes:
        
        if reviews_class['data-star-rating'] == 'five':
            class5_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text
            print("5 stars reviews percentage: ", class5_reviews_perc)
            
        if reviews_class['data-star-rating'] == 'four':
            class4_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text
            print("4 stars reviews percentage: ", class4_reviews_perc)
            
        if reviews_class['data-star-rating'] == 'three':
            class3_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text
            print("3 stars reviews percentage: ", class3_reviews_perc)
            
        if reviews_class['data-star-rating'] == 'two':
            class2_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text
            print("2 stars reviews percentage: ", class2_reviews_perc)
            
        if reviews_class['data-star-rating'] == 'one':
            class1_reviews_perc = reviews_class.find('p', class_='typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_cell__qnPHy styles_percentageCell__cHAnb').text
            print("1 star reviews percentage: ", class1_reviews_perc)