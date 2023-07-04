import fastf1 as f
import fastf1.plotting as p
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import csv

p.setup_mpl(misc_mpl_mods=False)

#What Race and Driver are we looking at?
driver = 'ALO'
year, grand_prix, session = 2023,'MONACO', 'R'
#set a threshold of fast laps for cleanliness
fastLapThreshold = 2

# Load the race session and create the plot
race = f.get_session(year, grand_prix, session)
race.load()
#fig, ax = plt.subplots(figsize=(8, 8))

# Get all the laps for a single driver
# Filter out slow laps (yellow flag, VSC, pitstops etc.) as they distort the graph axis
driver_laps = race.laps.pick_driver(driver).pick_quicklaps(fastLapThreshold).reset_index()

all_driver_laps = race.laps

# Seaborn doesn't have proper timedelta support
# So we have to convert timedelta to float (in seconds)
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
# Calculate the running avg lap time, up to 100 laps (covers all grand prixs)
driver_laps["RunningAvgDriver"] = driver_laps["LapTime(s)"].rolling(window=100, min_periods=1).mean()


#Let's see what the file looks like
#print(driver_laps)
"""
OK Let's actually try to write the lap
"""
with open('DriverData.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the data
#   writer.writerow(driver_laps)
    pd.DataFrame(driver_laps).to_csv('DriverData.csv')

""" Commenting out for now
#OK cool the above works, let's write data for all drivers
with open('allDrivers.csv', 'w', encoding='UTF8', newline='') as f:
    AllDriversWriter = csv.writer(f)
    # write the data
    pd.DataFrame(driver_laps).to_csv('allDrivers.csv')
"""

#Let's get Driver, Stint, Compound, and Lap Number
all_drivers_short_data = all_driver_laps[['Driver', 'Stint', 'Compound', 'LapNumber']].groupby(
    ['Driver', 'Stint', 'Compound']
).count().reset_index()
#print('short data', all_drivers_short_data)

#Let's write the driver stints to a csv
with open('allDriversShortData.csv', 'w', encoding='UTF8', newline='') as f:
    AllDriversWriter = csv.writer(f)
    # write the dataw
    pd.DataFrame(all_drivers_short_data).to_csv('allDriversStints.csv')

#Let's get all data
all_driver_stints = all_driver_laps.count().reset_index()
#    ['Driver', 'Stint', 'Compound']
# ).count().reset_index()
#print('all driver stints', all_driver_stints)

#Let's write the driver stints to a csv
with open('allDriversStints2.csv', 'w', encoding='UTF8', newline='') as f:
    AllDriversWriter_All = csv.writer(f)
    # write the data
    pd.DataFrame(all_driver_stints).to_csv('allDriversStints2.csv')


"""Clean up the timing data and pick the headers
"""
all_driver_stints_cleaned = all_driver_laps[['Driver', 'LapTime', 'LapNumber', 'Stint', 'Compound', 'TyreLife', 'LapNumber','Sector1Time','Sector2Time','Sector3Time']]#.groupby(
#    ['Driver', 'Stint', 'Compound']
#).count().reset_index()
#all_driver_stints_cleaned["LapTime(s)"] = all_driver_laps["LapTime"].datetime()
#all_driver_stints_cleaned["LapTime(s)"] = all_driver_stints_cleaned["LapTime"].datetime()
all_driver_stints_cleaned["LapTime(s)"] = all_driver_stints_cleaned["LapTime"].dt.total_seconds()
all_driver_stints_cleaned["Sector1Time(s)"] = all_driver_stints_cleaned["Sector1Time"].dt.total_seconds()
all_driver_stints_cleaned["Sector2Time(s)"] = all_driver_stints_cleaned["Sector2Time"].dt.total_seconds()
all_driver_stints_cleaned["Sector3Time(s)"] = all_driver_stints_cleaned["Sector3Time"].dt.total_seconds()
#all_driver_stints_cleaned['RunningAverageLap'] = all_driver_stints_cleaned['LapTime(s)'].rolling(window=52, min_periods=1).mean()

#Above only works for when there's just 1 driver?
all_driver_stints_cleaned['RollingAverageLap'] = all_driver_stints_cleaned.groupby('Driver')['LapTime(s)'].rolling(window=100, min_periods=1).mean().reset_index(0, drop=True)



#print('all driver stints', all_driver_stints_cleaned)

#Let's write the driver stints to a csv
with open('allDriversStintsCleaned.csv', 'w', encoding='UTF8', newline='') as f:
    allDriversWriter_All_cleaned = csv.writer(f)
    # write the data
    pd.DataFrame(all_driver_stints_cleaned).to_csv('allDriversStintsCleaned.csv')



###############################################################################
# LET'S MAKE A GRAPH
###############################################################################
#ENABLE THIS FOR HORIZONTAL
fig, axes = plt.subplots(1,2 , figsize=(16, 8), sharey=True)

#THIS IS FOR VERTICAL
#fig, axes = plt.subplots(2,1 , figsize=(8, 12), sharex=True)


fig.suptitle(f"{driver} at {race.event.year} {race.event.EventName} - {race.name}"
#"\n"
#"\n"
#r"Lap Time Vs Rolling Average Lap Time"
)

# Lap Time
sns.scatterplot(ax=axes[0], data=driver_laps,
                x="LapNumber",
                y="LapTime(s)",
                #ax=ax,
                hue="Compound",
                palette=p.COMPOUND_COLORS,
                s=100,
                linewidth=0,
                legend='auto')
axes[0].set_title("Lap Times")

# Running Average Lap Time
sns.scatterplot(ax=axes[1], data=driver_laps,
                x="LapNumber",
                y="RunningAvgDriver",
                #ax=ax,
                hue="Compound",
                palette=p.COMPOUND_COLORS,
                s=80,
                linewidth=0,
                legend='auto')
axes[1].set_title("Rolling Avg Times")

#Add the grid lines and despine
axes[0].grid()
axes[1].grid()
sns.despine(left=True, bottom=True)

plt.tight_layout()
plt.show()
