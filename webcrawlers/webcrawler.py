import os
import time
import requests
from bs4 import BeautifulSoup
import csv

def requestMangaCharacters(check_character_list,manga_id,soup):
    response_characters = None
    if check_character_list :
        href_characters = soup.find("a", string="More characters")['href']
        response_characters = requestWebsite(f"https://myanimelist.net"+href_characters,manga_id)
    if response_characters:
      soup = BeautifulSoup(response_characters.text, 'html.parser')
      characters_element = soup.find_all("h3", class_="h3_character_name")
      return characters_element
    return []

def requestWebsite(url,manga_id):
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
  return response

base_url = "https://myanimelist.net/manga/"
filename = 'mangas.csv'
processed_ids = set()

if os.path.exists(filename):
    with open(filename, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        processed_ids = {int(row['id']) for row in reader}

with open(filename, 'a', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['id', 'title', 'type', 'score_value', 'score_count', 'ranked',
     'popularity', 'volumes', 'chapters', 'status',  'genres', 'themes', 'demographic',
      'serialization', 'published', 'authors', 'synopsis', 'image_src', 'background',
      'alt_titles','characters']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames,quoting=csv.QUOTE_ALL)

    if os.stat(filename).st_size == 0:
        writer.writeheader()

    for manga_id in range(1,165248):
        if manga_id in processed_ids:
            print(f"{manga_id} Já existe na base.")
            continue

        url = base_url + str(manga_id)
        response = requestWebsite(url, manga_id)
                  
        if response.status_code == 200:

            soup = BeautifulSoup(response.text, 'html.parser')

            title_element = soup.find("span", class_="h1-title").find("span", itemprop="name") if soup.find("span", class_="h1-title") else None
            synopsis_element = soup.find("span", itemprop="description")
            image_element = soup.find("img", itemprop="image")
            background_element = soup.find("div", class_="pb24").find_parent("td").get_text(strip=False) if soup.find("div", class_="pb24") else None
            alternative_titles_element = soup.find("div", class_="js-alternative-titles").find_all("div",class_="spaceit_pad") if soup.find("div", class_="js-alternative-titles") else None
            types_element = soup.find('span', string='Type:').find_parent("div") if soup.find('span', string='Type:') else None
            volumes_element = soup.find('span', string='Volumes:').find_parent("div") if soup.find('span', string='Volumes:') else None
            chapters_element = soup.find('span', string='Chapters:').find_parent("div") if soup.find('span', string='Chapters:') else None
            status_element = soup.find('span', string='Status:').find_parent("div") if soup.find('span', string='Status:') else None
            published_element = soup.find('span', string='Published:').find_parent("div") if soup.find('span', string='Published:') else None
            genres_element = soup.find('span', string=lambda text: text and ('Genres:' in text or 'Genre:' in text)).find_next_siblings("span") if soup.find('span', string=lambda text: text and ('Genres:' in text or 'Genre:' in text)) else None
            themes_element = soup.find('span', string=lambda text: text and ('Themes:' in text or 'Theme:' in text)).find_next_siblings("span") if soup.find('span', string=lambda text: text and ('Themes:' in text or 'Theme:' in text)) else None
            demographic_element = soup.find('span', string='Demographic:').find_next_sibling("span") if soup.find('span', string='Demographic:') else None
            serialization_element = soup.find('span', string='Serialization:').find_parent("div") if soup.find('span', string='Serialization:') else None
            authors_element = soup.find('span', string='Authors:').find_next_siblings("a") if soup.find('span', string='Authors:') else None
            score_value_element = soup.find('span', string='Score:').find_parent("div").find("span", itemprop="ratingValue") if soup.find('span', string='Score:') else None
            score_count_element = soup.find('span', string='Score:').find_parent("div").find("span", itemprop="ratingCount") if soup.find('span', string='Score:') else None
            ranked_element = soup.find('span', string='Ranked:') if soup.find('span', string='Ranked:') else None
            popularity_element = soup.find('span', string='Popularity:') if soup.find('span', string='Popularity:') else None 
            check_character_list = soup.find_all('div', class_="detail-characters-list clearfix")
           
            title = title_element.get_text().split('\n')[0].replace('\n', '').replace('\r', '') if title_element else ""
            synopsis = synopsis_element.get_text(strip=False).replace('\n', ' ').replace('\r', '') if synopsis_element else ""
            image_src = image_element.get("data-src") if image_element else ""
            if background_element and not( "No background information has been added to this title." in background_element):
               if "EditBackground" in background_element:
                  background = background_element.split("EditBackground")[1].replace('\n', ' ').replace('\r', '').strip()
               elif "Background" in background_element:
                  background = background_element.split("Background")[-1].replace('\n', ' ').replace('\r', '').strip()
               else:
                  background = "SOMETHINGDIFFERENT"
            else:
               background = ""
            alternative_titles = [i.get_text(strip=False).split(": ", 1)[1] if i else None for i in alternative_titles_element] if alternative_titles_element else []
            types = types_element.get_text(strip=False).split(":",1)[1].strip() if types_element else ""
            volumes = volumes_element.get_text(strip=False).split(":",1)[1].strip() if volumes_element else ""
            chapters = chapters_element.get_text(strip=False).split(":",1)[1].strip() if chapters_element else ""
            status = status_element.get_text(strip=False).split(":",1)[1].strip() if status_element else ""
            published = published_element.get_text(strip=False).split(":",1)[1].strip() if published_element else ""
            genres = [i.get_text(strip=True) if i else None for i in genres_element] if genres_element else []
            themes = [i.get_text(strip=True) if i else None for i in themes_element] if themes_element else []
            demographic = demographic_element.get_text(strip=True).replace('\n', '').replace('\r', '') if demographic_element else ""
            serialization = serialization_element.get_text(strip=False).split(":",1)[1].strip() if serialization_element else ""
            authors = [i.get_text(strip=True) if i else None for i in authors_element] if authors_element else []
            score_value = score_value_element.get_text(strip=True).replace('\n', '').replace('\r', '') if score_value_element else ""
            score_count = score_count_element.get_text(strip=True).replace('\n', '').replace('\r', '') if score_count_element else ""
            ranked = ranked_element.next_sibling.strip() if ranked_element else ""
            popularity = popularity_element.next_sibling.strip() if popularity_element else ""

            characters_element = requestMangaCharacters(check_character_list,manga_id,soup)
            characters = [i.get_text(strip=True) if i else None for i in characters_element] if characters_element else []

            writer.writerow({'id': manga_id, 'title': title,'type':types, 'score_value': score_value,
             'score_count': score_count, 'ranked': ranked, 'popularity': popularity, 'volumes': volumes,
              'chapters': chapters, 'status': status,  'genres': genres, 'themes': themes,
               'demographic': demographic, 'serialization': serialization, 'published': published,
                'authors': authors,'synopsis': synopsis, 'image_src': image_src, 'background': background,
                 'alt_titles': alternative_titles,'characters': characters})
            
            processed_ids.add(manga_id)
            print(f"{manga_id} Adicionado!")

