import fastf1
import fastf1.plotting
import seaborn as sns
from matplotlib import pyplot as plt

# enabling misc_mpl_mods will turn on minor grid lines that clutters the plot
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)

# Load the race session
race = fastf1.get_session(2023, "Singapore", 'R')
race.load()

# Get all the laps for the point finishers only.
point_finishers = race.drivers[:5]
driver_laps = race.laps.pick_drivers(point_finishers)#.pick_quicklaps()
driver_laps = driver_laps.reset_index()

# To plot the drivers by finishing order,
# we need to get their three-letter abbreviations in the finishing order.
finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]

# We need to modify the DRIVER_COLORS palette.
driver_colors = {abv: fastf1.plotting.DRIVER_COLORS[driver] for abv,
driver in fastf1.plotting.DRIVER_TRANSLATE.items()}

# Convert timedelta to float (in seconds)
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

# Set a threshold value for filtering outliers
max_lap_time = 108  # Adjust this threshold as needed

# Create a new figure and axis
fig, ax = plt.subplots(figsize=(14, 10))

# Iterate through each driver to plot their continuous lap time line
for driver in finishing_order:
    driver_data = driver_laps[driver_laps["Driver"] == driver]
    lap_times = driver_data["LapTime(s)"].values
    x_values = range(len(lap_times))
    #x_values = driver_data["LapNumbers"].values
    #compound_colors = [fastf1.plotting.COMPOUND_COLORS[compound] for compound in driver_data["Compound"]]

    # Filter out lap times that exceed the threshold
    filtered_lap_times = [lt if lt <= max_lap_time else None for lt in lap_times]

    # Plot the continuous line for the driver's lap times
    ax.plot(x_values, filtered_lap_times, label=driver, color=driver_colors[driver], marker='o', markersize=3)

    # Plot the dots with tire color
    #ax.scatter(x_values, lap_times, label=None, c=compound_colors, cmap='viridis', s=30)

    # Plot the dots with tire color
    # ax.scatter(x_values, lap_times, label=None, c=compound_colors, cmap='viridis', s=30)

# Set the labels and title
ax.set_xlabel("Lap Number")
ax.set_ylabel("Lap Time (s)")
plt.suptitle(f"{race.event['EventName']} {race.event.year} Race")

# Add a legend
ax.legend()

# Set the maximum Y-axis value
max_y_value = 100  # Replace with your desired maximum Y value
plt.ylim(0, max_y_value)  # Adjust the range as needed

# Set the maximum Y-axis value
max_y_value = 110  # Replace with your desired maximum Y value
min_y_value = 95  # Replace with your desired maximum Y value
plt.ylim(min_y_value, max_y_value)  # Adjust the range as needed

# Remove spines
sns.despine(left=True, bottom=True)
plt.grid(axis='y', linestyle='--')
plt.tight_layout()
plt.show()
