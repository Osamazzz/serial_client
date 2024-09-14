import sys

from PyQt5.QtWidgets import QApplication

from Call_Ui_SerialPort import MyMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())