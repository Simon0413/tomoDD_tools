## ph2dt.py v1.0
## HypoDD或TomoDD中ph2dt程序的替代程序
## 暂时未考虑事件的最大震相数量和最大邻居数量,因此等效于ph2dt程序中MAXOBS和MAXNGH设置为无穷大
## 该程序已经对event.sel进行了补零，因此在下一步中无需运行addEve0.awk
import math
####################################################################
station_file = "station.dat"
'''
C.KCD01 	30.9612	103.9179	0588
C.KCD02 	30.9098	103.7578	0629
C.KCD03 	30.7189	103.8503	0536
C.KCD04 	30.5746	103.5190	0526
'''
####################################################################
phase_file = "phase.dat.sel" 
'''
# 2006 10 09 20 39 13.00 30.07 102.5 2 1.4 0 0 0 20061009203913
C.KKD04 	9.83420 	1 	P
C.KKD04 	15.8642 	1 	S
# 2006 10 10 07 49 47.00 29.87 101.88 5 1.3 0 0 0 20061010074947
C.KKD03 	7.38000 	1 	P
C.KKD03 	11.4500 	1 	S
# 2006 10 12 03 06 57.00 27.85 102.03 4 1.4 0 0 0 20061012030657
C.KKD05 	39.7600 	1 	P
# 2006 10 12 17 47 02.00 29.47 103.35 5 2 0 0 0 20061012174702
C.KDB07 	35.7000 	1 	P
C.KKD02 	58.6920 	1 	S
C.KKD03 	39.4900 	1 	S
C.KKD06 	31.8693 	1 	P
C.KKD06 	53.1193 	1 	S
'''
####################################################################
MINWGHT = 0 ## 震相数据最小拾取质量
MAXDIST = 800 ## 事件对于台站之间的最大距离
MINSEP = 0.10 ## 事件对之间的最小间距
MAXSEP = 30 ## 事件对之间的最大间距
## MAXNGH = 30 ## 每个事件的最大邻居数(该参数暂未使用)
MINLNK = 8 ## 一个事件如果能成为另一个事件的邻居，那么该事件对需要的相同震相个数
MINOBS = 8 ## 每一个事件对所需要的震相数的最小值
## MAXOBS = 120 ## 每一个事件对所需要的震相数的最大值（该参数暂未使用）
#####################################################################

## 计算事件与事件、事件与台站之间的位置
## position_n = [lat, lon, dep]
def distance(position_1, position_2):
    kmperdeg = 111.1949266
    lat1, lat2 = position_1[0], position_2[0]
    lon1, lon2 = position_1[1], position_2[1]
    dep1, dep2 = position_1[2], position_2[2]
    dlat = lat1-lat2
    dlon = lon1-lon2
    ddep = dep1-dep2
    dist = math.sqrt((dlat*kmperdeg)**2+(dlon*(math.cos(lat1*3.1415926/180)*kmperdeg))**2+ddep**2)
    return dist

## 读取台站文件
## {'XJI': [31.0, 102.4, 0.0]}
stations = {}
n = 0
with open(station_file, "r") as f:
    lines = f.readlines()
    for line in lines:
        n += 1
        line = line.split()
        key = line[0]
        value = [float(line[1]), float(line[2]), -float(line[3])/1000]
        stations[key] = value
print(f"stations:{n}")

## 读取震相文件
events = [] ## 存放事件编号，用于后面遍历
## ['620002','620003','620004','620005','620006','620007']
events_info = {} ## 存放事件信息，事件、经纬度等
## {'620002': ['2001','1','1','16','2','43.60','29.220','101.070','9.0','0','0','0','0']
phase = {} ## 存放震相信息，用事件编号索引
## {'620002': [['MDS', '35.82', '1', 'P'],['MEK', '49.19', '1', 'P']]}
key = "event"
pha = [["phase"],[]]
n1 = 0
n2 = 0
with open(phase_file, "r") as f:
    lines = f.readlines()
    for line in lines:
        line = line.split()
        if line[0] == "#":
            n1 += 1
            phase[key] = pha
            pha = []
            key = line[-1]
            value = line[1:-1]
            events.append(key)
            events_info[key] = value
        else:
            n2 += 1
            pha.append(line)
    phase[key] = pha
    phase.pop('event')
print(f"events:{n1}  phase:{n2}")

## 删除震中距大于MAXDIST的震相
## 筛选权重大于MINWGHT的震相
for event in events:
    event_position = list(map(float,events_info[event][6:9]))
    phas = phase[event]
    for pha in phas:
        sta_name = pha[0]
        sta_position = stations[sta_name]
        dist = distance(event_position,sta_position)
        if dist >= MAXDIST and pha[2] <= MINWGHT:
            phase[event].remove(pha)
            
## 生成event.dat
## 筛选震相数大于MINOBS的事件
## 生成event.sel
## 生成absolute.dat
event_dat = []
event_sel = []
absolute = {}
for event in events:
    date = events_info[event][0]+events_info[event][1].zfill(2)+events_info[event][2].zfill(2)
    time = events_info[event][3].zfill(2)+events_info[event][4].zfill(2)+events_info[event][5].split(".")[0].zfill(2)+events_info[event][5].split(".")[1].zfill(2)
    lat = str(format(float(events_info[event][6]),".4f"))
    lon = str(format(float(events_info[event][7]),".4f"))
    dep = str(format(float(events_info[event][8]),".3f"))
    mag = str(format(float(events_info[event][9]),".1f"))
    EH = str(format(float(events_info[event][10]),".2f"))
    EV = str(format(float(events_info[event][11]),".2f"))
    RMS = str(format(float(events_info[event][12]),".2f"))
    item = f"{date}\t{time}\t{lat}\t{lon}\t{dep}\t{mag}\t{EH}\t{EV}\t{RMS}\t{event}\n"
    event_dat.append(item)
    if len(phase[event]) >= MINOBS:
        item = f"{date}\t{time}\t{lat}\t{lon}\t{dep}\t{mag}\t{EH}\t{EV}\t{RMS}\t{event}\t0\n"
        event_sel.append(item)
        absolute[event] = phase[event]

## 写入文件
## 写入event.dat
with open("event.dat", "w") as f:
    for i in event_dat:
        f.writelines(i)
## 写入event.sel
with open("event.sel", "w") as f:
    for i in event_sel:
        f.writelines(i)
## 写入absolute.dat
with open("absolute.dat", "w") as f:
    for i in absolute.keys():
        f.writelines(f"#\t\t\t{i}\n")
        for j in absolute[i]:
            sta = j[0]
            ttime = str(format(float(j[1]),".2f"))
            weight = str(format(float(j[2]),".2f"))
            type = j[3]
            f.writelines(f"{sta}\t\t{ttime}\t\t{weight}\t\t{type}\n")
            
## 更新事件目录
events = []
for i in event_sel:
    events.append(i.split()[-2])
    
## 计算震相对，生成dt.ct文件
dtct = {} ## key = event1,value = event_pair
## event_pair = {} ## key = event2,value = [common phase]
for index in range(len(events)-1):
    event_pair = {} ## key = event2,value = [common phase]
    event1 = events[index]
    print(event1)
    event1_position = list(map(float,events_info[event1][6:9]))
    event1_phase = phase[event1]
    for event2 in events[index+1:]:
        event2_position = list(map(float,events_info[event2][6:9]))
        event2_phase = phase[event2]
        dist = distance(event1_position,event2_position)
        if MINSEP <= dist <= MAXSEP:
            common = []
            for pha1 in event1_phase:
                for pha2 in event2_phase:
                    if pha1[0] == pha2[0] and pha1[-1] == pha2[-1]:
                        t1 = str(format(float(pha1[1]),".4f"))
                        t2 = str(format(float(pha2[1]),".4f"))
                        weight = str(format((float(pha1[2])+float(pha2[2]))/2,".3f"))
                        item = f"{pha1[0]}\t\t{t1}\t\t{t2}\t\t{weight}\t\t{pha1[-1]}\n"
                        common.append(item)
            if len(common) >= MINOBS :
                event_pair[str(format(dist,".4f"))+" "+event2] = common
    if len(event_pair) != 0:
        dtct[event1] = event_pair
        
## 写入文件
with open("dt.ct", "w") as f:
    for i in dtct.keys():
        for j in dtct[i].keys():
            f.writelines(f"#\t\t\t{i}\t\t\t{j.split()[1]}\n")
            for k in dtct[i][j]:
                f.writelines(k)   