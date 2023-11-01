import csv

# Open the input CSV file for reading
with open('temperature_data.csv', 'r') as input_file:
    # Create a CSV reader
    csvreader = csv.reader(input_file)
    
    # Create a list to store all relevant data
    relevant_data = []
    
    # Initialize a flag to track if the header has been written
    header_written = False
    
    # Iterate through the rows in the CSV file
    for row in csvreader:
        if len(row) < 1:
            continue
        
        station = row[0]
        latitude = row[3]
        longitude = row[4]
        altitude = row[5]
        
        relevant_data.append([station, latitude, longitude, altitude])

# Open a new CSV file for writing
with open('all_stations_data.csv', 'w', newline='') as output_file:
    # Create a CSV writer
    csvwriter = csv.writer(output_file)
    
    for data in relevant_data:
        # Duplicate the header for each station
        if not header_written:
            csvwriter.writerow(["Station", "Latitude", "Longitude", "Altitude"])
            header_written = True
        
        # Write the relevant data to the output file
        csvwriter.writerow(data)
