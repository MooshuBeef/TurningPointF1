import fastf1
import fastf1.plotting
import seaborn as sns
from matplotlib import pyplot as plt

# enabling misc_mpl_mods will turn on minor grid lines that clutters the plot
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)

###############################################################################
# Load the race session

race = fastf1.get_session(2023, "Singapore", 'R')
race.load()

###############################################################################
# Get all the laps for the point finishers only.
# Filter out slow laps (yellow flag, VSC, pitstops, etc.)
# as they distort the graph axis.
point_finishers = race.drivers[:19]
print(point_finishers)
driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps()
driver_laps = driver_laps.reset_index()

###############################################################################
# To plot the drivers by finishing order,
# we need to get their three-letter abbreviations in the finishing order.
finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]
print(finishing_order)

###############################################################################
# We need to modify the DRIVER_COLORS palette.
# Its keys are the driver's full names, but we need the keys to be the drivers'
# three-letter abbreviations.
# We can do this with the DRIVER_TRANSLATE mapping.
driver_colors = {abv: fastf1.plotting.DRIVER_COLORS[driver] for abv,
                 driver in fastf1.plotting.DRIVER_TRANSLATE.items()}
print(driver_colors)

###############################################################################
# Create separate dataframes for the top and bottom subplots
driver_laps_top = driver_laps[driver_laps['Driver'].isin(finishing_order[:10])].copy()
driver_laps_bottom = driver_laps[driver_laps['Driver'].isin(finishing_order[10:])].copy()

###############################################################################
# First create the violin plots to show the distributions.
# Then use the swarm plot to show the actual laptimes.

# create the figure with two subplots
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(10, 10), sharex=True)

# Seaborn doesn't have proper timedelta support
# so we have to convert timedelta to float (in seconds)
driver_laps_top["LapTime(s)"] = driver_laps_top["LapTime"].dt.total_seconds()
driver_laps_bottom["LapTime(s)"] = driver_laps_bottom["LapTime"].dt.total_seconds()

# Top subplot for the first 10 drivers
sns.violinplot(data=driver_laps_top,
               x="Driver",
               y="LapTime(s)",
               inner=None,
               scale="area",
               order=finishing_order[:10],
               palette=driver_colors,
               ax=ax1)

sns.swarmplot(data=driver_laps_top,
              x="Driver",
              y="LapTime(s)",
              order=finishing_order[:10],
              hue="Compound",
              palette=fastf1.plotting.COMPOUND_COLORS,
              hue_order=["SOFT", "MEDIUM", "HARD"],
              linewidth=0,
              size=5,
              ax=ax1)

# Bottom subplot for the last 10 drivers
sns.violinplot(data=driver_laps_bottom,
               x="Driver",
               y="LapTime(s)",
               inner=None,
               scale="area",
               order=finishing_order[10:],
               palette=driver_colors,
               ax=ax2)

sns.swarmplot(data=driver_laps_bottom,
              x="Driver",
              y="LapTime(s)",
              order=finishing_order[10:],
              hue="Compound",
              palette=fastf1.plotting.COMPOUND_COLORS,
              hue_order=["SOFT", "MEDIUM", "HARD"],
              linewidth=0,
              size=5,
              ax=ax2)

# Set y-axis limits for the bottom subplot
bottom_ylim_min, bottom_ylim_max = driver_laps_bottom["LapTime(s)"].min() - 5, driver_laps_bottom["LapTime(s)"].max() + 5
ax2.set_ylim(bottom_ylim_min, bottom_ylim_max)

# Set the x-axis labels for both subplots
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha="right")

# Set the common xlabel for both subplots
fig.text(0.5, 0.04, "Driver", ha="center")

ax1.set_ylabel("Lap Time (s)")
ax2.set_ylabel("Lap Time (s)")

plt.suptitle(f"{race.event['EventName']} {race.event.year} Race")
sns.despine(left=True, bottom=True)

plt.tight_layout()
plt.show()
