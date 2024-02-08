# Run collect_wifi_data.py every hour
0 * * * * /usr/bin/python3 /path/to/collect_wifi_data.py

# Run email_wifi_report.py every Sunday at midnight
0 0 * * 0 /usr/bin/python3 /path/to/email_wifi_report.py