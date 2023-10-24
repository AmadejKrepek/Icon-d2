import csv
import requests
import xml.etree.ElementTree as ET

# URLs to the XML files for two stations
url1 = "https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observationAms_si_latest.xml"
url2 = "https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observation_si_latest.xml"

# Function to extract temperature data from XML
def extract_temperature_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        metData_list = root.findall(".//metData")
        temperature_data = []
        for metData in metData_list:
            domain_title = metData.find("domain_title").text
            temperature = metData.find("t").text
            valid_utc = metData.find("valid_UTC").text
            domain_lat = metData.find("domain_lat").text
            domain_lon = metData.find("domain_lon").text
            domain_altitude = metData.find("domain_altitude").text
            temperature_data.append([domain_title, temperature, valid_utc, domain_lat, domain_lon, domain_altitude])
        return temperature_data
    else:
        print(f"Failed to fetch XML data from the URL: {url}. Status code: {response.status_code}")
        return []

# Extract temperature data for both stations
temperature_data1 = extract_temperature_data(url1)
temperature_data2 = extract_temperature_data(url2)

# Write data to a CSV file
with open("temperature_data.csv", "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)

    # Create a header row in the CSV file
    header = ["Station", "Temperature", "Valid_UTC", "Latitude", "Longitude", "Altitude"]
    csvwriter.writerow(header)

    # Write data for station 1
    for data in temperature_data1:
        csvwriter.writerow([f"Auto_{data[0]}", data[1], data[2], data[3], data[4], data[5]])

    # Write data for station 2
    for data in temperature_data2:
        csvwriter.writerow([f"Obs_{data[0]}", data[1], data[2], data[3], data[4], data[5]])

print("Temperature data for both stations with valid UTC, latitude, longitude, and altitude has been successfully written to temperature_data.csv")
