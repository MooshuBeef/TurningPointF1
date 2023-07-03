"""Driver Laptimes Distribution Visualization
=============================================
Visualizae different drivers' laptime distributions.
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

race = fastf1.get_session(2023, "Austria", 'R')
race.load()

# set a threshold of fast laps for cleanliness
# Typically it's 1.1, but for messy races like Monaco 2023, 2.0 is needed
fastLapThreshold = 1.1

# Set percentile value
percentile_value = 0.95

###############################################################################
# Get all the laps for the point finishers only.
# Filter out slow laps (yellow flag, VSC, pitstops etc.)
# as they distort the graph axis.

# This spits out a 1 column array with the point finishers
point_finishers = race.drivers[:20]
# print(point_finishers)
driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps(fastLapThreshold).reset_index()
# driver_laps = driver_laps.reset_index()

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

# So actually let's get the lap times in seconds which we can do calculations with
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
driver_laps["Sector1(s)"] = driver_laps["Sector1Time"].dt.total_seconds()
driver_laps["Sector2(s)"] = driver_laps["Sector2Time"].dt.total_seconds()
driver_laps["Sector3(s)"] = driver_laps["Sector3Time"].dt.total_seconds()

# Let's calculate the 90th percentile
#Sector1_percentile = np.percentile(driver_laps["Sector1(s)"], 90)

#print("point finishers: ", point_finishers)


# Group the DataFrame by driver and calculate the 90th percentile lap time
percentile_lap_times = driver_laps.groupby('Driver')['LapTime(s)'].mean()
percentile_sector_1 = driver_laps.groupby('Driver')['Sector1(s)'].mean()
percentile_sector_2 = driver_laps.groupby('Driver')['Sector2(s)'].mean()
percentile_sector_3 = driver_laps.groupby('Driver')['Sector3(s)'].mean()

### Not sorting the below yet
# Sort the average lap times in ascending order
# sorted_percentile_lap_times = percentile_lap_times.sort_values()

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
final_data_sorted = final_data.sort_values(by='diff to median')

final_data_sorted['Sector1_DTM(s)'] = final_data_sorted['Sector1Time(s)'] - median_sector_1
final_data_sorted['Sector2_DTM(s)'] = final_data_sorted['Sector2Time(s)'] - median_sector_2
final_data_sorted['Sector3_DTM(s)'] = final_data_sorted['Sector3Time(s)'] - median_sector_3


# create the figure
#fig, ax = plt.subplots(figsize=(20, 5))


plot_size = [15,15]
plot_ratios = [1, 1, 1, 1]
fig, ax = plt.subplots(4, gridspec_kw={'height_ratios': plot_ratios})
ax[0].bar(final_data_sorted['DRIVERS'], final_data_sorted['diff to median'],
         edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax[0].set_yticklabels(final_data_sorted['diff to median'])
ax[0].yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
# show fastest at the top
ax[0].invert_yaxis()

ax[1].bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector1_DTM(s)'],
         edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax[1].set_yticklabels(final_data_sorted['Sector1_DTM(s)'])
ax[1].yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax[1].invert_yaxis()

ax[2].bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector2_DTM(s)'],
         edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax[2].set_yticklabels(final_data_sorted['Sector2_DTM(s)'])
ax[2].yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax[2].invert_yaxis()


ax[3].bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector3_DTM(s)'],
         edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax[3].set_yticklabels(final_data_sorted['Sector3_DTM(s)'])
ax[3].yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax[3].invert_yaxis()
# draw vertical lines behind the bars
#ax.set_axisbelow(True)
#ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
# sphinx_gallery_defer_figures


##############################################################################
# Finally, give the plot a meaningful title
"""
lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

plt.suptitle(f"{session.event['EventName']} {session.event.year} Qualifying\n"
             f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")
"""
plt.show()
"""
"""



# VALIDATION STEP: Print the Xth percentile lap time for each driver
#for driver, percentile_lap_times in percentile_lap_times.items():
#    print(f"{percentile_value * 100:.0f}th percentile lap time for {driver}: {percentile_lap_times:.3f}")

#final_data = percentile_lap_times.values
#print(final_data)
#######################
# NEXT STEP: Subtract the median lap time from each row.
#######################

# METHOD 1: Convert the 1D series into a 2D array, then subtract the median of 90th percentile times
# from the other 90th percentile times

# Converting the series to an array
# array_sorted_percentile_lap_times = sorted_percentile_lap_times.["LapTime(s)"].to_numpy()
#label_drivers = percentile_lap_times[:, 0]
#array_sorted_percentile_lap_times = np.array(percentile_lap_times.values, ndmin=2)
#print(array_sorted_percentile_lap_times)