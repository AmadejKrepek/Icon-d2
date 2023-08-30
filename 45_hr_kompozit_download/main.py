import os
import requests
import time
from datetime import datetime

def create_folder():
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour

    folder_path = f"data/{year}/{month:02d}/{day:02d}"
    os.makedirs(folder_path, exist_ok=True)
    
    return folder_path

def download_image(url, folder_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        image_data = response.content
        now = datetime.now()
        timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"meteo_hr_radar_stat_kompozit_{timestamp}.png"  # Save as PNG
        image_path = os.path.join(folder_path, filename)
        
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        print(f"Downloaded image and saved to: {image_path}")
        return image_path
    else:
        print(f"Failed to download image from URL: {url}")
        return None

def create_log_entry(log_path, image_path):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_path, "a") as f:
        f.write(f"{timestamp}: Image saved to {image_path}\n")

if __name__ == "__main__":
    image_url = "https://vrijeme.hr/kompozit-stat.png"  # Replace with the actual image URL
    interval_seconds = 300  # 5 minutes
    log_folder = "logs"
    
    while True:
        folder_path = create_folder()
        image_path = download_image(image_url, folder_path)
        
        if image_path:
            now = datetime.now()
            log_year_folder = os.path.join(log_folder, str(now.year))
            log_month_folder = os.path.join(log_year_folder, now.strftime("%m"))
            log_day_folder = os.path.join(log_month_folder, now.strftime("%d"))
            os.makedirs(log_day_folder, exist_ok=True)
            
            log_filename = now.strftime("%Y_%m_%d") + "_download_log.txt"
            log_path = os.path.join(log_day_folder, log_filename)
            
            if not os.path.exists(log_path):
                with open(log_path, "w") as f:
                    f.write("Log file created.\n")
            
            create_log_entry(log_path, image_path)
        
        time.sleep(interval_seconds)
