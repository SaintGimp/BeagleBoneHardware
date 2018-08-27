import datetime, numpy, scipy, pandas
import matplotlib.pyplot as plt

print "Loading data"
df = pandas.read_json("/Users/elee/Downloads/geiger.json", orient='records', dtype={'cpm' : 'int64', 'device_time' : 'datetime64[ns]', 'timestamp' : 'datetime64[ns]', 'pressure': 'float64', 'sea_level_pressure': 'float64'})
print "Loaded"
print "Building index"
df.drop('timestamp', axis=1, inplace=True)
df = df.set_index('device_time')
print "Built index"

#df['n'] = 1
#counts = df.n.resample('12H', how="sum")
#counts.plot(kind='line')
#plt.show()
#df = df.ix['2014/11/01':'2014/11/09']

def plot_correlation():
    fig, pressure_axis = plt.subplots()
    hours = df.pressure.resample('4H')
    hours = hours.ix[1:-1]
    pressure_axis.plot(hours, color='blue')
    #pressure_axis.ylim((98000,103000))
    #plt.show()

    cpm_axis = pressure_axis.twinx()
    hours = df.cpm.resample('4H')
    hours = hours.ix[1:-1]
    cpm_axis.set_ylim((12, 20))
    cpm_axis.plot(hours, color='red')
    plt.show()


def plot_josiah():
    fig, night_axis = plt.subplots()
    month = df.ix['2015/08/01':'2015/08/31']
    averages = month.cpm.resample('12H', how="mean")
    night = averages.iloc[::2]
    night_axis.plot(night, color='blue')

    day_axis = night_axis.twinx()
    day = averages.iloc[1::2]
    day_axis.plot(day, color='red')

    plt.show()


def plot_josiah2():
    month = df.ix['2015/07/01':'2015/08/31']
    hours = month.cpm.resample('1H', how="sum")
    hours.plot(kind='line')

    plt.show()

def plot_josiah3():
    data = df.ix['2015/08/01':'2015/08/31']
    fig, cpm_axis = plt.subplots()

    # show CPM average for each hour of the day
    average_cph = data.cpm.groupby(lambda x: (x.hour)).mean()
    cpm_axis.plot(average_cph, color='red')
    cpm_axis.set_ylim((12, 20))

    average_pressure = data.pressure.groupby(lambda x: (x.hour)).mean()
    pressure_axis = cpm_axis.twinx()
    pressure_axis.plot(average_pressure, color='blue')
    pressure_axis.set_ylim((100000, 101000))
    
    print "Average counts per minute for each hour of the day"
    print average_cph

    print "Average atmospheric pressure each hour of the day"
    print average_pressure

    plt.show()

plot_correlation()

# show pressure resampled to 1 hour
# hours = df.pressure.resample('24H')
# hours = hours.ix[1:-1]
# hours.plot(kind='line')
# plt.ylim((98000,103000))
# plt.ylim((0,100))
# plt.show()

# show CPM resampled to 1 hour
#hours = df.cpm.resample('1H')
#hours = hours.ix[1:-1]
#hours.plot(kind='line')
#plt.show()

# show CPM average for each hour of the day
#df = df.ix['2014/10/23':'2014/10/30']
#average_cph = df.cpm.groupby(lambda x: (x.hour)).mean()
#average_cph.plot(kind="bar")
#plt.ylim((10, 18))
#plt.show()

# Show histogram of CPM
#df.hist(bins=50, range=(0,50))
#plt.show()
