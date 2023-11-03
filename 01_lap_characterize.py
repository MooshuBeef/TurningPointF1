import fastf1 as ff1
import fastf1.plotting as plotting
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

plotting.setup_mpl()

year, grand_prix, session = 2022, 'Brazil', 'R'
#year, grand_prix, session = 2022, 19, 'R'

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


#What is the fastest lap time?
fastest_lap_time_total = fastest_lap['LapTime']

#Need to get times of Sector 1, Sector 2, and Sector 3
fastest_lap_time_start = fastest_lap['LapStartTime']
fastest_lap_time_Sector1 = fastest_lap['Sector1SessionTime']
fastest_lap_time_Sector2 = fastest_lap['Sector2SessionTime']
fastest_lap_time_Sector3 = fastest_lap['Sector3SessionTime']

""" Checking to make sure times are as expected
print(fastest_lap_time_total)
print(fastest_lap_time_start)
print(fastest_lap_time_Sector1)
print(fastest_lap_time_Sector2)
print(fastest_lap_time_Sector3)
"""

# Let's calculate the sector 1
telemetry_fastest_lap_sector1 = telemetry_fastest_lap.slice_by_time(fastest_lap_time_start, fastest_lap_time_Sector1)
# Bin the data by speed
speed_binned_sector1 = pd.cut(telemetry_fastest_lap['Speed'], bins=speed_bins)
cumulative_distance_sector1 = telemetry_fastest_lap_sector1.groupby(speed_binned)['DifferentialDistance'].sum()
# Calculate the total distance traveled
total_distance_sector1 = cumulative_distance_sector1.sum()
# Calculate the percentage for each cumulative bar vs the total lap distance
percentages_sector1 = (cumulative_distance_sector1 / total_distance) * 100

# Let's calculate the sector 2
telemetry_fastest_lap_sector2 = telemetry_fastest_lap.slice_by_time(fastest_lap_time_Sector1, fastest_lap_time_Sector2)
# Bin the data by speed
speed_binned_sector2 = pd.cut(telemetry_fastest_lap['Speed'], bins=speed_bins)
cumulative_distance_sector2 = telemetry_fastest_lap_sector2.groupby(speed_binned)['DifferentialDistance'].sum()
# Calculate the total distance traveled
total_distance_sector2 = cumulative_distance_sector2.sum()
# Calculate the percentage for each cumulative bar vs the total lap distance
percentages_sector2 = (cumulative_distance_sector2 / total_distance) * 100

# Let's calculate the sector 3
telemetry_fastest_lap_sector3 = telemetry_fastest_lap.slice_by_time(fastest_lap_time_Sector2, fastest_lap_time_Sector3)
# Bin the data by speed
speed_binned_sector3 = pd.cut(telemetry_fastest_lap['Speed'], bins=speed_bins)
cumulative_distance_sector3 = telemetry_fastest_lap_sector3.groupby(speed_binned)['DifferentialDistance'].sum()
# Calculate the total distance traveled
total_distance_sector3 = cumulative_distance_sector3.sum()
# Calculate the percentage for each cumulative bar vs the total lap distance
percentages_sector3 = (cumulative_distance_sector3 / total_distance) * 100
"""
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
"""

# create the figure
plt.figure(figsize=(12, 7))

# Calculate the center of each bin
bin_centers = bin_left_edges + (speed_bins[1] - speed_bins[0]) / 2

#Plot Titles
plt.suptitle(f"{race.event['EventName']} {race.event.year} - Cumulative Distance Traveled vs Speed"
             f"\nFastest Lap by {fastest_lap['Driver']} (Approx Track Length: {max_distance:.0f} m)", y=0.98, fontsize=16)
plot_title = f"Overall Lap"

# Left column
ax1 = plt.subplot(3, 2, (1, 5))

# Right column
ax2 = plt.subplot(3, 2, 2)
ax3 = plt.subplot(3, 2, 4, sharey=ax2)
ax4 = plt.subplot(3, 2, 6, sharey=ax2)
axes = [ax1, ax2, ax3, ax4]

plt.subplots_adjust(hspace=0.5)  # Increase the vertical spacing between subplots
plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.9)


max_y_value = max(cumulative_distance.values)  # Adding a buffer of 100 for the percentage labels

# Add labels to the bars with bold font
for x, y, percentage in zip(bin_centers, cumulative_distance.values, percentages):
    ax1.text(x, y, f'{y:.0f}m', ha='center', va='bottom', weight='bold',fontsize = 8)
    ax1.text(x, y + max_y_value/25, f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize = 8)


ax1.title.set_text(plot_title)
ax1.bar(bin_centers, cumulative_distance.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
#ax1.set_yticklabels(final_data_sorted['diff to median'])
#ax1.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax1.set_ylabel('Cumulative Distance(m)')


#Graph Sector 1 data
ax2.bar(bin_centers, cumulative_distance_sector1.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
ax2.title.set_text(f"Sector 1")
ax2.set_ylabel('Cumulative Distance(m)')

for x, y, percentage in zip(bin_centers, cumulative_distance_sector1.values, percentages_sector1):
    #ax2.text(x, y, f'{y:.0f}m', ha='center', va='bottom', weight='bold', fontsize=6)
    ax2.text(x, y, f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize = 8)

#Graph Sector 2 data
ax3.bar(bin_centers, cumulative_distance_sector2.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
ax3.title.set_text(f"Sector 2")
ax3.set_ylabel('Cumulative Distance(m)')
for x, y, percentage in zip(bin_centers, cumulative_distance_sector2.values, percentages_sector2):
    #ax3.text(x, y, f'{y:.0f}m', ha='center', va='bottom', weight='bold', fontsize=6)
    ax3.text(x, y , f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize = 8)


#Graph Sector 3 data
ax4.bar(bin_centers, cumulative_distance_sector3.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
ax4.title.set_text(f"Sector 3")
ax4.set_ylabel('Cumulative Distance(m)')
for x, y, percentage in zip(bin_centers, cumulative_distance_sector3.values, percentages_sector3):
    #ax4.text(x, y, f'{y:.0f}m', ha='center', va='bottom', weight='bold', fontsize=6)
    ax4.text(x, y, f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize = 8)


# Add gridlines to all subplots
for ax in [ax1, ax2, ax3, ax4]:
    ax.grid(which='major', axis='y', color='grey', alpha=0.7)
    ax.set_axisbelow(True)  # Ensure gridlines appear below the bars

# Rotate the x-axis labels for each subplot
for ax in axes:
    ax.set_xticks(speed_bins)  # Set the tick positions
    ax.set_xticklabels(speed_bins, rotation=45)


# Set the font size of subplot titles individually
for ax in plt.gcf().get_axes():
    ax.set_title(ax.get_title(), fontsize=12)  # Set the font size (12 points in this example)


plt.tight_layout()  # Adjust the layout to prevent text cutoff

plt.show()
