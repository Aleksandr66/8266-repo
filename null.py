bufs = {
    "type": None,  # -00 - нет блока
    # -01 - БУФ021 - 100А
    # -10 - БУФ024 - 50А
    # -11 - БУФ0хх - 25А
    "I": None,
    "U": None,
    "amp": None,
    "vol": None,
    "acc": None,  # OK HC K3
    "mode": None,  # "false" - тумблер в положении "АВТОМАТ", "true" - "РУЧ"
    "line": None,  # true на фазе 220В и нет аварий
    "state": None,  # канал ответил (включен)
    "delta": {"I": None, "U": None},
    "points": []
}

null_dev = {
    "online": False,  # True False
    "status": None,  # Normal Fire Emergency Security
    "struct": None,  # 0x01 - БК100-07, БКС12, КМ024
    # 0x02 - БК100-07, КМ024
    # 0x11 - БУР, БКС12, КМ024
    "label": "",
    "name": "",
    "notes": None,  # Записульки
    # "city":None,
    "type": None,  # old new0 new1 new2
    "addr": None,
    "config": None,
    "coord": [0, 0],
    "keys": [None, None],
    "door": None,  # True False
    "bks": None,  # - 0x10 - БКС12 - 16 входов - 0x30 - КС053
    "count": None,  # Меркурий 230 CE301
    "counts": {},
    "bufs": [bufs, bufs, bufs],
    "pass": [],
    "timeout": 0,
    "graph": None,
    "fw": False
}

null_company = {
    'name': None,
    'city': None,
    'task': [],
    'ports': [],
    'events': [],
    'device': {},
    'pages': {},
    'design': {},
    'files': {},
    'bk_pass': []
}

null_user = {
    "name": None,
    "photo": "",
    "pages": {},
    "passw": None,
    "2fa": None,
    "bindip": None,
    "local": False,
    "company": None,
    "rule": []
}


def without_keys_group(dc, *args):
    new_dc = {}
    for ndc in dc:
        new_dc[ndc] = {x: dc[ndc][x] for x in dc[ndc] if x not in args}
    return new_dc


def without_keys(dc, *args):
    return {x: dc[x] for x in dc if x not in args}


print(without_keys(null_dev, 'bks', 'count', 'label', 'online'))
lc = int(f'000{int(True)}0{int(True)}0{int(True)}', 2).to_bytes(1, 'big').hex()
lc = int(f'000{int(False)}0{int(False)}0{int(True)}', 2).to_bytes(1, 'big').hex()
lc = int(f'000{int(False)}0{int(True)}0{int(False)}', 2).to_bytes(1, 'big').hex()
print(lc)
print(bool(b'\x00'[0]))
