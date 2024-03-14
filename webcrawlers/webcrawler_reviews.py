import os
import time
import requests
from bs4 import BeautifulSoup
import csv
import html
import json

def get_reviews_info(url, manga_id, page, user_id_counter, review_id_counter, existing_users, existing_reviews):
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            break
        elif response.status_code == 429 or response.status_code == 405:
            print(f"A solicitação GET para ID {manga_id} falhou com o código de status {response.status_code}")
            time.sleep(180)
        else:
            print(f"A solicitação GET para ID {manga_id} falhou com o código de status {response.status_code}")
            break
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = []  
        users = [] 

        review_elements = soup.find_all("div", class_="review-element js-review-element")
        for review_element in review_elements:

            data_reactions_raw = review_element.get('data-reactions', '{}')
            try:
                data_reactions = json.loads(html.unescape(data_reactions_raw))['count']
            except json.JSONDecodeError as e:
                data_reactions = [0, 0, 0, 0, 0, 0, 0] 

            username = review_element.find("div", class_="username").get_text().replace('\n', '').replace('\r', '')
            user_id = user_id_counter.get(username, None)

            if user_id is None and username in existing_users:
                user_id = existing_users[username]
            elif user_id is None:
                user_id = len(user_id_counter) + 1
                user_id_counter[username] = user_id
                existing_users[username] = user_id
                users.append({"user_id": user_id, "username": username})

            review_text = review_element.find("div", class_="text").get_text(strip=False).replace('\n', ' ').replace('\r', '').strip()

            if review_text in existing_reviews:
                print(f"Review já existe. Manga: {manga_id}, Página: {page}")
                continue

            existing_reviews.add(review_text)

            review_info = {
                "review_id": review_id_counter,
                "user_id": user_id,
                "manga_id": manga_id,
                "rating": review_element.find("div", class_="rating mt20 mb20 js-hidden").find("span", class_="num").get_text().replace('\n', '').replace('\r', ''),
                "date": review_element.find("div", class_="update_at").get_text().replace('\n', '').replace('\r', ''),
                "review_text": review_text,
                "total_reactions": sum(int(i) for i in data_reactions),
                "nice": data_reactions[0],
                "loveit": data_reactions[1],
                "funny": data_reactions[2],
                "confusing": data_reactions[3],
                "informative": data_reactions[4],
                "well-written": data_reactions[5],
                "creative": data_reactions[6],
            }

            reviews.append(review_info)
            review_id_counter += 1

        with open('reviews.csv', 'a', newline='', encoding='utf-8') as reviews_csv:
            fieldnames = ["review_id", "user_id", "manga_id", "rating",#"evaluation", 
            "date", "review_text","total_reactions","nice","loveit","funny",
            "confusing","informative","well-written","creative"]

            writer = csv.DictWriter(reviews_csv, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            
            if os.stat("reviews.csv").st_size == 0:
                writer.writeheader()
            for review_info in reviews:
                writer.writerow(review_info)

        with open('users.csv', 'a', newline='', encoding='utf-8') as users_csv:
            fieldnames = ["user_id", "username"]

            writer = csv.DictWriter(users_csv, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            
            if os.stat("users.csv").st_size == 0:
                writer.writeheader()
            for user_info in users:
                writer.writerow(user_info)

        print(f"Manga: {manga_id}, review da página {page} Adicionada!")
        return page + 1, review_id_counter
    else:
        print(f"A solicitação GET para ID {manga_id} na página {page} falhou com o código de status {response.status_code}")
        return None

user_id_counter = {}
review_id_counter = 1
existing_users = {}
existing_reviews = set()

if os.path.exists('users.csv'):
    with open('users.csv', 'r', newline='', encoding='utf-8') as users_csv:
        reader = csv.DictReader(users_csv)
        for row in reader:
            user_id_counter[row['username']] = int(row['user_id'])
            existing_users[row['username']] = int(row['user_id'])
last_manga_id = 1
if os.path.exists('reviews.csv'):
    with open('reviews.csv', 'r', newline='', encoding='utf-8') as reviews_csv:
        reader = csv.DictReader(reviews_csv)
        for row in reader:
            existing_reviews.add(row['review_text'])

            last_review_id = max(review_id_counter, int(row['review_id']))
            last_manga_id = row['manga_id']
            review_id_counter = last_review_id + 1

with open('content.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        manga_id = row['id']
        if int(manga_id) < int(last_manga_id):
            continue
        manga_name = row['title']
        url_reviews = f'https://myanimelist.net/manga/{manga_id}/manga_name/reviews?sort=suggested&filter_check=&filter_hide=&preliminary=on&spoiler=on'

        page = 1 
        while page is not None:
            url_page = f'{url_reviews}&p={page}'
            result = get_reviews_info(url_page, manga_id, page, user_id_counter, review_id_counter, existing_users, existing_reviews)
            
            if result is None:
                break 
            
            page, review_id_counter = result
