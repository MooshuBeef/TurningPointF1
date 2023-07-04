import fastf1 as ff1
from fastf1 import plotting
from fastf1 import utils

from matplotlib import pyplot as plt
from matplotlib.pyplot import figure

import numpy as np
import pandas as pd
ff1.Cache.enable_cache('~/Documents/Formula1_python/venv/cache') # replace with your cache directory

# Setup plotting

plotting.setup_mpl()

year, grand_prix, session = 2023, 'AUSTRALIA', 'Q'

quali = ff1.get_session(year, grand_prix, session)
quali.load() # This is new with Fastf1 v.2.2

# This is how it used to be:

# laps = quali.load(with_telemetry=True)

driver_1, driver_2 = 'HAM', 'RUS'

# Laps can now be accessed through the .laps object coming from the session

laps_driver_1 = quali.laps.pick_driver(driver_1)
laps_driver_2 = quali.laps.pick_driver(driver_2)

# Select the fastest lap

fastest_driver_1 = laps_driver_1.pick_fastest()
fastest_driver_2 = laps_driver_2.pick_fastest()

# Retrieve the telemetry and add the distance column

telemetry_driver_1 = fastest_driver_1.get_telemetry().add_distance()
telemetry_driver_2 = fastest_driver_2.get_telemetry().add_distance()

# Make sure whe know the team name for coloring

team_driver_1 = fastest_driver_1['Team']
team_driver_2 = fastest_driver_2['Team']

#Set Colors

driver_1_color = 'cyan'
driver_2_color = 'orange'

# Extract the delta time

delta_time, ref_tel, compare_tel = utils.delta_time(fastest_driver_1, fastest_driver_2)

plot_size = [15, 15]
plot_title = f"{quali.event.year} {quali.event.EventName} - {quali.name} - {driver_1} VS {driver_2}"
plot_ratios = [1, 3, 2, 1, 1, 2, 1]
plot_filename = plot_title.replace(" ", "") + ".png"

# Make plot a bit bigger

plt.rcParams['figure.figsize'] = plot_size

# Create subplots with different sizes

fig, ax = plt.subplots(7, gridspec_kw={'height_ratios': plot_ratios})

# Set the plot title

ax[0].title.set_text(plot_title)

# Delta line

ax[0].plot(ref_tel['Distance'], delta_time, color=driver_1_color)
ax[0].axhline(0, color=driver_2_color)
ax[0].set(ylabel=f"Gap to {driver_2} (s)")

# Speed trace

ax[1].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Speed'], label=driver_1,
color=driver_1_color)
ax[1].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label=driver_2,
color=driver_2_color)
ax[1].set(ylabel='Speed')
ax[1].legend(loc="lower right")

# Throttle trace

ax[2].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Throttle'], label=driver_1,
color=driver_1_color)
ax[2].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Throttle'], label=driver_2,
color=driver_2_color)
ax[2].set(ylabel='Throttle')

# Brake trace

ax[3].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Brake'], label=driver_1,
color=driver_1_color)
ax[3].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Brake'], label=driver_2,
color=driver_2_color)
ax[3].set(ylabel='Brake')

# Gear trace

ax[4].plot(telemetry_driver_1['Distance'], telemetry_driver_1['nGear'], label=driver_1,
color=driver_1_color)
ax[4].plot(telemetry_driver_2['Distance'], telemetry_driver_2['nGear'], label=driver_2,
color=driver_2_color)
ax[4].set(ylabel='Gear')

# RPM trace

ax[5].plot(telemetry_driver_1['Distance'], telemetry_driver_1['RPM'], label=driver_1,
color=driver_1_color)
ax[5].plot(telemetry_driver_2['Distance'], telemetry_driver_2['RPM'], label=driver_2,
color=driver_2_color)
ax[5].set(ylabel='RPM')

# DRS trace

ax[6].plot(telemetry_driver_1['Distance'], telemetry_driver_1['DRS'], label=driver_1,
color=driver_1_color)
ax[6].plot(telemetry_driver_2['Distance'], telemetry_driver_2['DRS'], label=driver_2,
color=driver_2_color)
ax[6].set(ylabel='DRS')
ax[6].set(xlabel='Lap distance (meters)')

# Hide x labels and tick labels for top plots and y ticks for right plots.

for a in ax.flat:
    a.label_outer()

# Store figure

plt.savefig(plot_filename, dpi=300)
plt.show()