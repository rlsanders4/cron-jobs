import speedtest
from datetime import datetime, timedelta
import os
import sys
import time

WIFI_SPEED_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wifi_speed_data.csv")

def check_wifi_speed(max_attempts=5):
    for attempt in range(max_attempts):
        try:
            st = speedtest.Speedtest()
            download_speed = st.download() / 1024 / 1024  # Convert to Mbps
            upload_speed = st.upload() / 1024 / 1024  # Convert to Mbps
            return download_speed, upload_speed
        except Exception as e:
            if (attempt == max_attempts - 1):
                print(f"Error occured: {e}. All attempts failed.")
                sys.exit(1)
            else:
                print(f"Error occured: {e}. Retrying...")
                time.sleep(1)

def save_speed_data(download_speed, upload_speed):
    timestamp = datetime.now().isoformat()
    with open(WIFI_SPEED_DATA, "a") as f:
        f.write("{},{},{}\n".format(timestamp, download_speed, upload_speed))

def delete_old_data():
    current_time = datetime.now()
    with open(WIFI_SPEED_DATA, "r") as f:
        lines = f.readlines()
    with open(WIFI_SPEED_DATA, "w") as f:
        for line in lines:
            timestamp_str, _, _ = line.strip().split(',')
            timestamp = datetime.fromisoformat(timestamp_str)
            if current_time - timestamp <= timedelta(weeks=1):
                f.write(line)

if __name__ == "__main__":
    download_speed, upload_speed = check_wifi_speed()
    save_speed_data(download_speed, upload_speed)
    delete_old_data()

