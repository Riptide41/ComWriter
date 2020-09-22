import struct, re, binascii
import libscrc,time


# Ascii字符串转换为16进制字符串，每个字用空格隔开
def asciiB2HexString(strB):
    strHex = binascii.b2a_hex(strB).upper()
    # print(strHex)
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
    ask_info = '[Are you an emuart??]'
    def __init__(self, com):
        self.have_ue_flag = False
        self.frame_head = 'a5 06'
        self.frame_tail = 'b6 07'
        self.com = com

    # 连接设备
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
        self.com.write(self.emuart_frame(self.ask_info))
        time.sleep(0.1)
        length = max(1, min(2048, self.com.in_waiting))
        read_bytes = self.com.read(length)
        if read_bytes is not None:
            ret = self.emuart_unframe(read_bytes)
            print(ret)

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

    # 解帧
    def emuart_unframe(self, bytes):
        datas = re.findall(b"\xa5\x06(.*)\xb6\x07", bytes)
        for data in datas:
            re_crc = struct.unpack(">H", bytes[-4:-2])
            data = data[2:-2]
            if re_crc[0] != libscrc.modbus(data):
                return 0
            return data
            pass

    # 组帧
    def emuart_frame(self, data):
        data = asciiB2HexString(data.encode())
        data = hexStringB2Hex(data)
        crc_res = libscrc.modbus(self.ask_info.encode())
        frame = hexStringB2Hex(self.frame_head) + struct.pack('>H', len(data)) + data + \
                struct.pack('>H', crc_res) + hexStringB2Hex(self.frame_tail)
        return frame


    pass
