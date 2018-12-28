#!/usr/bin/env python


import urllib.request

url = "https://s3.eu-west-2.amazonaws.com/aws-earth-mo-examples/cafef7005477edb001aa7dc50eab78c5ef89d420.nc" # sns_message['bucket'] + "/" + sns_message['key']
urllib.request.urlretrieve(url, 'sample.nc') # save in this directory with same name

import iris 
[mydata] = iris.load('sample.nc')
air_temps = mydata.extract(iris.Constraint(realization=0))

air_temp = air_temps.extract(iris.Constraint(pressure=1000.0))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import iris.quickplot as qplt

# Set the size of the plot
plt.figure(figsize=(20, 20))

#cube = iris.load_cube(filepath)

qplt.pcolormesh(air_temp)
plt.gca().coastlines('50m')

plt.savefig('sample.png')


