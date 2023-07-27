import fastf1 as ff1
from fastf1 import plotting
from fastf1 import utils

from matplotlib import pyplot as plt
from matplotlib.pyplot import figure

import numpy as np
import pandas as pd
ff1.Cache.enable_cache

# Setup plotting

plotting.setup_mpl()

year, grand_prix, session = 2022, 'Belgium', 'R'

race = ff1.get_session(year, grand_prix, session)
race.load() # This is new with Fastf1 v.2.2

# This is how it used to be:

# laps = quali.load(with_telemetry=True)
#driver_1, driver_2 = 'HAM', 'RUS' #Removed for new exploration

# Laps can now be accessed through the .laps object coming from the session

fastestLapOverall = race.laps.pick_fastest()
#laps_driver_2 = race.laps.pick_driver(driver_2)

# Select the fastest lap
#fastest_driver_1 = laps_driver_1.pick_fastest()
#fastest_driver_2 = laps_driver_2.pick_fastest()

# Retrieve the telemetry and add the distance column

telemetry_fastestLapOverall = fastestLapOverall.get_telemetry().add_distance()
#telemetry_driver_2 = fastest_driver_2.get_telemetry().add_distance()

# Make sure whe know the team name for coloring

#team_driver_1 = fastest_driver_1['Team']
#team_driver_2 = fastest_driver_2['Team']

#Set Colors

driver_1_color = 'cyan'
#driver_2_color = 'orange'

# Extract the delta time
#delta_time, ref_tel, compare_tel = utils.delta_time(telemetry_fastestLapOverall)

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



# Speed trace

ax1.plot(telemetry_fastestLapOverall['Distance'], telemetry_fastestLapOverall['Speed'])
#ax1.plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label=driver_2,
#color=driver_2_color)
ax1.set(ylabel='Speed')
ax1.legend(loc="lower right")

# Store figure
#plt.savefig(plot_filename, dpi=300)
plt.show()