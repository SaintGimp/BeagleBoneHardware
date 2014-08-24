import datetime, numpy, scipy, pandas
import matplotlib.pyplot as plt

df = pandas.read_json("http://phant.saintgimp.org/output/3K2oGxKqelCo0ry50Ln4fpr1q7m.json", orient='records', dtype={'CPM' : 'int64', 'Device_Time' : 'datetime64[ns]'})
df.drop('timestamp', axis=1, inplace=True)
df = df.set_index('Device_Time')

# show resampled to 1 hour
hours = df.resample('1H')
hours = hours.ix[1:-1]
hours.plot(kind='bar')
plt.show()

# show average for each hour of the day
average_cph = df.groupby(lambda x: (x.hour)).mean()
average_cph.plot(kind="bar")
plt.show()

# Show histogram of CPM
df.hist(bins=50, range=(0,50))
plt.show()
