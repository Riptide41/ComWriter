import Mainwindow_Ui
from PyQt5 import QtCore
import sys
import threading
import serial
import serial.tools.list_ports

import time
from PyQt5.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    detecting_port_flag = False
    receive_progress_stop_flag = True
    ui = Mainwindow_Ui.Ui_MainWindow()
    com = serial.Serial()

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
        # self.ui.btn_open_close_port.connect(self.open_close_port)

    def open_close_port(self):
        t = threading.Thread(target=self.open_close_port_process)
        t.setDaemon(True)
        t.start()
    #
    # def open_close_port_process(self):
    #     try:
    #         if self.com.is_open:
    #             self.receive_progress_stop_flag = True
    #             self.com.close()

    def start_stop_detect(self, flag):
        if flag:
            if not self.timer_redetect.isActive():
                self.timer_redetect.start(30)
        elif self.timer_redetect.isActive():
            self.timer_redetect.stop()

    def serial_port_detect(self):
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
