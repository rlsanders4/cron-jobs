# cron-jobs
This repo contains a series of scripts that can be used with cron to automate tasks on your linux system.


## Generate a weekly internet speed report (sent to your email)
1) Create a <code>config.py</code> file that contains the following constants.
   ```
   SENDER_EMAIL = "sender@example.com"
   RECIEVER_EMAIL = "reciever@example.com"
   APP_PASSWORD = "########" (gmail app password)
   ```
3) Setup the cronjob for collecting network data. Run <code>collect_wifi_data.py</code> every hour:
   ```
   0 * * * * /usr/bin/python3 /path/to/collect_wifi_data.py
   ```

3) Setup the cronjob for emailing the report. Run <code>email_wifi_report.py</code> at the end of the week:
   ```
   59 23 * * 6 /usr/bin/python3 /path/to/email_wifi_report.py
   ```


## Update linux system with apt package manager
1) Setup the cronjob. Run <code>system_update.sh</code> every day at 0300. This must be added to the root crontab for correct permissions.
   ```
   0 3 * * * /bin/bash /path/to/system_update.sh
   ```

## Send a morning newsletter email containing the latest news headlines, weather forecast, and stock market info
1) Create a <code>config.py</code> file that contains the following constants.
   ```
   SENDER_EMAIL = "sender@example.com"
   RECIEVER_EMAIL = "reciever@example.com"
   APP_PASSWORD = "########" (gmail app password)
   WEATHER_TOKEN = "########" (openweathermap.com API key)
   LATITUDE = "40.730610"
   LONGITUDE = "-73.935242"
   TIMEZONE = "US/Eastern"
   FIREFOX_BINARY = "/path/to/firefox"
   GECKO_DRIVER = "/path/to/geckodriver"
   STOCKS = ["MSFT", "AAPL", "NVDA", "AMZN"]
   MARKET_TOKEN = "########" (financialmodelingprep.com API key)
   ```
3) Setup the cronjob. Run <code>newsletter.py</code> every morning:
   ```
   55 3 * * * /usr/bin/python3 /home/ralph/Documents/cron-jobs/newsletter.py
   ```
