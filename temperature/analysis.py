import datetime, numpy, scipy, pandas
import matplotlib.pyplot as plt

df = pandas.read_table("temperature_data.txt", sep=",", header=None, names=["timestamp", "temp"], index_col=0, parse_dates=True)

print df.columns
print df["temp"]


#cpm = df.temp.resample("1T", how="mean")
#cpm.plot(kind="line")
df.temp.plot(kind="line")
plt.show()
