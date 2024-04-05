import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

# Script arguments
email = sys.argv[1]
password = sys.argv[2]

# Create Chrome web driver
option = webdriver.ChromeOptions()
option.add_argument("start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

# Login to Sync Passport
login_url = "https://www.syncpassport.com/SignUp/SignIn"
driver.get(login_url)
driver.find_element(By.ID, "Email").send_keys(email)
driver.find_element(By.ID, "Password").send_keys(password)
driver.find_element(By.XPATH, "//button[@type='submit']").click()

# Go to score section
score_url = "https://www.syncpassport.com/MyScores"
driver.get(score_url)
driver.find_element(By.ID, "FilterDate").click()
driver.find_element(By.ID, "clearDateFilter").click() # clear date filter to list all scores

def extract_HTML_bowling_game_score(html_game):
    """
    Extracts a BeautifulSoup object of the SyncPassport bowling game
    structured within a div of class "clearfix loadingBackground". The
    game is structured and returned as a dictionary.
 
    Args:
        html_game (BeautifulSoup obj): Bowling game scraped from div on SyncPassport
 
    Returns:
        dict: the game stats (date, bowling center, and score)
    """
    bowling_score_dict = {}

    # Get date
    date = html_game.find('h2', class_='scoredate').text
    bowling_score_dict["date"] = date

    # Get bowling center
    bowling_center = html_game.find(class_='scorecenter').text
    bowling_score_dict["bowling_center"] = bowling_center

    # Get all bowling frame HTML markup
    cls_frame_regex = re.compile('^cls_frame(10)?$')
    frames = html_game.find_all('td', { "class": cls_frame_regex })

    frame_stats = []

    for frame_num, frame in enumerate(frames, start=1):
        frame_stat = {}
        frame_stat["frame_num"] = frame_num

        # Get all frame counts (3rd count in tenth frame)
        frame_counts = frame.find_all('td', { "class": re.compile('^cls_ball[123]$') })

        if (len(frame_counts) >= 2):
            frame_count_1 = frame_counts[0].text
            frame_count_2 = frame_counts[1].text
            frame_stat["frame_count_1"] = frame_count_1
            frame_stat["frame_count_2"] = frame_count_2

            if (len(frame_counts) == 3):
                frame_count_3 = frame_counts[2]
                frame_stat["frame_count_3"] = frame_count_3.text

            # Get frame score
            frame_score = frame.find('td', { "class": re.compile('^cls_framescore(10)?') }).text
            frame_stat["frame_score"] = frame_score

            frame_stats.append(frame_stat)

    bowling_score_dict["frame_stats"] = frame_stats

    # Get game total score
    score_total = html_game.find('td', class_='cls_scoretotal').text
    bowling_score_dict["score_total"] = score_total

    print(bowling_score_dict)
    return bowling_score_dict

# Extract all score data using Beautiful Soup
try:
    # Wait until score spinner disappears
    wait = WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner")))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    div_scores = soup.find(id="scoreSheetResults")

    bowling_scores = []
    for html_game in div_scores.find_all('div', class_='clearfix loadingBackground'):
        bowling_score_dict = extract_HTML_bowling_game_score(html_game)
        bowling_scores.append(bowling_score_dict)
        f = open('scores.json', 'w')
        f.write(str(bowling_scores))
        f.close()
except TimeoutException:
    print("Scores took too long to load")