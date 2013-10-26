import datetime, numpy, scipy, pandas
import matplotlib.pyplot as plt

df = pandas.read_table("/Users/elee/temperature_data.txt", sep=",", header=0, index_col=0, parse_dates=True)

print df.columns
print df["temp"]


minutes = df.temp.resample("1T", how="mean")
df.temp.plot(kind="line")
plt.show()