import pandas as pd

# Load the CSV file into a DataFrame
input_file = "output_data.csv"
df = pd.read_csv(input_file)

# Filter out data with time equal to 0
df_filtered = df[df["Time"] == 0]

# Remove the "time" column
df_filtered = df_filtered.drop(columns=["Time"])

# Save the filtered DataFrame to a new CSV file
output_file = "filtered_output_data.csv"
df_filtered.to_csv(output_file, index=False)

print(f"Filtered data saved to {output_file}")
