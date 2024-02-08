# cron-jobs

1) Create a 'script_data.py' file that contains the constants SENDER_EMAIL, RECIEVER_EMAIL, and APP_PASSWORD with appropriate values.

2) Run collect_wifi_data.py every hour:
```
0 * * * * /usr/bin/python3 /path/to/collect_wifi_data.py
```

3) Run email_wifi_report.py every Sunday at midnight:
```
0 0 * * 0 /usr/bin/python3 /path/to/email_wifi_report.py
```
