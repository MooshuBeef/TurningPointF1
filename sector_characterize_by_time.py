import fastf1 as ff1
import fastf1.plotting as plotting
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

plotting.setup_mpl()

year, grand_prix, session = 2022, 'Belgian', 'R'

race = ff1.get_session(year, grand_prix, session)
race.load()

# Select the fastest lap
fastest_lap = race.laps.pick_fastest()

# Retrieve the telemetry and add the distance column
telemetry_fastest_lap = fastest_lap.get_telemetry().add_distance()

# Create bins for speed
speed_bins = np.arange(0, 375, 25)

# Bin the data by speed
speed_binned = pd.cut(telemetry_fastest_lap['Speed'], bins=speed_bins)

# Calculate the mean distance for each speed bin
mean_distance = telemetry_fastest_lap.groupby(speed_binned)['Time'].mean()

# Calculate the left edges of each bin manually
bin_left_edges = [interval.left for interval in mean_distance.index.to_numpy()]

# Calculate the maximum distance of the lap
max_distance = telemetry_fastest_lap['Distance'].max()

# create the figure
plt.figure(figsize=(10, 6))

# Plot the bar graph with white borders
plt.bar(bin_left_edges, mean_distance.values, width=25, align='center', edgecolor='white')

# Add labels and titles
plt.xlabel('Speed (km/h)')
plt.ylabel('Distance Traveled')
plt.title(f"{race.event['EventName']} {race.event.year}\nDistance Traveled vs Speed - Fastest Lap by {fastest_lap['Driver']} (Max Distance: {max_distance:.2f} m)")
plt.xticks(bin_left_edges, rotation=45)
plt.grid(axis='y')

# Show the plot
plt.show()
