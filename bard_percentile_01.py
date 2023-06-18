import csv

def find_90th_percentile(data):
  data.sort()
  return data[int(len(data) * 0.90)]

def main():
  with open("driver_laps.csv", "r") as f:
    reader = csv.reader(f)
    data = []
    for row in reader:
      data.append(float(row[1]))

    # Find the 90th percentile of the lap times.
    p90 = find_90th_percentile(data)

    # Print the driver names and their 90th percentile lap times.
    for driver, lap_time in zip(reader, data):
      if lap_time >= p90:
        print(driver, lap_time)

if __name__ == "__main__":
  main()