import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import fastf1 as ff1
import numpy as np

# Load your FastF1 data and preprocess as you did before

year, grand_prix, session = 2023, 'Belgium', 'R'

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

#What is the fastest lap time?
fastest_lap_time_total = fastest_lap['LapTime']

#Need to get times of Sector 1, Sector 2, and Sector 3
fastest_lap_time_start = fastest_lap['LapStartTime']
fastest_lap_time_Sector1 = fastest_lap['Sector1SessionTime']
fastest_lap_time_Sector2 = fastest_lap['Sector2SessionTime']
fastest_lap_time_Sector3 = fastest_lap['Sector3SessionTime']

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






# Plot Titles
plt.suptitle(f"{race.event['EventName']} {race.event.year} - Cumulative Distance Traveled vs Speed"
             f"\nFastest Lap by {fastest_lap['Driver']}", y=0.98, fontsize=16)
plot_title = f"Overall Lap"

# Create a figure
plt.figure(figsize=(16, 10), dpi=80)

# Plot the kernel density estimate for the Speed column
sns.kdeplot(telemetry_fastest_lap['Speed'], color="g", alpha=.7, label="Overall Lap") #fill=True
sns.kdeplot(telemetry_fastest_lap_sector1['Speed'], color="deeppink", alpha=.7, label="Sector 1")
#sns.kdeplot(df.loc[df['cyl'] == 5, "cty"], shade=True, color="deeppink", label="Cyl=5", alpha=.7)
#sns.kdeplot(df.loc[df['cyl'] == 6, "cty"], shade=True, color="dodgerblue", label="Cyl=6", alpha=.7)
#sns.kdeplot(df.loc[df['cyl'] == 8, "cty"], shade=True, color="orange", label="Cyl=8", alpha=.7)


# Decoration
plt.title('Kernel Density Estimate of Speed', fontsize=22)
plt.xlabel('Speed (km/h)')
plt.ylabel('Density')
plt.legend()
plt.legend([plot_title])
plt.show()
