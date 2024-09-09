import time

from PyQt5.QtCore import *

from Client_Util import recPacQueue


# TODO 设置定时器。处理超时事件

class MyThread(QThread):
    def __init__(self, handler):
        self.handler = handler
        super().__init__(parent=None)

    def run(self):
        while not self.isInterruptionRequested():
            # 阻塞接收数据
            self.receive_packet()

    def receive_packet(self):
        cur = recPacQueue.get()  # 阻塞获取数据
        # self.handler.TextEdit_Receive.insertPlainText("接收到第" + cur[0] + "个包, 信号强度为:" + cur[1])
        # print("接收到第" + cur[0] + "个包, 信号强度为:" + cur[1])
