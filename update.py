# insert_data包含帧类型，分块数，每块起始地址列表，每块长度列表，数据字符串
# 为什么叫插入帧我也不知道，应该是有其他类型帧的功能还没有实现
class Update(object):
    update_frame = []  # 成员为insert_data字典
    check = []  # 存放写入帧的情况

    index = 0

    def __init__(self, dicts):
        self.dicts = dicts
        self.generate_update_frame()  # 生成升级帧列表
        self.generate_return_data()

    def generate_update_frame(self):
        idata = {"seg_num": 0}  # 字典，存放insert_data数据
        for dict in self.dicts:
            new_addr = dict["data_addr"]
            length = dict["data_len"]
            data = dict["data"]
            if idata["seg_num"] is 0:
                idata = {"type": 2, "seg_num": 1, "addr": [new_addr], "len": [length], "data": data}
            else:
                length_sum = sum(idata["len"])
                if length_sum + length > 400 or idata["seg_num"] >= 12:
                    self.update_frame.append(idata)
                    idata = {"type": 2, "seg_num": 1, "addr": [new_addr], "len": [length], "data": data}
                else:
                    if idata["addr"][-1] + idata["len"][-1] == new_addr:
                        idata["data"] += data
                        idata["len"][-1] += length
                    else:
                        idata["addr"].append(new_addr)
                        idata["len"].append(length)
                        idata["seg_num"] += 1
                        idata["data"] += data
        self.update_frame.append(idata)

    def generate_return_data(self):
        self.frame_data = []
        # 计算更新数据长度
        code_size = self.dicts[-1]["data_addr"] + self.dicts[-1]["data_len"] - self.dicts[0]["data_addr"]
        self.frame_sum = len(self.update_frame) + 3  # 帧总数,除了insert_data 外还有1更新开始帧，1更新检查帧，1更新命令帧
        self.check = [0] * self.frame_sum
        print(len(self.update_frame))
        self.update_frame.insert(0, {"type": 0, "style": 0, "frame_num": self.frame_sum, "cur_num": 0, "code_size": code_size})
        self.update_frame.append({"type": 3, "cur_num": len(self.update_frame)})
        self.update_frame.append({"type": 4, "cur_num": len(self.update_frame)})
        cur_num = 0
        for frame in self.update_frame:
            if frame["type"] == 0:
                data = frame["type"].to_bytes(1, "little") + frame["style"].to_bytes(1, "little") \
                       + frame["frame_num"].to_bytes(2, "little") + cur_num.to_bytes(2, "little") \
                       + frame["code_size"].to_bytes(4, "little")
                cur_num += 1
            if frame["type"] == 2:
                data = frame["type"].to_bytes(1, "little") + cur_num.to_bytes(2, "little") \
                       + frame["seg_num"].to_bytes(1, "little")
                add_num = 0
                for addr in frame["addr"]:
                    add_num += 1
                    data += addr.to_bytes(4, "little")
                while add_num < 12:
                    data += (0).to_bytes(4, "little")
                    add_num += 1
                len_num = 0
                for length in frame["len"]:
                    len_num += 1
                    data += length.to_bytes(2, "little")
                while len_num < 12:
                    data += (0).to_bytes(2, "little")
                    len_num += 1
                data += frame["data"]
                if len(frame["data"]) != 400:
                    l = 400 - len(frame["data"])
                    data += (0).to_bytes(l, "little")
                cur_num += 1
            if frame["type"] == 3:
                data = frame["type"].to_bytes(1, "little") + cur_num.to_bytes(2, "little") + b"\x00" * 81
                cur_num += 1
            if frame["type"] == 4:
                data = frame["type"].to_bytes(1, "little") + cur_num.to_bytes(2, "little")
                cur_num += 1
            self.frame_data.append(data)

    def get_next_index_frame(self):
        # index = self.check.index(0)
        # if index >= len(self.check) - 1:
        #     if index == len(self.check) - 1:  # 下一帧为更新命令帧时无需返回
        #         self.check[index] = 1
        #         return self.frame_data[index]
        #     else:
        #         return None    # 全部发送结束返回None
        # else:
        #     return index, self.frame_data[index]
        if self.index < len(self.check):

            print(self.index, len(self.frame_data))
            print(self.frame_data[self.index])
            self.index += 1
            return self.index-1, self.frame_data[self.index-1]
        return None


