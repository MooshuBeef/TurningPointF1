import fastf1 as f
import fastf1.plotting as p
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
import csv

p.setup_mpl(misc_mpl_mods=False)

#What Race and Driver are we looking at?
driver = 'VER'
year, grand_prix, session = 2023,'Austrian', 'R'

#set a threshold of fast laps for cleanliness
# Typically it's 1.1, but for messy races like Monaco 2023, 2.0 is needed
fastLapThreshold = 1.5

# Load the race session and create the plot
race = f.get_session(year, grand_prix, session)
race.load()
#fig, ax = plt.subplots(figsize=(8, 8))

# Get all the laps for a single driver
# Filter out slow laps (yellow flag, VSC, pitstops etc.) as they distort the graph axis
driver_laps = race.laps.pick_driver(driver).pick_quicklaps(fastLapThreshold).reset_index()

# Seaborn doesn't have proper timedelta support
# So we have to convert timedelta to float (in seconds)
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

# Calculate the running avg lap time, up to 100 laps (covers all grand prixs)
driver_laps["RunningAvgDriver"] = driver_laps["LapTime(s)"].rolling(window=100, min_periods=1).mean()


###############################################################################
# LET'S MAKE A GRAPH
###############################################################################
#ENABLE THIS FOR HORIZONTAL
fig, axes = plt.subplots(1,2 , figsize=(16, 8), sharey=True)

#THIS IS FOR VERTICAL PLOT STYLE
#fig, axes = plt.subplots(2,1 , figsize=(8, 12), sharex=True)


fig.suptitle(f"{driver} at {race.event.year} {race.event.EventName} - {race.name}"
#I enable the below when I want the sub header
#"\n"
#"\n"
#r"Lap Time Vs Rolling Average Lap Time"
)

# Lap Time goes to plot 1
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

# Rolling Average Lap Time to plot 2
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
