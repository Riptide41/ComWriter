from PyQt5 import QtWidgets, QtCore


class Combobox(QtWidgets.QComboBox):
    signal_show_popup = QtCore.pyqtSignal(bool)
    signal_hidden_popup = QtCore.pyqtSignal()

    def showPopup(self):
        self.signal_show_popup.emit(False)
        super(Combobox, self).showPopup()

    def hidePopup(self):
        self.signal_show_popup.emit(True)
        super(Combobox, self).hidePopup()
