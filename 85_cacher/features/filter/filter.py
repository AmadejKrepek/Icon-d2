from datetime import datetime


def filterSpecificDate(df, date_choice, predefined_dates):
    try:
        date_choice = int(date_choice)
        if 1 <= date_choice <= len(predefined_dates):
            selected_date = predefined_dates[date_choice - 1]
            # Convert selected_date to a datetime object
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d")

            # Extract year, month, and day from the selected date
            year = selected_date.year
            month = selected_date.month
            day = selected_date.day

            # Filter the data for the same year, month, and day and perform aggregation
            df_filtered = df[
                (df['Datetime'].dt.year == year) &
                (df['Datetime'].dt.month == month) &
                (df['Datetime'].dt.day == day)
                ]

            # Perform aggregation here using df_filtered
            return df_filtered, selected_date
        else:
            print("Invalid date number. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")