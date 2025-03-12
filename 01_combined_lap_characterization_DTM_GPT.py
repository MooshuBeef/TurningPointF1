import fastf1 as ff1
import fastf1.plotting as plotting
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Initialize matplotlib plotting settings
plotting.setup_mpl()

# Load the race session data
year, grand_prix, session = 2024, 10, 'R'
race = ff1.get_session(year, grand_prix, session)
race.load()

# Define parameters
fastLapThreshold = 1.07
percentile_value = 0.95

# Select the fastest lap and retrieve telemetry
fastest_lap = race.laps.pick_fastest()
telemetry_fastest_lap = fastest_lap.get_telemetry().add_differential_distance()

# Bin the data by speed
speed_bins = np.arange(0, 375, 25)
speed_binned = pd.cut(telemetry_fastest_lap['Speed'], bins=speed_bins)

# Calculate time spent
telemetry_fastest_lap['TimeSpent'] = telemetry_fastest_lap['DifferentialDistance'] / telemetry_fastest_lap['Speed'] / 1000 * 3600
total_time = telemetry_fastest_lap['TimeSpent'].sum()

# Calculate cumulative time for each speed bin
cumulative_time = telemetry_fastest_lap.groupby(speed_binned)['TimeSpent'].sum()
percentagesTime = (cumulative_time / total_time) * 100
bin_centers = [interval.left + (interval.right - interval.left) / 2 for interval in cumulative_time.index]

# Retrieve race results
race_results = race.results
finished_count = len(race_results[race_results['Status'].isin(['Finished', '+1 Lap', '+2 Laps'])])
did_not_finish = race_results[~race_results['Status'].isin(['Finished', '+1 Lap', '+2 Laps'])][['DriverNumber', 'Abbreviation', 'Status']]
did_not_finish = did_not_finish.iloc[:-1]

# Get point finishers and their lap data
point_finishers = race.drivers[:finished_count]
driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps(fastLapThreshold).reset_index()

# Calculate percentile lap times and differences
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
percentile_lap_times = driver_laps.groupby('Driver')['LapTime(s)'].mean()
median_lap_time = percentile_lap_times.median()
lap_series = percentile_lap_times.reset_index()
final_data = pd.DataFrame(lap_series.values, columns=["DRIVERS", "LAP TIME"])
final_data['diff to median'] = final_data['LAP TIME'] - median_lap_time

# Get finishing order and driver colors
finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]
final_data["DRIVERS"] = pd.Categorical(final_data["DRIVERS"], categories=finishing_order, ordered=True)
final_data_sorted = final_data.sort_values(by="DRIVERS")

# Create the figure and subplots
fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(12, 9))
plt.subplots_adjust(hspace=0.5, left=0.05, right=0.95, bottom=0.05, top=0.9)

# Main plot: Cumulative Time vs Speed
ax1 = axes[0, 0]
ax1.bar(bin_centers, cumulative_time.values, width=speed_bins[1] - speed_bins[0], align='center', edgecolor='white', color='darkblue')
ax1.set_ylabel('Time at Speed (s)')
ax1.set_xlabel('Speed (km/h)')
ax1.set_title(f"Overall Lap - {race.event['EventName']} {race.event.year}")
for x, y, percentage in zip(bin_centers, cumulative_time.values, percentagesTime):
    ax1.text(x, y, f'{y:.1f}s', ha='center', va='bottom', weight='bold', fontsize=8)
    ax1.text(x, y + cumulative_time.max()/50, f'{percentage:.1f}%', ha='center', va='bottom', weight='bold', color='red', fontsize=8)

# DTM plot: Sector-wise comparisons
sectors = ["Sector1Time", "Sector2Time", "Sector3Time"]
sector_axes = [axes[i, 2] for i in range(3)]
for i, (sector, ax) in enumerate(zip(sectors, sector_axes)):
    sector_time = driver_laps.groupby('Driver')[f'{sector}(s)'].mean()
    median_sector_time = sector_time.median()
    final_data_sorted[f'{sector}_DTM(s)'] = final_data_sorted[f'{sector}(s)'] - median_sector_time
    bars = ax.bar(final_data_sorted['DRIVERS'], final_data_sorted[f'{sector}_DTM(s)'], color=final_data_sorted['DRIVERS'].map(driver_colors), edgecolor='grey')
    ax.set_title(f"{sector} - {race.event['EventName']} {race.event.year}")
    ax.set_ylabel('Delta (s)')
    ax.invert_yaxis()
    ax.set_xticklabels([])
    ax.set_xticks([])
    for bar, value, label in zip(bars, final_data_sorted[f'{sector}_DTM(s)'], final_data_sorted['DRIVERS']):
        height = bar.get_height()
        if value < 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height - 0.02, label, ha='center', va='bottom', fontsize=9, fontweight='bold')
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, -0.07, label, ha='center', va='top', fontsize=9, fontweight='bold')

plt.show()
