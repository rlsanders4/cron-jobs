import speedtest
from datetime import datetime, timedelta

WIFI_SPEED_DATA = "wifi_speed_data.csv"

def check_wifi_speed():
    st = speedtest.Speedtest()
    download_speed = st.download() / 1024 / 1024  # Convert to Mbps
    upload_speed = st.upload() / 1024 / 1024  # Convert to Mbps

    return download_speed, upload_speed

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

