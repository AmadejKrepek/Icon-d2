import pandas as pd

# Load the CSV file into a DataFrame
input_file = "output_data.csv"
df = pd.read_csv(input_file)

# Remove the "time" column
df_filtered = df.drop(columns=["Time"])

# Save the filtered DataFrame to a new CSV file
output_file = "filtered_output_data_time_series.csv"
df_filtered.to_csv(output_file, index=False)

print(f"Filtered data saved to {output_file}")
