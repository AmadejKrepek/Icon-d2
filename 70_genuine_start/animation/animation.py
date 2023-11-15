import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation


def create_frames(df, agg_name):
    # Assuming your DataFrame has a 'Timestamp' column
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    # Sort the DataFrame by timestamp
    df = df.sort_values(by='Datetime')

    # Create a figure and axis for the plot
    fig, ax = plt.subplots()

    # Function to update the plot for each animation frame
    def update(frame):
        ax.clear()
        hour_df = df[df['Datetime'].dt.hour == frame]
        # Plot your data here based on 'hour_df'
        # For example, you can scatter plot latitude and longitude:
        ax.scatter(hour_df['Longitude'], hour_df['Latitude'], c=hour_df[agg_name], cmap='viridis')
        ax.set_title(f'Hour {frame}')

    # Set the range of frames (hours in a day)
    frames_range = range(24)

    # Create the animation
    animation = FuncAnimation(fig, update, frames=frames_range, repeat=True)

    # Display the animation
    plt.show()