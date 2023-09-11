
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt  # Correct import

import fastf1 as ff1
import fastf1.plotting as plotting
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


#plotting.setup_mpl()
#this was causing an error

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


# Calculate the center of each bin
bin_centers = bin_left_edges + (speed_bins[1] - speed_bins[0]) / 2

#Plot Titles
plt.suptitle(f"{race.event['EventName']} {race.event.year} - Cumulative Distance Traveled vs Speed"
             f"\nFastest Lap by {fastest_lap['Driver']} (Approx Track Length: {max_distance:.0f} m)", y=0.98, fontsize=16)
plot_title = f"Overall Lap"



# Import Data
#df = pd.read_csv("https://github.com/selva86/datasets/raw/master/mpg_ggplot2.csv")

# Draw Plot
plt.figure(figsize=(16,10), dpi=80)
sns.kdeplot(speed_bins, cumulative_distance, fill=True, color="g", alpha=.7)
#sns.kdeplot(df.loc[df['cyl'] == 5, "cty"], shade=True, color="deeppink", label="Cyl=5", alpha=.7)
#sns.kdeplot(df.loc[df['cyl'] == 6, "cty"], shade=True, color="dodgerblue", label="Cyl=6", alpha=.7)
#sns.kdeplot(df.loc[df['cyl'] == 8, "cty"], shade=True, color="orange", label="Cyl=8", alpha=.7)

# Decoration
#plt.title('Density Plot of City Mileage by n_Cylinders', fontsize=22)
plt.legend()
plt.show()

