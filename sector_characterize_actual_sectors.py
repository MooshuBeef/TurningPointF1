import fastf1 as ff1
import fastf1.plotting as plotting
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

# Create the figure with three vertically stacked subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 18), sharex=True)

# Calculate the center of each bin
bin_centers = bin_left_edges + (speed_bins[1] - speed_bins[0]) / 2

# Plot the bar graph with dark blue color and white borders on each subplot
bars1 = ax1.bar(bin_centers, cumulative_distance.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
bars2 = ax2.bar(bin_centers, cumulative_distance.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
bars3 = ax3.bar(bin_centers, cumulative_distance.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')

# Add labels and titles for each subplot
ax1.set(ylabel='Cumulative Distance Traveled (m)')
ax2.set(ylabel='Cumulative Distance Traveled (m)')
ax3.set(xlabel='Speed (km/h)', ylabel='Cumulative Distance Traveled (m)')

ax1.set_title(f"{race.event['EventName']} {race.event.year} - Cumulative Distance Traveled vs Speed\nSector 1 - Fastest Lap by {fastest_lap['Driver']} (Approx Track Length: {max_distance:.0f} m)", fontsize=12)
ax2.set_title(f"Sector 2")
ax3.set_title(f"Sector 3")

# Adjust the x-axis ticks and labels
ax3.set_xticks(speed_bins)
ax3.set_xticklabels(speed_bins, rotation=45)

# Add labels to the bars with bold font in each subplot
for ax, y, percentage in zip([ax1, ax2, ax3], cumulative_distance.values, percentages):
    for x, label in zip(bin_centers, [f'{y:.0f}m', f'{percentage:.1f}%']):
        ax.text(x, y, label, ha='center', va='bottom', weight='bold', fontsize=8)

# Show the plot with a grid for each subplot
ax1.grid(axis='y', linestyle='--')
ax2.grid(axis='y', linestyle='--')
ax3.grid(axis='y', linestyle='--')

# Adjust spacing between subplots
plt.tight_layout()

# Show the plot
plt.show()
