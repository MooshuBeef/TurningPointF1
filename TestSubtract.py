import pandas as pd

driver_laps = pd.DataFrame({
    'Driver': ["VER", "HAM", "SAI", "RUS", "STR", "OCO", "TSU", "ZHO", "PER", "ALO", "PIA", "LEC", "GAS", "NOR", "DEV", "HUL", "ALB", "MAG", "SAR", "BOT"],
    'LapTime': [80.51685, 80.86370, 80.93500, 81.32670, 81.36000, 81.51600, 81.64700, 81.70500, 81.71860, 81.76875, 81.85080, 81.85270, 81.97200, 82.13505, 82.17805, 82.21185, 82.44620, 82.55800, 82.81230, 83.00705]
})

value_to_subtract = 81.809775

# Subtract the value from the 'LapTime' column
driver_laps['Difference'] = driver_laps['LapTime'] - value_to_subtract

print(driver_laps)
