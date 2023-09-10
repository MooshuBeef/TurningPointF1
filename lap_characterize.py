import fastf1 as ff1
import fastf1.plotting as plotting
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

plotting.setup_mpl()

year, grand_prix, session = 2022, 'Netherlands', 'R'

race = ff1.get_session(year, grand_prix, session)
race.load()

# Select the fastest lap
fastest_lap = race.laps.pick_fastest()

# Retrieve the telemetry and add the distance column
telemetry_fastest_lap = fastest_lap.get_telemetry().add_differential_distance()

# Create bins for speed
speed_bins = np.arange(0, 375, 25)

# Bin the data by speed
speed_binned = pd.cut(telemetry_fastest_lap['Speed'], bins=speed_bins)

# Calculate the cumulative distance for each speed bin
cumulative_distance = telemetry_fastest_lap.groupby(speed_binned)['DifferentialDistance'].sum()

# Calculate the total distance traveled
total_distance = cumulative_distance.sum()

# Calculate the percentage for each cumulative bar
percentages = (cumulative_distance / total_distance) * 100

# Calculate the left edges of each bin manually
bin_left_edges = [interval.left for interval in cumulative_distance.index.to_numpy()]

# Calculate the maximum distance of the lap
max_distance = telemetry_fastest_lap['Distance'].max()

# Create the figure
plt.figure(figsize=(10, 6))

# Calculate the center of each bin
bin_centers = bin_left_edges + (speed_bins[1] - speed_bins[0]) / 2

# Plot the bar graph with dark blue color and white borders
bars = plt.bar(bin_centers, cumulative_distance.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')

# Add labels and titles
plt.xlabel('Speed (km/h)')
plt.ylabel('Cumulative Distance Traveled (m)')
plt.title(f"{race.event['EventName']} {race.event.year} - Cumulative Distance Traveled vs Speed\nFastest Lap by {fastest_lap['Driver']} (Approx Track Length: {max_distance:.0f} m)", fontsize=12)

# Adjust the x-axis ticks and labels
plt.xticks(speed_bins, rotation=45)


# find the max y axis value
max_y_value = max(cumulative_distance.values)  # Adding a buffer of 100 for the percentage labels

# Add labels to the bars with bold font
for x, y, percentage in zip(bin_centers, cumulative_distance.values, percentages):
    plt.text(x, y, f'{y:.0f}m', ha='center', va='bottom', weight='bold',fontsize = 8)
    plt.text(x, y + max_y_value/25, f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize = 8)

# Show the plot with a grid
#plt.grid(axis='y',linestyle='--')
plt.show()
