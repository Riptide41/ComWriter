import Mainwindow_Ui
from PyQt5 import QtCore
import sys
import threading
import serial
import serial.tools.list_ports
import emuart
import parsehex

import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog


class MainWindow(QMainWindow):
    detecting_port_flag = False
    receive_progress_stop_flag = True
    ui = Mainwindow_Ui.Ui_MainWindow()
    com = serial.Serial()
    setDisableSettingsSignal = QtCore.pyqtSignal(bool)
    show_error_message_signal = QtCore.pyqtSignal(int)
    read_file_error_signal = QtCore.pyqtSignal(int)
    display_hex_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui.setupUi(self)
        self.timer_redetect = QtCore.QTimer()
        self.start_stop_detect(True)  # 每1s重新检测串口一次
        self.init_event()
        self.serial_port_detect()

    def init_event(self):
        self.ui.cmb_port.signal_hidden_popup.connect(self.start_stop_detect)
        self.ui.cmb_port.signal_show_popup.connect(self.start_stop_detect)
        self.timer_redetect.timeout.connect(self.serial_port_detect)
        self.ui.btn_open_close_port.clicked.connect(self.open_close_port)
        self.setDisableSettingsSignal.connect(self.disable_setting)
        self.show_error_message_signal.connect(self.connect_serial_failed_message)
        self.ui.btn_select_file.clicked.connect(self.select_file)
        self.ui.btn_open_file.clicked.connect(self.open_hex_file)
        self.read_file_error_signal.connect(self.open_file_error_meesage)
        self.display_hex_signal.connect(self.display_hex)

    def select_file(self):
        file_path = QFileDialog.getOpenFileName(self, "选择文件", "", "Hex Files(*.hex)")
        print(file_path)
        self.ui.le_file_path.setText(file_path[0])

    def open_hex_file(self):
        t = threading.Thread(target=self.open_hex_file_process)
        t.setDaemon(True)
        t.start()

    def display_hex(self):
        self.ui.tb_hex_file.document().clear()
        t = threading.Thread(target=self.display_hex_process,args=(self.ui.tb_hex_file, self.hex.hex_string))
        t.start()

    # def slot1(self):
    #     def _slot1(textBrowser, hex_string):
    #         for line in hex_string:
    #             textBrowser.append(line)  # 文本框逐条添加数据
    #             textBrowser.moveCursor(textBrowser.textCursor().End)  # 文本框显示到底部
    #             time.sleep(0.2)
    #     threading.Thread(target=_slot1, args=(self.ui.tb_hex_file, self.hex.hex_string)).start()
    def display_hex_process(self, tb, lines):

        # tb.document().clear()
        for line in lines:
            tb.append(line)
            time.sleep(0.001)
        pass

    def open_hex_file_process(self):
        file_path = self.ui.le_file_path.text()
        self.hex = parsehex.Hex()
        if self.hex.load_file(file_path):
            self.read_file_error_signal.emit(1)
        self.display_hex_signal.emit()

    def disable_setting(self, disable):
        if disable:
            self.ui.btn_open_close_port.setText("关闭串口")
            # self.statusBarStauts.setText("<font color=%s>%s</font>" % ("#008200", parameters.strReady))
            self.ui.cmb_port.setDisabled(True)
            # self.serailBaudrateCombobox.setDisabled(True)
            # self.serailParityCombobox.setDisabled(True)
            # self.serailStopbitsCombobox.setDisabled(True)
            # self.serailBytesCombobox.setDisabled(True)
            # self.ui.btn_open_close_port.setDisabled(False)
        else:
            self.ui.btn_open_close_port.setText("开启串口")
            # self.statusBarStauts.setText("<font color=%s>%s</font>" % ("#f31414", parameters.strClosed))
            self.ui.cmb_port.setDisabled(False)
            # self.serailBaudrateCombobox.setDisabled(False)
            # self.serailParityCombobox.setDisabled(False)
            # self.serailStopbitsCombobox.setDisabled(False)
            # self.serailBytesCombobox.setDisabled(False)
            # self.programExitSaveParameters()

    def open_close_port(self):
        # self.open_close_port_process()
        t = threading.Thread(target=self.open_close_port_process)
        t.setDaemon(True)
        t.start()

    def open_file_error_meesage(self,errortype):
        if errortype is 1:
            QMessageBox.critical(self, "打开失败", "打开文件失败！\r\n")

    def connect_serial_failed_message(self, errortype):
        print(errortype)
        if errortype is 1:
            self.ui.label_connect_info.setText("打开串口失败！")
            QMessageBox.critical(self, "打开失败", "打开串口失败，没有找到USB串口，可能原因如下：\r\n"
                                               "（1）USB串口未插上PC\r\n（2）PC未安装串口驱动\r\n（3）串口被其他程序占用\r\n.")
        elif errortype is 2:
            self.ui.label_connect_info.setText("握手失败！")
            QMessageBox.critical(self, "握手失败", "打开串口成功，但未连接终端。可能原因如下：\r\n"
                                               "（1）USB串口驱动需更新\r\n（2）USB串口未连接终端\r\n（3）终端程序未运行\r\n。")
        elif errortype is 3:
            self.ui.label_connect_info.setText("连接失败！")
            QMessageBox.critical(self, "连接失败", "发现设备，但连接失败！")


    def open_close_port_process(self):
        if self.com.is_open:
            self.com.close()
            self.setDisableSettingsSignal.emit(False)
            self.receive_progress_stop_flag = False
        else:
            self.com.port = self.ui.cmb_port.currentText().split(" ")[0]
            self.emuart = emuart.Emuart(self.com)
            self.setDisableSettingsSignal.emit(True)
            self.receive_progress_stop_flag = True
            ret, self.device_info = self.emuart.connect_device()
            if ret:
                self.show_error_message_signal.emit(ret)
                self.setDisableSettingsSignal.emit(False)
                # self.receive_progress_stop_flag = False
            else:
                self.ui.label_connect_info.setText(self.com.name+":"+self.device_info.mcu_type+" "+self.device_info.bios_version)
                print("探测成功")

        # try:
        #     if self.com.is_open:
        #         self.receive_progress_stop_flag = True
        #         self.com.close()
        #         self.setDisableSettingsSignal.emit(False)
        #     else:
        #         try:
        #             self.com.baudrate = 115200
        #             self.com.port = self.ui.cmb_port.currentText().split(" ")[0]
        #             self.com.bytesize = 8
        #             self.com.parity = 'N'
        #             self.com.stopbits = 1
        #             self.com.timeout = None
        #             self.com.open()
        #             print("open success")
        #             data = '[Are you an emuart??]'
        #             a= emuart.Emuart('a')
        #             self.com.write(a.emuart_frame(data))
        #             self.setDisableSettingsSignal.emit(True)
        #             # self.receiveProcess = threading.Thread(target=self.receiveData)
        #             # self.receiveProcess.setDaemon(True)
        #             # self.receiveProcess.start()
        #         except Exception as e:
        #             self.com.close()
        #             self.receiveProgressStop = True
        #             print(e)
        #             # self.errorSignal.emit( parameters.strOpenFailed +"\n"+ str(e))
        #             # self.setDisableSettingsSignal.emit(False)
        # except Exception as e:
        #     print(e)

    def start_stop_detect(self, flag):
        if flag:
            if not self.timer_redetect.isActive():
                self.timer_redetect.start(30)
        elif self.timer_redetect.isActive():
            self.timer_redetect.stop()

    def serial_port_detect(self):
        # self.detect_serial_port_process()
        if not self.detecting_port_flag:
            t = threading.Thread(target=self.detect_serial_port_process)
            t.setDaemon(True)
            t.start()

    def detect_serial_port_process(self):
        while True:
            portList = list(serial.tools.list_ports.comports())
            if len(portList) > 0:
                currText = self.ui.cmb_port.currentText()
                self.ui.cmb_port.clear()
                for i in portList:
                    showStr = str(i[0]) + " " + str(i[1])
                    if i[0].startswith("/dev/cu.Bluetooth-Incoming-Port"):
                        continue
                    self.ui.cmb_port.addItem(showStr)
                index = self.ui.cmb_port.findText(currText)
                if index >= 0:
                    self.ui.cmb_port.setCurrentIndex(index)
                else:
                    self.ui.cmb_port.setCurrentIndex(0)
                break
            time.sleep(1)
        self.detecting_port_flag = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
