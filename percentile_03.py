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

race = fastf1.get_session(2023, "Spain", 'R')
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
# print(finishing_order)

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

# Let's calculate the 90th percentile
#Sector1_percentile = np.percentile(driver_laps["Sector1(s)"], 90)

print("point finishers: ", point_finishers)


# Group the DataFrame by driver and calculate the 90th percentile lap time
percentile_lap_times = driver_laps.groupby('Driver')['LapTime(s)'].quantile(percentile_value)


### Not sorting the below yet
# Sort the average lap times in ascending order
# sorted_percentile_lap_times = percentile_lap_times.sort_values()

# Find Median time from the 90th percentile
#percentile_lap_times_int = percentile_lap_times.astype(int)
median_lap_time = percentile_lap_times.median()
print(f"Median time is {median_lap_time}")

#array = percentile_lap_times.to_frame().values
series_with_index = percentile_lap_times.reset_index()
array = series_with_index.values

# Create a DataFrame from the array
final_data = pd.DataFrame(array)

# Set the column names
final_data.columns = ["DRIVERS", "LAP TIME"]

final_data['diff to median'] = final_data['LAP TIME'] - median_lap_time


#fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']


print(final_data)
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