import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_usage_within_timeframe(start_time_str, end_time_str):
    # Load data from the JSON file
    with open('./Framework/system_info.json') as file:
        data = json.load(file)

    # Extracting timestamps, CPU usage, and RAM usage for plotting
    timestamps = [datetime.strptime(entry['Timestamp'], '%Y-%m-%d %H:%M:%S') for entry in data]
    cpu_usage = [entry['CPU_Usage'] for entry in data]
    ram_usage = [entry['RAM_Usage'] for entry in data]

    # Convert start and end time strings to datetime objects
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

    # Filter data within the specified time frame
    filtered_data = [(ts, cpu, ram) for ts, cpu, ram in zip(timestamps, cpu_usage, ram_usage) if start_time <= ts <= end_time]

    # Unpack the filtered data into separate lists
    timestamps, cpu_usage, ram_usage = zip(*filtered_data)

    # Plot CPU and RAM usage over the specified time frame
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))

    ax1.plot(timestamps, cpu_usage, color='red')
    ax1.set_title('CPU Usage between {} and {}'.format(start_time_str, end_time_str))
    ax1.set_xlabel('Time')
    ax1.set_ylabel('CPU Usage (%)')

    ax2.plot(timestamps, ram_usage, color='blue')
    ax2.set_title('RAM Usage between {} and {}'.format(start_time_str, end_time_str))
    ax2.set_xlabel('Time')
    ax2.set_ylabel('RAM Usage (%)')

    # Format x-axis date labels
    date_format = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax1.xaxis.set_major_formatter(date_format)
    ax1.xaxis.set_tick_params(rotation=45)
    ax2.xaxis.set_major_formatter(date_format)
    ax2.xaxis.set_tick_params(rotation=45)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    start_time = '2023-11-09 15:42:31'  # Replace with your desired start time
    end_time = '2023-11-09 15:47:35'    # Replace with your desired end time
    plot_usage_within_timeframe(start_time, end_time)
