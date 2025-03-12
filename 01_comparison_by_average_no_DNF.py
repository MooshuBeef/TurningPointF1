"""Driver Laptimes Distribution Visualization
=============================================
Visualize different drivers' laptime distributions.
"""

import fastf1
import fastf1.plotting
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import csv
from timple.timedelta import strftimedelta
from fastf1.core import Laps


# enabling misc_mpl_mods will turn on minor grid lines that clutters the plot
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)

###############################################################################
# Load the race session

race = fastf1.get_session(2024, 10, 'R')
race.load()

# set a threshold of fast laps for cleanliness˘
# Typically it's 1.07, but for messy races like Monaco 2023, 2.0 is needed
fastLapThreshold = 1.07

# Set percentile value
percentile_value = 0.95

###############################################################################
# Get all the laps for the point finishers only.
# Filter out slow laps (yellow flag, VSC, pitstops etc.)
# as they distort the graph axis.

#Let's try to identify the number of race finishers
race_results = race.results

# Count how many drivers finished the race successfully
finished_count = len(race_results[race_results['Status'].isin(['Finished', '+1 Lap', '+2 Laps'])])

# Create a variable to store driver names and their statuses for those who didn't finish
did_not_finish = race_results[~race_results['Status'].isin(['Finished', '+1 Lap', '+2 Laps'])][['DriverNumber', 'Abbreviation', 'Status']]

#IN case the did not finish rows needs to be deleted for an error
rows_to_delete = 1
did_not_finish = did_not_finish.iloc[:-rows_to_delete]


# Print the counts and the DataFrame for drivers who didn't finish
print("Number of drivers who finished the race:", finished_count)
print("\nDrivers who didn't finish:")
print(did_not_finish)

# This spits out a 1 column array with the point finishers
#point_finishers = race.drivers[:finished_count]

# This spits out a 1 column array with the point finishers
point_finishers = race.drivers[:finished_count]


#Now we can get the data for all the points finishers
driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps(fastLapThreshold).reset_index()

#Let's get the maximum lap from those who didn't finish
no_finish_laps = race.laps.pick_drivers(did_not_finish['DriverNumber'])
no_finish_last_lap = no_finish_laps.groupby('DriverNumber')['LapNumber'].max()
#print(no_finish_last_lap)

#Create a new variable with the driver, reason for retirement, and last lap completed
did_not_finish = did_not_finish.merge(no_finish_last_lap, left_on='DriverNumber', right_index=True, how='left')
did_not_finish = did_not_finish.rename(columns={'LapNumber': 'LastLap'})
print(did_not_finish)


###############################################################################
# To plot the drivers by finishing order,
# we need to get their three-letter abbreviations in the finishing order.
finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]
print(finishing_order)

###############################################################################
# We need to modify the DRIVER_COLORS palette.
# Its keys are the driver's full names but we need the keys to be the drivers'
# three-letter abbreviations.
# We can do this with the DRIVER_TRANSLATE mapping.
driver_colors = {abv: fastf1.plotting.DRIVER_COLORS[driver] for abv,
driver in fastf1.plotting.DRIVER_TRANSLATE.items()}
# print(driver_colors)

# Get the lap times in seconds which we can do calculations with
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
driver_laps["Sector1(s)"] = driver_laps["Sector1Time"].dt.total_seconds()
driver_laps["Sector2(s)"] = driver_laps["Sector2Time"].dt.total_seconds()
driver_laps["Sector3(s)"] = driver_laps["Sector3Time"].dt.total_seconds()

# Let's calculate the 90th percentile
#Sector1_percentile = np.percentile(driver_laps["Sector1(s)"], 90)


# Group the DataFrame by driver and calculate the 90th percentile lap time
percentile_lap_times = driver_laps.groupby('Driver')['LapTime(s)'].mean()
percentile_sector_1 = driver_laps.groupby('Driver')['Sector1(s)'].mean()
percentile_sector_2 = driver_laps.groupby('Driver')['Sector2(s)'].mean()
percentile_sector_3 = driver_laps.groupby('Driver')['Sector3(s)'].mean()


# Find Median time from the 90th percentile
#percentile_lap_times_int = percentile_lap_times.astype(int)
median_lap_time = percentile_lap_times.median()
median_sector_1 = percentile_sector_1.median()
median_sector_2 = percentile_sector_2.median()
median_sector_3 = percentile_sector_3.median()

print(f"Median time is {median_lap_time}")

#breaking out data from the series into the driver label and times
lap_series = percentile_lap_times.reset_index()
sector1_series = percentile_sector_1
sector2_series = percentile_sector_2
sector3_series = percentile_sector_3
lap_array = lap_series.values
sector1_array = sector1_series.values
sector2_array = sector2_series.values
sector3_array = sector3_series.values

# Create a DataFrame from the array
final_data = pd.DataFrame(lap_array)
#print(sector1_series)
# Set the column names
final_data.columns = ["DRIVERS", "LAP TIME"]
final_data['Sector1Time(s)'] = sector1_array
final_data['Sector2Time(s)'] = sector2_array
final_data['Sector3Time(s)'] = sector3_array




final_data['diff to median'] = final_data['LAP TIME'] - median_lap_time
#final_data_sorted = final_data#.sort_values(by='diff to median')

# Convert the "Drivers" column of the final_data DataFrame to a Categorical data type
# with the custom order specified by the finishing_order list
final_data["DRIVERS"] = pd.Categorical(final_data["DRIVERS"], categories=finishing_order, ordered=True)

# Sort the DataFrame based on the custom order of the "Drivers" column
final_data_sorted = final_data.sort_values(by="DRIVERS")

final_data_sorted['Sector1_DTM(s)'] = final_data_sorted['Sector1Time(s)'] - median_sector_1
final_data_sorted['Sector2_DTM(s)'] = final_data_sorted['Sector2Time(s)'] - median_sector_2
final_data_sorted['Sector3_DTM(s)'] = final_data_sorted['Sector3Time(s)'] - median_sector_3


# create the figure
plt.figure(figsize=(24, 10))

#Plot Titles
plt.suptitle(f"{race.event['EventName']} {race.event.year} Race\n Delta to Overall Average Lap (All Drivers)", y=0.98, fontsize=16)
plot_title = f"By Lap Time"

# Left column
ax1 = plt.subplot(3, 2, (1, 5))

# Right column
ax2 = plt.subplot(3, 2, 2)
ax3 = plt.subplot(3, 2, 4, sharey=ax2)
ax4 = plt.subplot(3, 2, 6, sharey=ax2)
axes = [ax1, ax2, ax3, ax4]

plt.subplots_adjust(hspace=0.5)  # Increase the vertical spacing between subplots
plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.9)


# Assuming 'diff to median' contains NaN values
final_data_sorted['diff to median'].fillna('gray', inplace=True)

ax1.title.set_text(plot_title)
ax1.bar(final_data_sorted['DRIVERS'], final_data_sorted['diff to median'],
        color=final_data_sorted['DRIVERS'].map(driver_colors),
        edgecolor='grey')
#ax.set_yticks(fastest_laps.index)
ax1.set_yticklabels(final_data_sorted['diff to median'])
ax1.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax1.set_ylabel('Delta (s)')
# show fastest at the top
ax1.invert_yaxis()
# remove driver names and tick marks along the bottom of the graph
ax1.set_xticklabels([])
ax1.set_xticks([])

# Calculate y-coordinate for the text box
y_coord = -0.12  # Adjust this value as needed

# Create a text box with a white background to serve as a legend
legend_text = '\n'.join([f"{driver} retired Lap {int(last_lap)} ({status})" for driver, last_lap, status in zip(did_not_finish['Abbreviation'], did_not_finish['LastLap'], did_not_finish['Status'])])
ax1.text(0.02, 0.02*(20-finished_count), legend_text, ha='left', va='top', fontsize=10, fontweight='bold', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round'), transform=ax1.transAxes)
#ax1.text(12.5, -1.0, legend_text, ha='left', va='top', fontsize=10, fontweight='bold', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round'))
#ax1.text(0.5, y_coord, legend_text, ha='center', va='center', fontsize=10, fontweight='bold', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))

# Hide the x-axis labels for ax1
ax1.set_xticks([])

# Adjust the plot layout to make space for the text box
plt.tight_layout()


ax2.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector1_DTM(s)'],
         color=final_data_sorted['DRIVERS'].map(driver_colors), edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax2.title.set_text(f"Sector 1")
ax2.set_yticklabels(final_data_sorted['Sector1_DTM(s)'])
ax2.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax2.set_ylabel('Delta (s)')
ax2.invert_yaxis()
# remove driver names and tick marks along the bottom of the graph
ax2.set_xticklabels([])
ax2.set_xticks([])


ax3.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector2_DTM(s)'],
         color=final_data_sorted['DRIVERS'].map(driver_colors), edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax3.title.set_text(f"Sector 2")
ax3.set_yticklabels(final_data_sorted['Sector2_DTM(s)'])
ax3.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax3.invert_yaxis()
# remove driver names and tick marks along the bottom of the graph
ax3.set_xticklabels([])
ax3.set_xticks([])

ax4.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector3_DTM(s)'],
         color=final_data_sorted['DRIVERS'].map(driver_colors), edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax4.title.set_text(f"Sector 3")
ax4.set_yticklabels(final_data_sorted['Sector3_DTM(s)'])
ax4.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax4.invert_yaxis()
# remove driver names and tick marks along the bottom of the graph
ax4.set_xticklabels([])
ax4.set_xticks([])

###############################################################################
# Set font size of charts

driverFontSize = 9


###############################################################################
# GRAPH 1 X AXIS LABEL FORMATTING
# Modify the ax1.bar() function to color the bars based on the team
bars = ax1.bar(final_data_sorted['DRIVERS'], final_data_sorted['diff to median'],
               color=final_data_sorted['DRIVERS'].map(driver_colors),
               edgecolor='grey')

# Manually adjust the x-axis label positions to be below the bar for negative values
for bar, value, label in zip(bars, final_data_sorted['diff to median'], final_data_sorted['DRIVERS']):
    height = bar.get_height()
    if value < 0:
        # If the value is negative, place the label below the bar
        ax1.text(bar.get_x() + bar.get_width() / 2, height - 0.02, label, ha='center', va='bottom', fontsize=driverFontSize, fontweight='bold')
    else:
        # If the value is non-negative, place the label above the bar
        ax1.text(bar.get_x() + bar.get_width() / 2, -0.05, label, ha='center', va='top', fontsize=driverFontSize, fontweight='bold')


###############################################################################
# SECTOR 1 X AXIS LABEL FORMATTING
# Modify the ax2.bar() function to color the bars based on the team
bars2 = ax2.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector1_DTM(s)'],
               color=final_data_sorted['DRIVERS'].map(driver_colors),
               edgecolor='grey')

# Manually adjust the x-axis label positions to be below the bar for negative values
for bar, value, label in zip(bars2, final_data_sorted['Sector1_DTM(s)'], final_data_sorted['DRIVERS']):
    height = bar.get_height()
    if value < 0:
        # If the value is negative, place the label below the bar
        ax2.text(bar.get_x() + bar.get_width() / 2, height - 0.02, label, ha='center', va='bottom', fontsize=driverFontSize, fontweight='bold')
    else:
        # If the value is non-negative, place the label above the bar
        ax2.text(bar.get_x() + bar.get_width() / 2, -0.07, label, ha='center', va='top', fontsize=driverFontSize, fontweight='bold')

###############################################################################
# SECTOR 2 X AXIS LABEL FORMATTING
# Modify the ax3.bar() function to color the bars based on the team
bars3 = ax3.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector2_DTM(s)'],
               color=final_data_sorted['DRIVERS'].map(driver_colors),
               edgecolor='grey')

# Manually adjust the x-axis label positions to be below the bar for negative values
for bar, value, label in zip(bars3, final_data_sorted['Sector2_DTM(s)'], final_data_sorted['DRIVERS']):
    height = bar.get_height()
    if value < 0:
        # If the value is negative, place the label below the bar
        ax3.text(bar.get_x() + bar.get_width() / 2, height - 0.02, label, ha='center', va='bottom', fontsize=driverFontSize, fontweight='bold')
    else:
        # If the value is non-negative, place the label above the bar
        ax3.text(bar.get_x() + bar.get_width() / 2, -0.07, label, ha='center', va='top', fontsize=driverFontSize, fontweight='bold')

###############################################################################
# SECTOR 3 X AXIS LABEL FORMATTING
# Modify the ax1.bar() function to color the bars based on the team
bars4 = ax4.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector3_DTM(s)'],
               color=final_data_sorted['DRIVERS'].map(driver_colors),
               edgecolor='grey')

# Manually adjust the x-axis label positions to be below the bar for negative values
for bar, value, label in zip(bars4, final_data_sorted['Sector3_DTM(s)'], final_data_sorted['DRIVERS']):
    height = bar.get_height()
    if value < 0:
        # If the value is negative, place the label below the bar
        ax4.text(bar.get_x() + bar.get_width() / 2, height - 0.02, label, ha='center', va='bottom', fontsize=driverFontSize, fontweight='bold')
    else:
        # If the value is non-negative, place the label above the bar
        ax4.text(bar.get_x() + bar.get_width() / 2, -0.07, label, ha='center', va='top', fontsize=driverFontSize, fontweight='bold')



# Add gridlines to all subplots
for ax in [ax1, ax2, ax3, ax4]:
    ax.grid(which='major', axis='y', color='grey', alpha=0.7)
    ax.set_axisbelow(True)  # Ensure gridlines appear below the bars

#set minor gridlines in right column subplots
for ax in [ax2, ax3, ax4]:
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.1))

# Add minor gridlines
for ax in [ax1, ax2, ax3, ax4]:
    ax.grid(which='minor', linestyle='--', color='grey', alpha=0.5)
    ax1.yaxis.set_minor_locator(plt.MultipleLocator(0.1))  # Add minor gridlines between each major

# Set the font size of subplot titles individually
for ax in plt.gcf().get_axes():
    ax.set_title(ax.get_title(), fontsize=12)  # Set the font size (12 points in this example)


plt.tight_layout()  # Adjust the layout to prevent text cutoff

plt.show()
