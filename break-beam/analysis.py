import datetime, numpy, scipy, pandas
import matplotlib.pyplot as plt

df = pandas.read_table("/Users/elee/breakbeam_data.txt", index_col=0, parse_dates=True)

df["timestamp"] = df.index
df["delta"] = (df["timestamp"] - df["timestamp"].shift()).fillna(0)
df["delta_numeric"] = df.delta.apply(lambda x: x / numpy.timedelta64(1, 's'))

cpm = df.timestamp.resample("15T", how="count")
cpm.plot(kind="bar")
plt.show()

# cps = df.resample("1S", how='count')
# cps.hist(bins=50)
# plt.show()
