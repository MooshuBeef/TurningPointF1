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
year, grand_prix, session = 2023,'MIAMI', 'R'

# Load the race session and create the plot
race = f.get_session(year, grand_prix, session)
race.load()
fig, ax = plt.subplots(figsize=(8, 8))

# Get all the laps for a single driver
# Filter out slow laps (yellow flag, VSC, pitstops etc.) as they distort the graph axis
driver_laps = race.laps.pick_driver(driver).pick_quicklaps().reset_index()
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
    pd.DataFrame(driver_laps).to_csv('Data.csv')


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
all_driver_stints_cleaned['RollingAverageLap'] = all_driver_stints_cleaned.groupby('Driver')['LapTime(s)'].rolling(window=52, min_periods=1).mean().reset_index(0, drop=True)

#Let's write the driver stints to a csv
with open('allDriversStintsCleaned.csv', 'w', encoding='UTF8', newline='') as f:
    allDriversWriter_All_cleaned = csv.writer(f)
    # write the data
    pd.DataFrame(all_driver_stints_cleaned).to_csv('allDriversStintsCleaned.csv')
