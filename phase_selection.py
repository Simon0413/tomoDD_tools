## phase_selection.py v1.0
## HypoDD或TomoDD中phaseSelection的替代
## 原程序只能使用一次函数进行拟合，对于震中距较远的事件拟合较差，无法筛选
## 该程序可以自行设置拟合函数，尝试得到最好的拟合结果

import scipy
import matplotlib.pyplot as plt 
import numpy as np
import math
###########################文件位置####################################
station_file = "../data/station.dat"
phase_file = "../data/phase.dat"
sel_file = "./phase.dat.sel"
###########################拟合函数####################################
def p_func(x,a,b,c):
    return c*x**a+b
def s_func(x,a,b):
    return x**a+b
###########################调整截距####################################
pd1 = 5
pd2 = 6
sd1 = 7
sd2 = 7
######################################################################
## 计算台站和事件的距离
def distance(lat1,lat2,lon1,lon2,dep1,dep2):
    dlat = lat1-lat2
    dlon = lon1-lon2
    ddep = dep1-dep2
    dist = math.sqrt((dlat*111)**2+(dlon*(math.cos(lat1*3.1415926/180)*111))**2+ddep**2)
    return dist
## 读取台站位置信息
stations = {}
with open(station_file, "r") as f:
    lines = f.readlines()
    for line in lines:
        line = line.split()
        stations[line[0]] = [float(line[1]),float(line[2]),-float(line[3])/1000]
        
p_dist = []
p_ttime = []
s_dist = []
s_ttime = []
e_lat,e_lon,e_dep = 0,0,0
with open(phase_file, "r") as f:
    lines = f.readlines()
    for line in lines:
        line = line.split()
        if line[0] == "#":
            e_lat = float(line[7])
            e_lon = float(line[8])
            e_dep = float(line[9])
        else:
            sta = line[0]
            t_time = float(line[1])
            p_type = line[-1]
            s_lat = stations[sta][0]
            s_lon = stations[sta][1]
            s_dep = stations[sta][2]
            dist = distance(e_lat,s_lat,e_lon,s_lon,e_dep,s_dep)
            if p_type == "P":
                p_dist.append(dist)
                p_ttime.append(t_time)
            else:
                s_dist.append(dist)
                s_ttime.append(t_time)

p_fit = scipy.optimize.curve_fit(p_func,p_dist,p_ttime)[0]
p_a = p_fit[0]
p_b = p_fit[1]
p_c = p_fit[2]
p_x = []
p_y = []
for i in range(0,700,10):
    p_x.append(i)
    p_y.append(p_func(i, p_a, p_b, p_c))
p_y1 = []
p_y2 = []
for i in p_y:
    p_y1.append(i+pd1)
    p_y2.append(i-pd2)

s_fit = scipy.optimize.curve_fit(s_func,s_dist,s_ttime)[0]
s_a = s_fit[0]
s_b = s_fit[1]
s_x = []
s_y = []
for i in range(0,700,10):
    s_x.append(i)
    s_y.append(s_func(i, s_a, s_b))
s_y1 = []
s_y2 = []
for i in s_y:
    s_y1.append(i+sd1)
    s_y2.append(i-sd2)

plt.figure(1)
plt.xlabel("distance")
plt.ylabel("travel time")
plt.scatter(p_dist,p_ttime,s=1,c="b",alpha=1)
plt.plot(p_x,p_y,c = "orange")
plt.plot(p_x,p_y1,c = "orange")
plt.plot(p_x,p_y2,c = "orange")
plt.text(0, max(p_ttime),str(len(p_dist)))

plt.figure(2)
plt.xlabel("distance")
plt.ylabel("travel time")
plt.scatter(s_dist,s_ttime,s=1,c="r",alpha=1)
plt.plot(s_x,s_y,c = "orange")
plt.plot(s_x,s_y1,c = "orange")
plt.plot(s_x,s_y2,c = "orange")
plt.text(0, max(s_ttime),str(len(s_dist)))
## 绘制筛选前的走时曲线
plt.show()

catalog = []
e_lat,e_lon,e_dep = 0,0,0
with open(phase_file, "r") as f:
    lines = f.readlines()
    for line in lines:
        if line[0] == "#":
            lin = line.split()
            e_lat = float(lin[7])
            e_lon = float(lin[8])
            e_dep = float(lin[9])
            catalog.append(line)
        else:
            lin = line.split()
            sta = lin[0]
            t_time = float(lin[1])
            p_type = lin[-1]
            s_lat = stations[sta][0]
            s_lon = stations[sta][1]
            s_dep = stations[sta][2]
            dist = distance(e_lat,s_lat,e_lon,s_lon,e_dep,s_dep)
            if p_type == "P":
                pred_tt = p_func(dist,p_a,p_b,p_c)
            else:
                pred_tt = s_func(dist,s_a,s_b)
            if dist>50 and pred_tt-pd2 <= t_time <= pred_tt+pd1:
                catalog.append(line)
            elif dist<=50:
                catalog.append(line)

p_dist = []
p_ttime = []
s_dist = []
s_ttime = []
e_lat,e_lon,e_dep = 0,0,0
for phase in catalog:
    line = phase.split()
    if line[0] == "#":
        e_lat = float(line[7])
        e_lon = float(line[8])
        e_dep = float(line[9])
    else:
        sta = line[0]
        t_time = float(line[1])
        p_type = line[-1]
        s_lat = stations[sta][0]
        s_lon = stations[sta][1]
        s_dep = stations[sta][2]
        dist = distance(e_lat,s_lat,e_lon,s_lon,e_dep,s_dep)
        if p_type == "P":
            p_dist.append(dist)
            p_ttime.append(t_time)
        else:
            s_dist.append(dist)
            s_ttime.append(t_time)
            
p_fit = scipy.optimize.curve_fit(p_func,p_dist,p_ttime)[0]
p_a = p_fit[0]
p_b = p_fit[1]
p_x = []
p_y = []
for i in range(0,700,10):
    p_x.append(i)
    p_y.append(p_func(i, p_a, p_b, p_c))
p_y1 = []
p_y2 = []
for i in p_y:
    p_y1.append(i+pd1)
    p_y2.append(i-pd2)

s_fit = scipy.optimize.curve_fit(s_func,s_dist,s_ttime)[0]
s_a = s_fit[0]
s_b = s_fit[1]
s_x = []
s_y = []
for i in range(0,700,10):
    s_x.append(i)
    s_y.append(s_func(i, s_a, s_b))
s_y1 = []
s_y2 = []
for i in s_y:
    s_y1.append(i+sd1)
    s_y2.append(i-sd2)

plt.figure(3)
plt.xlabel("distance")
plt.ylabel("travel time")
plt.scatter(p_dist,p_ttime,s=1,c="b",alpha=1)
plt.plot(p_x,p_y,c = "orange")
plt.plot(p_x,p_y1,c = "orange")
plt.plot(p_x,p_y2,c = "orange")
plt.text(0, max(p_ttime),str(len(p_dist)))

plt.figure(4)
plt.xlabel("distance")
plt.ylabel("travel time")
plt.scatter(s_dist,s_ttime,s=1,c="r",alpha=1)
plt.plot(s_x,s_y,c = "orange")
plt.plot(s_x,s_y1,c = "orange")
plt.plot(s_x,s_y2,c = "orange")
plt.text(0, max(s_ttime),str(len(s_dist)))
## 绘制筛选后的走时曲线
plt.show()
## 将筛选后的震相写入文件
with open(sel_file, "w") as f:
    for i in catalog:
        f.writelines(i)