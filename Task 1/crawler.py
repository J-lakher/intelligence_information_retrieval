import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from threading import Timer

# Path to your ChromeDriver
CHROMEDRIVER_PATH = 'chromedriver/chromedriver.exe'

# Base URL to the publications page
BASE_URL = "https://pureportal.coventry.ac.uk/en/organisations/eec-school-of-computing-mathematics-and-data-sciences-cmds/publications/"

# Setup Selenium options
options = Options()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--disable-gpu')  # Disable GPU acceleration
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

def fetch_page(url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

def get_total_pages():
    fetch_page(BASE_URL)
    try:
        pagination = driver.find_element(By.CSS_SELECTOR, 'nav.pages ul')
        pages = pagination.find_elements(By.CSS_SELECTOR, 'li a.step')
        page_numbers = [int(page.text) for page in pages if page.text.isdigit()]
        if page_numbers:
            return max(page_numbers)
        return 1  # If no pagination is found, assume only 1 page
    except Exception as e:
        # print(f"No pagination found: {e}")
        return 1  # If an error occurs, assume only 1 page

def fetch_publications():
    publications = []
    total_pages = get_total_pages()

    # Fetch the initial page
    fetch_page(BASE_URL)
    publications.extend(extract_publications())

    # Fetch subsequent pages
    for page_number in range(2, total_pages + 1):
        fetch_page(f"{BASE_URL}?page={page_number - 1}")
        publications.extend(extract_publications())
    
    return publications

def extract_publications():
    publications = []
    pubs = driver.find_elements(By.CSS_SELECTOR, 'li.list-result-item')

    for pub in pubs:
        title_element = pub.find_element(By.CSS_SELECTOR, 'h3.title a')
        title = title_element.text.strip()
        link = title_element.get_attribute('href')
        
        authors = []
        author_elements = pub.find_elements(By.CSS_SELECTOR, 'a.link.person')
        for author_element in author_elements:
            author_name = author_element.text.strip()
            author_link = author_element.get_attribute('href')
            authors.append({'name': author_name, 'link': author_link})
            
        try:
            pub_year = pub.find_element(By.CSS_SELECTOR, 'span.date').text.strip()
        except:
            pub_year = None
        
        publications.append({'Title': title, 'Authors': authors, 'Year': pub_year, 'Link': link})
    
    return publications

def main():
    publications = fetch_publications()
    
    # Reset the JSON file
    if os.path.exists('publications.json'):
        os.remove('publications.json')

    # Save data to JSON file
    with open('publications.json', 'w', encoding='utf-8') as f:
        json.dump(publications, f, ensure_ascii=False, indent=4)
    
    print("Crawling complete, data saved to publications.json")

def schedule_crawler(interval=300):
    main()
    Timer(interval, schedule_crawler, [interval]).start()

if __name__ == "__main__":
    schedule_crawler()
    driver.quit()
