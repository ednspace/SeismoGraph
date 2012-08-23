#!/usr/bin/python
from pylab import *
from matplotlib.dates import num2date

CDC=[]
Date=[]
count = 0

file = open('log.txt', 'r')
print "Slurping Raw Data... ummmmmm!!!"
while 1:
        line = file.readline()
        if not line:
                break

        comma = line.rfind(',')

        paren = line.rfind(')')
        CDC.append(line[comma-7:comma])
        Date.append(line[paren-19:paren-1])

        if count%100000 == 0:
                print CDC[count]
                print count

        count = count + 1
file.close()


CDC_float = map(float, CDC)
Date_float = map(float, Date)

figure(1)
grid()
title('CDC-Counts Against Time')
xlabel('Time')
ylabel('CDC-Counts')
plot_date(Date_float,CDC_float,'-b',label='Whole Tamali')


show()





