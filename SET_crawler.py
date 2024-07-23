from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os

###1. Go to 三立
###2. Use beautifulsoup to analysis the page
###3. find img tag and else under <a> tag
###4. extract imgs and its name, and call save_image function.

# Path to the Edge WebDriver
PATH = "E:/edgedriver_win64/msedgedriver.exe"
service = EdgeService(PATH)

# Initialize WebDriver
driver = webdriver.Edge(service=service)
driver.get('https://www.setn.com/')

# Wait until the images are loaded
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))

# Get the page source and parse it with BeautifulSoup
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")


driver.quit()

# Directory to save images
save_dir = "E:/三立"
os.makedirs(save_dir, exist_ok=True)

# Function to save image
def save_image(name, url, save_dir):
    try:
        response = requests.get(url)
        img_data = response.content
        img_path = os.path.join(save_dir, f'{name}.png')

        with open(img_path, 'wb') as f:
            f.write(img_data)
        print(f'Saved: {name}, {url}')
    except Exception as e:
        print(f'Error saving image {name}: {e}')

# Find and save standalone images
imgs = soup.find_all('img')     
for img in imgs:
    try:
        name = img.get('alt', 'no_name')
        url = img.get('src')

        if url:
            save_image(name, url, save_dir)
        else:
            print(f'Skipping image with no URL: {name}')
    except Exception as e:
        print(f'Error processing image: {e}')

# Find and save images inside <a> tags
a_tags = soup.find_all('a', class_='gt')
for a in a_tags:
    try:
        img = a.find('img')
        if img:
            url_a = img.get('src')
            text_div = a.find('div', class_='newsimg-area-text')
            if text_div and text_div.text.strip():      # clean div tag <div class="newsimg-area-text ">民調／賴清德聲望曝光！獲48.2%民意讚同</div>
                clean_name = text_div.text.strip()

            if clean_name and url_a:
                save_image(clean_name, url_a, save_dir)
    except Exception as e:
        print(f'Error processing image in <a> tag: {e}')
