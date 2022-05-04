######################
ws_command_list = {}


def ws_api(command):
    #print("start decor")
    def decor(func):
        # print("pre")
        for st in command.split(':'):
            ws_command_list[st.lower()] = func
        # async def wrap(ID,data):
            # print('wrap')
            #print('what is my wrap')
            # print(bytes.fromhex(start_bit), bytes([data[0]])) bytes.fromhex('','little')
            # if bytes([data[0]]) in bytes.fromhex(start_bit.replace(':','')):
            # await func(ID,data)
            # return

        # return wrap
    return decor


###########
tcp_funct_list = {}


def tcp_to_json(start_bit):
    def decor(func):
        for st in start_bit.split(':'):
            tcp_funct_list[st.lower()] = func
        # async def wrap(ID,info):
            # print(bytes.fromhex(start_bit), bytes([data[0]])) bytes.fromhex('','little')
            # if bytes([data[0]]) in bytes.fromhex(start_bit.replace(':','')):
        #    await func(ID,info)
        #    return

        # return wrap
    return decor

###################################################


if __name__ == '__main__':
    """egor = 'false'
    print(bool(egor))
    bb = b'\x01\x02\x02'
    print(bb.hex())
    pp = bb.hex()
    print(bytes.fromhex(pp))
    print(pp[0:-1])
    points = [
        {'zav_num': 2162688, 'num_st': 22, 'num_grp': 0},
        {'zav_num': 2000000, 'num_st': 0, 'num_grp': 0},
        {'zav_num': 23423, 'num_st': 0, 'num_grp': 0},
        {'zav_num': 333, 'num_st': 0, 'num_grp': 0}
    ]
    rev = b''
    for ar in points:
        rev += ar['zav_num'].to_bytes(4, byteorder='little')
        print(rev)
        rev += b'\x00'*2
        rev += ar['num_st'].to_bytes(1, byteorder='little')
        rev += ar['num_grp'].to_bytes(1, byteorder='little')
        rev += b'\x00'*8
    rev = rev.hex()
    print((2162688).to_bytes(4, byteorder='little'))
    """
    dictionary = ''
    with open('C:/russian.txt', 'r') as fl:
        dictionary = fl.read()
    dictionary = dictionary.splitlines()
    #dictionary = ['кот', 'ток', 'крот', 'картотека', 'собака', 'хаха', 'ляля']
    #letters = 'кротатаек'
    # print(dictionary)
    #answer = []
    # for let in letters:
    #    dictionary = [dic for dic in dictionary if let in dic]
    #print(let, dictionary)
    tem = b'v8\x05\x00\x00\x00\x02\x02\x00\x00\x00\x00\x00\x00\x00\x00'

    gem = b'\x01\x00'
    gg = 256
    #print(gg.to_bytes(2, byteorder='little'), int.from_bytes(gem, 'little'))
    print(len(tem))
