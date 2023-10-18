import csv
import requests
import xml.etree.ElementTree as ET

# URL to the XML file
url = "https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observationAms_si_latest.xml"

# Send a GET request to fetch the XML data
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the XML content
    root = ET.fromstring(response.text)

    # Open a CSV file for writing
    with open("temperature_data.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)

        # Create a header row in the CSV file
        header = ["domain_title", "t"]

        csvwriter.writerow(header)

        # Find all 'metData' elements and extract the "t" element
        metData_list = root.findall(".//metData")
        for metData in metData_list:
            domain_title = metData.find("domain_title").text
            temperature = metData.find("t").text
            row = [domain_title, temperature]
            csvwriter.writerow(row)

    print("Temperature data has been successfully written to temperature_data.csv")

else:
    print(f"Failed to fetch XML data from the URL. Status code: {response.status_code}")
