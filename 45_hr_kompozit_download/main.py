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
    response = requests.get(url)
    if response.status_code == 200:
        image_data = response.content
        now = datetime.now()
        timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"meteo_hr_radar_stat_kompozit_{timestamp}.jpg"  # You can adjust the file extension as needed
        image_path = os.path.join(folder_path, filename)
        
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        print(f"Downloaded image and saved to: {image_path}")
    else:
        print(f"Failed to download image from URL: {url}")

if __name__ == "__main__":
    image_url = "https://vrijeme.hr/kompozit-stat.png"  # Replace with the actual image URL
    interval_seconds = 300  # 5 minutes
    
    while True:
        folder_path = create_folder()
        download_image(image_url, folder_path)
        
        time.sleep(interval_seconds)
