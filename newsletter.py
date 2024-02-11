from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import datetime
import pytz
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from script_data import SENDER_EMAIL, RECIEVER_EMAIL, APP_PASSWORD, WEATHER_TOKEN, LATITUDE, LONGITUDE, TIMEZONE, FIREFOX_BINARY, GECKO_DRIVER
import smtplib
import os
import shutil

PYCACHE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "__pycache__")

class Newsletter:
    def __init__(self, debug=False):
        self.debug=debug   
        self.html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>News Aggregator</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; color: #333; line-height: 1.6; padding: 20px;">
<h1 style="text-align: center; margin-bottom: 30px;">The Morning Report</h1>
'''
    
    def add(self, content):
        self.html_content += content + "\n"

    def finish(self):
        self.html_content += '''
</body>
</html>
'''
        if self.debug:
            with open('newsletter_debug.html', 'w', encoding='utf-8') as file:
                file.write(str(newsletter))


    def __str__(self):
     return self.html_content
    
def format_article(newsletter, headline, summary, link):
    newsletter.add("<div style=\"background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); margin-bottom: 20px; padding: 20px;\">")
    newsletter.add(f"<h3 style=\"font-size: 20px; margin-bottom: 10px;\">{headline}</h3>")
    newsletter.add(f"<p style=\"font-size: 16px; margin-bottom: 15px;\">{summary}<a href=\"{link}\" style=\"color: #007bff; text-decoration: none;\">Read more</a></p>")
    newsletter.add("</div>")
        

def scrape_wsj(newsletter):
    # Set up Firefox options
    options = Options()
    options.binary_location = FIREFOX_BINARY
    options.add_argument("-headless")
    #options.set_preference("general.useragent.override", " Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0")

    service = Service(GECKO_DRIVER)  # Replace with the path to your geckodriver executable
    driver = webdriver.Firefox(service=service, options=options)
    newsletter.add("<hr style=\"border-top: 1px solid #ddd; margin-bottom: 30px;\">")
    newsletter.add("<div style=\"margin-bottom: 50px;\">")
    newsletter.add("<h2 style=\"text-align: center; font-size: 28px; margin-bottom: 30px;\">The Wall Street Journal</h2>")

    try:
        # Open the Wall Street Journal website
        driver.get('https://www.wsj.com')
        # Wait for the main content to load (adjust timeout as needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'WSJTheme--headline--unZqjb45')))

        articles = driver.find_elements(By.CLASS_NAME, 'WSJTheme--story--XB4V2mLz')

        # Scrape headline, summary, and link for each article
        for article in articles[:5]:  # Get top 5 articles
            headline_element = article.find_element(By.CLASS_NAME, "WSJTheme--headline--unZqjb45")
            summary_element = article.find_element(By.CLASS_NAME, "WSJTheme--summaryText--2LRaCWgJ")
            link_element = headline_element.find_element(By.TAG_NAME, "a")

            headline = headline_element.text
            summary = summary_element.text + "<br>"
            link = link_element.get_attribute("href")

            format_article(newsletter, headline, summary, link)
    except Exception as e:
        print(e)
    finally:
        # Close the browser
        driver.quit()

    newsletter.add("</div>")

def scrape_nyt(newsletter):
    # Set up Firefox options
    options = Options()
    options.binary_location = FIREFOX_BINARY
    options.add_argument("-headless")

    # Set up the Firefox driver
    service = Service(GECKO_DRIVER)  # Replace with the path to your geckodriver executable
    driver = webdriver.Firefox(service=service, options=options)

    newsletter.add("<hr style=\"border-top: 1px solid #ddd; margin-bottom: 30px;\">")
    newsletter.add("<div style=\"margin-bottom: 50px;\">")
    newsletter.add("<h2 style=\"text-align: center; font-size: 28px; margin-bottom: 30px;\">The New York Times</h2>")

    try:
        # Open the New York Times website
        driver.get('https://www.nytimes.com')

        # Wait for the main content to load (adjust timeout as needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'story-wrapper')))

        articles = driver.find_elements(By.XPATH, '//section[@class="story-wrapper" and a]')

        # Scrape headline, summary, and link for each article
        for article in articles[:5]:  # Get top 5 articles
            headline_element = article.find_element(By.CLASS_NAME, "indicate-hover")

            try:
                summary_element = article.find_element(By.CLASS_NAME, "summary-class")
            except:
                summary_element = ""

            link_element = article.find_element(By.TAG_NAME, "a")

            headline = headline_element.text
            summary = " "
            if summary_element: summary = summary_element.text + "<br>"
            link = link_element.get_attribute("href")

            format_article(newsletter, headline, summary, link)

    except Exception as e:
        print(e)
    finally:
        # Close the browser
        driver.quit()
    
    newsletter.add("</div>")
    
def get_weather(newsletter, api_key, lat, lon, timezone):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=imperial"
    response = requests.get(url)
    data = response.json()

    newsletter.add("<hr style=\"border-top: 1px solid #ddd; margin-bottom: 30px;\">")
    newsletter.add("<div>")
    newsletter.add("<h2 style=\"text-align: center; font-size: 24px; margin-bottom: 20px;\">Today's Weather Forecast</h2>")

    if data["cod"] == '200':
        current_time_eastern = datetime.datetime.now(pytz.timezone(timezone))
        for forecast in data["list"]:
            time = datetime.datetime.fromtimestamp(forecast["dt"], pytz.utc).astimezone(pytz.timezone(timezone))
            if time.date() != current_time_eastern.date():
               break
            time = time.strftime('%H:%M')
            weather_desc = forecast["weather"][0]["description"]
            temp = str(round(float(forecast["main"]["temp"])))
            feels_like = forecast["main"]["feels_like"]
            humidity = forecast["main"]["humidity"]
            wind_speed = forecast["wind"]["speed"]

            newsletter.add("<div style=\"background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); padding: 20px; margin-bottom: 10px;\">")
            newsletter.add("<div style=\"font-size: 16px;\">")
            newsletter.add(f"<span>{time}</span>")
            newsletter.add(f"<span style=\"float: right;\">{weather_desc}, {temp}°F</span>")
            newsletter.add("</div>")
            newsletter.add("</div>")
    else:
        print("Error:" + data["message"])
    
    newsletter.add("</div>")

def send_email(newsletter):
    # Send email
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIEVER_EMAIL
    msg['Subject'] = "The Morning Report"

    if (newsletter.debug):
        with open('newsletter_debug.html', "r", encoding='utf-8') as text:
            msg.attach(MIMEText(text.read(), 'html', 'utf-8'))
    else:
        msg.attach(MIMEText(str(newsletter), 'html', 'utf-8'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, APP_PASSWORD)
    text = msg.as_string()
    server.sendmail(SENDER_EMAIL, RECIEVER_EMAIL, text)
    server.quit()

def clean_up():
    # Check if the __pycache__ folder exists
    if os.path.exists(PYCACHE):
        try:
            # Delete the __pycache__ folder and all its contents recursively
            shutil.rmtree(PYCACHE)
        except OSError as e:
            print(f"Error: {e.strerror}")

if __name__ == "__main__":
    newsletter = Newsletter(True)
    scrape_wsj(newsletter)
    scrape_nyt(newsletter)
    get_weather(newsletter, WEATHER_TOKEN, LATITUDE, LONGITUDE, TIMEZONE)
    newsletter.finish()
    send_email(newsletter)
    clean_up()
