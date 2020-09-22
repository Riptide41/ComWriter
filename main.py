import Mainwindow_Ui
from PyQt5 import QtCore
import sys
import threading
import serial
import serial.tools.list_ports
import emuart

import time
from PyQt5.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    detecting_port_flag = False
    receive_progress_stop_flag = True
    ui = Mainwindow_Ui.Ui_MainWindow()
    com = serial.Serial()
    setDisableSettingsSignal = QtCore.pyqtSignal(bool)

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
        # self.open_close_port()
        t = threading.Thread(target=self.open_close_port_process)
        t.setDaemon(True)
        t.start()

    def open_close_port_process(self):
        if self.com.is_open:
            self.com.close()
        self.com.port = self.ui.cmb_port.currentText().split(" ")[0]
        self.emuart = emuart.Emuart(self.com)

        self.setDisableSettingsSignal.emit(True)
        self.receive_progress_stop_flag = True
        ret = self.emuart.connect_device()
        self.setDisableSettingsSignal.emit(False)
        self.receive_progress_stop_flag = False

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
