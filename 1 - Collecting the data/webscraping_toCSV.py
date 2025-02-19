import csv
import requests
from bs4 import BeautifulSoup

url = 'https://www.trustpilot.com/categories/atm'

response = requests.get(url)
parser = "html.parser"
soup = BeautifulSoup(response.text, parser)

companies = soup.find_all('div', class_='styles_businessUnitMain__e_tIa')

with open('trustpilot_reviews.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Company", "Domain", "Number of Reviews", "Trustscore", "5 stars reviews percentage", "4 stars reviews percentage", "3 stars reviews percentage", "2 stars reviews percentage", "1 star reviews percentage", "Review Stars", "Review Comment", "Company Response"])

    for company in companies:
        name = company.find('p', class_ = 'typography_heading-xs__osRhC typography_appearance-default__t8iAq').text
        domain = company.find('p', class_ = 'typography_body-m__k2UI7 typography_appearance-subtle__PYOVM styles_websiteUrlDisplayed__lSw1A').text
        reviews = company.find('p', class_ = 'typography_body-m__k2UI7 typography_appearance-subtle__PYOVM styles_ratingText__A2dmB').text.split("|")[1].split(" ")[0]
        trustscore = company.find('span', class_ = 'typography_body-m__k2UI7 typography_appearance-subtle__PYOVM styles_trustScore__iURkS').text.split(" ")[1]

        url = 'https://www.trustpilot.com/review/' + domain

        response = requests.get(url)
        soup = BeautifulSoup(response.text, parser)

        reviews_classes = soup.find_all('label', class_='styles_row__4BwV6')

        class5_reviews_perc = ""
        class4_reviews_perc = ""
        class3_reviews_perc = ""
        class2_reviews_perc = ""
        class1_reviews_perc = ""

        class_to_search = 'typography_body-m__k2UI7 typography_appearance-default__t8iAq styles_cell__2f_al styles_percentageCell__AKkqm'

        for reviews_class in reviews_classes:
            if reviews_class['data-star-rating'] == 'five':
                class5_reviews_perc = reviews_class.find('p', class_ = class_to_search).text
                
            if reviews_class['data-star-rating'] == 'four':
                class4_reviews_perc = reviews_class.find('p', class_ = class_to_search).text
                
            if reviews_class['data-star-rating'] == 'three':
                class3_reviews_perc = reviews_class.find('p', class_ = class_to_search).text
                
            if reviews_class['data-star-rating'] == 'two':
                class2_reviews_perc = reviews_class.find('p', class_ = class_to_search).text
                
            if reviews_class['data-star-rating'] == 'one':
                class1_reviews_perc = reviews_class.find('p', class_ = class_to_search).text

        pageNumber = 0
        while response.status_code == 200:
            pageNumber += 1
            url_with_page = url + '?page=' + str(pageNumber)

            response = requests.get(url_with_page)
            soup = BeautifulSoup(response.text, "html.parser")

            reviews_list = soup.find_all('div', class_ = 'styles_reviewCardInner__UZk1x')

            for review in reviews_list:
                stars = review.find('div', class_ = 'star-rating_starRating__sdbkn star-rating_medium__Oj7C9').find('img')['alt'][6]
                if (review.find('p', class_ = 'typography_body-l__v5JLj typography_appearance-default__t8iAq typography_color-black__wpn7m')):
                    comment = review.find('p', class_ = 'typography_body-l__v5JLj typography_appearance-default__t8iAq typography_color-black__wpn7m').text
                else:
                    comment = ""
                response_text = review.find('p', class_ = 'typography_body-m__k2UI7 typography_appearance-default__t8iAq styles_message____SVk')

                if int(stars) <= 2:
                    if response_text:
                        company_response = "Company has responded to this review."
                    else:
                        company_response = "Company has NOT responded to this review."
                else:
                    company_response = ""

                writer.writerow([name, domain, reviews, trustscore, class5_reviews_perc, class4_reviews_perc, class3_reviews_perc, class2_reviews_perc, class1_reviews_perc, stars, comment, company_response])

print("Data correctly written to trustpilot_reviews.csv")