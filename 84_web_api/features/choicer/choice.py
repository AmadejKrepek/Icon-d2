import datetime


def getChosenDate(result, day):
    # Convert start_date string to datetime object
    start_date_str = result["start_date"]
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")

    # Calculate the new date by adding 'day' days to start_date
    date_choice = start_date + datetime.timedelta(days=int(day))

    return date_choice


def getPredefinedDates(start_date, end_date):
    # Convert start_date and end_date strings to datetime objects
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

    # Generate an array of dates incrementing by one day
    predefined_dates = []

    current_date = start_date
    while current_date <= end_date:
        predefined_dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += datetime.timedelta(days=1)

    return predefined_dates
