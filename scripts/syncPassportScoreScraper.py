from urllib.request import urlopen
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Script arguments
email = sys.argv[1]
password = sys.argv[2]

url = "https://www.syncpassport.com/MyScores"

# page = urlopen(url)
# html_bytes = page.read()
# html = html_bytes.decode("utf_8")
# print(html)

# login
# import requests
login_url = "https://www.syncpassport.com/SignUp/SignIn"
# login_payload = {
#     "Email": "some-email",
#     "Password": "some-password"
# }
# s = requests.session()
# response = s.post(login_url, login_payload)
# print(response.status_code)
# print(response.content)

# Create Chrome web driver
option = webdriver.ChromeOptions()
option.add_argument("start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

driver.implicitly_wait(3)

# Login to Sync Passport
driver.get(login_url)
driver.find_element(By.ID, "Email").send_keys(email)
driver.find_element(By.ID, "Password").send_keys(password)
driver.find_element(By.XPATH, "//button[@type='submit']").click()

# Go to score section
score_url = "https://www.syncpassport.com/MyScores"
driver.get(score_url)
driver.find_element(By.ID, "FilterDate").click()
driver.find_element(By.ID, "clearDateFilter").click() # clear date filter to list all scores

# Extract all score data using Beautiful Soup

try:
    # Wait until score spinner disappears
    wait = WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner")))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    div_scores = soup.find(id="scoreSheetResults")

    for child in div_scores.find_all('div', class_='clearfix loadingBackground'):
        print(child)
        break
except TimeoutException:
    print("Scores took too long to load")
    