from enum import EnumMeta
import json
import asyncio
from os import write
import re
import ephem
# from asyncio import asyncio, sleep
from random import randint, sample, shuffle
from datetime import datetime, timedelta
from time import sleep, time, gmtime, strftime


# from public.web import one_day


async def get_random_passw():
    value = sample("1234567890", 4)
    while value[0] == '0':
        shuffle(value)
    return int(''.join(value))


def td_min(minutes):
    return timedelta(minutes=minutes)


def math_min(prec=1):
    return


def point_to_int(point):
    res = point.split(':')
    return int(res[0])*60+int(res[1])


def point_to_str(point):
    # #print(datetime.fromtimestamp(point))
    # if isinstance(point,str):

    # #print(point)
    hour = datetime.fromtimestamp(point).hour
    minute = datetime.fromtimestamp(point).minute
    # return hour*60 + minute
    return datetime.fromtimestamp(point).strftime("%H:%M")
    # return f"{hour}:{minute}"


def this_spec(spec):
    return spec


def int_to_bin(lst):
    result = ''
    for i, intt in enumerate(lst):
        # #print(type(intt))
        intt = int(intt)
        ret = "{0:b}".format(intt)
        if len(ret) == 1 and i < 3:
            ret = '0'+ret
        result += ret

    return result[::-1]


def time_to_int(time):
    time = time.split(':')
    hh = int(time[0])
    # #print(time)
    mm = int(time[1])
    result = hh*60+mm  # -720

    # #print(result)
    if result < 720:
        result += 720
    else:
        result -= 720
    return result


def convert_graf_to_byte(graf, lvl, relay):
    result = b''
    # #print(lvl)
    for day, line in enumerate(graf):
        for num, point in enumerate(line):
            ##print(point, lvl[day][num])
            pnt = [3, 3, 3, 1, 1]
            #lvl = bytes([int(int_to_bin(pnt), 2)])
            # #print(point)
            point = time_to_int(point)  # point_to_int(point)
            # #print(point)
            result += point.to_bytes(2, byteorder='little')  # +lvl+lvl+lvl+lvl  # + b'\xff\xff'
            for l in lvl[day][num]:
                ##print(bytes([int(int_to_bin(l), 2)]))
                result += bytes([int(int_to_bin(l), 2)])
                ##print(bytes([int(int_to_bin(l), 2)]))
            # if len(line) != num+1:
            #    result += b'\xff'
            # else:
            #    result += '\r\n'
        result += b'\xff\xff'
    # #print(graf)
    cs = 0
    for cc in result:
        cs += cc

    #print(cs.to_bytes(4, byteorder='little'))
    result += cs.to_bytes(4, byteorder='little')
    result += b'\x0a\x0d'
    footer = f"""Ekb_001_{datetime.now().strftime("%d.%m.%y")}""".encode("cp1251") + b'\x55\xaa'
    return result+footer


def list_to_int(lst, fn):
    return [fn(nn) for nn in lst]


def time_exe(time, last):

    res = time_to_int(last.strftime("%H:%M"))-time_to_int(time.strftime("%H:%M"))
    return res


async def grafik_generator(settings, citys):
    #print('gen graf')

    #delta_start = td_min(20)
    #delta_end = td_min(0)
    city = ephem.Observer()
    sun = ephem.Sun()
    #fixed = settings['fixed']
    latlon = settings['city']
    if ',' in latlon:
        coord = latlon.split(',')
        # city.elevation = 10000
        utc = int(settings['utc'])
    else:
        coord = [(cit['lat'], cit['lon'], cit['alt'], cit['utc']) for cit in citys if cit['city'].lower() == latlon.lower()][0]
        utc = int(coord[3])

    city.lat = coord[0]  # "44.5888"  # self.linelat.text(), 33.5224
    city.lon = coord[1]  # "33.5224"  # self.linelon.text()
    city.pressure = 0
    angle = 0
    city.elevation = 72
    graf_file = []
    level_fl = []
    relay_fl = []

    hours = timedelta(hours=utc)
    Oday = timedelta(1)
    null_delta = timedelta(0)
    # #print(null_delta+hours*5)
    start = datetime.strptime("1-1-2020", "%d-%m-%Y")
    end = datetime.strptime("3-1-2020", "%d-%m-%Y")
    end = start+timedelta(366)
    date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days)]
    null_summ = 0
    end_summ = datetime.strptime("1-1-1970", "%d-%m-%Y")
    all_msg = ''

    ############
    scheme = settings['scheme']  # ['ligth']
    days = settings['bday']
    city.horizon = str(angle)

    astro = True
    last_sunup = False
    last_sundown = False
    for i, dates in enumerate(date_generated):

        st = int(settings['start'])
        num_day = i-st
        city.date = dates
        #city.horizon = str(-angle)

        ###################################
        try:
            sunup = city.next_rising(sun).datetime() + hours
            if not i:
                last_sunup = city.previous_rising(sun).datetime() + hours
        except ephem.AlwaysUpError:
            print("Солнце не зайдет" + str(sunup))
        except ephem.NeverUpError:
            print("Солнце не зайдет" + str(sunup))

        try:
            sundown = city.next_setting(sun).datetime() + hours
            if not i:
                last_sundown = city.previous_setting(sun).datetime() + hours
        except ephem.AlwaysUpError:
            print("Солнце не заходило sndwn")
        except ephem.NeverUpError:
            print("Солнце не зайдет snudown")
            #######################################
            # if last_sunup:
        if astro:
            astronom = (time_exe(sunup, last_sunup), time_exe(sundown, last_sundown))
        else:
            astronom = 0

        ##############################
        d = [(dd['time'], dd['day'], dd['scheme']) for dd in days if i+1 >= dd['day'] and i+1 <= dd['day']+dd['days']]
        # #print(d)
        sche = [dd['scheme'] for dd in days if i+1 >= dd['day'] and i+1 <= dd['day']+dd['days']]
        if len(d):

            if not i+1 == d[-1][1]:
                line = [ln for ln in d[-1][0]]
                line[0] = int_to_time(round_min(time_to_int(line[0])+astronom[0]))  # int_to_time()
                if time_to_int(line[0]) > time_to_int(line[1]):
                    line[0] = line[1]

                line[-1] = int_to_time(round_min(time_to_int(line[-1])+astronom[1]))
                if time_to_int(line[-2]) > time_to_int(line[-1]):
                    line[-1] = line[-2]

            else:
                last_sunup = sunup
                line = d[-1][0]

            graf_file.append(line)
            #print(astronom, i+1, d[-1][1], line)
            level_fl.append(scheme[d[-1][2]-1]['ligth'])

            continue

        tab = "\t"
        ephm = False

        period = sunup-sundown
        if sundown > sunup:
            period = period+Oday

        # if last_sunup:
            ##print(period, (last_sunup-period).seconds)
            ##print(time_exe(sunup, last_sunup))

          # period

        # NEW GEN ######################

        period = period.seconds//60

        period = period//100
        lvl = []
        day = []
        correct = settings['correct']  # [15, 59.5, 0, 0, 30, 0]

        roun = int(settings['round'])
        point = round_min(sundown.timestamp()/60, roun)
        # day.append(sunup.strftime("%d/%m"))
        # day.append(sunup-sundown)
        len_auto = len(scheme[0]['ligth'][0][0])
        # #print(scheme)
        for rn in range(len_auto):
            if rn:
                corr = round_min(correct[rn]*period)
                # #print(corr)
            else:
                corr = correct[rn]
            point += corr  # round_min(sundown.timestamp()/60+corr, 5)*60
            day.append(point_to_str(point*60))
            lvl.append('00000000')
            # day.append(corr)
        point = round_min(sunup.timestamp()/60+correct[5], roun)*60
        day.append(point_to_str(point))
        lvl.append('00000000')
        # RELAY
        # day.append(sundown.strftime("%H:%M"))  # datetime.fromtimestamp(point).strftime("%H:%M")
        # day.append(sunup.strftime("%H:%M"))
        # day.append(sundown.strftime("%H:%M"))
        # day.append(sunup.strftime("%H:%M"))
        ################
        # for cr in range(1):
        # settings['start'] = 2
        step = int(settings['step'])
        # #print(i)+settings['start']
        if not num_day % step:
            for ni in range(step):
                if i+ni < 366:
                    graf_file.append(day)
                    level_fl.append(lvl)
                    # if i in range(295, 316):
                    #    #print(i+1, '#', day, period)
        elif i < st:
            #print('add', i)
            graf_file.append(day)
            level_fl.append(lvl)
            # if i in range(295, 316):
            #    #print(i+1, '#', day, period)
        # elif num_day < sredne:
        #    graf_file.append(day)

        # elif i <= sredne:
        #    graf_file.append(day)
            # graf_file.append(day)
        # continue
    # for n, gr in enumerate(graf_file[:45]):  # graf_file[301:315]:
    #    #print(n+1, gr)
    # #print('#######################################', len(graf_file))  # 0ff 0ff
   # for l, gr in enumerate(graf_file[299:315]):  # graf_file[301:315]:
   ##     line = ''
    #    for i, nl in enumerate(gr):
    #        line += f"{nl.to_bytes(2, byteorder='little')} {level_fl[l][i]} "
    #    #print(line)
    # #print(level_fl)
    return graf_file, level_fl  # True
    #################################
    # null_summ+=(sundown.timetuple().tm_hour*60)+sundown.timetuple().tm_min
    # #print((sundown.timetuple().tm_hour*60)+sundown.timetuple().tm_min)
    # #print("Summ",null_summ)
"""
            end_summ += timedelta(minutes=sunup.timetuple().tm_min, hours=sunup.timetuple().tm_hour)
            ##########################################
            # #print(msg.split(tab))
            graf_file.append(msg.split(tab))
            all_msg += msg+"\r\n"

    all_msg += end_summ.strftime("%H:%M")+"\r\n"+(tab*8)+"\r\n"
    all_msg += 'Ekb_001_'+datetime.now().strftime("%d.%m.%y")+'\r\n'  # "Sim_"+strftime('%d%m',gmtime(time()))#+datetime.now().strftime("%d.%m.%y")
    all_msg += "Любые коментарии текст\r\n"
    all_msg += "55aa"
"""
# #print(null_summ)
# #print(null_summ%1440)
# #print(null_summ%3600)
# #print(end_summ)
# jf = Path("//pr-332-02/DATA/grafic.txt")
# jf.write_text(all_msg)
# with open('/home/pi/hi/public/file/'+settings+'.txt', 'w+') as fp:  # strftime('%d%m%H%M%S',gmtime(time()))+'.txt'
# with open(settings+'.txt', 'w+') as fp:
#    fp.write(all_msg)

#[b'\x00\x00', b'', b'\x01\x00', b'', b'\x02\x00\x00\x00\x00\x00s\x01\xc0\xca\xfb\xffu\x01\xaa\xaa\xaa\xaaw\x01\x00\x01\x10"y\x01\x00\x00\x00\x00', b'']


def split_days(bt):  # ff ff 65535
    # bt[0]
    # bt[1]
    # bt[2]
    # bt[3]
    # bt[4]
    # bt[5]
    # print(bt)
    length = 0
    result = []
    #print(len(bt), "BTTTTTTTTTTTTTTTTTTTTTT", bt)

    ################
    z = 0
    for i in range(0, len(bt), 6):
        if int.from_bytes(bt[i: i+2], 'little') == 65535:
            print('end~')
            length = i+2
            break
        #print(i, i+1, bt[i: i+2], int.from_bytes(bt[i: i+2], 'little'))
        z += 1
    # bt[6]  # if 65535
    # print(length)
    for i in range(0, len(bt), length):
        if len(result) == 366:
            result.append(bt[i:])
            break
        else:
            result.append(bt[i:i+length-2])
    else:
        result.append(b'')
    #print(f"RESULT!!!!!!!!!!!!!!!! {len(result)}")

    return result


def file_to_array(line):
    #num_point = int(len(line)/6)
    day = []
    lvl = []
    last_i = 0
    for i in range(6, len(line)+6, 6):
        point = line[last_i:i]
        # #print(i)
        bbb = int.from_bytes(point[:2], 'little')
        ##print(int_to_time(bbb), byte_to_array(point[2]), byte_to_array(point[3]), byte_to_array(point[4]), byte_to_array(point[5]))
        day.append(int_to_time(bbb))
        lvl.append([byte_to_array(point[2]), byte_to_array(point[3]), byte_to_array(point[4]), byte_to_array(point[5])])
        last_i = i
    return day, lvl


def int_to_time(integer):
    if integer < 720:
        integer += 720
    else:
        integer -= 720
    ##################
    hour = integer//60
    if hour < 10:
        hour = "0"+str(hour)
    minute = integer % 60
    if minute < 10:
        minute = "0"+str(minute)
    return f'{hour}:{minute}'


def byte_to_array(byt):
    byt = "{0:b}".format(byt)
    while len(byt) < 8:
        byt += '0'

    return [
        int(byt[0: 2], 2),
        int(byt[2: 4], 2),
        int(byt[4: 6], 2),
        int(byt[6]),
        int(byt[7])
    ]


def round_min(minute, prec=5):
    if not prec:
        return minute
    if minute % prec:
        roun = round(minute % prec/5)*prec
        minute -= minute % prec
        minute += roun
    # if minute == 60:
    #    minute = 55
    return minute


async def getLog(levelname, ip='', lines=500):
    with open("log.json", 'r') as afp:
        jsn_log = afp.read()
        jsn_log = jsn_log.splitlines()
        # #print(jsn_log)
        lng = len(jsn_log)
        return_log = []
        if lng-lines < 0:
            lng = 0
        else:
            lng -= lines

        for lg in jsn_log[lng:]:
            lg = json.loads(lg)
            if lg['levelname'] in levelname and lg['type'] in levelname and ip in lg['ip']:
                return_log.append(lg)
        # #print(jsn_log)
        # if lng < 500:
        #    for each in range(0, lng):
        #        return_log.append(json.loads(jsn_log[each]))
        # else:
        #    for each in range(lng-500, lng):
        #        return_log.append(json.loads(jsn_log[each]))
        # #print(return_log)
        # for ln in return_log:
            # #print(ln)
        return return_log

if __name__ == '__main__':
    print(hex(2)[2:])
