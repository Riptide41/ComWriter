
import os
from toolz import reduce
import re
from emuart import hexStringB2Hex

def char2hex(line):
    line = list(map(ord, list(line)))
    for num in range(len(line)):
        if 0x30 <= line[num] <= 0x39:
            line[num] = line[num] - 0x30
        elif 0x41 <= line[num] <= 0x5A:
            line[num] = line[num] - 55
        else:
            pass
    for i in range(0, len(line), 2):
        line[i] = line[i] * 16 + line[i + 1]
        newline = line[::2]
    return newline


class Hex(object):
    def __init__(self):
        self.hex_dicts = []
        self.hex_string = []
        self.addr_offset = 0

    def load_file(self, file_path):
        file_name = os.path.basename(file_path)
        file_type = file_path.split(".")[-1]
        if file_name == "" or file_type != "hex":
            return 1  # 输入文件失败
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
        except Exception:
            return 2  # 打开文件失败返回2
        for line in lines:  # 此循环内可加判断hex是否全读取成功
            self.add_dict(line.strip())
            self.hex_string.append(line)
        return 0  # 成功返回0

    def add_dict(self, line):
        hex_dict = {}  # 初始化字典放置每行信息
        if line[0] != ":":
            # print(line[0])
            return 1
        hex_dict["data_len"] = int(line[1:3], 16)
        if len(line) != 2 * hex_dict["data_len"] + 11 or hex_dict["data_len"] == 0:
            # print(hex_dict["data_len"], len(line))
            return 2  # 最后一行或数据长不匹配返回
        hex_dict["data_type"] = int(line[7:9], 16)
        if hex_dict["data_type"] not in (0, 1, 2, 4):
            return 1
        if hex_dict["data_type"] == 2:
            self.addr_offset = int(line[9:13], 16) << 4
            return 0
        elif hex_dict["data_type"] == 4:
            self.addr_offset = int(line[9:13], 16) << 16
            return 0
        hex_dict["data_addr"] = int(line[3:7], 16) + self.addr_offset
        data = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", line[9:9 + hex_dict["data_len"] * 2])
        hex_dict["data"] = hexStringB2Hex(data)
        # 以下用作校验hex行
        line = char2hex(line[1:])
        check_sum = (0x100 - (reduce(lambda x, y: x + y, line[:-1]) % 256)) % 256
        if check_sum == line[-1]:
            hex_dict["check"] = line[-1]
            # print(hex_dict)
            self.hex_dicts.append(hex_dict)
            return 0
        else:
            return 3
