import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up Selenium WebDriver with options
def create_driver():
    chrome_options = Options()
    # Remove headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up the WebDriver path to your ChromeDriver executable
    service = Service()  # Change this to your path
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_webpage(url):
    driver = create_driver()
    try:
        driver.get(url)
        
        # Extract data from the page using Selenium
        scraped_data = {
            'title': driver.find_element(By.XPATH, '//h1[@property="headline"]').text if driver.find_elements(By.XPATH, '//h1[@property="headline"]') else "N/A",
            'genre': [],
            'developers': [],
            'publishers': [],
            'links': [],
            'release_date': ""
        }

        # Extract all <p> tags for data
        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        for p in paragraphs:
            text = p.text
            # Extract links
            if "Link" in text:
                link_element = p.find_element(By.XPATH, './/a')
                if link_element and link_element.get_attribute('href'):
                    scraped_data['links'].append(link_element.get_attribute('href'))

            # Extract genres
            if "Genre" in text:
                genre_text = text.replace("Genre:", '').strip()
                scraped_data['genre'] = [genre.strip() for genre in genre_text.split(',') if genre.strip()]

        logging.info(f"Successfully scraped data from {url}")
        return scraped_data

    except Exception as e:
        logging.error(f"Error while scraping {url}: {e}")
        return None
    finally:
        driver.quit()

def refresh_list():
    # Specify the path to your local JSON file
    file_path = "games.json"

    try:
        with open(file_path, "r") as f:
            game_data = json.load(f)

        for url in game_data.values():
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
