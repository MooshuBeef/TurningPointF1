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

###############################################################################
# First create the violin plots to show the distributions.
# Then use the swarm plot to show the actual laptimes.

# create the figure
fig, ax = plt.subplots(figsize=(20, 5))

# Seaborn doesn't have proper timedelta support
# so we have to convert timedelta to float (in seconds)
# driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

# So actually let's get the sector times
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
driver_laps["Sector1(s)"] = driver_laps["Sector1Time"].dt.total_seconds()

# Let's calculate the 90th percentile
Sector1_percentile = np.percentile(driver_laps["Sector1(s)"], 90)

print("point finishers: ", point_finishers)
print(Sector1_percentile)

with open('percentile_01.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the data
    pd.DataFrame(point_finishers).to_csv('percentile_01.csv')

with open('driver_laps.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the data
    pd.DataFrame(driver_laps).to_csv('driver_laps.csv')

# CHAT GPT CODE!
# Assuming the 'driver_laps' DataFrame is already defined and populated

# Group the DataFrame by driver and calculate the average lap time
# average_lap_times = driver_laps.groupby('Driver')['LapTime(s)'].mean()

# Let's do percentile instead
# percentile_lap_times = np.percentile(driver_laps.groupby('Driver')['LapTime(s)'],90)

# Another solution from https://stackoverflow.com/questions/19894939/calculate-arbitrary-percentile-on-pandas-groupby
# point_finishers["lap_percentile"] = driver_laps.groupby(['DriverNumber'])['LapTime(s)'].quantile(0.90)


# Group the DataFrame by driver and calculate the 90th percentile lap time
percentile_lap_times = driver_laps.groupby('Driver')['LapTime(s)'].quantile(percentile_value)
percentile_lap_times_keep = percentile_lap_times

### Not sorting the below yet
# Sort the average lap times in ascending order
# sorted_percentile_lap_times = percentile_lap_times.sort_values()



# VALIDATION STEP: Print the Xth percentile lap time for each driver
for driver, percentile_lap_times in percentile_lap_times.items():
    print(f"{percentile_value * 100:.0f}th percentile lap time for {driver}: {percentile_lap_times:.3f}")

# Print the average lap time for each driver, not sorted
# print(sorted_percentile_lap_times)

# Find Median time:
median_lap_time = percentile_lap_times.median()
print(f"Median time is {median_lap_time}")


# Converting the series to an array
# array_sorted_percentile_lap_times = sorted_percentile_lap_times.["LapTime(s)"].to_numpy()
label_drivers = percentile_lap_times[:, 0]
array_sorted_percentile_lap_times = np.array(percentile_lap_times.values, ndmin=2)

print(array_sorted_percentile_lap_times)
print(array_sorted_percentile_lap_times)

# print(array_sorted_percentile_lap_times)


# Subtract the median from each value and create a new column
# differences_lap = sorted_percentile_lap_times - median_lap_time

# Add the differences column to the existing array
# sorted_percentile_lap_times_update = np.column_stack((sorted_percentile_lap_times, differences_lap))

# Print the updated array
# print(sorted_percentile_lap_times_update)


################
# VERIFY WITH CSV
################
"""
with open('sorted_percentile_lap_times.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the data
    pd.DataFrame(df).to_csv('sorted_percentile_lap_times.csv')
"""
################


# Find difference to mean
# Subtract the median from each value
# lap_time_to_median = [x - median_lap_time for x in sorted_percentile_lap_times]

# Reference
# driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()


# Add a new row
# sorted_percentile_lap_times["LapDiffToMedian(s)"] = [sorted_percentile_lap_times - median_lap_time]
# print(sorted_percentile_lap_times)
# Print the differences
# for difference in lap_time_to_median:
#    print(difference)
"""
for driver, average_lap_time in average_lap_times.items():
    print(f"Average lap time for {driver}: {average_lap_time}")
"""
"""Fix this all later 
        # Sort the average lap times in ascending order
        sorted_percentile_lap_times = percentile_lap_times.sort_values()

        # Print the sorted average lap times
        for driver, percentile_lap_times in sorted_percentile_lap_times.items():
            print(f"Average lap time for {driver}: {percentile_lap_times}")

        with open('percentile_lap_times.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            # write the data
        pd.DataFrame(driver_laps).to_csv('percentile_average_lap_times.csv')
"""
"""Code from other plot
##############################################################################
# Finally, we'll create a list of team colors per lap to color our plot.
team_colors = list()
for index, lap in fastest_laps.iterlaps():
    color = fastf1.plotting.team_color(lap['Team'])
    team_colors.append(color)


##############################################################################
# Now, we can plot all the data
fig, ax = plt.subplots()
ax.bar(fastest_laps.index, fastest_laps['LapTimeDelta'],
        color=team_colors, edgecolor='grey')
ax.set_yticks(fastest_laps.index)
ax.set_yticklabels(fastest_laps['Driver'])

# show fastest at the top
ax.invert_yaxis()

# draw vertical lines behind the bars
ax.set_axisbelow(True)
ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
# sphinx_gallery_defer_figures


##############################################################################
# Finally, give the plot a meaningful title

lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

plt.suptitle(f"{session.event['EventName']} {session.event.year} Qualifying\n"
             f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")

plt.show()
"""
"""
sns.violinplot(data=driver_laps,
               x="Driver",
               y="Sector1(s)",
               inner=None,
               scale="area",
               order=finishing_order,
               palette=driver_colors
               )

sns.swarmplot(data=driver_laps,
              x="Driver",
              y="Sector1(s)",
              order=finishing_order,
              hue="Compound",
              palette=fastf1.plotting.COMPOUND_COLORS,
              hue_order=["SOFT", "MEDIUM", "HARD"],
              linewidth=0,
              size=5,
              )




# sphinx_gallery_defer_figures

###############################################################################
# Make the plot more aesthetic
ax.set_xlabel("Driver")
ax.set_ylabel("Sector1(s)")
plt.suptitle("2023 Azerbaijan Grand Prix Lap Time Distributions")
sns.despine(left=True, bottom=True)

plt.tight_layout()
plt.show()
"""

########################
# ALL GRAPH THINGS BELOW
########################
"""
##############################################################################
# Finally, we'll create a list of team colors per lap to color our plot.
team_colors = list()
for index, lap in driver_laps.iterlaps():
    color = fastf1.plotting.team_color(lap['Team'])
    team_colors.append(color)

##############################################################################
# Now, we can plot all the data
fig, ax = plt.subplots()
#ax.barh(fastest_laps.index, sorted_percentile_lap_times['LapTime(s)'],
ax.bar(sorted_percentile_lap_times.index,sorted_percentile_lap_times, color=team_colors, edgecolor='grey')
#ax.set_yticks(fastest_laps.index)
#ax.set_yticklabels(fastest_laps['Driver'])

# show fastest at the top
#x.invert_yaxis()

# draw vertical lines behind the bars
#ax.set_axisbelow(True)
#ax.xaxis.grid(True, which='major', linestyle='--', color='black', zorder=-1000)
# sphinx_gallery_defer_figures


##############################################################################
# Finally, give the plot a meaningful title

#lap_time_string = strftimedelta(pole_lap['LapTime'], '%m:%s.%ms')

#plt.suptitle(f"{session.event['EventName']} {session.event.year} Qualifying\n"
#             f"Fastest Lap: {lap_time_string} ({pole_lap['Driver']})")

plt.show()
"""