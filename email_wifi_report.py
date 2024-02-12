import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import csv
from datetime import datetime, timedelta
from config import SENDER_EMAIL, RECIEVER_EMAIL, APP_PASSWORD
import os
import shutil

WIFI_SPEED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wifi_speed_data.csv")
WIFI_SPEED_DAILY_AVERAGES = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wifi_speed_daily_averages.png")
PYCACHE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "__pycache__")


def clean_up():
    #Delete wifi_speed_daily_averags.png
    os.remove(WIFI_SPEED_DAILY_AVERAGES)
    
    # Check if the __pycache__ folder exists
    if os.path.exists(PYCACHE):
        try:
            # Delete the __pycache__ folder and all its contents recursively
            shutil.rmtree(PYCACHE)
        except OSError as e:
            print(f"Error: {e.strerror}")

def calculate_daily_averages():
    daily_data = {}
    with open(WIFI_SPEED_DATA, "r") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            timestamp_str, download_speed, upload_speed = row
            date = datetime.fromisoformat(timestamp_str).date()
            if date not in daily_data:
                daily_data[date] = {"download_sum": 0, "upload_sum": 0, "count": 0}
            daily_data[date]["download_sum"] += float(download_speed)
            daily_data[date]["upload_sum"] += float(upload_speed)
            daily_data[date]["count"] += 1
    daily_averages = {}
    for date, data in daily_data.items():
        daily_averages[date] = {
            "download_avg": data["download_sum"] / data["count"],
            "upload_avg": data["upload_sum"] / data["count"]
        }
    return daily_averages

def create_report_graph():
    daily_averages = calculate_daily_averages()

    # Get the dates of the previous seven days
    dates = [datetime.now().date() - timedelta(days=i) for i in range(6, -1, -1)]
    download_averages = [daily_averages.get(date, {"download_avg": 0})["download_avg"] for date in dates]
    upload_averages = [daily_averages.get(date, {"upload_avg": 0})["upload_avg"] for date in dates]

    # Create graph
    plt.plot(dates, download_averages, label="Average Download Speed (Mbps)")
    plt.plot(dates, upload_averages, label="Average Upload Speed (Mbps)")
    plt.xlabel("Date")
    plt.ylabel("Speed (Mbps)")
    plt.title("WiFi Speed Daily Averages")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(WIFI_SPEED_DAILY_AVERAGES)

def send_email_with_report():
    create_report_graph()

    # Send email
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIEVER_EMAIL
    msg['Subject'] = "WiFi Speed Daily Averages Report"

    body = "WiFi speed daily averages report is attached."
    msg.attach(MIMEText(body, 'plain'))

    with open(WIFI_SPEED_DAILY_AVERAGES, "rb") as img_file:
        img = MIMEImage(img_file.read())
    msg.attach(img)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, APP_PASSWORD)
    text = msg.as_string()
    server.sendmail(SENDER_EMAIL, RECIEVER_EMAIL, text)
    server.quit()

if __name__ == "__main__":
    send_email_with_report()
    clean_up()

