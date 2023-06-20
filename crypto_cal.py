import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
from datetime import datetime

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Setup the driver
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(30)

# Open the page
driver.get("https://defillama.com/calendar")

# Parse the page source
soup = BeautifulSoup(driver.page_source, "html.parser")

# Scrape the events
event_elements = soup.select('.sc-762d8551-0.dGOocz, .sc-96c31c29-4.gPSdtR, .sc-96c31c29-3.ewkuan')

# Parse the events
events = []
for i in range(0, len(event_elements), 3):
    event_name_element = event_elements[i+1]
    date_info_element = event_elements[i+2]
    
    # Extract the event name
    event_name = event_name_element.text
    
    # Extract the date string
    date_info_text = date_info_element.text
    date_str = ""
    try:
        date_str = date_info_text.split("S")[-2].split("M")[-1]
    except:
        continue
    
    # Append to events list
    events.append({"Event Name": event_name, "Date": date_str})

# Slack OAuth Access Token
slack_token = os.environ.get('SLACK_OAUTH_ACCESS_TOKEN')

# Slack channel to post to
channel_id = os.environ.get('SLACK_CHANNEL_ID')

# Today's date
today = datetime.now()

# Post today's events to Slack
for event in events:
    event_date = datetime.strptime(event["Date"], '%d %b %Y%H:%M')
    if event_date.date() == today.date():
        text = f"{event['Event Name']} is happening today at {event_date.strftime('%H:%M')}"
        # Posting JSON formatted message
        response = requests.post('https://slack.com/api/chat.postMessage',
                                 headers={'Authorization': f'Bearer {slack_token}'},
                                 json={'channel': channel_id, 'text': text})

# Close the driver
driver.quit()
