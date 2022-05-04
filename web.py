################
#import di
################

from ast import While
import pickle
import json
import struct
import time
from aioinflux import InfluxDBClient, iterpoints
import webbrowser
import sys
from asyncio.streams import start_server
from aiologger.formatters.json import FUNCTION_NAME_FIELDNAME, LOGGED_AT_FIELDNAME
from aiologger.loggers.json import JsonLogger
import copy
from os import urandom
import asyncio
import random
import string
from datetime import datetime, timedelta
from aiofile import async_open
from pythonjsonlogger import jsonlogger
from urllib3 import Timeout
from null import null_dev, null_company, null_user
import logging.handlers
import logging
import multiprocessing
import os
import pathlib
from helpers import get_random_passw, grafik_generator, convert_graf_to_byte, file_to_array, split_days
import re
import decors as dc
from decors import ws_command_list, tcp_funct_list
import requests
from aiohttp.client import request
from distutils import command
from aiohttp import web
from typing import Union
from random import randrange
import socket
from socket import EAGAIN, timeout

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '5167869943:AAFgJkC5HoMLN3Ew65tXLXxJ_YAr7DDAxB0'

# Configure logging
# logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['clear'])  # 'start', 'help',
async def send_welcome(message: types.Message):
    if message.reply_to_message is not None:
        who = message.reply_to_message.text.splitlines()[0]
        login = who.split(':')[0]
        """
        This handler will be called when user sends `/start` or `/help` command
        """
        if login in chat:
            print(login, 'in', chat)
            chat.pop(login)
            print(login, 'in', chat)
            await send_ws_all({'support': []}, user=login)
            await message.reply(f"Clear chat {login}")
        else:
            await message.reply(f"No open chat {login}")
    else:
        await message.delete()


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    if message.reply_to_message is not None:
        who = message.reply_to_message.text.splitlines()[0]
        login = who.split(':')[0]
        print(login, message.text)
        msg = {'text': message.text, 'new': True,
               'ts': time.time()*1000, 'support': True}

        if login in chat:
            chat[login].append(msg)
        else:
            chat.update({login: [msg]})

        await send_ws_all({'support': msg}, user=login)
    else:
        await message.delete()
    # await message.answer(message.text)


# import tcp
## LOGS ##


##########
###########
start_time = time.time()


def get_up_time():
    return int(time.time()-start_time)


root_path = str(pathlib.Path(__file__).parent)+'/'
# print(root_path)


# import decors as dc DEBUG < INFO < WARNING < ERROR < CRITICAL

queue_tcp = {'horizont': {'98': {'time': 123123,
                                 'msg': [b'\xff', b'\xff', b'\xff'], 'retry': 1}}}
queue_tcp = {'horizont': {}}


def sb(sb='00'):
    return bytes.fromhex(sb)


def bi(*args):
    a = []
    for b in args:
        a.append(int(b, 16))
    return a


def ih(b):
    return hex(b)[2:].upper()


async def send_tcp(ID, data, login=False, now=True, wait=2, all=True):
    print(data, get_up_time())
    nnow = get_up_time()
    if ID in tcp_sess:
        if now:
            tcp_sess[ID].write(data)
            log.info(f">>now>>\n{byte_to_string(data)}", extra={'type': 'TCP', 'host': str(ID)})
            await tcp_sess[ID].drain()

        if wait:
            que = queue_tcp['horizont'].get(ID, False)
            if que:
                que['time'] = nnow+wait
                que['msg'].append(data)
            else:
                queue_tcp['horizont'][ID] = {'time': nnow+wait, 'msg': [data], 'user': login, 'retry': 1}

        print('tcp quuee', queue_tcp)
        answer = {'new': {ID: {'load': True}}}
        answer.update(notif_wss(ID, 'запрос отправлен', 'success'))
        return answer
    else:
        # await
        answ = notif_wss(ID, 'нет соединения', 'error')
        answ.update({'new': {ID: {'load': False}}})
        return answ

design = {
    "dark": False,
    "status": {
        "normal": "green-300",
        "fire": "red-400",
        "emergency": "orange-500",
        "security": "yellow-400",
        "hands": "pink-300",
        "offline": "gray-500"
    }}


def without_keys_group(dc, *args):
    new_dc = {}
    for ndc in dc:
        new_dc[ndc] = {x: dc[ndc][x] for x in dc[ndc] if x not in args}
    return new_dc


def without_keys(dc, *args):
    return {x: dc[x] for x in dc if x not in args}


async def ws_idd(ID):
    login = user_sess[ID]['name']
    des = users[user_sess[ID]['name']].get('design', False)
    pg = users[user_sess[ID]['name']].get('pages', False)
    if not pg:
        pg = []
    if not des:
        des = design
    answer = {
        'design': des,
        'support': chat.get(login, []),
        'priv': privileges,
        'pages': pg,
        'device': incoming,
        'city': city,
        'sessions': without_keys_group(user_sess, 'ws'),
        # 'log': await getLog(),
        'events': events,
        'sett': settings,
        'company': company,
        # 'graf': json.loads(graf),
        'files': company['horizont']['files'],
        'firmware': await get_files(),
        'profile': without_keys(users[user_sess[ID]['name']], 'passw', 'salt', '2fa'),
        'users': without_keys_group(users, 'passw', 'salt', '2fa'),
        'time': int(datetime.now().strftime("%s"))
    }
    return answer


# @dc.ws_api('id')
async def ws_id(ID, info):
    if ID in user_sess:
        des = users[user_sess[ID]['name']].get('design', False)
        pg = users[user_sess[ID]['name']].get('pages', False)
        if not pg:
            pg = []
        if not des:
            des = design
        answer = {
            'priv': privileges,
            'design': des,
            'pages': pg,
            'device': incoming,
            'city': city,
            'log': await getLog(),
            'events': events,
            'sett': settings,
            'company': company,
            # 'graf': json.loads(graf),
            'files': await get_files(),
            'profile': users[user_sess[ID]['name']],
            'users': without_keys_group(users, 'passw', 'salt', '2fa'),
            'time': int(datetime.now().strftime("%s"))
        }
        return answer
    else:
        answer = {}
        return answer
# @dc.ws_api('id')


@ dc.ws_api('test')
async def test_ui(ans, ID, info):
    print('########TEST########')
    answer = {}  # {'user_sess': without_keys_group(user_sess, 'ws')}
    print(info)
    if info in user_sess:
        print('session off', info)
        user_sess[info]['time'] = 0
        answer.update({'sessions': without_keys_group(user_sess, 'ws')})
    # print(json.dumps(user_sess, indent=2))
    # for us, itm in user_sess.items():
    #    print(us, itm)

    pending = asyncio.all_tasks()
    for i, task in enumerate(pending):
        # task.cancel()
        print(i+1, task)
    # print([usr['ws'] for tk, usr in user_sess.items() if usr['company'] == 'horizont'] and)
    await send_ws_all({'test': 'test'}, user='admin')
    print('####################')
    return answer


@ dc.ws_api('download')
async def ws_download(ans, ID, info):
    answer = {}
    print(info)
    if '.grf' in info:
        file_d = company['horizont']['files'][info]
        # await read_bin(upload_file[str(obj[2])]['name'], upload_file[str(obj[2])]['slice'])
        fl = convert_graf_to_byte(file_d['data'], file_d['level'], '')
        async with async_open(f"{root_path}file/deleted/{info}", 'wb') as afp:
            await afp.write(fl)

        answer.update({'download': f'{info}'})
    # answer.update(notif_wss('', 'UI RELOADS', 'info'))
    # await send_ws_all({'reload': True})
    return answer


@ dc.ws_api('task')
async def ws_task(ans, ID, info):
    answer = {}
    answer.update(notif_wss('', 'UI RELOADS', 'info'))
    await send_ws_all({'reload': True})
    return answer


@ dc.ws_api('reload')
async def reload_ui(ans, ID, info):
    answer = {}
    answer.update(notif_wss('', 'UI RELOADS', 'info'))
    await send_ws_all({'reload': True})
    return answer


@ dc.ws_api('logout')
async def ws_logout(ans, ID, info):
    answer = {"auth": None}
    user_sess.pop(ID)
    return answer


@ dc.ws_api('device')
async def ws_dev(ans, ID, info, company='fff'):
    answer = {}
    for dev, data in info.items():
        devc = incoming.get(dev)
        if data:
            if devc:  # обновление
                incoming[dev].update(data)
            elif devc is None:  # создание
                incoming[dev] = copy.deepcopy(null_dev)
                incoming[dev].update(data)
        elif devc is not None:  # удаление
            incoming.pop(dev)
        else:
            await notif_ws(dev, 'нету такого адреса', 'warning')

    #    'chart': await get_chart(info[0], info[1])
    # }
    # await send_ws_all()
    await send_ws_all({'device': incoming}, 'horizont')
    # answer.update({'device': incoming})
    return answer


@ dc.ws_api('chart')
async def ws_chart(ans, ID, info):
    answer = {
        'chart': await get_chart(info[0], info[1])
    }
    return answer


@ dc.ws_api('profile')
async def ws_profile(ans, ID, info):
    answer = {}
    user = user_sess[ID]['name']
    # print(user, info, users[user])
    users[user].update(info)
    answer = {
        'profile': without_keys(users[user], 'passw', 'salt', '2fa'),
    }
    answer.update(notif_wss('', 'профиль обновлен', 'success'))
    return answer


@ dc.ws_api('user')
async def ws_user(ans, ID, info):
    text = ''
    for login, data in info.items():
        if login in users:  # есть компания
            if data:  # update
                text = 'сохранение пользователя '+login
                users[login].update(data)
            else:  # delete
                text = 'удаление пользователя '+login
                users.pop(login)
        elif data:  # создаем компанию
            text = 'создал пользователя '+login
            users[login] = copy.deepcopy(null_user)
            users[login].update(data)
        else:
            text = 'такой пользователя нет'
    # users.update(info)
    answer = {
        'users': without_keys_group(users, 'passw', 'salt', '2fa'),
    }
    answer.update(notif_wss(login, text, 'success'))
    return answer


@ dc.ws_api('company')
async def ws_user(ans, ID, info):
    text = ''
    for comp, data in info.items():
        if comp in company:  # есть компания
            if data:  # update
                text = 'сохранение компании '
                company[comp].update(data)
            else:  # delete
                text = 'удаление компании'
                company.pop(comp)
        elif data:  # создаем компанию
            text = 'создал компанию '
            company[comp] = copy.deepcopy(null_company)
            company[comp].update(data)
        else:
            text = 'такой компании нет'

    answer = {
        'company': company
    }
    answer.update(notif_wss(comp, text, 'success'))
    return answer


@ dc.ws_api('news')
async def ws_news(ans, ID, info):
    text = ''
    answer = {}
    for date, delete in info.items():
        if date in news:
            if not delete:
                news.pop(date)
                # answer.update({'news': news})
                answer.update(notif_wss('удалил', 'новость', 'success'))
                break
    else:
        now = int(time.time())
        news[str(now)] = info
        answer.update(notif_wss('добавил', 'новость', 'success'))
        await send_ws_all({'news': {now: info}})
    return answer


@ dc.ws_api('km')
async def data_km(ans, ID, data):
    answer = {}
    # print(ID, data)
    msg = msg_str_q(3, 0, int(data))  # hex 15
    answer.update(await send_tcp(data, msg))
    # res = await grafik_generator(data)
    # if res:
    #    answer = {'files': await get_files()}
    #    answer.update(notif_wss(ID, 'text', 'gray'))
    return answer


@ dc.ws_api('ip')
async def data_ip_ws(ans, ID, data):
    answer = {}
    # print(ID, data)
    msg = msg_str_q(1, 0, int(data))  # hex 15
    await send_tcp(data, msg)
    # msg = msg_str_q(21, 0, int(data), "03:1b:1b:1b")  # hex 15
    # await send_tcp(data, msg)
    # res = await grafik_generator(data)
    # if res:
    #    answer = {'files': await get_files()}
    # answer.update(notif_wss(ID, 'text', 'orange'))
    return answer


@ dc.ws_api('gen')
async def ws_gen(ans, ID, data):
    fl, level = await grafik_generator(data, city)
    if level:
        answer = {'files': company['horizont']['files']}
        answer.update(notif_wss('график', 'сгенерирован', 'success'))
        answer.update({'generator': fl, 'level': level})
        return answer


@ dc.ws_api('hex')
async def ws_hex(ans, ID, data):

    for dev_n in data:
        msg = b''

        byte = data[dev_n]
        if len(byte) <= 4:
            return {}
        byte = byte.replace('\n', '')
        byte = byte.split(' ')
        # print(byte)
        for bb in byte:
            try:
                msg += bytes.fromhex(bb)
            except:
                text = 'неправильный формат сообщения'
                color = 'yellow'
                continue
    # print('split bytes',msg)
        Nbt = len(msg)+1
        msg = bytearray(msg)
        # msg[1] = Nbt
        # длины пакета, команды, адреса, информации и CRC
        summ = struct.unpack('>'+str(len(msg))+'B', msg)
        cs = 0
        for each in summ:
            cs += each
        cs = struct.pack('<i', cs)
        # print("CSSSSSSSSSSSS",cs)
        if cs[0] == 0:
            cs = bytes([255])
        else:
            cs = bytes([256-cs[0]])  # CS
        msg += cs

        text = await send_tcp(dev_n, msg, wait=5)

        # for i in range(0, len(msg), 16):
        # log.info('>>>'+strr,extra={'type':'TCP','host':str(ip)})
    answer = {}
    answer = {'new': {dev_n: {'load': True}}}
    answer.update(text)
    return answer


@ dc.ws_api('auth')
async def ws_auth(ans, ID, data):
    session_time = 28800
    text = ''
    if data[0] in users:
        if data[1] == users[data[0]]['passw']:
            user = data[0]
            new_tkt = randomword(64)
            times = int(time.time())
            user_sess[new_tkt] = {'name': data[0], 'company': users[data[0]]
                                  ['company'], 'time': times+session_time}  # 'host':str(ip)800
            answer = {}
            answer.update(await ws_idd(new_tkt))
            answer.update({"auth": True,
                           "TKT": new_tkt
                           })

            # await notif_ws("","успешная авторизация на 4 часа","green")
            text = f"авторизован на {session_time//3600} часов"
        else:
            answer = {"auth": False}  # Не верный пароль
            # text = 'не верный пароль'
            log.critical(f'не верный пароль', extra={'type': 'TCP', 'host': ID})
    else:
        answer = {"auth": False}  # Нету такого пользователя
        log.critical(f'нет такого пользователя', extra={'type': 'TCP', 'host': ID})
    # await resp.send_json(msg)
    # answer = {}
    answer.update(notif_wss(data[0], text, 'success'))
    return answer


@ dc.ws_api('tkt')
async def ws_tkt(ans, ID, data):
    tkt = user_sess.get(data, False)
    # print('TKT is', tkt)
    user = ''
    answer = {}
    if tkt:
        user = user_sess[data]['name']
        answer.update({"auth": True})  # =
        answer.update(await ws_idd(ID))
        # print(resp.cookies.items())
        # text = 'востановлена прошлая сессия'
        # color = 'blue'
    else:
        answer = {"auth": None}
        text = 'сессия закрылась'
        color = 'orage'
        answer.update(notif_wss(user, text))
    return answer


@ dc.ws_api('log')
async def ws_log(ans, ID, data):
    # print(data)
    logs = await getLog(data[0], data[1], 8000)
    logs = {"log": logs}
    return logs


@ dc.ws_api('sync')
async def ws_sync(ans, ID, data):
    # log.critical("sync", extra={'type': 'TCP', 'host': user_sess[ID]['host']})
    # log.warning("sync", extra={'type': 'TCP', 'host': user_sess[ID]['host']})
    # print('send sync time')
    # sync = datetime.now()
    #########################
    tim = datetime.now()
    # tim = datetime(2021,3,31,12,37,45)
    dt_dict = [
        tim.year-2000,
        tim.month,
        tim.day,
        tim.hour,
        tim.minute,
        tim.second
    ]
    sync = ''
    for number in range(len(dt_dict)):
        dt = str(dt_dict[number])
        if len(dt) == 1:
            dt = '0'+dt
            if number == 1:
                m = int_to_bin(int(dt[1]))
                d_m = int_to_bin(int(dt[0]))[-1]
                w_m = int_to_bin(datetime.isoweekday(tim))
                m = w_m+d_m+m
                m = int(m, 2).to_bytes(1, byteorder='little')
                m = hex(m[0])[2:]
                dt = m
        sync += dt+':'
    sync = sync[:-1]
    #########################
    msg = msg_str_q(19, 0, int(data), sync)

    # await send_tcp(data, msg)

    answer = {'new': {data: {'load': True}}}
    answer.update(await send_tcp(data, msg))
    # answer.update(notif_wss(ID, 'Синхронизация времени', 'success'))
    return answer


@ dc.ws_api('comm')
async def ws_comm(ans, ID, data):
    dev_nn = data
    dev_n = dev_nn['addr']
    # log.debug("comm" +str(comm[each]),extra={'type':'TCP','host':str(ip)})
    if dev_nn['pack'] > 9:
        stringg = str(dev_nn['pack'])
        # incoming[str(dev_n)]['norm_st'] = "hands"
        # incoming[str(dev_n)]['status'] = "hands"
    elif dev_nn['pack'] == 0:
        stringg = "0"+str(dev_nn['pack'])
        # incoming[str(dev_n)]['norm_st'] = "normal"
        # incoming[str(dev_n)]['status'] = "normal"
    else:
        # incoming[str(dev_n)]['norm_st'] = "hands"
        # incoming[str(dev_n)]['status'] = "hands"
        stringg = "0"+str(dev_nn['pack'])

    msg = msg_str_q(21, 0, int(dev_n), "02:"+stringg)
    await send_tcp(dev_n, msg)
    answer = {'new': {dev_n: {'load': True}}}
    # answer.update(notif_wss(ID,'text','gray'))
    return answer

# example {'addr': '99', 'chnl': [1, 2], 'pack': 'OFF'}

"""
                    <Input type="radio" label="всем" name="zz" value={0} bind:group={curent_type} />
                    <Input type="radio" label="зав.№" name="zz" value={1} bind:group={curent_type} />
                    <Input type="radio" label="точка" name="zz" value={2} bind:group={curent_type} />
                    <Input type="radio" label="группа" name="zz" value={3} bind:group={curent_type} />

    - OFF_ALL   – Np=40    – выключить все;
    - ON+/-_ALL – Np=44    – включить все;
    - OFF_GRP   – Np=44+4g – выключить группу;
    - ON+/-_GRP – Np=46+4g – включить группу;
    - OFF_PNT   – Np=64+2p – выключить светоточку;
    - ON+/-_PNT – Np=65+2p – включить светоточку.
"""


@ dc.ws_api('addr')
async def ws_addr(ans, ID, data):
    dev_n = data['addr']
    command = data['comm']
    way = data['way']
    typ = data['type']
    off = 40

    num = data['num']
####################
    Np = f'{44:x}'
    if typ == 3:
        Np = f'{46+(4*num):x}'
    elif typ == 2:
        Np = f'{65+(2*num):x}'
####################
    if command == 'cut':
        if way == '-':
            command = '0b'
        else:
            command = '03'

        if way == 'off':
            Np = f'{40:x}'
            if typ == 3:
                Np = f'{44+(4*num):x}'
            elif typ == 2:
                Np = f'{64+(2*num):x}'

    # if way == 'up':

    bf = ['10', '12', '14']
    buf = data['buf']
    bufs = data['bufs']

    KOD = '01'
    zav = '01'
    if command == 'msg':
        past = data['past']
        command = '05'
        KOD = '0d'
        Np = num.to_bytes(3, byteorder='big').hex(':')
        zav = past.to_bytes(1, byteorder='big').hex()

        if typ == 2:
            KOD = '03'
            Np = past.to_bytes(1, byteorder='big').hex()
            zav = num.to_bytes(1, byteorder='big').hex()

        if typ == 5:
            KOD = '1d'
            Np = num.to_bytes(3, byteorder='big').hex(':')
            zav = past.to_bytes(1, byteorder='big').hex()

        if typ == 6:
            bf[buf] = "10"
            KOD = '1e'
            Np = int(f'000{int(bufs[2])}0{int(bufs[1])}0{int(bufs[0])}', 2).to_bytes(
                1, 'big').hex()
            zav = '00'

        if typ == 7:  # поиск зав
            bf[buf] = "10"
            KOD = '1f'
            Np = int(f'000{int(bufs[2])}0{int(bufs[1])}0{int(bufs[0])}', 2).to_bytes(
                1, 'big').hex()
            # Np = '11'
            zav = '00'

        #               LN BF CM KD NP NP NP ZV
# 65 0d 63 00 15 [01 ][ 05 10 05 03 01 02 		-/присвоение № g (01) по № p (02)

# 65 0f 63 00 15 [01 ][ 07 10 05 0d 00 f2 fe 05	-/присвоение № p (05) по зав.# 62206

# 65 0f 63 00 15 [01 ][ 07 10 05 15 40 f2 fe 14	-/передача упр. байта (14) типа 2 по зав.# 62206

# 65 0f 63 00 15 [01 ][ 07 10 05 1d 00 f2 fe 01	-/запрос на диагностику зав.# 62206 тип 1.

# 65 0b 63 00 15 [01 ][ 03 10 05 1e			-/запуск диагностики всех абонентов на фазе

# 65 0c 63 00 15 [01 ][ 04 10 05 1f 11		-/поиск зав. номеров на фазах A и C
    line = bf[buf]+command+KOD+Np+zav
    len_msg = len(line.replace(':', ''))//2
    # print(bf[buf]+command+KOD+Np+zav, len_msg)
    # msg = msg_str_q(21, 0, int(dev_n), f"01:05:10:{command}:01:{Np}:01") (62206).to_bytes(2, byteorder='big') # OFF ALL
    msg = msg_str_q(21, 0, int(
        dev_n), f"01:0{len_msg}:{bf[buf]}:{command}:{KOD}:{Np}:{zav}")  # ON+- ALL
    answer = await send_tcp(dev_n, msg, wait=0)
    answer.update({'new': {dev_n: {'load': True}}})

# answer.update(notif_wss(dev_n, 'text', 'gray'))
    return answer


@ dc.ws_api('keypad')
async def ws_keypad(ans, ID, data):
    # print('keypad')
    # print(type(data))
    if type(data) is str:  # старт управления через кнопки
        # print(type(data))
        msg = msg_str_q(21, 0, int(data), "03:1b:1b:1b")  # hex 15
        await send_tcp(data, msg)
    else:
        for num in data:
            # print(num, data[num])
            msg = msg_str_q(21, 0, int(num), "03:"+data[num])  # hex 15
            await send_tcp(num, msg)
            # print(msg)


@ dc.ws_api('control')
async def ws_send_control(ans, ID, data):
    dev_n = data['addr']
    packi = data['pack']
    for buf in data['chnl']:
        buf *= 2
        buf += 16
        buf = buf.to_bytes(1, 'little').hex()
        msg = msg_str_q(21, 0, int(dev_n), "01:02:"+buf+":"+packi)  # hex 15
        await send_tcp(dev_n, msg)
        await asyncio.sleep(0.3)

    ############################
    answer = {'new': {dev_n: {'load': True}}}
    answer.update(notif_wss('', 'команда отправлена', 'success'))
    return answer


chat = {}


@ dc.ws_api('support')
async def ws_support(ans, ID, data):

    login = user_sess[ID]['name']
    comp = user_sess[ID]['company']

    if isinstance(data, list):
        chat[login] = data
    else:
        if login in chat:
            chat[login].append(data)
        else:
            chat.update({login: [data]})
    # print(chat)

        msg = f"""{login}:{comp}
    {data['text']}
    """
        await bot.send_message('205377996', msg)
    # pass


@ dc.ws_api('send_conf')
async def ws_send_conf(ans, ID, data):
    login = user_sess[ID]['name']
    dev_n = data['addr']
    com = data['com']
    conf = data['cfg']
    rev = b''
    if com > 0:
        for ar in conf[:-1]:
            # print('send conf zav_num', ar['zav_num'])
            # if ar['zav_num'] is not None:  # and ar['zav_num'] != '':
            # if ar['zav_num'] is None:
            #    print('delete ligth point', ar['num_st'])
            #    ar['zav_num'] = 0

            if ar['zav_num'] is not None and ar['zav_num'] != 0:

                if ar['num_st'] == '':
                    ar['num_st'] = 0
                if ar['num_grp'] == '':
                    ar['num_grp'] = 0
                rev += ar['zav_num'].to_bytes(4, byteorder='little')
                rev += b'\x00'*2
                rev += ar['num_st'].to_bytes(1, byteorder='little')
                rev += ar['num_grp'].to_bytes(1, byteorder='little')
                rev += b'\x00'*8
            # else:

            # else:
            #    conf.pop(indx)
        rev = rev.hex()
    else:
        rev = ''
        for cf in conf:
            rev += cf

    upload_file[dev_n] = rev+str(com)
    print(upload_file[dev_n])
    # incom[dev_n]['config'] = comm[each]['cfg']
    text = 'send cfg'
    #########################
    msg = msg_str_q(27, 0, int(dev_n), '0'+str(com))
    await send_tcp(dev_n, msg, login)  # Запрос перед отправкой файла
    answer = {'new': {dev_n: {'load': True}}}
    answer.update(notif_wss('ID', text, 'gray'))
    return answer


@ dc.ws_api('save_conf')
async def ws_save_conf(ans, ID, data):
    dev_n = data['addr']
    incoming[dev_n]['config'] = data['cfg']
    print('save cfg', dev_n)
    text = 'save cfg'
    answer = {}
    answer.update(notif_wss('ID', text, 'gray'))
    return answer


@ dc.ws_api('files')
async def ws_files(ans, ID, data):
    answer = {}
    text = ''
    for name, datas in data.items():
        if name in company['horizont']['files']:
            if datas:
                company['horizont']['files'].update(data)
            else:
                company['horizont']['files'].pop(name)
        elif datas:
            # datas.update({'time': time.time()})
            company['horizont']['files'][name] = datas
            # if data:
            #    company['horizont']['files'].update()
            # dev_n = data['adr']
            # commnd = data['com']
            # msg = msg_str_q(11, 0, int(dev_n), '0'+str(commnd))
            # print('get conf >', msg)

            # await send_tcp(dev_n, msg)  # Запрос перед отправкой файла
            # answer = {'new': {dev_n: {'load': True}}}
            # answer.update(notif_wss(ID,text,'gray'))
    answer.update({
        'files': company['horizont']['files']
    })
    return answer


@ dc.ws_api('conf')
async def ws_conf(ans, ID, data):
    dev_n = data['adr']
    commnd = data['com']
    msg = msg_str_q(11, 0, int(dev_n), '0'+str(commnd))
    # print('get conf >', msg)

    answer = await send_tcp(dev_n, msg)  # Запрос перед отправкой файла

    # answer.update(notif_wss(ID,text,'gray'))
    return answer


@ dc.ws_api('sch')
async def ws_sch(ans, ID, data):
    answer = {}
    # answer.update(notif_wss(ID,'text','gray'))
    return answer


@ dc.ws_api('evnt')
async def ws_evnt(ans, ID, data):
    # print(data)
    try:
        events.pop(data)
    except:
        events.clear()
    answer = {'events': events}
    # answer.update(notif_wss(ID,'text','gray'))
    return answer

# @dc.ws_api('file')
# async def ws_file(ID, data):
color = 'green'


@ dc.ws_api('one_day')
async def one_day(ans, ID, data):

    dev_n = data[0][0]
    msg = msg_str_q(23, 0, int(dev_n))
    await send_tcp(dev_n, msg)  # Запрос перед отправкой файла
    data[0] = data[0][1]
    upload_file[str(dev_n)] = data
    text = 'график 1 дня принят'
    answer = {'new': {dev_n: {'load': True}}}
    answer.update(notif_wss('ID', text, color))
    return answer


@ dc.ws_api('rename')
async def ws_rename(ans, ID, data):
    how = data['how']
    to = data['to']
    os.rename(f"{root_path}file/{how}", f"{root_path}file/{to}")
    return notif_wss('', f"{to} save")


@ dc.ws_api('file')
async def ws_file(ans, ID, data):
    print(type(data))
    typ = isinstance(data, list)

    if isinstance(data, list):
        dev_n = data[0]
        msg = msg_str_q(23, 0, int(dev_n))
        await send_tcp(dev_n, msg)  # Запрос перед отправкой файла
        text = 'график 1 дня принят'
    elif isinstance(data, dict):
        for dev_n in data:
            exp = data[dev_n]['name'][-3:]
            if exp == 'bin':
                msg = msg_str_q(25, 0, int(dev_n))
            elif exp == 'cfg':
                msg = msg_str_q(27, 0, int(dev_n), '0' +
                                str(data[dev_n]['name'][-5]))
            else:
                msg = msg_str_q(23, 0, int(dev_n))

            await send_tcp(dev_n, msg)  # Запрос перед отправкой файла
            # for i in range(0, len(msg), 16):
            #    strr+=(msg[i:i+16].hex(':'))+'\n'
            log.debug(f'>>file>>{byte_to_string(msg)}', extra={'type': 'TCP', 'host': str('ip')})
            upload_file[dev_n] = data[dev_n]
            text = f"файл принят к отправке {upload_file[dev_n]['name']}"
            log.debug(f"файл принят к отправке {upload_file[dev_n]['name']} в ИП{dev_n}", extra={'type': 'TCP', 'host': str('dd')})

    answer = {'new': {dev_n: {'load': True}}}
    answer.update(notif_wss(dev_n, text, 'success'))
    return answer


@ dc.ws_api('del')
async def ws_del(ans, ID, data):
    # print('удаление файла',comm[each])
    if os.path.isfile(root_path+"file/"+data):
        os.remove(root_path+"file/"+data)
        log.info(f'файл {data} удален', extra={'type': 'WSS', 'host': str('d')})
        files = {'firmware': await get_files()}
    # else:
        # company['horizont']['files'].pop(name)
    #    if data in company['horizont']['firmware']:
    #        company['horizont']['files'].pop(data)
    answer = {}
    # answer.update(notif_wss(ID,'text','gray'))
    return files


@ dc.ws_api('sett')
async def ws_sett(ans, ID, data):
    for sett in data:
        log.debug(f'изменение параметра {sett}={data[sett]}', extra={'type': 'WSS', 'host': str('gg')})
        settings[sett] = int(data[sett])
        await save_cfg()
    answer = {}
    # answer.update(notif_wss(ID,'text','gray'))
    return answer


@ dc.ws_api('upload')
async def ws_upload(ans, ID, data):
    by_str = b''

    for btt in data['file']:
        by_str += bytes([data['file'][btt]])

    if '.grf' in data['name']:
        array_file = split_days(by_str)  # by_str.split(b'\xff\xff')
        print(split_days(by_str))
        print('##############################')
        # for day in arr
        print(array_file)
        print(len(array_file))
        datad = []
        level = []
        for day in array_file[:-1]:
            d, l = file_to_array(day)
            datad.append(d)
            level.append(l)
        desc = array_file[-1]
        desc = desc[desc.find(b'\n\r')+2:]
        date = desc[8:16].decode("cp1251")  # Ekb_001_20.11.21
        desc = desc[16:].decode("cp1251")

        company['horizont']['files'][data['name']] = {
            'data': datad, 'level': level, 'options': False, 'date': date, 'desc': desc, 'time': time.time(), 'size': len(by_str)}
        print('##############################')

    async with async_open(f"{root_path}file/{data['name']}", 'wb') as afp:
        byte_dev = await afp.write(by_str)
        log.info(f"загружен файл {data['name']} {byte_dev}byte", extra={'type': 'WSS', 'host': str('ed')})
    files = {'firmware': await get_files()}
    answer = {}
    # answer.update(notif_wss(ID,'text','gray'))
    return files


@ dc.ws_api('passw')
async def passw(ans, ID, data):
    # print('новые пароли', data)

    passw = data[0].to_bytes(2, 'little')
    passw += data[1].to_bytes(2, 'little')
    passw += data[2].to_bytes(2, 'little')
    passw += data[3].to_bytes(2, 'little')

    # print('bytes', passw)
    settings['passw'] = data
    ########################################
    # print(tcp_sess)
    dt = {}
    for each in tcp_sess:
        # print('запрос на', each)
        upload_file[each] = passw
        dt[each] = {'load': True}
        msg = msg_str_q(23, 0, int(each))
        await send_tcp(each, msg)  # Запрос перед отправкой файла

    # for dev_n in incoming:
    #    upload_file[dev_n] = passw
    #    dt[dev_n] = {'load': True}
    # print(upload_file)
    await send_ws_all({'sett': settings})
    answer = {'new': dt}
    # answer.update(notif_wss(ID,'text','gray'))
    return answer

# {'addr': '98', 'slice': [98, 1]}


@ dc.ws_api('get_graph')
async def ws_graph(ans, ID, data):
    print(data)  # 0x65, 0x07, 0x63, 0x00, 0x0b, 0x00
    addr = data['addr']
    sli = data['slice']
    login = user_sess[ID]['name']
    answer = {'new': {addr: {'load': True}}}
    slic = b''

    slic += int(sli[0]).to_bytes(2, byteorder='little')
    slic += int(sli[1]).to_bytes(2, byteorder='little')
  # slice start
    msg = msg_str_q(7, 0, int(addr), slic)
    answer.update(await send_tcp(addr, msg, login, wait=15))
    # answer.update(notif_wss(ID,'text','gray'))
    return answer


@ dc.ws_api('page')
async def ws_page(ans, ID, data):

    # print('добавление страницы', data)
    # print(user_sess[ID]['name'])
    user = user_sess[ID]['name']
    for name, text in data.items():
        if not text:
            # print('удаление страницы', name)
            users[user]['pages'].pop(name)
        else:
            users[user]['pages'].update(data)
    answer = {}
    answer.update({'pages': users[user]['pages']})
    answer.update(notif_wss('ID', 'страница добавлена', 'success'))
    return answer

ws_aNd_tcp = 0
"""
		0x01		data_ip
		0x03		data_km
		0x05		data_sch
		0x07		RS485.log
		0x09		modem.log
		0x0b		config
		0x0d		zav_num
"""


@ dc.tcp_to_json('11')
async def data_ip11(ans, ID, info):
    print('@data_ip', ID)
    print(queue_tcp)
    # await asyncio.sleep(1.3)

    return {}


"""
Коды ответа <REP>:
0x00 - команда принята без сбоев
бит 0...
"""
errs = [
    'несуществующий код команды <CMD>',
    'контрольная сумма не совпала',
    'неправильный блок <INFO>',
    'ошибка в заголовке команды',
    'ошибка - дублирование зав.номера',
    'ошибка - ИП в ручном режиме',
    'ошибка - есть запрет вырезаний (no_epr)',
    'ошибка - канала нет или выключен (v max_fon_tok)'
]


# 95:10:62:00:95:01:00:00:01:ec:16:01:c7:10:00:88 конец диагностики
# b'\x01\x00\x00\x01\xec\x18\x80\x00\xc6\x00' INFO

# {'adr': '98', 'com': 1}
# @addr_manager 98 b'\x01\x00\x10\x1d\x01\xec\x16\x019\x00\x00'
# @addr_manager 98 b'\x01\x80\x10\x00\x00\x00\x00\x00\x00\x00\x00'
@ dc.tcp_to_json('95')
async def adrmanager(ans, ID, info):
    text = 'выполнено'
    typ = 'success'

    answer = {}
    print('@addr_manager', ID, info)
    if len(info) < 3:
        pass
    else:

        # await asyncio.sleep(1.3)
        error = info[1]
        if error:  # error
            error = byte_to_bin(error)
            print('warning')
            print(error)
            text = ''
            typ = 'warning'
            for i, er in enumerate(error):
                if int(er):
                    print(errs[i])
                    text += errs[i]+'<br/>'
            answer.update(notif_wss(ID, text, typ))
        # bf = ['10', '12', '14']
        go = 0
        bff = [16, 18, 20]
        for i, bf in enumerate(bff):
            if bf == info[2]:
                go = i+1
                # pass
        if go:
            msg = msg_str_q(11, 0, int(ID), f'0{go}')
            await send_tcp(ID, msg)  # Запрос перед отправкой файла

        answer.update(notif_wss(ID, text, typ))
    answer.update({'new': {ID: {'cut': False}}})
    # await send_ws_all(answer)
    return answer


@ dc.tcp_to_json('81')
async def data_ip(ans, ID, info):
    print('@data_ip', ID, info)
    info = info[1:]
    answer = []
    for bb in info:
        bit = hex(bb).replace('0x', '')
        if len(bit) == 1:
            answer.append('0'+bit)
        else:
            answer.append(bit)
    await send_ws_all({'data_ip': answer})


def byte_to_lcd(data, leng=16):
    strr = ''
    arr = []
    for i in range(0, len(data), leng):
        strr += (data[i:i+16])+'\n'
        arr.append(data[i:i+16])
    return arr


@ dc.tcp_to_json('15')
async def data_lcd(ans, ID, info):
    print('@data_lcd')
    lcd = byte_to_lcd(info.decode("cp1251")[1:])  # info.decode("cp1251")[1:]
    # lcd = lcd.replace(" ", "&emsp;")
    await send_ws_all({'lcd': {ID: lcd}})
    # prnt = byte_to_lcd(info.decode("cp1251")[1:])
    print(lcd)


def revers(strr):
    return ''.join(reversed(list(strr)))


@ dc.tcp_to_json('83')
async def data_km_tcp(ans, ID, info):
    print('@data_km', info)

    answer = {}
    answer['zav_num'] = int.from_bytes(info[1:4], 'little')
    answer['ver_prog'] = f"""{info[5]}.{info[4]}"""
    answer['ver_exe'] = info[6]
    answer['status_pass'] = hex(info[7])[2:]
    status_km = info[8:12]
    answer['status_km'] = status_km[::-1].hex()
    error = info[12:16]
    answer['error'] = error[::-1].hex()
    answer['uptime'] = int.from_bytes(info[17:21], 'little')
    answer['modem'] = revers(info[21:25].decode('ascii'))

    await send_ws_all({'km': answer})


@ dc.tcp_to_json('85')
async def data_sch(ans, ID, info):
    print('@no answer ')


@ dc.tcp_to_json('87')
async def log_rs485(ans, ID, info):
    print('@log_rs485')


@ dc.tcp_to_json('89')
async def log_modem(ans, ID, info):
    print('@log_modem')


@ dc.tcp_to_json('8B')
async def config(ans, ID, info):
    print('@config')


@ dc.tcp_to_json('8D')
async def zav_num(ans, ID, info):
    print('@zav_num')
#########UPLOAD##############


@ dc.tcp_to_json('97')
async def upl_file(ans, ID, info):
    print('@upload 97')


@ dc.tcp_to_json('99')
async def upl_file1(ans, ID, info):
    print('@upload 99')


@ dc.tcp_to_json('9B')
async def upl_file2(ans, ID, info):
    print('@upload 9B')
#############################

###########
#### influx bd client #
print('WORK FOR INFLUX')
infl_client = InfluxDBClient(
    db='test', host='localhost', port=8086)  # , ssl=True)
# infl_client.drop_database()
# infl_client.drop_database('test')
#######################
# logging.getLogger('aioinflux').setLevel(logging.DEBUG)
#### логирование ######
log = logging.getLogger(__name__)
# logging.DEBUG DEBUG < INFO < WARNING < ERROR < CRITICAL
log.setLevel(logging.DEBUG)
# строка формата сообщения
# strfmt = '[%(asctime)s][%(lineno)s][%(levelname)s][%(type)s][%(ip)s][%(funcName)s] %(msg)s'
# %(msg)s [%(name)s]
strfmt = '[%(asctime)s][%(levelname)s][%(type)s][%(funcName)s][%(host)s] %(msg)s'
# строка формата времени
datefmt = '%Y-%m-%d %H:%M:%S'  # '%H:%M:%S'
# потоки логов
log_file = logging.handlers.TimedRotatingFileHandler(f'{root_path}log.json', when='d', interval=1, backupCount=10, encoding='utf-8', delay=False)
log_stream = logging.StreamHandler()
# настройки
jsn_formatter = jsonlogger.JsonFormatter(fmt=strfmt, datefmt=datefmt)
str_formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)
log_file.setFormatter(jsn_formatter)
log_stream.setFormatter(str_formatter)
log.addHandler(log_stream)
log.addHandler(log_file)
########################


def cs_check(byte):
    # summ=struct.unpack('>'+str(len(byte))+'B',byte)
    cs = 0
    for num in byte:
        cs += num
    cs = cs.to_bytes(4, byteorder="little")
    # cs=struct.pack('<i', cs)
    return bool(not cs[0])


def int_to_bin(intt):
    result = "{:04b}".format(intt)
    return result


ppa = root_path+'file/'


async def get_chart(num, segment=""):
    """
    Отдает график в нужном формате
    """
    if len(segment) > 5:
        next_day = int((datetime.fromisoformat(segment) +
                       timedelta(1)).timestamp())*1000000000
        segment = int(datetime.fromisoformat(segment).timestamp())*1000000000
        # print(f'SELECT * FROM "{num}"  WHERE time >= {segment} AND time <= {next_day}')
        # group by time(5m)
        requ = await infl_client.query(f'SELECT * FROM "{num}"  WHERE time > {segment} AND time < {next_day}')
    else:
        # time > now() - 1h
        requ = await infl_client.query(f'SELECT * FROM "{num}"  WHERE time > now() - {segment}')
    # print(requ)
    # for pnt in iterpoints(requ):
    # print(requ)

    # ORDER BY desc LIMIT 20
    # WHERE time > now() - 1h
    if not requ['results'][0].get('series', False):
        return {}
    cols = requ['results'][0]['series'][0]['columns']
    requ = requ['results'][0]['series'][0]['values']
    # print(cols)
    answ = {}
    for num, col in enumerate(cols):

        if col == 'time':
            answ[col] = [value[num]/1000000 for value in requ]
        else:
            answ[col] = [value[num] for value in requ]
   # answ = {
    #    'time': [int(point[0]/1000000) for point in requ],
    #    'buf_1_volt': [point[1]for point in requ],
    #    'buf_2_volt': [point[2]for point in requ],
    #    'buf_3_volt': [point[3]for point in requ]
    # }
    return answ


async def get_files():

    arr = {}
    list_dir = os.listdir(ppa)
    print(list_dir)
    for each in list_dir:
        pathh = ppa+each
        if '.' in each:
            arr[each] = {}
            arr[each]['size'] = os.path.getsize(ppa+each)
            arr[each]['time'] = os.path.getmtime(ppa+each)
            arr[each]['ctime'] = os.path.getctime(ppa+each)
            # time_tuple = datetime.fromtimestamp(os.path.getatime(ppa+each)).strftime("%H:%M:%S %d.%m.%y")
            arr[each]['atime'] = os.path.getatime(ppa+each)

    # print(arr)
    return arr


async def get_size(file):
    return os.path.getsize(root_path+file)


async def send_tcp_all(msg):
    for each in tcp_sess:
        if each in upload_file:
            print('ИП', each, 'еще принимает файл')
            # log.critical('ИП'+str(each)+'еще принимает файл'+str(upload_file[each]['name']),extra={'type':'WSS'})
        else:
            # print(each ,clients[each]['a'],clients[each]['id_n'])
            if not tcp_sess[each].is_closing():
                # msg=msg_str_q(1,0,int(each))
                msgg = msg_str_f(23, 0, int(each), msg, [2, 0])
            # msg=b'\xFF\xFF\xFF\xFF'
            # print(tcp_sess[each].is_closing(),'send>len',len(msg), msg)
            # print(tcp_sess[each].transport.get_write_buffer_limits())
                tcp_sess[each].write(msgg)
                # print('опрос ип', each)
                # print('send dataip',each)
                await asyncio.wait_for(tcp_sess[each].drain(), timeout=5)


async def read_bin(name_file, slices=False):
    async with async_open(root_path+"file/"+name_file, 'rb') as afp:
        result = await afp.read()

    print('len file', slices, len(result))

    if slices:
        if slices[0] == 0:
            return result

        strr = b''
        result = result.split(b'\xff\xff')

        for lin in result[slices[0]-1:slices[0]+slices[1]-1]:
            print(lin)
            strr += lin+b'\xff\xff'

        result = strr
        # print(result)
    print('#####################')
    print('len file', len(result))
    return result


async def getLog(choice, ip='', lines=20):
    async with async_open(f"{root_path}log.json", 'r') as afp:
        jsn_log = await afp.read()
        jsn_log = jsn_log.splitlines()
        lng = len(jsn_log)
        return_log = []
        for lg in jsn_log:
            lg = json.loads(lg)
            if lg['levelname'] in choice and lg['type'] in choice and ip in lg['host']:
                return_log.append(lg)

        lng = len(return_log)
        if lng-lines < 0:
            lng = 0
        else:
            lng -= lines

        # if lng < 500:
        #    for each in range(0, lng):
        #        return_log.append(json.loads(jsn_log[each]))
        # else:
        #    for each in range(lng-500, lng):
        #        return_log.append(json.loads(jsn_log[each]))
        return return_log[lng:]


async def save_file(file_data, name, typ):
    async with async_open(f"{root_path}file/{name}.{typ}", 'wb') as afp:
        byte_dev = await afp.write(file_data)


async def save_cfg():

    for usr in user_sess:
        user_sess[usr].pop('ws', False)

    # for num in incoming:
    #    incoming[num]['online'] = False
    # incom[num]['status']=False
    # user_sess
    async with async_open(f"{root_path}cfg.json", 'w+') as afp:
        byte_dev = await afp.write(json.dumps(load, indent=4))
        log.info(f'конфиг сохранен {byte_dev}byte', extra={'type': 'SYS', 'host': '127.0.0.1'})

    # with open(root_path+"config.cfg", 'wb') as afp:
    #    pickle.dump(load, afp)
    # await infl_client.close()


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


ws_sess = {}


async def send_ws_all(msg, company=False, user=False, tkt=False):
    #print('SEND WS ALL start', company, user)
    # try:
    if company:
        if user:
            for ws in [sess['ws'] for sess in user_sess.values() if sess['company'] == company and sess['name'] != user and 'ws' in sess]:
                await ws.send_json(msg)
        else:
            for ws in [sess['ws'] for sess in user_sess.values() if sess['company'] == company and 'ws' in sess]:
                await ws.send_json(msg)
    elif user:
        print('send for only user', user)
        for ws in [sess['ws'] for sess in user_sess.values() if sess['name'] == user and 'ws' in sess]:
            print(f'send {user} ws_status ', ws.status)
            if ws.status:
                try:
                    await ws.send_json(msg)
                except Exception as ex:
                    # FIXME ws send all ws.status
                    print(f'fix ConnectionResetError: Cannot write to closing transport {ex}')
            else:
                print('send user ws_status ', ws.status)
    else:
        # print('wabl trabl')
        for ws in ws_sess:
            # print("snd ws for all session", ws)
            await ws.send_json(msg)
    # except:
    #    print('нету ещё сокетов сессий потом исправлю')


async def notif_ws(ids, txt, color="red"):
    msg = {"notif": {
        "id": ids,
        "txt": txt,
        "col": color
    }}
    await send_ws_all(msg)


def notif_wss(ids, txt, color="red"):
    """
    success
    info
    warning
    critical
    error
    """
    msg = {"notif": {
        "id": ids,
        "txt": txt,
        "col": color
    }}
    return msg


async def start_msg(msg):
    print(msg)
    return


async def web_br_op():
    webbrowser.open_new('http://192.168.11.237:8080')
    return

# async def tray_ico():
#    print('start tray icon')
#    await icon.run()
#    return

# def action():
#    icon.stop()

#    print('tray click')

# image = Image.open("tray.png")
# menu = menx(
#    item('закрыть иконку',lambda: action()),
#    item('уведомление',lambda: icon.notify('Проверка системного уведомления')),
    # item('выход',lambda: icon.stop())
#    )
# icon = pystray.Icon(name ="SPAM!", icon =image, title ="интелекон", menu =menu)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
i = 1
clients = {}
wri = ''

upload_file = {}


def noww():
    return str(time.strftime('%d.%m %H:%M:%S', time.localtime()))


tcp_sess = {}
device = {}
old_num = {}

with open(root_path+'cfg.json', "r") as f:
    load = json.load(f)


with open(root_path+'city.json.txt', "r") as f:
    city = json.load(f)
# print(load)

ev_null = {}
company = load['company']
events = load['events']
# events.append({"systm": {"msg": "server reload", "ts": noww()}})
# load['settings']['replay'] = 4
# load['settings']['retry'] = 5
settings = load['settings']
users = load['users']
news = load['news']
# print(users)
user_sess = load['user_sess']
incoming = load['device']
# proxy = multiprocessing.Manager().dict()
# proxy = incom


def msg_str_a(cmd, rep, addr, info=None):  # iNTELECON OLD VER

    msg = b''
    cs = 0
    start_bit = bytes.fromhex('95')  # 0x7e 1byte
    stop_bit = bytes.fromhex('0d')  # 0x0d 1byte

    if info is None:
        N_bit = 6
    else:
        info = info.split(':')
        buff = b''
        for each in info:
            buff += bytes.fromhex(each)
        info = buff
        N_bit = len(info)+6
    N_bit = bytes([N_bit])

    msg += start_bit
    msg += N_bit
    msg += bytes([addr])
    msg += bytes([rep])
    msg += bytes([cmd])

    if info is not None:
        msg += info  # .encode('ascii')#bytes.fromhex(info)

    # длины пакета, команды, адреса, информации и CRC
    summ = struct.unpack('>'+str(len(msg))+'B', msg)
    for each in summ:
        cs += each
    # print(cs)
    cs = struct.pack('<i', cs)
    # print(cs)
    # print(cs[0])
    cs = bytes([256-cs[0]])  # CS
    msg += cs
###################
    return msg


def msg_str_q(cmd, rep, addr, info=None):  # iNTELECON OLD VER

    msg = b''
    cs = 0
    start_bit = bytes.fromhex('65')  # 0x7e 1byte
    stop_bit = bytes.fromhex('0d')  # 0x0d 1byte

    if info is None:
        N_bit = 6
    else:
        if not isinstance(info, bytes):
            info = info.split(':')
            buff = b''
            for each in info:
                buff += bytes.fromhex(each)
            info = buff
        N_bit = len(info)+6
    # print(info)
    N_bit = bytes([N_bit])

    msg += start_bit
    msg += N_bit
    msg += bytes([addr])
    msg += bytes([rep])
    msg += bytes([cmd])

    if info is not None:
        msg += info  # .encode('ascii')#bytes.fromhex(info)

    # длины пакета, команды, адреса, информации и CRC
    summ = struct.unpack('>'+str(len(msg))+'B', msg)
    for each in summ:
        cs += each
    # print(cs)
    cs = struct.pack('<i', cs)
    # print(cs)
    # print(cs[0])
    cs = bytes([256-cs[0]])  # CS
    msg += cs
###################
    return msg


def msg_str_f(cmd, rep, addr, info=b'\x00', slices=False):  # iNTELECON NEW VER

    msg = b''
    cs = 0
    start_bit = bytes.fromhex('6a')  # 0x6a 1byte
    # stop_bit=bytes.fromhex('0d')  #0x0d 1byte
    if slices:
        N_bit = len(info)+13
    else:
        N_bit = len(info)+9
    N_bit = N_bit.to_bytes(4, byteorder='little')

    msg += start_bit
    msg += N_bit
    msg += bytes([addr])
    msg += bytes([rep])
    msg += bytes([cmd])
    if slices:
        if isinstance(slices, bytes):
            msg += slices
        else:
            msg += slices[0].to_bytes(2, byteorder='little')  # slice start
            msg += slices[1].to_bytes(2, byteorder='little')  # slice end
    msg += info  # .encode('ascii')#bytes.fromhex(info)
    # msg+=b'\x55\xaa'
    # длины пакета, команды, адреса, информации и CRC
    summ = struct.unpack('>'+str(len(msg))+'B', msg)
    for each in summ:
        cs += each
    # print(cs)
    cs = struct.pack('<i', cs)
    # print(cs)
    if cs[0] == 0:
        cs = bytes([255])
    else:
        cs = bytes([256-cs[0]])  # CS
    msg += cs
    # print(cs[0])
    # cs=bytes([256-cs[0]])###########CS
    # msg+=cs
###################
    return msg


WS_FILE = os.path.join(os.path.dirname(__file__), "index.html")
# print(os.path.dirname(__file__))


def b_In_Slice(byte, slices=0):
    result = "{:08b}".format(byte)
    # print(result)
    return int(result[slices:], 2)


def byte_to_bin(byte, pos=None):
    result = "{:08b}".format(byte)
    # print(result)
    if pos is not None:
        return int(result[::-1][pos])

    return result[::-1]


data_sch = {}


async def tcp_to_jsn(adr, cmd, info):
    status = False
    # print('=======tcp=======', noww())
    # print('adr:',adr)
    # print('cmd:',cmd)
    # print('info:',info)
    # print('=================')
    if cmd in [17, 129]:  # 11 81
        # print('data_ip')

        add = ('graph',)
        for ad in add:
            if ad not in incoming[str(adr)]:
                incoming[str(adr)][ad] = None
        # incoming[str(adr)]['status'] = incoming[str(adr)]['norm_st']
        # incom[str(adr)]['norm_st']="normal"
        # for num in range(0,54):
        #    print('B'+str(num+1)+'=',int(info[num]))

        mod_a = "{:08b}".format(int(info[6]))
        mod_b = "{:08b}".format(int(info[8]))
        mod_c = "{:08b}".format(int(info[10]))

        bsip = "{:08b}".format(int(info[15]))

        # print('modex', mod_a[7], mod_b[7], mod_c[7])
        incoming[str(adr)]['dwn'] = False

        incoming[str(adr)]['bufs'][0]['online'] = bool(int(mod_a[7]))
        incoming[str(adr)]['bufs'][1]['online'] = bool(int(mod_b[7]))
        incoming[str(adr)]['bufs'][2]['online'] = bool(int(mod_c[7]))

        bsf_a = "{:08b}".format(int(info[12]))
        bsf_b = "{:08b}".format(int(info[13]))
        bsf_c = "{:08b}".format(int(info[14]))

        if incoming[str(adr)]['bufs'][0]['mode'] != bool(int(bsf_a[6])):
            print('change mode A')
            incoming[str(adr)]['bufs'][0]['mode'] = bool(int(bsf_a[6]))

        if incoming[str(adr)]['bufs'][1]['mode'] != bool(int(bsf_b[6])):
            print('change mode B')
            incoming[str(adr)]['bufs'][1]['mode'] = bool(int(bsf_b[6]))

        if incoming[str(adr)]['bufs'][2]['mode'] != bool(int(bsf_c[6])):
            print('change mode C')
            incoming[str(adr)]['bufs'][2]['mode'] = bool(int(bsf_c[6]))

        if not bool(int(bsf_a[0])) and not bool(int(bsf_a[2])):
            incoming[str(adr)]['bufs'][0]['acc'] = 'ok'

        if not bool(int(bsf_b[0])) and not bool(int(bsf_b[2])):
            incoming[str(adr)]['bufs'][1]['acc'] = 'ok'

        if not bool(int(bsf_c[0])) and not bool(int(bsf_c[2])):
            incoming[str(adr)]['bufs'][2]['acc'] = 'ok'

#########################
        if bool(int(bsf_a[0])):
            if incoming[str(adr)]['bufs'][0]['acc'] != 'kz':
                await notif_ws(str(adr), "короткое замыкание БУФ А", 'critical')
                incoming[str(adr)]['bufs'][0]['acc'] = 'kz'

        if bool(int(bsf_b[0])):
            if incoming[str(adr)]['bufs'][1]['acc'] != 'kz':
                await notif_ws(str(adr), "короткое замыкание БУФ В", 'critical')
                incoming[str(adr)]['bufs'][1]['acc'] = 'kz'

        if bool(int(bsf_c[0])):
            if incoming[str(adr)]['bufs'][2]['acc'] != 'kz':
                await notif_ws(str(adr), "короткое замыкание БУФ С", 'critical')
                incoming[str(adr)]['bufs'][2]['acc'] = 'kz'
###########################
        if bool(int(bsf_a[2])):
            if incoming[str(adr)]['bufs'][0]['acc'] != 'ns':
                await notif_ws(str(adr), "неисправность силовой цепи БУФ А", 'critical')
                incoming[str(adr)]['bufs'][0]['acc'] = 'ns'

        if bool(int(bsf_b[2])):
            if incoming[str(adr)]['bufs'][1]['acc'] != 'ns':
                await notif_ws(str(adr), "неисправность силовой цепи БУФ В", 'critical')
                incoming[str(adr)]['bufs'][1]['acc'] = 'ns'

        if bool(int(bsf_c[2])):
            if incoming[str(adr)]['bufs'][2]['acc'] != 'ns':
                await notif_ws(str(adr), "неисправность силовой цепи БУФ С", 'critical')
                incoming[str(adr)]['bufs'][2]['acc'] = 'ns'
##################
        if incoming[str(adr)]['bufs'][0]['line'] != bool(int(mod_a[6])):
            print('change line A')
            incoming[str(adr)]['bufs'][0]['line'] = bool(int(mod_a[6]))

        if incoming[str(adr)]['bufs'][1]['line'] != bool(int(mod_b[6])):
            print('change line B')
            incoming[str(adr)]['bufs'][1]['line'] = bool(int(mod_b[6]))

        if incoming[str(adr)]['bufs'][2]['line'] != bool(int(mod_c[6])):
            print('change line C')
            incoming[str(adr)]['bufs'][2]['line'] = bool(int(mod_c[6]))
        new = ""

        mnoz_a = 1
        mnoz_b = 1
        mnoz_c = 1

        if int(bsf_a[7]) == 0:
            mnoz_a = 0.5
        if int(bsf_b[7]) == 0:
            mnoz_b = 0.5
        if int(bsf_c[7]) == 0:
            mnoz_c = 0.5

        # print(mnoz_a, mnoz_b, mnoz_c)
        # print("БУФ Б", bsf_b, bsf_b[7], int(info[1]))

        if incoming[str(adr)]['bufs'][0]['amp'] != int(info[0])*mnoz_a:
            incoming[str(adr)]['bufs'][0]['amp'] = int(info[0])*mnoz_a

        if incoming[str(adr)]['bufs'][1]['amp'] != int(info[1])*mnoz_b:
            incoming[str(adr)]['bufs'][1]['amp'] = int(info[1])*mnoz_b

        if incoming[str(adr)]['bufs'][2]['amp'] != int(info[2])*mnoz_c:
            incoming[str(adr)]['bufs'][2]['amp'] = int(info[2])*mnoz_c

        # print(mnoz_a, mnoz_b, mnoz_c)
        # print(incom[str(adr)]['A']['amp'], incom[str(adr)]
        #      ['B']['amp'], incom[str(adr)]['C']['amp'],)
###################################
        if incoming[str(adr)]['bufs'][0]['vol'] != int(info[3])+70:
            if info[3] == 0:
                incoming[str(adr)]['bufs'][0]['vol'] = 0
            else:
                incoming[str(adr)]['bufs'][0]['vol'] = int(info[3])+70

        if incoming[str(adr)]['bufs'][1]['vol'] != int(info[4])+70:
            if info[4] == 0:
                incoming[str(adr)]['bufs'][1]['vol'] = 0
            else:
                incoming[str(adr)]['bufs'][1]['vol'] = int(info[4])+70

        if incoming[str(adr)]['bufs'][2]['vol'] != int(info[5])+70:
            if info[5] == 0:
                incoming[str(adr)]['bufs'][2]['vol'] = 0
            else:
                incoming[str(adr)]['bufs'][2]['vol'] = int(info[5])+70

        incoming[str(adr)]['count'] = b_In_Slice(info[19], 4)

        # print('info 51', info[51])
        print('AVAR')
        print('19', byte_to_bin(info[19]))
        incoming[str(adr)]['rssi'] = info[50]
        print('51', byte_to_bin(info[51]))
        print('52', byte_to_bin(info[52]))

        if info[52] > 0:  # Аварийный пакет 00100000

            if byte_to_bin(info[52], 0):  # потеря питания по всем фазам
                if incoming[str(adr)]['status'] != "emergency":
                    log.info(f'потеря питания пакет номер: {info[-2]}', extra={'type': 'SYS', 'host': str(adr)})
                    # incoming[str(adr)]['online'] = False
                    # Normal Fire Emergency Security Hands
                    incoming[str(adr)]['fw'] = False
                    incoming[str(adr)]['load'] = False
                    incoming[str(adr)]['cut'] = False
                    incoming[str(adr)]['status'] = "emergency"
                    status = "emergency"
                    # FIXMEtcp_sess[str(adr)].close()
                    # tcp_sess.pop(str(adr))
                    # FIXMEawait tcp_sess[str(adr)].wait_closed()
                    await notif_ws(str(adr), "потеря питания!", 'critical')
                    events.append({str(adr): {"msg": "потеря питания", "ts": noww(), "st": "emergency"}})
                    await send_ws_all({"events": events})
                    await send_ws_all({'new': {str(adr): incoming[str(adr)]}})
            elif byte_to_bin(info[52], 1):  # потеря питания от БАП
                if incoming[str(adr)]['status'] != "emergency":
                    log.info(f'потеря питания от БАП пакет номер: {info[-2]}', extra={'type': 'SYS', 'host': str(adr)})
                    # incoming[str(adr)]['online'] = False
                    # Normal Fire Emergency Security Hands
                    incoming[str(adr)]['fw'] = False
                    incoming[str(adr)]['load'] = False
                    incoming[str(adr)]['status'] = "emergency"
                    status = "emergency"
                    # tcp_sess[str(adr)].close()
                    # tcp_sess.pop(str(adr))
                    # await tcp_sess[str(adr)].wait_closed()
                    await notif_ws(str(adr), "потеря питания от БАП!", 'critical')
                    events.append(
                        {str(adr): {"msg": "потеря питания", "ts": noww(), "st": "emergency"}})
                    await send_ws_all({"events": events})
                    await send_ws_all({'new': {str(adr): incoming[str(adr)]}})
            elif byte_to_bin(info[52], 2):  # плохой график
                # incoming[str(adr)]['graph'] = '22'

                # if incoming[str(adr)]['graph']:
                await notif_ws(str(adr), "ошибка графика!", 'warning')
                if incoming[str(adr)]['graph']:
                    events.append(
                        {str(adr): {"msg": "ошибка графика", "ts": noww(), "st": "emergency"}})
                    await send_ws_all({"events": events})
                    incoming[str(adr)]['graph'] = False

        else:
            incoming[str(adr)]['status'] = "normal"
        # print('A=',int(info[0])*0.5,'A')
        # print('B=',int(info[1])*0.5,'A')
        # print('C=',int(info[2])*0.5,'A')
        # print('температура КМ', int(info[48]-45))
        # print('=================')
        # print('A=',int(info[3])+70,'V')
        # print('B=',int(info[4])+70,'V')
        # print('C=',int(info[5])+70,'V')

        point = {
            # 'time': current_time,
            'measurement': str(adr),  # №IP или Зав номер.
            # №IP или Зав номер. другие характеристики
            # 'tags': {'host': 'server01', 'region': 'Ekb'},
            # Метрика
            'fields': {
                'buf_1_volt': incoming[str(adr)]['bufs'][0]['vol'],
                'buf_2_volt': incoming[str(adr)]['bufs'][1]['vol'],
                'buf_3_volt': incoming[str(adr)]['bufs'][2]['vol'],
                'buf_1_amp': float(incoming[str(adr)]['bufs'][0]['amp']),
                'buf_2_amp': float(incoming[str(adr)]['bufs'][1]['amp']),
                'buf_3_amp': float(incoming[str(adr)]['bufs'][2]['amp'])
            }
        }

        if False:
            print("cur_adr_bks", info[36])
            print("tip_bks", info[37])
            print("stbks", info[38])
            print("bks (1..8)", info[39])
            print("bks (9..16)", info[40])
            print("variant", info[16])
            print("tip_buf1", info[17])
            print("tip_buf2", info[18])
            print("tip_sch", info[46])
            print("bsip", info[15])
            print("bsip2", byte_to_bin(info[46]))
            print("stat_graf", info[47])

        incoming[str(adr)]['cut'] = bool(
            byte_to_bin(info[46], 1)+byte_to_bin(info[46], 4))

        incoming[str(adr)]['timeout'] = info[48]
        if info[48]:
            incoming[str(adr)]['status'] = "hands"

        if info[49] != 255:
            point['fields']['temp'] = info[49]-45
        # №IP или Зав номер. другие характеристики

        # print("BSIPpppppppppppppppppppppppppppppppppp", bsip)
        # if incoming[str(adr)]['door']:
        if bool(int(bsip[0])):
            incoming[str(adr)]['status'] = "security"
            if not incoming[str(adr)]['door']:
                incoming[str(adr)]['door'] = True
                await notif_ws(str(adr), 'дверь открыли', 'warning')
                status = 'open'
        else:
            # доделать обязательно!!!
            if incoming[str(adr)]['door']:
                incoming[str(adr)]['door'] = False
                await notif_ws(str(adr), 'дверь закрыли', 'warning')
                incoming[str(adr)]['status'] = "normal"
                status = 'close'
# доделать обязательно!!!
        # if bool(int(bsip[0])):
        #    incoming[str(adr)]['status'] = "security"

        if status:
            point['tags'] = {'status': status}
        if not incoming[str(adr)]['online']:
            incoming[str(adr)]['online'] = True
            point['tags'] = {'status': 'online'}
        # infl_client.db = 'horizont'
        # FIXME записыыать не всё подряд!!! if info[51] or 'tags' in point:  # cmd == 129 or
        await infl_client.write(point)
        await send_ws_all({'new': {str(adr):  incoming[str(adr)]}})
        # if incom[str(adr)]['info']!=info:
        # if incom[str(adr)]['info']!=info:
        #    print('change info')
        #    incom[str(adr)]['info']=info
    elif cmd == 133:
        # print(info)
        sch_type = ['Меркурий 230', 'СЕ 301', '', '', '', '', '', '', '', '', '',
                    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
        # data_sch['num']=info[0]
        # data_sch['type']=sch_type[info[1]-1]
        # data_sch['f_num']=int.from_bytes(info[106:110] , 'little')
        jsonc = {"dir_p_active": [],
                 "dir_p_reactive": [],
                 "rev_p_active": [],
                 "rev_p_reactive": [],
                 "power": [],
                 "curre": []
                 }

        numsss = 0
        for nums, name in enumerate(jsonc):
            i = 5
            if nums > 3:
                i = 3
            for num in range(numsss+2, numsss+2+i):  # int(len(data)/4)
               # print(num)
                value = int.from_bytes(info[num*4-6:(num*4-6)+4], 'little')
                if value == 4294967295:
                    value = 0
                jsonc[name].append(value)
                # print("DW",num-1 ,"[", num*4 ,",",(num*4)+4 ,"]", int.from_bytes(datas[num*4:(num*4)+4], 'little'))
            numsss += i
        jsonc['num'] = info[0]
        jsonc['type'] = sch_type[info[1]-1]
        # int.from_bytes(info[106:110] , 'little')
        jsonc['f_num'] = str(info[106])+str(info[107]) + \
            str(info[108])+str(info[109])
        jsonc['prod'] = str(info[110])+"."+str(info[111]) + \
            "."+str(info[112]+2000)
        jsonc['ver'] = int.from_bytes(info[114:118], 'little')
        jsonc['exec'] = int.from_bytes(info[118:122], 'little')

        # incom[str(adr)]['counts'][str(info[0])]=

        # await send_ws_all("{\"sch\":{\""+str(adr)+"\":"+json.dumps(jsonc)+"}"+"}")
        await send_ws_all({'sch': {str(adr): jsonc}})
    elif cmd == 149:
        # incom[str(adr)]['norm_st']="hands"#Normal Fire Emergency Security Hands
        # incom[str(adr)]['status']="hands"
        await send_ws_all({'new': {str(adr): incoming[str(adr)]}})
    # print('=======jsn=======')
    return True


# TCP
async def handle_tcp(reader, writer):
    dlina = len(clients)+1
###########################
    user = None
###########################
    in_port = writer.get_extra_info('sockname')[1]
    this_company = [
        name for name in company if in_port in company[name]['ports']][0]
    # wri=writer
    # in_port=writer.get_extra_info('sockname')#sock.getsockopt
    # in_port=str(in_port[1]+dlina)
    addr = writer.get_extra_info('peername')
    addr = addr[0]

    # print(writer.get_extra_info('socket'))
    log.info(f'connect ({this_company}) device ip: {addr}',             extra={'type': 'TCP', 'host': str(addr)})

    # print(addr)
    # client_id=str(in_port)
    write_file = None
    # print(writer.transport.get_write_buffer_limits())
    # writer.transport.set_write_buffer_limits(1000,1)
    # print(writer.transport.get_write_buffer_limits())
    # print(writer.transport.get_write_buffer_size())
    # clients[client_id]={'w':writer,'a':addr, 'id_n':dlina}
    # msg=msg_str_q(1,0,99)
    # writer.write(msg)
    await writer.drain()
    # writer.transport.set_write_buffer_limits(0,64)
    addr_ip = 0
    down_file = False
    file_data = b''
    normal = "normal"
    t_out = settings['reload']*3
    cyrcle = 0
    ID = 'first'
    while True:

        # data = await reader.read(1024)
        # addr_ip=0
        try:
            cyrcle += 1
            # writer.write(b'tennbytess')
            # data = await reader.read(1000000)
            #print('time out> cyrcle', cyrcle, ID, '\n')
            if addr_ip in upload_file:
                t_out = 300
                #print('увеличен тайм аут')
            else:
                t_out = settings['reload']

            data = await asyncio.wait_for(reader.read(3000), timeout=t_out)

            # data = await reader.read(10240)
            # strr='\n'
            # for i in range(0, len(data), 16):
            #    strr+=(data[i:i+16].hex(':'))+'\n'

            # print(data)
            # print(await noww())
            # data = await asyncio.wait_for(reader.read(1024), timeout=5)
        except Exception as ex:

            log.debug(f'{type(ex).__name__} {ID} ip:{addr} пакет № {cyrcle}', extra={'type': 'TCP', 'host': str(addr)})

            if type(ex).__name__ == 'TimeoutError':
                msg = msg_str_q(1, 0, int(ID))
                # await send_tcp(ID, msg, wait=0)
                if ID in tcp_sess:
                    tcp_sess.pop(ID)
                writer.write(msg)
                await writer.drain()

                try:
                    data = await asyncio.wait_for(reader.read(3000), timeout=5)
                except:
                    data = b''

                if ID in tcp_sess:
                    log.debug(f'{ID} успел переподключится, убиваем этот цикл', extra={'type': 'TCP', 'host': str(addr)})
                    break

            else:
                data = b''

        if not data:
            # print(data)

            # print('client #',client_id, 'off')
            log.debug(f'disconnect device ИП {ID} ip:{addr}->цикл #{cyrcle}', extra={'type': 'TCP', 'host': str(addr)})
            incoming[addr_ip]['online'] = False
            incoming[addr_ip]['fw'] = False
            incoming[addr_ip]['load'] = False
            incoming[addr_ip]['dwn'] = False
            point = {
                'measurement': str(addr_ip),
                'fields': {
                    'buf_1_volt': incoming[str(addr_ip)]['bufs'][0]['vol'],
                    'buf_2_volt': incoming[str(addr_ip)]['bufs'][1]['vol'],
                    'buf_3_volt': incoming[str(addr_ip)]['bufs'][2]['vol'],
                    'buf_1_amp': float(incoming[str(addr_ip)]['bufs'][0]['amp']),
                    'buf_2_amp': float(incoming[str(addr_ip)]['bufs'][1]['amp']),
                    'buf_3_amp': float(incoming[str(addr_ip)]['bufs'][2]['amp'])
                },
                'tags': {'status': 'offline'}
            }

            await infl_client.write(point)

        # РАЗОБРАТЬСЯ С ЭТИМ ОБЯЗАТЕЛЬНО НЕ ВСЕГДА ПРИХОДИТ ПАКЕТ

            events.append(
                {str(addr_ip): {"msg": "потеря связи", "ts": noww(), "st": "offline"}})

            await send_ws_all({"events": events})

        # await send_ws_all("{\"new\":{\""+str(addr_ip)+"\":"+json.dumps(incom[str(addr_ip)])+"}"+"}")
            await send_ws_all({'new': {str(addr_ip): incoming[str(addr_ip)]}})
            # if ID in tcp_sess:
            #    tcp_sess.pop(ID)
            # writer.close() закрыть связь
            # await writer.wait_closed() дождаться
            break
        else:
            #########################
            # print('ENTER MSG')
            # print(data)
            msg = []
            if ih(data[0]) in ('65', '95'):  # '9A'
                while data:
                    msg.append(data[:data[1]])
                    # print(data)
                    data = data[data[1]:]
            else:
                msg.append(data)
            # if data[1] != len(data):
            #    print('склееное сообщение\n', data)
            #    continue

            #########################
            for data in msg:
                if data[1] != len(data) and ih(data[0]) in ('65', '95'):
                    log.debug(f"не сходится размер сообщения\n{byte_to_string(data)}", extra={'type': 'TCP', 'host': str(addr)})
                    continue

                if ih(data[0]) in ('65', '95', '9A'):
                    log.info(f"<<<\n{byte_to_string(data)}", extra={'type': 'TCP', 'host': str(addr)})
                ################################################
                ID = str(int.from_bytes(data[2:4], 'little'))
                if ih(data[0]) == '9A':
                    ID = str(int.from_bytes(data[5:7], 'little'))

                if ID not in incoming and data[1] == len(data) and not down_file:
                    print('send incoming', ID)
                    log.debug(f"send incoming {ID}\n{byte_to_string(data)}", extra={
                              'type': 'TCP', 'host': str(addr)})
                    await send_ws_all({'incoming': ID})
                    addr_ip = ID
                    continue
                else:
                    pass
                    # обязательно разобратьтся
                    # cmd = data[4]
                    # adr_ip=int.from_bytes(data[5:6], 'little')
                    # try:
                try:
                    cmd = hex(data[4])[2:]
                except:
                    cmd = '00'
                #    cmd = hex(data[7])[2:]
                #
                # cmd = data[4:5].hex()
                # rep = data[5]
                # cs = data[-1]
                answer = {}
                info = data[5:-1]
                print('len is', data[1] == len(data))
                if data[1] == len(data):
                    if tcp_funct_list.get(cmd, False):
                        retu = await tcp_funct_list[cmd]({}, ID, info)
                        if retu is not None:
                            answer.update(retu)
                    else:
                        print('tcp no function', cyrcle, ID)
                        # await send_ws_all({'new': {ID: {'upload': False}}})
                    if len(answer):
                        await send_ws_all(answer)
    ################################################
                # print("#########")
                # message = data.decode()
                # addr = writer.get_extra_info('peername')
                # print(addr)
                # print(data)
                # print("#########")
                # print("ID#%r Received %r from %r" % (client_id, message, addr))
                start_bit = data[0]
                # print('stb',start_bit)

                # print('st bit:',start_bit)
                # print('ln bit:',data[1])
                # print('ml a bit:',data[2])
                # print('st a bit:',data[3])
            # print(f"Received Syslog message: {data}")
            # print(f"Received Syslog message: {addr}")
                # NEW ERA!!!!!!!!!!
                if ih(start_bit) in ('95', '9A'):
                    # print('TESTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT', addr_ip)
                    cmd_bit = data[4]-128
                    if ih(start_bit) == '9A':
                        cmd_bit = data[7]-128
                    if addr_ip in queue_tcp['horizont']:
                        for num, msg in enumerate(queue_tcp['horizont'][addr_ip]['msg']):
                            if cmd_bit == msg[4]:
                                print("DELETE MSG K&L", num, cmd_bit)
                                # обязательно разобратьтся
                                await send_ws_all({'new': {ID: {'keys': False, 'load': False}}})
                                queue_tcp['horizont'][addr_ip]['msg'].pop(num)
                                user = queue_tcp['horizont'][addr_ip]['user']
                                if len(queue_tcp['horizont'][addr_ip]['msg']) == 0:
                                    queue_tcp['horizont'].pop(addr_ip)
            # CMD 01..0x09
            # self.transport.sendto()
                length = len(data)
                if start_bit == 154:  # 9A 65 06 63 00 0b
                    print('i am big msg')
                    # obj = struct.unpack('<BihB'+str(length-3)+'sc', data)
                    down_file = True
                    incoming[addr_ip]['dwn'] = down_file
                    data_len = int.from_bytes(data[1:5], 'little')
                    print("file len", data_len)
                    file_data = data
                    await send_ws_all({'progress': int(len(file_data)/(data_len/100))}, user=user)
                    if len(file_data) >= data_len:
                        file_data = file_data[:data_len]
                        down_file = False
                        incoming[addr_ip]['dwn'] = down_file
                        if cs_check(file_data):
                            # print('CS ok')
                            sub_com = ih(file_data[7])
                            if(sub_com == '87'):  # FIXME разбираем файл графика и шлем обратно
                                if len(file_data) < 13:
                                    await notif_ws(ID, "данных графика у ИП НЕТ", "success")
                                    await send_ws_all({'progress': 0}, user=user)
                                    continue
                                array_file = split_days(file_data[13:-1])  # file_data[13:-1].split(b'\xff\xff')
                                file_size = len(file_data[13:-1])
                                # print('##############################')
                                # for day in arr
                                # print(array_file)
                                # print(len(array_file))
                                datad = []
                                level = []
                                for day in array_file[:-1]:
                                    d, l = file_to_array(day)
                                    datad.append(d)
                                    level.append(l)
                                desc = array_file[-1]
                                desc = desc[desc.find(b'\n\r')+2:]
                                date = desc[8:16].decode("cp1251")  # Ekb_001_20.11.21
                                desc = desc[16:].decode("cp1251")

                                conf = {'data': datad, 'level': level, 'options': False, 'date': date, 'desc': desc, 'time': time.time(), 'size': file_size}
                                await send_ws_all({'get_graph': conf, 'progress': 0}, user=user)
                            else:
                                com = file_data[8]
                                print('name+', com)
                                save_conf = file_data[10:-1]
                                print(save_conf)
                                faza = ['config', 'A', 'B', 'C',
                                        'A', 'B', 'C', 'A', 'B', 'C']

                                if len(save_conf) >= 16 and faza[int(com)] != 'config':
                                    # incom[addr_ip][faza[int(com)]]['points'] = []
                                    points = []
                                    for x in range(0, len(save_conf), 16):
                                        point = save_conf[x:x+16]
                                        print(point)
                                        # incom[addr_ip][faza[int(com)]]['points']
                                        points.append({
                                            'zav_num': int.from_bytes(point[:4], 'little'),
                                            'num_st': int(point[6]),
                                            'num_grp': int(point[7]),
                                            'diag': int(point[8]),
                                            'level': int(point[9]),
                                            'fon_tok': int(point[10])
                                        })

                                    conf = points

                                else:
                                    strr = ''
                                    for ind, i in enumerate(range(0, len(save_conf), 32)):

                                        strr += save_conf[i:i+32].hex(' ')+' '

                                    conf = strr.split(' ')
                                    if len(conf) < 3:
                                        conf = []

                                # if len(conf) < 3:
                                #    conf = []
                                # print('bliaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                                await save_file(save_conf, str(addr_ip)+"-"+str(com), 'cfg')
                                await notif_ws(addr_ip, "файл принят кс ок", "success")
                                await send_ws_all({'conf': conf}, user=user)

                            await send_ws_all({'files': company['horizont']['files']}, user=user)
                            # print(com)
                            # if faza[int(com)] == 'config':
                            #    incoming[addr_ip]['config'] = strr.split(' ')
                        else:
                            # print('CS bad')
                            await notif_ws(addr_ip, "файл принят кс не сошлась", 'warning')
                    # elif len(file_data) > data_len:
                    #    down_file = False
                    #    await notif_ws(addr_ip, "файл не принят длина больше чем в заголовке", "orange")

                elif start_bit == 149:  # 95 No Answered
                    # Борьба с таймаутами
                    # t_out=settings['reload']*3
                    # print('No answered')

                    obj = struct.unpack('<BBhBB'+str(length-7) +
                                        'sc', data)  # ADR CDM INFO
                    addr_ip = str(obj[2])

                    # if addr_ip in tcp_sess:
                    #    print('есть уже')
                    # else:
                    # print('set tcp_sess',addr_ip)
                    ####################

                    # queue_tcp['horizont'][addr_ip]['msg']
                    # if addr_ip in tcp_sess:
                    #    if tcp_sess[addr_ip].is_closing():
                    # tcp_sess.pop(addr_ip)
                    #        tcp_sess[addr_ip]=writer
                    # else:
                    # if tcp_sess.get(addr_ip,False):
                    if ID not in tcp_sess:
                        incoming[ID]['online'] = True
                        incoming[ID]['fw'] = False
                        incoming[ID]['load'] = False
                        incoming[ID]['dwn'] = False
                        tcp_sess[ID] = writer
                    ###############
                    # ADR CDM INFO
                    ress = await tcp_to_jsn(obj[2], obj[3], obj[5])

                    if obj[3] in [151, 153, 155]:  # 97 99 9b
                        if upload_file[str(obj[2])]:

                            print(type(upload_file[str(obj[2])]), upload_file[str(obj[2])])
                            if isinstance(upload_file[str(obj[2])], dict):
                                write_file = upload_file[str(obj[2])]['name']
                                log.debug(f"отправляю файл {upload_file[str(obj[2])]['name']} на ИП {obj[2]}", extra={'type': 'TCP', 'host': str(addr)})

                                # await asyncio.sleep(0.1)
                                exp = upload_file[str(obj[2])]['name'][-3:]
                                num_f = upload_file[str(obj[2])]['name'][-5]
                                print('отправка', exp, num_f)
                                if exp == 'bin':
                                    # name File
                                    msg = await read_bin(upload_file[str(obj[2])]['name'])
                                    # File no slice
                                    msg = msg_str_f(25, 0, obj[2], msg)
                                elif exp == 'cfg':
                                    msg = await read_bin(upload_file[str(obj[2])]['name'])
                                    msg = msg_str_f(27, 0, obj[2], bytes.fromhex(
                                        '0'+str(num_f))+msg)  # File no slice

                                else:  # GRF
                                    # name File
                                    if 'level' in upload_file[str(obj[2])]:
                                        file_d = upload_file[str(obj[2])]
                                        msg = convert_graf_to_byte(
                                            file_d['data'], file_d['level'], '')
                                        sl = upload_file[str(obj[2])]['slice']

                                        # if sl[1] != 0:
                                        msg = msg[:msg.rfind(b'\xff\xff')+2]
                                        # print(msg)
                                        msg = msg_str_f(
                                            23, 0, obj[2], msg, upload_file[str(obj[2])]['slice'])

                                    else:

                                        ##############
                                        get_fl = await get_files()

                                        # company['horizont']['firmware']
                                        if upload_file[str(obj[2])]['name'] in get_fl:
                                            msg = await read_bin(upload_file[str(obj[2])]['name'], upload_file[str(obj[2])]['slice'])
                                            msg = msg_str_f(23, 0, obj[2], msg, upload_file[str(
                                                obj[2])]['slice'])  # File & slice
                                        else:

                                            # if upload_file[str(obj[2])]['name'] in company['horizont']['files']:
                                            file_d = company['horizont']['files'][upload_file[str(
                                                obj[2])]['name']]
                                            sli = upload_file[str(
                                                obj[2])]['slice']
                                            if sli[0] and sli[1]:
                                                msg = convert_graf_to_byte(
                                                    file_d['data'][sli[0]:sli[0]+sli[1]], file_d['level'][sli[0]:sli[0]+sli[1]], '')
                                                msg = msg[:msg.rfind(
                                                    b'\xff\xff')+2]
                                            else:
                                                # await read_bin(upload_file[str(obj[2])]['name'], upload_file[str(obj[2])]['slice'])
                                                msg = convert_graf_to_byte(
                                                    file_d['data'], file_d['level'], '')
                                            # print(msg)
                                            #

                                            msg = msg_str_f(23, 0, obj[2], msg, upload_file[str(
                                                obj[2])]['slice'])  # File & slice

                                        # else:
                                        #    msg = await read_bin(upload_file[str(obj[2])]['name'], upload_file[str(obj[2])]['slice'])
                                        #    msg = msg_str_f(23, 0, obj[2], msg, upload_file[str(obj[2])]['slice'])  # File & slice

                            elif isinstance(upload_file[str(obj[2])], bytes):
                                print('отправка паролей в', str(obj[2]))
                                msg = msg_str_f(
                                    23, 0, obj[2], upload_file[str(obj[2])], b'\x00\x02\x00\x00')

                            elif isinstance(upload_file[str(obj[2])], str):
                                com = upload_file[str(obj[2])][-1]
                                print('отправка конфигурации', str(obj[2]))
                                msg = bytes.fromhex(
                                    upload_file[str(obj[2])][:-1])
                                msg = msg_str_f(27, 0, obj[2], bytes.fromhex(
                                    '0'+com)+msg)  # +str(num_f)

                            elif isinstance(upload_file[str(obj[2])], list):
                                print('отправка 1 дня в', str(obj[2]))
                                fil = upload_file[str(obj[2])]
                                day = fil[0]
                                msg = ''
                                for indx, fl in enumerate(fil):
                                    if indx != 0:
                                        msg += fl
                                        if len(fil)-1 != indx:
                                            msg += '\t'
                                        else:
                                            msg += '\r\n'
                                print(msg, day)
                                print(msg.encode('ascii'))
                                msg = msg_str_f(23, 0, obj[2], msg.encode(
                                    'ascii'), day.to_bytes(2, byteorder='little')+b'\x01\x00')

                            log.debug(f"начало отправки file \n{byte_to_string(msg)}", extra={'type': 'TCP', 'host': str(addr)})
                            writer.write(msg)
                            # print(msg)
                            await writer.drain()
                            log.debug("конец отправки file", extra={'type': 'TCP', 'host': str(addr)})
                            # print('send file bytes', upload_file[str(obj[2])])
                            # log.debug('send file '+upload_file[str(obj[2])]['name'],extra={'type':'TCP','host':str(addr)})
                            upload_file[str(obj[2])] = False
                            # send_ws_all
                            await send_ws_all(notif_wss(str(obj[2]), 'данные отправлены', 'success'), user=user)
                            incoming[ID]['fw'] = True
                            await send_ws_all({'new': {ID: {'fw': True}}})
                            # await resp.send_str(await notif_wss("","файл "+comm[each][dev_n]+" отправлен","green"))
                        else:

                            if data[-2] == 0:
                                await send_ws_all(notif_wss(str(obj[2]), 'данные получены', 'success'), user=user)
                                if write_file is not None:
                                    exp = write_file[-3:]
                                    if exp == 'grf':
                                        incoming[ID]['graph'] = write_file
                            else:
                                text = ''
                                bnb = byte_to_bin(data[-2])

                                if int(bnb[0]):
                                    text += '<br/>несуществующий код команды [CMD]'
                                if int(bnb[1]):
                                    text += '<br/>контрольная сумма не совпала [CS]'
                                if int(bnb[2]):
                                    text += '<br/>неправильный блок [INFO]'
                                if int(bnb[3]):
                                    text += '<br/>ошибка в заголовке команды [HEAD]'
                                # print(bnb)
                                await send_ws_all(notif_wss(str(obj[2]), text, 'warning'), user=user)
                                # if
                            upload_file.pop(str(obj[2]))
                            print(data[-2], b_In_Slice(data[-2]),
                                  byte_to_bin(data[-2]))
                            incoming[ID]['fw'] = False
                            await send_ws_all({'new': {ID: {'fw': False}}})

                            log.debug(f'файл сохранен в ИП{obj[2]}', extra={'type': 'TCP', 'host': str(addr)})

                elif start_bit == 101:  # 65 Answered
                    if incoming[ID]['fw']:
                        incoming[ID]['fw'] = False
                    # print('Answered')
                    obj = struct.unpack('<BBhB'+str(length-6)+'sc', data)
                    addr_ip = str(obj[2])

                    # if addr_ip in tcp_sess:
                    #    pass
                    # print('')
                    # else:
                    # print('set tcp_sess',addr_ip)
                    ####################
                    # if addr_ip in tcp_sess:
                    #    if tcp_sess[addr_ip].is_closing():
                    #        #tcp_sess.pop(addr_ip)
                    #        tcp_sess[addr_ip]=writer
                    # else:
                    if ID not in tcp_sess:  # FIXME правильно обновлять
                        incoming[ID]['online'] = True
                        incoming[ID]['fw'] = False
                        incoming[ID]['load'] = False
                        incoming[ID]['dwn'] = False
                        tcp_sess[ID] = writer
                    ###############
                    ress = await tcp_to_jsn(obj[2], obj[3], obj[4])
                    # print(obj)
                    start_bit = obj[0]
                    n_bit = obj[1]
                    adr_bit = obj[2]
                    cmd_bit = obj[3]
                    cmd_bit += 128
                    info_bit = obj[4]
                    cs_bit = obj[5]
                    # summ=struct.unpack('>'+str(len(data))+'B',data)
                    # cs=0
                    # for num in summ:
                    #    cs+=num
                    # cs=struct.pack('<i', cs)
                    # print(cs)
                    # print(cs[0])
                    # cs=bytes([256-cs[0]])###########CS
                    if not writer.is_closing():
                        if cs_check(data):
                            # print('CS OK')
                            msg = msg_str_a(cmd_bit, 0, adr_bit, '00')
                            #print(cmd_bit, 'send>OK', msg)
                        else:
                            # print('CS BAD')
                            msg = msg_str_a(cmd_bit, 0, adr_bit, '02')
                            #print(cmd_bit, 'send>BAD', msg)

                        if cmd_bit == 145:
                            print('send answ ->', msg)
                            await send_tcp(ID, msg, now=False)
                            # print(queue_tcp)
                        else:
                            writer.write(msg)
                            await writer.drain()
                    else:
                        print('no send> connect is closing', msg)
                        break

                else:
                    # print(data)
                    # print('bad start bit & part file', length)
                    if down_file:
                        file_data += data

                        #print(f"[{length}] {len(file_data)} = {data_len}")
                        await send_ws_all({'progress': int(len(file_data)/(data_len/100))}, user=user)
                        if len(file_data) >= data_len:
                            file_data = file_data[:data_len]

                            # print(byte_to_string(file_data[:11]))
                            save_conf = file_data[10:-1]
                            strr = ''
                            for ind, i in enumerate(range(0, len(save_conf), 32)):

                                strr += save_conf[i:i+32].hex(' ')+' '

                            conf = strr.split(' ')
                            if len(conf) < 3:
                                conf = []

                            down_file = False
                            incoming[addr_ip]['dwn'] = down_file
                            if cs_check(file_data):
                                # print('CS ok')
                                sub_com = ih(file_data[7])
                                await save_file(file_data[13:-1], str(addr_ip), 'grf')
                                if(sub_com == '87'):  # FIXME разбираем файл графика и шлем обратно
                                    array_file = split_days(file_data[13:-1])  # file_data[13:-1].split(b'\xff\xff')
                                    file_size = len(file_data[13:-1])
                                    print('##############################')
                                    # for day in arr
                                    print(array_file)
                                    print(len(array_file))
                                    datad = []
                                    level = []
                                    for day in array_file[:-1]:
                                        d, l = file_to_array(day)
                                        datad.append(d)
                                        level.append(l)
                                    desc = array_file[-1]
                                    desc = desc[desc.find(b'\n\r')+2:]
                                    date = desc[8:16].decode("cp1251")  # Ekb_001_20.11.21
                                    desc = desc[16:].decode("cp1251")

                                    conf = {'data': datad, 'level': level, 'options': False, 'date': date, 'desc': desc, 'time': time.time(), 'size': file_size}
                                    await send_ws_all({'get_graph': conf, 'progress': 0}, user=user)
                                else:

                                    save_conf = file_data[9:-1]
                                    await save_file(save_conf, str(addr_ip), 'cfg')
                                    await notif_ws(addr_ip, "файл принят кс ок", "success")
                                    await send_ws_all({'conf': conf}, user=user)

                                await send_ws_all({'files': company['horizont']['files']})

                            else:
                                # print('CS bad')
                                await notif_ws(addr_ip, "файл принят кс не сошлась", "warning")
                        # elif len(file_data) > data_len:
                        #    down_file = False
                        #    await notif_ws(addr_ip, "файл не принят длина больше чем в заголовке", "warning")


def get_news(dates):
    if dates:
        print('get news not date', dates)
        newss = {}
        for nn in news:
            print(nn)
            if str(nn) not in dates:
                newss[nn] = news[nn]

        return newss
    else:
        print('get all news')
        return news

##############################


async def wshandler(request: web.Request) -> Union[web.WebSocketResponse, web.Response]:

    global ws_sess
    ip = str(request.remote)
    if ip[:3] == '192':
        # print('local client',ip)
        ips = 'loc'
    else:
        # print('extern client',ip)
        ips = 'ext'
    tkt = request.cookies.get('tkt', False)
    news_read = request.cookies.get('news', False)

    print('news read cookies', news_read)
    if tkt:
        print('tkt is ', tkt)
    print("ips is ", ips)
    resp = web.WebSocketResponse()
    available = resp.can_prepare(request)
    if not available:
        # print('get web UI files')
        head = {

        }
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)
    # FIXME новости ебучие
    # разобраться с новостями СРОЧНО!!!!!
    msg = {"connect": True, "news": get_news(news_read)}
    user = 'guest'

    await resp.send_json(msg)

    addr_ip = 0
    print('start ws code', user)
    try:
        # print("Someone joined.")
        for ws in request.app["sockets"]:
            log.info(f'connect user ip: {ip}', extra={'type': 'WSS', 'host': str(ip)})
            # msg={"connect":True}    #Вы подключились
            # await ws.send_str(json.dumps(msg))

        request.app["sockets"].append(resp)
        ws_sess = request.app["sockets"]
        # print(tcp_sess)
        # print(request.app["sockets"])

        async for msg in resp:
            jsn = json.loads(msg.data)

            # print(jsn)
            for token, datas in jsn.items():
                for comm, data in datas.items():
                    # print(token, 'neww', comm, data)
                    pass
            # print(jsn['id'])
            # print(noww())
            for each in jsn:
                if each != 'false' and each in user_sess:
                    user = user_sess[each]['name']
                comm = jsn[each]
                """НЕЗАБЫТЬ РАЗОБРАТЬСЯ"""
                # if each in user_sess:
                #    print('session true',ip,each)
                # else:
                #    print('session false',ip,each)
                # return
                # Разбираем JSON
                # print('########JSN################')
                # print(jsn)
                # print('########JSN################')
                # print(jsn[each])
                # print('########JSN################')
                text = ''
                color = 'green'
                # print(comm)
                # print('########JSN################')
                for each in comm:
                    print('WS>>', user, each, comm[each], ip)
                    if each not in users[user]['rule']:
                        if each != 'ping':
                            answer = notif_wss(
                                user, 'вам недостаточно привилегий!!! '+each, 'warning')
                            await resp.send_json(answer)
                            continue

                    if ws_command_list.get(each, False):
                        # print('play')
                        if each == 'auth':
                            answer = await ws_command_list[each]({}, ip, comm[each])
                        else:
                            answer = await ws_command_list[each]({}, token, comm[each])
                    else:
                        # print('неизвестная команда', each)
                        answer = notif_wss("", 'неизвестная команда '+each, 'error')
                        # await resp.send_json([])

                    # print(answer)
                    if answer is not None and len(answer):
                        # answer.update
                        # au =
                        if answer.get('auth', False):
                            ttkn = answer.get('TKT', False)
                            if ttkn:
                                user_sess[ttkn]['ws'] = resp
                                user_sess[ttkn]['host'] = ip
                            else:
                                user_sess[token]['ws'] = resp
                                user_sess[token]['host'] = ip
                        # print(answer)
                        await resp.send_json(answer)

            """
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not resp:
                        await ws.send_str(msg.data)
                    else:
                        print(ws)
                        await ws.send_str(json.dumps(incom))
            else:
                return resp
            """
        return resp

    finally:
        request.app["sockets"].remove(resp)
        print("Someone disconnected.", tkt, user)
        # TODO разобраться с этим
        # FIXME разобраться с этим
       # if tkt in user_sess:
        # user_sess[tkt].pop('ws')  # ['time'] = int(time.time()) + 1800
        # for ws in request.app["sockets"]:
        #    pass
        # await ws.send_str("Someone disconnected.")#кто то отключился


# {'horizont': {'98': {'time': 123123, 'msg': [b'\xff'], 'retry': 1}}}
async def tcp_queue():
    print('start tcp_queue')

    time_com = {
        '01': 3,
        '03': 3,
        '05': 7,
        '07': 15,
        '0b': 3,
        '0f': 3,
    }

    while True:
        now = get_up_time()
        answer = {}
        pop_id = []

# FIXME !!!!!
# """
# _GatheringFuture exception was never retrieved
# future: <_GatheringFuture finished exception=RuntimeError('dictionary changed size during iteration')>
# Traceback (most recent call last):
#  File "/home/pi/hi/public/web.py", line 2878, in tcp_queue
#    for ID, msgs in queue.items():
# RuntimeError: dictionary changed size during iteration
# """

        for comp, queue in queue_tcp.items():
            for ID, msgs in queue.items():
                if len(msgs['msg']) and msgs['time'] <= now:

                    cmd = msgs['msg'][0][4]
                    cmd = '0'+hex(cmd)[2:]
                    if cmd in time_com:
                        msgs['time'] = now+time_com[cmd]  # settings['replay']
                        print(f'CMD {now} timeout', cmd, time_com[cmd])
                    else:
                        msgs['time'] = now+2
                        print(f'DEF {now} timeout', cmd)

                    if msgs['retry'] < settings['retry']:

                        # print('###############################')
                        # print('resend msg', msgs['msg'][0], now)
                        if msgs['msg'][0][0] == 149:  # x95
                            log.info(f">>>{comp} timeout answer {byte_to_string(msgs['msg'][0])}", extra={'type': 'TCP', 'host': str(ID)})
                        else:
                            log.info(f">>>{comp} retry {msgs['retry']}\n{byte_to_string(msgs['msg'][0])}", extra={'type': 'TCP', 'host': str(ID)})
                        msgs['retry'] += 1

                        if ID in tcp_sess:  # ConnectionResetError: 'Connection reset by peer' #FIXME
                            if not tcp_sess[ID].is_closing():
                                tcp_sess[ID].write(msgs['msg'][0])
                                await asyncio.wait_for(tcp_sess[ID].drain(), timeout=5)
                        # else:
                        #    msgs['msg'].pop(0)

                        if msgs['msg'][0][0] == 149:  # x95
                            msgs['retry'] = 1
                            msgs['msg'].pop(0)
                            # if len(msgs['msg']) == 0:
                            #    pop_id.append({comp: ID})
                            # print('###############################')
                            # print(queue_tcp)
                    else:
                        # if not msgs['retry']:
                        msgs['retry'] = 1
                        print(f"пакет не доставлен\n{byte_to_string(msgs['msg'][0])}")
                        msgs['msg'].pop(0)
                        answer.update(notif_wss(ID, 'пакет не доставлен', 'critical'))
                        answer.update({'new': {ID: {'load': False}}})
                        await send_ws_all(answer)

                        # if len(msgs['msg']) == 0:
                        # pop_id.append({comp: ID})

        # for idd in pop_id:
        #    for cm, dev in idd.items():
        #        queue_tcp[cm].pop(dev)

        # for msg in [msg for msg in data if msg['time'] <= now]:
        # tcp_sess[ID].write(msg)
        # print('send msg', msg[0])
        # msg.pop(0)
        await asyncio.sleep(0.5)

ws_reload = 0


async def waiter():
    loop = 0
    global ws_reload
    print('start waiter & aioinflux')
    ws_reload = await get_size('build/bundle.js')
    perf = time.perf_counter()
    mono = time.monotonic()
    # print(await infl_client.drop_measurement('98'))
    # print(await infl_client.drop_measurement('99'))
    while True:

        uptime = get_up_time()
        if uptime >= 150 and uptime < 170:
            for ink, obj in incoming.items():
                if obj['online'] and not ink in tcp_sess:
                    obj['online'] = False
                    obj['fw'] = False
                    obj['load'] = False
                    obj['dwn'] = False
                    await send_ws_all({'new': {ink: obj}})
                    point = {
                        'measurement': str(ink),
                        'fields': {
                            'buf_1_volt': incoming[str(ink)]['bufs'][0]['vol'],
                            'buf_2_volt': incoming[str(ink)]['bufs'][1]['vol'],
                            'buf_3_volt': incoming[str(ink)]['bufs'][2]['vol'],
                            'buf_1_amp': float(incoming[str(ink)]['bufs'][0]['amp']),
                            'buf_2_amp': float(incoming[str(ink)]['bufs'][1]['amp']),
                            'buf_3_amp': float(incoming[str(ink)]['bufs'][2]['amp'])
                        },
                        'tags': {'status': 'offline'}
                    }

                    await infl_client.write(point)
                    events.append({str(ink): {"msg": "потеря связи", "ts": noww(), "st": "offline"}})
                    await send_ws_all({"events": events})

                # user_sess.items():
            for token in [tkt for tkt in user_sess if user_sess[tkt].get('ws') is None]:
                user_sess.pop(token)

        times = int(time.time())
        off_list = []
        for token, sess in user_sess.items():
            # print(sess)
            if sess['time'] < times:
                off_list.append(token)
        print(off_list)
        for pop in off_list:
            # await send_ws_all({"auth": None}, user=user_sess[pop]['name'])
            ans = 'no ws'
            if 'ws' in user_sess[pop]:
                ans = 'with ws'
                await user_sess[pop]['ws'].send_json({"auth": None})
            print("session", pop, user_sess[pop]['name'], "time off", ans)
            user_sess.pop(pop)

            # print("##SESSIONS###")
            # for sess in user_sess:
            #    print("TKT#",sess)
            #    print("ID#",user_sess[sess]['name'])
            #    tt=int(user_sess[sess]['time'])-times
            #    print(tt,"сек")
            # print("#############")
            # print("TCP SESSIONS")
            # for tcp in tcp_sess:
            #    print(tcp,"->",tcp_sess[tcp])
            # print(settings['reload'])

        # except Exception as ex:
        #    log.warning(f'ошибка в цикле {type(ex).__name__}', extra={'type': 'TCP', 'host': 'sys'})
#########################
        # if settings['reload']:
        #    await asyncio.sleep(settings['reload'])
        # else:
        print('sleep waiter now:', uptime)  # , 'perf:', time.perf_counter()-perf, 'mono:', time.monotonic()-mono)
        await asyncio.sleep(10)
##########################


async def on_shutdown(app: web.Application) -> None:
    for ws in app["sockets"]:
        await ws.close()


def init() -> web.Application:
    app = web.Application()
    app["sockets"] = []
    app.router.add_static("/build", root_path+'/build', show_index=True, append_version=True)
    app.router.add_static("/assets", root_path+'/assets', show_index=True, append_version=True)
    app.router.add_static("/img", root_path+'/img', show_index=True, append_version=True)
    app.router.add_static("/file", root_path+'/file', show_index=True, append_version=True)
    app.router.add_static("/mp3", root_path+'/mp3', show_index=True, append_version=True)
    # app.router
    app.router.add_get("/{tail:.*}", wshandler)
    app.on_shutdown.append(on_shutdown)
    return app


ports = (40802,)


async def rel():
    if ws_reload != await get_size('build/bundle.js'):
        print('WS RELOADS!!!')
        await send_ws_all({'reload': True})
    await save_cfg()
    print('reload What !!!')
    await infl_client.close()


def main():
    loop = asyncio.get_event_loop()

    # await icon.run(
    # await asyncio.gather(
    #    web._run_app(init(), host='192.168.11.237'),
    # webbrowser.open_new('http://192.168.11.237:8080'),
    # icon.notify('Вы запустили приложение '+__file__)
    # )

    log.debug('start server', extra={'type': 'SYS', 'host': '127.0.0.1'})
    # tcp

    for name, comp in company.items():  # 40802
        for port in comp['ports']:
            asyncio.gather(asyncio.start_server(handle_tcp, '0.0.0.0', port, limit=12, reuse_port=name,
                           reuse_address=name), start_msg(f'start tcp {port} for company {name}'))  # , loop=loop
    asyncio.gather(web._run_app(init(), host='0.0.0.0', port=40810,
                   print=None), start_msg('start ws ui '+'0.0.0.0'+':40810'))
    asyncio.gather(waiter())
    asyncio.gather(dp.start_polling())
    asyncio.gather(tcp_queue())
    # asyncio.gather(asyncio.start_server(handle_tcp, '0.0.0.0', 40802, limit=12),start_msg('start tcp '+'0.0.0.0'+':'+str(40802)))
    # asyncio.gather(logg())
    # asyncio.gather(web_br_op())

    try:
        # icon.visible = True
        loop.run_forever()
    except KeyboardInterrupt:
        # icon.visible = False
        pass

    finally:
        loop.run_until_complete(rel())


def byte_to_string(data, leng=16):
    strr = ''
    for i in range(0, len(data), leng):
        strr += (data[i:i+16].hex(':'))+'\n'
    return strr


# tcp_to_json_list= [obj for (name,obj) in vars().items() if hasattr(obj, '__class__') and obj.__class__.__name__ == 'function' and obj.__name__ == 'wrap']
if __name__ == '__main__':
    privileges = [priv for priv in ws_command_list]
    for st, fn in tcp_funct_list.items():
        print('tcp api', st, fn)

    for st, fn in ws_command_list.items():
        print('ws api', st, fn)

    # print('😀')
    main()


"""
        try:
            loop += 1
            # log.debug()
            ##############################
            uptime = get_up_time()
            if uptime >= 150 and uptime < 170:
                for ink, obj in incoming.items():
                    if obj['online'] and not ink in tcp_sess:
                        obj['online'] = False
                        await send_ws_all({'new': {ink: obj}})

                for token in [tkt for tkt in user_sess if user_sess[tkt].get('ws') is None]:  # user_sess.items():
                    user_sess.pop(token)

            for name, obj in company.items():
                # if obj.get('task') is None:#на случай правки старых компаний
                #    obj['task'] = []
                for task in obj['task']:
                    log.debug(f"company {name} start task {task}", extra={'type': 'TCP', 'host': '127.0.0.1'})

            ################################
            log.debug(f"[{uptime}]waiter circle {loop}", extra={'type': 'TCP', 'host': '127.0.0.1'})
            transport = requests.get('http://map.ettu.ru/api/v2/troll/boards/?apiKey=111&order=1').json()['vehicles']
            # await send_ws_all({'tran': transport})
            print('send transport')
            dlina = len(tcp_sess)
            if dlina > 0:

                for each in []:  # tcp_sess:
                    # if loop>10:
                    #    incoming[str(adr)]['bufs'][2]['online'] = bool(int(mod_c[7]))
                    if each in upload_file:
                        print('ИП', each, 'еще принимает файл', upload_file[each])

                        # log.critical('ИП'+str(each)+'еще принимает файл'+str(upload_file[each]['name']),extra={'type':'WSS'})
                    else:
                        # print(each ,clients[each]['a'],clients[each]['id_n'])
                        if not tcp_sess[each].is_closing():
                            msg = msg_str_q(1, 0, int(each))
                        # msg=b'\xFF\xFF\xFF\xFF'
                        # print(tcp_sess[each].is_closing(),'send>len',len(msg), msg)
                        # print(tcp_sess[each].transport.get_write_buffer_limits())
                            tcp_sess[each].write(msg)
                            print('опрос состояния ип', each)
                            # print('send dataip',each)
                            await asyncio.wait_for(tcp_sess[each].drain(), timeout=5)
                            # print('stop send dataip',each)
                        else:
                            print('funct is close', each)
"""
