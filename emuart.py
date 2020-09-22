import struct, re, binascii
import libscrc,time


# Ascii字符串转换为16进制字符串，每个字用空格隔开
def asciiB2HexString(strB):
    strHex = binascii.b2a_hex(strB).upper()
    print(strHex)
    return re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", strHex.decode()) + " "


# 16进制字符串转换为16进制字节串
def hexStringB2Hex(hexString):
    dataList = hexString.split(" ")
    j = 0
    for i in dataList:
        if len(i) > 2:
            return -1
        elif len(i) == 1:
            dataList[j] = "0" + i
        j += 1
    data = "".join(dataList)
    try:
        data = bytes.fromhex(data)
    except Exception:
        return -1
    # print(data)
    return data


class Emuart(object):
    def __init__(self, com):
        self.have_ue_flag = False
        self.frame_head = 'a5 06'
        self.frame_tail = 'b6 07'
        self.com = com

    def connect_device(self):
        ret = 0
        self.com.baudrate = 115200
        self.com.bytesize = 8
        self.com.parity = 'N'
        self.com.stopbits = 1
        self.com.timeout = None
        self.com.open()
        ret += 1
        print("open success")
        data = '[Are you an emuart??]'
        self.com.write(self.emuart_frame(data))
        time.sleep(0.1)
        length = max(1, min(2048, self.com.in_waiting))
        bytes = self.com.read(length)
        if bytes != None:
            self.emuart_unframe(bytes)
            print(re.search(b"\xa5\x06.*\xb6\x07", bytes))
            print(struct.unpack(">H", bytes[-4:-2]))
            print(bytes[-4:-2])
            print(bytes)

        # if
        #     # self.receiveProcess = threading.Thread(target=self.receiveData)
        #     # self.receiveProcess.setDaemon(True)
        #     # self.receiveProcess.start()
        # except Exception as e:
        #     self.com.close()
        #     self.receiveProgressStop = True
        #     print(e)
        #     # self.errorSignal.emit( parameters.strOpenFailed +"\n"+ str(e))
        #     # self.setDisableSettingsSignal.emit(False)
    def emuart_unframe(self, data):
        re.search(b"\xa5\x06.*\xb6\x07", bytes)

    # 组帧
    def emuart_frame(self, data):
        data = asciiB2HexString(data.encode())
        data = hexStringB2Hex(data)
        crc_res = libscrc.modbus('[Are you an emuart??]'.encode())
        frame = hexStringB2Hex(self.frame_head) + struct.pack('>H', len(data)) + data + \
                struct.pack('>H', crc_res) + hexStringB2Hex(self.frame_tail)
        return frame

    def shake_hand(self):
        shake_info = b"a5 06 00 15 5b 41 72 65 20 79 6F 75 20 61 6e 20 65 6d 75 61 72 74 3f 3f 5d 61 34 b6 07"

    pass
