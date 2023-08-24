import pandas as pd
import os
def aggregate_data(df, agg_column, agg_function):
    if agg_function == 'sum':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].sum()
    elif agg_function == 'max':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].max()
    elif agg_function == 'min':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].min()

def main():
    csv_file = './output/2_metre_temperature/2023/08/24/15z/2_metre_temperature_2023_08_24_15.csv'  # Replace with your CSV file path
    output_folder = '2_metre_temperature_max'  # Replace with your desired output folder

    df = pd.read_csv(csv_file)
    
    # Convert 'ValidDate' column to datetime format
    df['ValidDate'] = pd.to_datetime(df['ValidDate'])

    agg_column = df.columns[2]  # Default to the third column

    print(f"Variable read: {agg_column}")

    print("Available aggregation functions: sum, max, min")
    agg_function = input("Enter aggregation function: ")

    if agg_function not in ['sum', 'max', 'min']:
        print("Invalid aggregation function. Exiting.")
        return

    print("Choose aggregation time frame:")
    print("1. Single day")
    print("2. Interval of days")
    time_frame_choice = input("Enter your choice (1 or 2): ")
    
    if time_frame_choice == '1':
        unique_days = df['ValidDate'].dt.date.unique()
        print("Available days:")
        for idx, day in enumerate(unique_days):
            print(f"{idx+1}. {day}")

        day_choice = int(input("Choose a day (enter the corresponding number): ")) - 1
        selected_day = unique_days[day_choice]

        # Filter data for the selected day
        filtered_data = df[df['ValidDate'].dt.date == selected_day]
        print(filtered_data)

    elif time_frame_choice == '2':
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        filtered_data = df[(df['ValidDate'] >= start_date) & (df['ValidDate'] <= end_date)]
        
    else:
        print("Invalid choice. Exiting.")
        return

    aggregated_data = aggregate_data(filtered_data, agg_column, agg_function).reset_index()
# Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file = f"{output_folder}aggregated_{agg_function}_{agg_column.replace(' ', '_')}.csv"
    aggregated_data.to_csv(output_file, index=False)

    print(f"Aggregated data written to {output_file}")

if __name__ == "__main__":
    main()
