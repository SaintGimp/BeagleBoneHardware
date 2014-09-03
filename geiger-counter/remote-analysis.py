import datetime, numpy, scipy, pandas
import matplotlib.pyplot as plt

df = pandas.read_json("http://data.sparkfun.com/output/WGG8ONW8bMf7x2ad0WOY.json", orient='records', dtype={'cpm' : 'int64', 'device_time' : 'datetime64[ns]', 'pressure': 'float64', 'sea_level_pressure': 'float64'})
df.drop('timestamp', axis=1, inplace=True)
df = df.set_index('device_time')

# show pressure resampled to 1 hour
hours = df.pressure.resample('1H')
hours = hours.ix[1:-1]
hours.plot(kind='line')
plt.ylim((100000,101000))
plt.show()

# show CPM resampled to 1 hour
hours = df.cpm.resample('1H')
hours = hours.ix[1:-1]
hours.plot(kind='bar')
plt.show()

# show CPM average for each hour of the day
average_cph = df.groupby(lambda x: (x.hour)).mean()
average_cph.plot(kind="bar")
plt.show()

# Show histogram of CPM
df.hist(bins=50, range=(0,50))
plt.show()
