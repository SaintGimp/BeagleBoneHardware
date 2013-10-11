import datetime, numpy, scipy, pandas
import matplotlib.pyplot as plt

df = pandas.read_table("temperature_data.txt", sep=",", header=None, names=["timestamp", "temp"], index_col=0, parse_dates=True)

print df.columns
print df["temp"]


minutes = df.temp.resample("1T", how="mean")
minutes.plot(kind="line")
plt.show()
