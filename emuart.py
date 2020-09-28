import binascii
import re
import struct

import libscrc
import time


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
    return data


# 存放采集到的串口信息
class DeviceInfo(object):
    def __init__(self, bytes):
        self.uecom_type = bytes[0:24].decode("ascii")
        self.mcu_type = bytes[25:45].decode("ascii")
        self.U_Start_Ads = struct.unpack("<I", bytes[45:49])[0]
        self.U_code_size = struct.unpack("<I", bytes[49:53])[0]
        self.replace_num = struct.unpack("<I", bytes[53:57])[0]
        self.reserve_num = struct.unpack("<I", bytes[57:61])[0]
        self.bios_version = bytes[61:69].decode("ascii")


class Emuart(object):
    ask_info = '[Are you an emuart??]'
    shake_info = "\nshake"
    frame_head = 'a5 06'
    frame_tail = 'b6 07'
    terminate_info = 'StOpUeMySeLf'
    update_info = '\vupdate'

    def __init__(self, com):
        self.have_ue_flag = False
        self.com = com

    # 组帧发送字符串并接收返回数据进行解帧返回
    def send_and_receive(self, data, wait_time=500, cnt=1):
        if not self.com.is_open or len(data) == 0:
            return False
        if not isinstance(data, bytes):
            data = data.encode()
        if wait_time is 0:
            self.com.write(self.emuart_frame(data))
            return
        while cnt is not 0:
            # print(self.emuart_frame(data))
            self.com.flushInput()
            self.com.write(self.emuart_frame(data))
            try_time = 0
            while try_time != wait_time / 4:
                time.sleep(0.05)
                if self.com.in_waiting:
                    length = max(1, min(2048, self.com.in_waiting))
                    read_bytes = self.com.read(length)
                    # print("receive:", read_bytes)
                    if read_bytes is not None:
                        # print("unframe:", self.emuart_unframe(read_bytes))
                        return self.emuart_unframe(read_bytes)
                try_time += 1
            cnt -= 1
        return False

    # 连接设备
    def connect_device(self):
        try:
            self.com.baudrate = 115200
            self.com.bytesize = 8
            self.com.parity = 'N'
            self.com.stopbits = 1
            self.com.timeout = None
            self.com.open()
            # print("open success")
            # self.com.write(self.emuart_frame(self.ask_info))
        except Exception as e:
            self.com.close()
            return 2, None  # 返回2打开串口失败
        res = self.send_and_receive(self.ask_info, 500, 1)
        if res != b"[Yes,I am an emuart!!]":
            self.com.write(self.terminate_info.encode())    # 终结下位机组帧状态
            self.com.close()
            return 1, None  # 返回1打开串口成功但未接收程序
        else:
            res = self.send_and_receive(self.shake_info, 100, 3)  # 成功识别，发送握手帧
            if res:
                try:
                    self.device_info = DeviceInfo(res)
                except Exception as e:
                    # print(e)
                    return 3, None
                return 0, self.device_info    # 握手成功，返回设备信息
            else:
                # print("error:",res)
                return 3, None

    # 解帧
    def emuart_unframe(self, bytes):
        datas = re.findall(b"\xa5\x06([\s\S]*)\xb6\x07", bytes)
        for data in datas:
            re_crc = struct.unpack(">H", bytes[-4:-2])
            data = data[2:-2]
            # print(data)
            # print("crc", re_crc)
            if re_crc[0] != libscrc.modbus(data):
                return 0

            return data
            pass

    # 组帧

    def emuart_frame(self, bytes):
        crc_res = libscrc.modbus(bytes)
        frame = hexStringB2Hex(self.frame_head) + struct.pack('>H', len(bytes)) + bytes + \
                struct.pack('>H', crc_res) + hexStringB2Hex(self.frame_tail)
        return frame

    pass
