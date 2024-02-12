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
from config import SENDER_EMAIL, RECIEVER_EMAIL, APP_PASSWORD, WEATHER_TOKEN, LATITUDE, LONGITUDE, TIMEZONE, FIREFOX_BINARY, GECKO_DRIVER, MARKET_TOKEN, STOCKS
import smtplib
import os
import shutil
import traceback

PYCACHE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "__pycache__")

class Newsletter:
    def __init__(self, debug=False):
        self.debug=debug   
        self.html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Morning Report</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f5f5f5; color: #333; line-height: 1.6; padding: 20px; max-width: 600px; margin: auto">
<h1 style="text-align: center; margin-bottom: 30px; font-size: 32px">The Morning Report</h1>
'''
    
    def add(self, content):
        self.html_content += content + "\n"

    def finish(self):
        self.html_content += '''</body>
</html>
'''
        if self.debug:
            with open('newsletter_debug.html', 'w', encoding='utf-8') as file:
                file.write(str(newsletter))


    def __str__(self):
     return self.html_content
    
def format_article(headline, summary, link):
    return f'''<div style=\"background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); margin-bottom: 20px; padding: 20px;\">
<h3 style=\"font-size: 20px; margin-bottom: 10px;\">{headline}</h3>
<p style=\"font-size: 16px; margin-bottom: 15px;\">{summary}<a href=\"{link}\" style=\"color: #007bff; text-decoration: none;\">Read more</a></p>
</div>'''
        

def scrape_wsj(newsletter):
    wsj_section = ""
    # Set up Firefox options
    options = Options()
    options.binary_location = FIREFOX_BINARY
    options.add_argument("-headless")
    #options.set_preference("general.useragent.override", " Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0")

    service = Service(GECKO_DRIVER)  # Replace with the path to your geckodriver executable
    driver = webdriver.Firefox(service=service, options=options)
    wsj_section += '''<hr style=\"border-top: 1px solid #ddd; margin-bottom: 30px;\">
<div style=\"margin-bottom: 50px;\">
<h2 style=\"text-align: center; font-size: 28px; margin-bottom: 30px;\">WSJ Top Stories</h2>'''

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

            wsj_section += format_article(headline, summary, link)
        
        wsj_section += "</div>"
    except:
        print("Error scraping the WSJ:")
        traceback.print_exc()
    finally:
        # Close the browser
        driver.quit()

    newsletter.add(wsj_section)

def scrape_nyt(newsletter):
    nyt_section = ""
    try:
        # Set up Firefox options
        options = Options()
        options.binary_location = FIREFOX_BINARY
        options.add_argument("-headless")

        # Set up the Firefox driver
        service = Service(GECKO_DRIVER)  # Replace with the path to your geckodriver executable
        driver = webdriver.Firefox(service=service, options=options)

        nyt_section += '''<hr style=\"border-top: 1px solid #ddd; margin-bottom: 30px;\">
<div style=\"margin-bottom: 50px;\">
<h2 style=\"text-align: center; font-size: 28px; margin-bottom: 30px;\">NYT Top Stories</h2>'''

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

            nyt_section += format_article(headline, summary, link)

        nyt_section += "</div>"

    except:
        print("Error scraping the NYT:")
        traceback.print_exc()
    finally:
        # Close the browser
        driver.quit()

    newsletter.add(nyt_section)
    
    
def get_weather(newsletter):
    weather_section = ""
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={LATITUDE}&lon={LONGITUDE}&appid={WEATHER_TOKEN}&units=imperial"
        response = requests.get(url)
        data = response.json()

        weather_section += '''<hr style=\"border-top: 1px solid #ddd; margin-bottom: 30px;\">
<div style=\"margin-bottom: 50px;\">
<h2 style=\"text-align: center; font-size: 28px; margin-bottom: 20px;\">Today's Forecast</h2>'''

        if data["cod"] == '200':
            current_time_eastern = datetime.datetime.now(pytz.timezone(TIMEZONE))
            for forecast in data["list"]:
                time = datetime.datetime.fromtimestamp(forecast["dt"], pytz.utc).astimezone(pytz.timezone(TIMEZONE))
                if time.date() != current_time_eastern.date():
                    break
                time = time.strftime('%H:%M')
                weather_desc = forecast["weather"][0]["description"].capitalize()
                temp = str(round(float(forecast["main"]["temp"])))

                weather_section += f'''<div style="background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); padding: 20px; margin-bottom: 10px;\">
<div style="font-size: 16px;">
<div style="display: inline-block; width: 20%; text-align: left">{time}</div>
<div style="display: inline-block; width: 57%; text-align: center">{weather_desc}</div>
<div style="display: inline-block; width: 20%; text-align: right">{temp}°F</div>
</div>
</div>'''
                
            weather_section += "</div>"
        else:
            raise Exception(data["message"])
        
    except:
        print("Error getting weather data:")
        traceback.print_exc()

    newsletter.add(weather_section)

def get_markets(newsletter):
    markets_section = ""
    try:
        markets_section += '''<hr style="border-top: 1px solid #ddd; margin-bottom: 30px;">
<div>
<h2 style="text-align: center; font-size: 28px; margin-bottom: 30px;">Markets</h2>
<div style="background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); margin-bottom: 20px; padding: 20px; font-size: 16px">
<table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
    <thead>
        <tr>
            <th style="border-bottom: 1px solid #ddd; padding: 10px; text-align: left;">Stock</th>
            <th style="border-bottom: 1px solid #ddd; padding: 10px; text-align: left;">Price</th>
            <th style="border-bottom: 1px solid #ddd; padding: 10px; text-align: left;">Today</th>
            <th style="border-bottom: 1px solid #ddd; padding: 10px; text-align: left;">5 Days</th>
        </tr>
    </thead>
    <tbody>  
'''

        for stock in STOCKS:
            price_change_url = f"https://financialmodelingprep.com/api/v3/stock-price-change/{stock}?apikey={MARKET_TOKEN}"
            price_change_data = requests.get(price_change_url).json()[0]

            quote_short_url = f"https://financialmodelingprep.com/api/v3/quote-short/{stock}?apikey={MARKET_TOKEN}"
            quote_short_data = requests.get(quote_short_url).json()[0]

            price = f"{quote_short_data['price']:.2f}"
            today = f"{price_change_data['1D']:.2f}"
            five_day = f"{price_change_data['5D']:.2f}"

            if float(today) < 0.0:
                today_color = "red"
            else:
                today_color = "green"
                today = "+" + today

            if float(five_day) < 0.0:
                five_day_color = "red"
            else:
                five_day_color = "green"
                five_day = "+" + five_day

            markets_section += f'''<tr>
<td style=\"border-bottom: 1px solid #ddd; padding: 10px; text-align: left;\">{stock}</td>
<td style=\"border-bottom: 1px solid #ddd; padding: 10px; text-align: left;\">{price}</td>
<td style=\"border-bottom: 1px solid #ddd; padding: 10px; color: {today_color}; text-align: left;\">{today}%</td>
<td style=\"border-bottom: 1px solid #ddd; padding: 10px; color: {five_day_color}; text-align: left;\">{five_day}%</td>
</tr>'''

        markets_section += '''
</tbody>
</table>
</div>
</div>
'''
    except:
        print ("Error getting market info:")
        traceback.print_exc()
    
    newsletter.add(markets_section)

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
        except:
            print("Error cleaning files:")
            traceback.print_exc()

if __name__ == "__main__":
    newsletter = Newsletter()
    scrape_wsj(newsletter)
    scrape_nyt(newsletter)
    get_weather(newsletter)
    get_markets(newsletter)
    newsletter.finish()
    send_email(newsletter)
    clean_up()
