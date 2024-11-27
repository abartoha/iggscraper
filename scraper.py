import json
from bs4 import BeautifulSoup

# Specify the path to your local HTML file
file_path = "source.html"

# Open the file and read its content (specifying encoding can help)
with open(file_path, "r", encoding='utf-8') as f:
    html_content = f.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the mother list
mother_div = soup.find('div', attrs={"property": "text", "class": "uk-margin-medium-top"})

# Find the lists for all the games
game_data = {x.text: x['href'] for ul in mother_div.find_all('ul') for x in ul.find_all('a')}

# Save the extracted list as a JSON file
with open("games.json", "w", encoding='utf-8') as outfile:
    json.dump(game_data, outfile, indent=4)  # Optional: indent for readability

print("Game data saved to games.json!")
