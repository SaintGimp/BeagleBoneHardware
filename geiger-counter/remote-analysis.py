import datetime, numpy, scipy, pandas
import matplotlib.pyplot as plt

#df = pandas.DataFrame()

#for x in range(1,80):
	#print("Loading page " + str(x))
	#pageFrame = pandas.read_json("http://data.sparkfun.com/output/WGG8ONW8bMf7x2ad0WOY.json?page=" + str(x), orient='records', dtype={'cpm' : 'int64', 'device_time' : 'datetime64[ns]', 'pressure': 'float64', 'sea_level_pressure': 'float64'})
	#pageFrame = pandas.read_json("/Users/elee/Downloads/stream_WGG8ONW8bMf7x2ad0WOY.json", orient='records', dtype={'cpm' : 'int64', 'device_time' : 'datetime64[ns]', 'pressure': 'float64', 'sea_level_pressure': 'float64'})
	#pageFrame.drop('timestamp', axis=1, inplace=True)
	#df = df.append(pageFrame)

df = pandas.read_json("/Users/elee/Downloads/stream_WGG8ONW8bMf7x2ad0WOY.json", orient='records', dtype={'cpm' : 'int64', 'device_time' : 'datetime64[ns]', 'timestamp' : 'datetime64[ns]', 'pressure': 'float64', 'sea_level_pressure': 'float64'})
df.drop('timestamp', axis=1, inplace=True)
df = df.set_index('device_time')

#df['n'] = 1
#counts = df.n.resample('12H', how="sum")
#counts.plot(kind='line')
#plt.show()
#df = df.ix['2014/11/01':'2014/11/09']

fig, pressure_axis = plt.subplots()
hours = df.pressure.resample('4H')
hours = hours.ix[1:-1]
pressure_axis.plot(hours, color='blue')
#pressure_axis.ylim((98000,103000))
#plt.show()

cpm_axis = pressure_axis.twinx()
hours = df.cpm.resample('4H')
hours = hours.ix[1:-1]
cpm_axis.plot(hours, color='red')
plt.show()

# show pressure resampled to 1 hour
# hours = df.pressure.resample('24H')
# hours = hours.ix[1:-1]
# hours.plot(kind='line')
# plt.ylim((98000,103000))
# plt.ylim((0,100))
# plt.show()

# show CPM resampled to 1 hour
# hours = df.cpm.resample('24H')
# hours = hours.ix[1:-1]
# hours.plot(kind='line')
# plt.show()

# show CPM average for each hour of the day
#df = df.ix['2014/10/23':'2014/10/30']
#average_cph = df.cpm.groupby(lambda x: (x.hour)).mean()
#average_cph.plot(kind="bar")
#plt.ylim((10, 18))
#plt.show()

# Show histogram of CPM
#df.hist(bins=50, range=(0,50))
#plt.show()
