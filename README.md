# cron-jobs

### Generate a weekly internet speed report (sent to your email)
1) Create a <code>script_data.py</code> file that contains the constants <code>SENDER_EMAIL</code>, <code>RECIEVER_EMAIL</code>, and <code>APP_PASSWORD</code> with appropriate values.

2) Run <code>collect_wifi_data.py</code> every hour:
```
0 * * * * /usr/bin/python3 /path/to/collect_wifi_data.py
```

3) Run <code>email_wifi_report.py</code> at the end of the week:
```
59 23 * * 6 /usr/bin/python3 /path/to/email_wifi_report.py
```
