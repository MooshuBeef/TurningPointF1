import fastf1
import fastf1.plotting
import seaborn as sns
from matplotlib import pyplot as plt

# enabling misc_mpl_mods will turn on minor grid lines that clutters the plot
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)

# Load the race session
race = fastf1.get_session(2023, 'Singapore', 'R')
#race = fastf1.get_session(2023, 9, 'R')
race.load()
#How many people are we evaluating?
number_of_drivers = 5

# Typically it's 1.07, but for messy races like Monaco 2023, 2.0 is needed
fastLapThreshold = 1.07

fastlaps = race.laps.pick_quicklaps(fastLapThreshold)
upperTime = fastlaps['LapTime'].max()
upperTime=upperTime.total_seconds()

lowerTime = fastlaps['LapTime'].min()
lowerTime = lowerTime.total_seconds()

# Get all the laps for the point finishers only.
point_finishers = race.drivers[:number_of_drivers]
driver_laps = race.laps.pick_drivers(point_finishers)
driver_laps = driver_laps.reset_index()


# To plot the drivers by finishing order,
# we need to get their three-letter abbreviations in the finishing order.
finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]

# We need to modify the DRIVER_COLORS palette.
driver_colors = {abv: fastf1.plotting.DRIVER_COLORS[driver] for abv,
                 driver in fastf1.plotting.DRIVER_TRANSLATE.items()}

# Convert timedelta to float (in seconds)
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

# Set the maximum Y-axis value for the top subplot
#max_y_value = 90  # Replace with your desired maximum Y value
#min_y_value = 85   # Replace with your desired minimum Y value

max_y_value = upperTime + 0.1
min_y_value = lowerTime - 0.1



# Set a threshold value for filtering outliers
#max_lap_time = 107  # Adjust this threshold as needed
max_lap_time = max_y_value

# Create a new figure and axes with subplots
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(14, 10), gridspec_kw={'height_ratios': [5, 1]}, sharex=True)

# Iterate through each driver to plot their continuous lap time line
for driver in finishing_order:
    driver_data = driver_laps[driver_laps["Driver"] == driver]
    lap_times = driver_data["LapTime(s)"].values
    x_values = range(len(lap_times))

    # Filter out lap times that exceed the threshold
    filtered_lap_times = [lt if lt <= max_lap_time else None for lt in lap_times]

    # Plot the continuous line for the driver's lap times in the top subplot
    ax1.plot(x_values, filtered_lap_times, label=driver, color=driver_colors[driver], marker='o', markersize=5)

# Set the labels and title for the top subplot
ax1.set_ylabel("Lap Time (s)")
ax1.set_title(f"{race.event['EventName']} {race.event.year} Race - Lap Times \n (Lower = Faster)")


# Add a legend for the top subplot
ax1.legend()


ax1.set_ylim(min_y_value, max_y_value)  # Adjust the range as needed

# Set the labels and title for the bottom subplot
ax2.set_xlabel("Lap Number")
ax2.set_ylabel("Tire Compound")

# Remove spines for both subplots
#sns.despine(left=True, bottom=True, ax=ax1)
sns.despine(left=True, bottom=True, ax=ax2)

# Add a grid for the top subplot
ax1.grid(axis='y', linestyle='--')
#ax1.invert_yaxis()

# Plot the dots with tire color in the bottom subplot
for driver in finishing_order:
    driver_data = driver_laps[driver_laps["Driver"] == driver]
    x_values = range(len(driver_data))
    compound_colors = [fastf1.plotting.COMPOUND_COLORS[compound] for compound in driver_data["Compound"]]
    #ax2.plot(x_values, [finishing_order.index(driver)] * len(x_values), label=driver, color=driver_colors[driver])
    ax2.scatter(x_values, [finishing_order.index(driver)] * len(x_values), label=None, c=compound_colors, cmap='viridis', s=40)



# Set Y ticks for the bottom subplot based on finishing order
ax2.set_yticks(range(len(finishing_order)))
ax2.set_yticklabels(finishing_order)
ax2.invert_yaxis()

# Tight layout for both subplots
plt.tight_layout()

# Show the plot
plt.show()
