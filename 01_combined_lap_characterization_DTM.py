import fastf1 as ff1
import fastf1.plotting as plotting
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.gridspec as gridspec


plotting.setup_mpl()

#year, grand_prix, session = 2022, 'Netherlands', 'R'
year, grand_prix, session = 2024, 23, 'R'

race = ff1.get_session(year, grand_prix, session)
race.load()

# For DTM Controls
# set a threshold of fast laps for cleanliness˘
# Typically it's 1.07, but for messy races like Monaco 2023, 2.0 is needed
fastLapThreshold = 1.07

# Set percentile value
percentile_value = 0.95

###############################################################################

# Select the fastest lap
fastest_lap = race.laps.pick_fastest()

# Retrieve the telemetry and add the distance column
telemetry_fastest_lap = fastest_lap.get_telemetry().add_differential_distance()

# Create bins for speed
speed_bins = np.arange(0, 375, 25)

# Bin the data by speed
speed_binned = pd.cut(telemetry_fastest_lap['Speed'], bins=speed_bins)

#We're calculating how long the time is spent at the distance travelled: m / (km/hr) / 1000 * 3600 = seconds
telemetry_fastest_lap['TimeSpent'] = telemetry_fastest_lap['DifferentialDistance'] / telemetry_fastest_lap['Speed'] / 1000 * 3600

total_time = telemetry_fastest_lap['TimeSpent'].sum()
print(total_time)


# Calculate the cumulative distance for each speed bin
cumulative_distance = telemetry_fastest_lap.groupby(speed_binned)['DifferentialDistance'].sum()
# Doing the above but by time
cumulative_time = telemetry_fastest_lap.groupby(speed_binned)['TimeSpent'].sum()

# We're gonna calculate for time spent vs cumulative distance

# Calculate the total distance traveled
total_distance = cumulative_distance.sum()

# Calculate the percentage for each cumulative bar
percentagesTime = (cumulative_time / total_time) * 100

# Calculate the left edges of each bin manually
bin_left_edges = [interval.left for interval in cumulative_time.index.to_numpy()]

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
cumulative_time_sector1 = telemetry_fastest_lap_sector1.groupby(speed_binned)['TimeSpent'].sum()
# Calculate the total distance traveled
total_time_sector1 = cumulative_time.sum()
# Calculate the percentage for each cumulative bar vs the total lap distance
percentagesTime_sector1 = (cumulative_time_sector1 / total_distance) * 100

# Let's calculate the sector 2
telemetry_fastest_lap_sector2 = telemetry_fastest_lap.slice_by_time(fastest_lap_time_Sector1, fastest_lap_time_Sector2)
# Bin the data by speed
speed_binned_sector2 = pd.cut(telemetry_fastest_lap['Speed'], bins=speed_bins)
cumulative_time_sector2 = telemetry_fastest_lap_sector2.groupby(speed_binned)['TimeSpent'].sum()
# Calculate the total distance traveled
#total_distance_sector2 = cumulative_distance_sector2.sum()
# Calculate the percentage for each cumulative bar vs the total lap distance
percentagesTime_sector2 = (cumulative_time_sector2 / total_distance) * 100

# Let's calculate the sector 3
telemetry_fastest_lap_sector3 = telemetry_fastest_lap.slice_by_time(fastest_lap_time_Sector2, fastest_lap_time_Sector3)
# Bin the data by speed
speed_binned_sector3 = pd.cut(telemetry_fastest_lap['Speed'], bins=speed_bins)
cumulative_time_sector3 = telemetry_fastest_lap_sector3.groupby(speed_binned)['TimeSpent'].sum()
# Calculate the total distance traveled
#total_distance_sector3 = cumulative_distance_sector3.sum()
# Calculate the percentage for each cumulative bar vs the total lap distance
percentagesTime_sector3 = (cumulative_time_sector3 / total_distance) * 100

################################################################################################
#DTM CODE
################################################################################################

# Get all the laps for the point finishers only.
# Filter out slow laps (yellow flag, VSC, pitstops etc.)
# as they distort the graph axis.

#Let's try to identify the number of race finishers
race_results = race.results

# Count how many drivers finished the race successfully
finished_count = len(race_results[race_results['Status'].isin(['Finished', '+1 Lap', '+2 Laps'])])

# Create a variable to store driver names and their statuses for those who didn't finish
did_not_finish = race_results[~race_results['Status'].isin(['Finished', '+1 Lap', '+2 Laps'])][['DriverNumber', 'Abbreviation', 'Status']]

#IN case the did not finish rows needs to be deleted for an error
rows_to_delete = 1
did_not_finish = did_not_finish.iloc[:-rows_to_delete]


# Print the counts and the DataFrame for drivers who didn't finish
print("Number of drivers who finished the race:", finished_count)
print("\nDrivers who didn't finish:")
print(did_not_finish)

# This spits out a 1 column array with the point finishers
#point_finishers = race.drivers[:finished_count]

# This spits out a 1 column array with the point finishers
point_finishers = race.drivers[:finished_count]


#Now we can get the data for all the points finishers
driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps(fastLapThreshold).reset_index()

#Let's get the maximum lap from those who didn't finish
no_finish_laps = race.laps.pick_drivers(did_not_finish['DriverNumber'])
no_finish_last_lap = no_finish_laps.groupby('DriverNumber')['LapNumber'].max()
#print(no_finish_last_lap)

#Create a new variable with the driver, reason for retirement, and last lap completed
did_not_finish = did_not_finish.merge(no_finish_last_lap, left_on='DriverNumber', right_index=True, how='left')
did_not_finish = did_not_finish.rename(columns={'LapNumber': 'LastLap'})
print(did_not_finish)


###############################################################################
# To plot the drivers by finishing order,
# we need to get their three-letter abbreviations in the finishing order.
finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]
print(finishing_order)

###############################################################################
# We need to modify the DRIVER_COLORS palette.
# Its keys are the driver's full names but we need the keys to be the drivers'
# three-letter abbreviations.
# We can do this with the DRIVER_TRANSLATE mapping.
driver_colors = {abv: ff1.plotting.DRIVER_COLORS[driver] for abv,
driver in ff1.plotting.DRIVER_TRANSLATE.items()}
# print(driver_colors)

# Get the lap times in seconds which we can do calculations with
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
driver_laps["Sector1(s)"] = driver_laps["Sector1Time"].dt.total_seconds()
driver_laps["Sector2(s)"] = driver_laps["Sector2Time"].dt.total_seconds()
driver_laps["Sector3(s)"] = driver_laps["Sector3Time"].dt.total_seconds()

# Let's calculate the 90th percentile
#Sector1_percentile = np.percentile(driver_laps["Sector1(s)"], 90)


# Group the DataFrame by driver and calculate the 90th percentile lap time
percentile_lap_times = driver_laps.groupby('Driver')['LapTime(s)'].mean()
percentile_sector_1 = driver_laps.groupby('Driver')['Sector1(s)'].mean()
percentile_sector_2 = driver_laps.groupby('Driver')['Sector2(s)'].mean()
percentile_sector_3 = driver_laps.groupby('Driver')['Sector3(s)'].mean()


# Find Median time from the 90th percentile
#percentile_lap_times_int = percentile_lap_times.astype(int)
median_lap_time = percentile_lap_times.median()
median_sector_1 = percentile_sector_1.median()
median_sector_2 = percentile_sector_2.median()
median_sector_3 = percentile_sector_3.median()

print(f"Median time is {median_lap_time}")

#breaking out data from the series into the driver label and times
lap_series = percentile_lap_times.reset_index()
sector1_series = percentile_sector_1
sector2_series = percentile_sector_2
sector3_series = percentile_sector_3
lap_array = lap_series.values
sector1_array = sector1_series.values
sector2_array = sector2_series.values
sector3_array = sector3_series.values

# Create a DataFrame from the array
final_data = pd.DataFrame(lap_array)
#print(sector1_series)
# Set the column names
final_data.columns = ["DRIVERS", "LAP TIME"]
final_data['Sector1Time(s)'] = sector1_array
final_data['Sector2Time(s)'] = sector2_array
final_data['Sector3Time(s)'] = sector3_array




final_data['diff to median'] = final_data['LAP TIME'] - median_lap_time
#final_data_sorted = final_data#.sort_values(by='diff to median')

# Convert the "Drivers" column of the final_data DataFrame to a Categorical data type
# with the custom order specified by the finishing_order list
final_data["DRIVERS"] = pd.Categorical(final_data["DRIVERS"], categories=finishing_order, ordered=True)

# Sort the DataFrame based on the custom order of the "Drivers" column
final_data_sorted = final_data.sort_values(by="DRIVERS")

final_data_sorted['Sector1_DTM(s)'] = final_data_sorted['Sector1Time(s)'] - median_sector_1
final_data_sorted['Sector2_DTM(s)'] = final_data_sorted['Sector2Time(s)'] - median_sector_2
final_data_sorted['Sector3_DTM(s)'] = final_data_sorted['Sector3Time(s)'] - median_sector_3

#########################################
#END DTM
#########################################


# create the figure
plt.figure(figsize=(15, 10))

# Calculate the center of each bin
bin_centers = bin_left_edges + (speed_bins[1] - speed_bins[0]) / 2

# Create a figure
fig = plt.figure(figsize=(17, 10))
gs = gridspec.GridSpec(3, 3, figure=fig)

#Plot Titles
plt.suptitle(f"{race.event['EventName']} {race.event.year} - Cumulative Time Traveled vs Speed"
             f"\nFastest Lap by {fastest_lap['Driver']} ({total_time:.3f} seconds)", y=0.98, fontsize=16)

plot_title = f"Overall Lap"


# Left column (spanning 3 rows)
ax1 = fig.add_subplot(gs[:, 0])  # All rows, first column

# Middle column
ax2 = fig.add_subplot(gs[0, 1])  # First row, second column
ax3 = fig.add_subplot(gs[1, 1], sharey=ax2)  # Second row, second column
ax4 = fig.add_subplot(gs[2, 1], sharey=ax2)  # Third row, second column

# Right column (DTM)
ax5 = fig.add_subplot(gs[0, 2])  # First row, third column
ax6 = fig.add_subplot(gs[1, 2], sharey=ax5)  # Second row, third column
ax7 = fig.add_subplot(gs[2, 2], sharey=ax5)  # Third row, third column


""" Trying another way to plot the grid
# Left column
ax1 = plt.subplot(3, 3, (1, 7))

#ax1 = plt.subplot(3, 2, (1, 5))
#Old Code with just the lap characterization

# Middle column
ax2 = plt.subplot(3, 6, 2)
ax3 = plt.subplot(3, 6, 4, sharey=ax2)
ax4 = plt.subplot(3, 6, 6, sharey=ax2)

# Right column (DTM)
ax5 = plt.subplot(3, 3, 3)
ax6 = plt.subplot(3, 3, 6, sharey=ax5)
ax7 = plt.subplot(3, 3, 9, sharey=ax5)
"""
axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7]




plt.subplots_adjust(hspace=0.5)  # Increase the vertical spacing between subplots
plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.9)


max_y_value = max(cumulative_time.values)  # Adding a buffer of 100 for the percentage labels

# Add labels to the bars with bold font
for x, y, percentage in zip(bin_centers, cumulative_time.values, percentagesTime):
    ax1.text(x, y, f'{y:.1f}s', ha='center', va='bottom', weight='bold',fontsize = 8)
    ax1.text(x, y + max_y_value/50, f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize = 8)


ax1.title.set_text(plot_title)
ax1.bar(bin_centers, cumulative_time.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
#ax1.set_yticklabels(final_data_sorted['diff to median'])
#ax1.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax1.set_ylabel('Time at Speed (s)')
ax1.set_xlabel('Speed (km/h)')



#Graph Sector 1 data
ax2.bar(bin_centers, cumulative_time_sector1.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
ax2.title.set_text(f"Sector 1 - {race.event['EventName']} {race.event.year}" )
ax2.set_ylabel('Time at Speed (s)')
#ax2.set_xlabel('Speed (km/h)')


for x, y, percentage in zip(bin_centers, cumulative_time_sector1.values, percentagesTime_sector1):
    ax2.text(x, y, f'{y:.1f}s', ha='center', va='bottom', weight='bold',fontsize = 8)
    #ax2.text(x, y, f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize = 8)

#Graph Sector 2 data
ax3.bar(bin_centers, cumulative_time_sector2.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
ax3.title.set_text(f"Sector 2 - {race.event['EventName']} {race.event.year}")
ax3.set_ylabel('Time at Speed (s)')
#ax3.set_xlabel('Speed (km/h)')
for x, y, percentage in zip(bin_centers, cumulative_time_sector2.values, percentagesTime_sector2):
    ax3.text(x, y, f'{y:.1f}s', ha='center', va='bottom', weight='bold',fontsize = 8)
    #ax3.text(x, y , f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize = 8)


#Graph Sector 3 data
ax4.bar(bin_centers, cumulative_time_sector3.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
ax4.title.set_text(f"Sector 3 - {race.event['EventName']} {race.event.year}")
ax4.set_ylabel('Time at Speed (s)')
ax4.set_xlabel('Speed (km/h)')

for x, y, percentage in zip(bin_centers, cumulative_time_sector3.values, percentagesTime_sector3):
    ax4.text(x, y, f'{y:.1f}s', ha='center', va='bottom', weight='bold',fontsize = 8)
    #ax4.text(x, y, f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize = 8)

############################################
# DTM GRAPHING
############################################


# Assuming 'diff to median' contains NaN values
final_data_sorted['diff to median'].fillna('gray', inplace=True)

#ax1.title.set_text(plot_title)
#ax1.bar(final_data_sorted['DRIVERS'], final_data_sorted['diff to median'],
#        color=final_data_sorted['DRIVERS'].map(driver_colors),
#        edgecolor='grey')
#ax.set_yticks(fastest_laps.index)
#ax1.set_yticklabels(final_data_sorted['diff to median'])
#ax1.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
#ax1.set_ylabel('Delta (s)')
# show fastest at the top
#ax1.invert_yaxis()
# remove driver names and tick marks along the bottom of the graph
#ax1.set_xticklabels([])
#ax1.set_xticks([])

# Calculate y-coordinate for the text box
y_coord = -0.12  # Adjust this value as needed

# Create a text box with a white background to serve as a legend
legend_text = '\n'.join([f"{driver} retired Lap {int(last_lap)} ({status})" for driver, last_lap, status in zip(did_not_finish['Abbreviation'], did_not_finish['LastLap'], did_not_finish['Status'])])
ax1.text(0.02, 0.02*(20-finished_count), legend_text, ha='left', va='top', fontsize=10, fontweight='bold', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round'), transform=ax1.transAxes)
#ax1.text(12.5, -1.0, legend_text, ha='left', va='top', fontsize=10, fontweight='bold', bbox=dict(facecolor='black', edgecolor='black', boxstyle='round'))
#ax1.text(0.5, y_coord, legend_text, ha='center', va='center', fontsize=10, fontweight='bold', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))

# Hide the x-axis labels for ax1
#ax1.set_xticks([])

# Adjust the plot layout to make space for the text box
#plt.tight_layout()


ax5.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector1_DTM(s)'],
         color=final_data_sorted['DRIVERS'].map(driver_colors), edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax5.title.set_text(f"Sector 1")
ax5.set_yticklabels(final_data_sorted['Sector1_DTM(s)'])
ax5.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax5.set_ylabel('Delta (s)')
ax5.invert_yaxis()
# remove driver names and tick marks along the bottom of the graph
ax5.set_xticklabels([])
ax5.set_xticks([])


ax6.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector2_DTM(s)'],
         color=final_data_sorted['DRIVERS'].map(driver_colors), edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax6.title.set_text(f"Sector 2")
ax6.set_yticklabels(final_data_sorted['Sector2_DTM(s)'])
ax6.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax6.invert_yaxis()
# remove driver names and tick marks along the bottom of the graph
ax6.set_xticklabels([])
ax6.set_xticks([])

ax7.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector3_DTM(s)'],
         color=final_data_sorted['DRIVERS'].map(driver_colors), edgecolor='grey') ##color=team_colors,
#ax.set_yticks(fastest_laps.index)
ax7.title.set_text(f"Sector 3")
ax7.set_yticklabels(final_data_sorted['Sector3_DTM(s)'])
ax7.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
ax7.invert_yaxis()
# remove driver names and tick marks along the bottom of the graph
ax7.set_xticklabels([])
ax7.set_xticks([])

###############################################################################
# Set font size of charts

driverFontSize = 9


###############################################################################
# GRAPH 1 X AXIS LABEL FORMATTING
# Modify the ax1.bar() function to color the bars based on the team
#bars = ax1.bar(final_data_sorted['DRIVERS'], final_data_sorted['diff to median'],
#               color=final_data_sorted['DRIVERS'].map(driver_colors),
#               edgecolor='grey')

# Manually adjust the x-axis label positions to be below the bar for negative values
#for bar, value, label in zip(bars, final_data_sorted['diff to median'], final_data_sorted['DRIVERS']):
#    height = bar.get_height()
#    if value < 0:
#        # If the value is negative, place the label below the bar
#        ax1.text(bar.get_x() + bar.get_width() / 2, height - 0.02, label, ha='center', va='bottom', fontsize=driverFontSize, fontweight='bold')
#    else:
#        # If the value is non-negative, place the label above the bar
#        ax1.text(bar.get_x() + bar.get_width() / 2, -0.05, label, ha='center', va='top', fontsize=driverFontSize, fontweight='bold')


###############################################################################
# SECTOR 1 X AXIS LABEL FORMATTING
# Modify the ax2.bar() function to color the bars based on the team
bars2 = ax5.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector1_DTM(s)'],
               color=final_data_sorted['DRIVERS'].map(driver_colors),
               edgecolor='grey')

# Manually adjust the x-axis label positions to be below the bar for negative values
for bar, value, label in zip(bars2, final_data_sorted['Sector1_DTM(s)'], final_data_sorted['DRIVERS']):
    height = bar.get_height()
    if value < 0:
        # If the value is negative, place the label below the bar
        ax5.text(bar.get_x() + bar.get_width() / 2, height - 0.02, label, ha='center', va='bottom', fontsize=driverFontSize, fontweight='bold', rotation=60)
    else:
        # If the value is non-negative, place the label above the bar
        ax5.text(bar.get_x() + bar.get_width() / 2, -0.07, label, ha='center', va='top', fontsize=driverFontSize, fontweight='bold', rotation=60)

###############################################################################
# SECTOR 2 X AXIS LABEL FORMATTING
# Modify the ax3.bar() function to color the bars based on the team
bars3 = ax6.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector2_DTM(s)'],
               color=final_data_sorted['DRIVERS'].map(driver_colors),
               edgecolor='grey')

# Manually adjust the x-axis label positions to be below the bar for negative values
for bar, value, label in zip(bars3, final_data_sorted['Sector2_DTM(s)'], final_data_sorted['DRIVERS']):
    height = bar.get_height()
    if value < 0:
        # If the value is negative, place the label below the bar
        ax6.text(bar.get_x() + bar.get_width() / 2, height - 0.02, label, ha='center', va='bottom', fontsize=driverFontSize, fontweight='bold', rotation=60)
    else:
        # If the value is non-negative, place the label above the bar
        ax6.text(bar.get_x() + bar.get_width() / 2, -0.07, label, ha='center', va='top', fontsize=driverFontSize, fontweight='bold', rotation=60)

###############################################################################
# SECTOR 3 X AXIS LABEL FORMATTING
# Modify the ax1.bar() function to color the bars based on the team
bars4 = ax7.bar(final_data_sorted['DRIVERS'], final_data_sorted['Sector3_DTM(s)'],
               color=final_data_sorted['DRIVERS'].map(driver_colors),
               edgecolor='grey')

# Manually adjust the x-axis label positions to be below the bar for negative values
for bar, value, label in zip(bars4, final_data_sorted['Sector3_DTM(s)'], final_data_sorted['DRIVERS']):
    height = bar.get_height()
    if value < 0:
        # If the value is negative, place the label below the bar
        ax7.text(bar.get_x() + bar.get_width() / 2, height - 0.02, label, ha='center', va='bottom', fontsize=driverFontSize, fontweight='bold', rotation=60)
    else:
        # If the value is non-negative, place the label above the bar
        ax7.text(bar.get_x() + bar.get_width() / 2, -0.07, label, ha='center', va='top', fontsize=driverFontSize, fontweight='bold', rotation=60)




#################################
# END DTM GRAPHING
#################################





# Add gridlines to all subplots
for ax in [ax1, ax2, ax3, ax4, ax5, ax6, ax7]:
    ax.grid(which='major', axis='y', color='grey', alpha=0.7)
    ax.set_axisbelow(True)  # Ensure gridlines appear below the bars

# List of specific axes to modify for Characterization Only
specific_axes = [ax1, ax2, ax3, ax4]

# Rotate the x-axis labels for each subplot
###### Not sure what is wrong here, comment for now
#for ax in specific_axes:
#    ax.set_xticks(speed_bins)  # Set the tick positions
#    ax.set_xticklabels(speed_bins, rotation=45)


# Set the font size of subplot titles individually
for ax in plt.gcf().get_axes():
    ax.set_title(ax.get_title(), fontsize=12)  # Set the font size (12 points in this example)


plt.tight_layout()  # Adjust the layout to prevent text cutoff

plt.show()
