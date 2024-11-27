import json
from bs4 import BeautifulSoup
import requests

def scrape_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    scraped_data = {}
    scraped_data['title'] = soup.find('h1', attrs={"property":"headline"}).text
    scraped_data['genre'] = []
    scraped_data['developers'] = []
    scraped_data['publishers'] = []
    scraped_data['links'] = []
    scraped_data['release_date'] = ""
    for p in soup.find_all('p'):
        # adding links
        if p.contents[0].name == 'b' and p.contents[0].text.__contains__("Link"):
            link = p.find('a')
            if link:
                scraped_data['links'].append(link['href'])
        # if p.contents[0].name == 'span' and p.contents[0].text.__contains__("Genre"):
        # if p.contents[0].name == 'span' and p.contents[0].text.__contains__(""):
    return scraped_data

def refresh_list():
    # Specify the path to your local JSON file
    file_path = "games.json"

    with open(file_path, "r") as f:
        game_data = json.load(f)

    for url in game_data.values():
        scraped_data = scrape_webpage(url)
        # print(scraped_data)

if __name__ == "__main__":
    print("Running job::module module")
    refresh_list()