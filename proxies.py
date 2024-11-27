import json
import time
import random
import logging
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from tqdm import tqdm

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a UserAgent instance to generate a random User-Agent
ua = UserAgent()

# Read proxies from proxies_list.txt
def load_proxies(file_path="proxies_list.txt"):
    try:
        with open(file_path, "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
            logging.info(f"Loaded {len(proxies)} proxies from {file_path}")
            return proxies
    except FileNotFoundError:
        logging.error(f"Proxies file {file_path} not found.")
        return []

# Rotate through proxies in a round-robin fashion
class ProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
        self.index = 0

    def get_proxy(self):
        if not self.proxies:
            raise ValueError("No proxies available")
        proxy = self.proxies[self.index]
        self.index = (self.index + 1) % len(self.proxies)
        return proxy

# Initialize proxy rotator
proxies = load_proxies()
proxy_rotator = ProxyRotator(proxies)

def scrape_webpage(url):
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
        'Referer': 'https://www.google.com/',
        'TE': 'Trailers'
    }

    for attempt in range(len(proxies)):  # Retry up to the number of available proxies
        proxy = proxy_rotator.get_proxy()
        proxies_dict = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        
        try:
            # Adding a random sleep to mimic human behavior
            sleep_time = random.uniform(1, 5)
            logging.info(f"Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            
            response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            
            # If request is successful, break out of retry loop
            if response.status_code != 423:
                break
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for {url} using proxy {proxy}: {e}")
            if attempt == len(proxies) - 1:
                logging.error("All proxies failed. Exiting.")
                return None
            logging.info("Retrying with the next proxy.")
            continue

    # Parsing the response if it was successful
    soup = BeautifulSoup(response.content, 'html.parser')
    scraped_data = {
        'title': soup.find('h1', attrs={"property": "headline"}).text if soup.find('h1', attrs={"property": "headline"}) else "N/A",
        'genre': [],
        'developers': [],
        'publishers': [],
        'links': [],
        'release_date': ""
    }

    for p in soup.find_all('p'):
        # Adding links
        if p.contents and p.contents[0].name == 'b' and "Link" in p.contents[0].text:
            link = p.find('a')
            if link and 'href' in link.attrs:
                scraped_data['links'].append(link['href'])

        # Extracting genre
        if p.contents and p.contents[0].name == 'span' and "Genre" in p.contents[0].text:
            genre_text = p.text.replace(p.contents[0].text, '').strip()
            scraped_data['genre'] = [genre.strip() for genre in genre_text.split(',') if genre.strip()]

    logging.info(f"Successfully scraped data from {url}")
    return scraped_data

def refresh_list():
    # Specify the path to your local JSON file
    file_path = "games.json"

    try:
        with open(file_path, "r") as f:
            game_data = json.load(f)

        # Display progress bar
        for url in tqdm(game_data.values(), desc="Scraping URLs"):
            scraped_data = scrape_webpage(url)
            if scraped_data:
                print(scraped_data)  # Print the scraped data for verification

    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
        print(f"File {file_path} not found.")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {file_path}.")
        print(f"Error decoding JSON from {file_path}.")

if __name__ == "__main__":
    logging.info("Starting the scraping job")
    print("Running job::module module")
    refresh_list()
    logging.info("Scraping job completed")
