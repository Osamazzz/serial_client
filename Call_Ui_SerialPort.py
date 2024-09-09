# 逻辑文件

import binascii
import re
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow
from tornado.gen import sleep

from Client_Util import State
from Client_Util import int8_from_unsigned
from MyThread import MyThread
from SerialPort import Ui_ModelTestHelper

PACKET_SIZE = 16  # AT指令包大小
TotalPacketNum = 100  # 每轮测试应该发送的包为100个，用于丢包率测试
SendingInterval = 100  # 发送间隔(ms)


class MyMainWindow(QMainWindow, Ui_ModelTestHelper):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.com1 = QSerialPort()  # 设置Qt串口类实例1 -> 待测设备
        self.com2 = QSerialPort()  # 设置Qt串口类实例2 -> 陪测设备
        self.curState = State.IDLE
        self.my_thread = MyThread(self)
        self.timer = QTimer(parent=self)  # 设置定时器
        self.receivePacketNum = 0  # 初始化实际收到的包数,用于计算丢包率
        self.totalRSSI = 0  # 总的RSSI，用于计算平均RSSI
        self.curPacketNum = -1  # 当前包序号
        self.isTimeOut = False  # 超时标志
        self.setupUi(self)
        self.createSignalSlot()

    # 设置信号与槽
    def createSignalSlot(self):
        self.ClearButton.clicked.connect(self.clearText)  # 清空按钮
        self.Com_Refresh_Button.clicked.connect(self.Com_Refresh_Button_Clicked)  # 串口搜索刷新按钮
        self.Com_Open_Button.clicked.connect(self.Com_Open_Button_Clicked)  # 串口打开按钮
        self.Com_Close_Button.clicked.connect(self.Com_Close_Button_Clicked)  # 串口关闭按钮
        # 注册设置发射模式按钮，发送两组AT指令
        self.Com_TX_Set_Button.clicked.connect(self.Com_TX_Set_Button_Clicked)
        # 注册设置接收模式按钮，发送两组AT指令
        self.Com_RX_Set_Button.clicked.connect(self.Com_RX_Set_Button_Clicked)
        self.Com_Reset_Button.clicked.connect(self.Com_Reset_Button_Clicked)  # 注册重置按钮，发送重置AT指令
        self.hexShowing_checkBox.stateChanged.connect(self.hexShowingClicked)  # 注册16进制显示勾选框
        self.hexSending_checkBox.stateChanged.connect(self.hexSendingClicked)  # 注册16进制发送勾选框
        self.Button_Sava_Log.clicked.connect(self.saveLog)  # 注册保存日志按钮
        # 接收数据
        self.com1.readyRead.connect(self.Com_Receive_Data)
        self.com2.readyRead.connect(self.Com_Receive_Data)
        self.timer.timeout.connect(self.timer_timeout)

    # 清空接收缓冲区
    def clearText(self):
        self.TextEdit_Receive.clear()

    # 定时器超时方法
    def timer_timeout(self):
        self.TextEdit_Receive.insertPlainText("超时,测试结束" + "\r\n")
        # self.curState = State.IDLE
        self.timer.stop()

    #  打开两个串口
    def Com_Open_Button_Clicked(self):
        comTestName1 = self.Com_Test_Combo.currentText()  # 待测设备串口名
        comTestName2 = self.Com_Test_Combo_2.currentText()  # 陪测设备串口名
        comBaud = int(self.Com_Baud_Combo.currentText())  # 获取波特率
        # 设置对象的串口名
        self.com1.setPortName(comTestName1)
        self.com2.setPortName(comTestName2)
        try:
            # 打开两个串口
            self.com1.open(QSerialPort.ReadWrite)
            # 设置波特率
            self.com1.setBaudRate(comBaud)
            self.com1.setStopBits(1)
            self.com1.setDataBits(8)
            try:
                self.com2.open(QSerialPort.ReadWrite)
                self.com2.setBaudRate(comBaud)
                self.com2.setStopBits(1)
                self.com2.setDataBits(8)
            except Exception as e:
                QMessageBox.critical(self, 'Error', '串口2打开失败:{}'.format(e))
                return
        except Exception as e:
            QMessageBox.critical(self, 'Error', '串口1打开失败:{}'.format(e))
            return
        self.Com_Close_Button.setEnabled(True)
        self.Com_Open_Button.setEnabled(False)
        self.Com_Refresh_Button.setEnabled(False)
        self.Com_Test_Combo.setEnabled(False)
        self.Com_Test_Combo_2.setEnabled(False)
        self.Com_Baud_Combo.setEnabled(False)
        self.Com_isOpenOrNot_Label.setText('  已打开')
        QMessageBox.information(self, 'OK', '打开成功')

    # 关闭两个串口
    def Com_Close_Button_Clicked(self):
        try:
            self.com1.close()
            self.com2.close()
        except Exception as e:
            QMessageBox.critical(self, 'Error', '串口关闭失败')
            return
        QMessageBox.information(self, 'OK', '串口关闭成功')
        self.Com_Close_Button.setEnabled(False)
        self.Com_Open_Button.setEnabled(True)
        self.Com_Refresh_Button.setEnabled(True)
        self.Com_Test_Combo.setEnabled(True)
        self.Com_Test_Combo_2.setEnabled(True)
        self.Com_Baud_Combo.setEnabled(True)
        self.Com_isOpenOrNot_Label.setText("已关闭")
        pass

    # 通用串口发送函数
    def Com_Send_Data(self, com: QSerialPort, txData: str):
        if len(txData) == 0:
            return
        if not self.hexSending_checkBox.isChecked():  # 如果不以16进制发送
            com.write(txData.encode('ascii'))
        else:
            Data = txData.replace(' ', '')
            # 如果16进制不是偶数个字符, 去掉最后一个, [ ]左闭右开
            if len(Data) % 2 == 1:
                Data = Data[0:len(Data) - 1]
            # 如果遇到非16进制字符
            if Data.isalnum() is False:
                QMessageBox.critical(self, '错误', '包含非十六进制数')
            try:
                hexData = binascii.a2b_hex(Data)
            except Exception as e:
                QMessageBox.critical(self, '错误', '转换编码错误')
                return
            # 发送16进制数据, 发送格式如 ‘31 32 33 41 42 43’, 代表'123ABC'
            try:
                com.write(hexData)
            except Exception as e:
                QMessageBox.critical(self, '异常', '十六进制发送错误')
                return

    # TODO 在进行测试的时候，除复位和清除键位，其他键位不能使用

    # 发射功能测试
    def Com_TX_Set_Button_Clicked(self):
        # 重置客户端模式，设置为发送测试模式，重置丢包率和信号强度统计
        # 先清空串口缓冲区
        self.com1.readAll()
        self.com2.readAll()
        self.curState = State.SENDING
        self.totalRSSI = 0
        self.receivePacketNum = 0
        self.TextEdit_Receive.insertPlainText("开始进行发送测试..\n")
        self.Com_Send_Data(self.com1, "AT+SET=TESTTX\r\n")  # 向待测设备串口发送->发送模式AT指令
        self.Com_Send_Data(self.com2, "AT+SET=TESTRX\r\n")  # 向陪测设备串口发送->接收模式AT指令
        self.timer.start(TotalPacketNum * SendingInterval + 2000)   # 开启定时器
        self.Com_Close_Button.setEnabled(False)
        self.Com_Open_Button.setEnabled(False)
        self.Com_Reset_Button.setEnabled(True)
        self.ClearButton.setEnabled(True)
        self.Com_TX_Set_Button.setEnabled(True)
        self.Com_RX_Set_Button.setEnabled(False)

    # 接收功能测试
    def Com_RX_Set_Button_Clicked(self):
        # 重置客户端模式，设置为接收测试模式，重置丢包率和信号强度统计
        # 先清空串口缓冲区，以免发生错误
        self.com1.readAll()
        self.com2.readAll()
        self.curState = State.RECEIVING
        self.totalRSSI = 0
        self.receivePacketNum = 0
        self.TextEdit_Receive.insertPlainText("开始进行接收测试..\n")
        self.Com_Send_Data(self.com1, "AT+SET=TESTRX\r\n")  # 向待测设备串口发送->接收模式AT指令
        self.Com_Send_Data(self.com2, "AT+SET=TESTTX\r\n")  # 向陪测设备串口发送->发送模式AT指令
        self.timer.start(TotalPacketNum * SendingInterval + 2000)   # 开启定时器
        self.Com_Close_Button.setEnabled(False)
        self.Com_Open_Button.setEnabled(False)
        self.Com_Reset_Button.setEnabled(True)
        self.ClearButton.setEnabled(True)
        self.Com_TX_Set_Button.setEnabled(False)
        self.Com_RX_Set_Button.setEnabled(True)

    # 发送复位AT指令，使两个设备进入IDLE状态
    def Com_Reset_Button_Clicked(self):
        # TODO 重置客户端模式，设置为IDLE模式，重置丢包率和信号强度统计
        # 先清空串口缓冲区，以免发生错误
        self.com1.readAll()
        self.com2.readAll()
        self.curState = State.IDLE
        self.totalRSSI = 0
        self.receivePacketNum = 0
        self.TextEdit_Receive.insertPlainText("进入空闲状态..\n")
        self.Com_Send_Data(self.com1, "AT+RESET\r\n")
        self.Com_Send_Data(self.com2, "AT+RESET\r\n")
        self.timer.stop()
        self.Com_Close_Button.setEnabled(True)
        self.Com_Open_Button.setEnabled(True)
        self.Com_Reset_Button.setEnabled(True)
        self.ClearButton.setEnabled(True)
        self.Com_TX_Set_Button.setEnabled(True)
        self.Com_RX_Set_Button.setEnabled(True)

    # 串口刷新
    def Com_Refresh_Button_Clicked(self):
        self.Com_Test_Combo.clear()
        self.Com_Test_Combo_2.clear()
        com1 = QSerialPort()
        com2 = QSerialPort()
        com_list_1 = QSerialPortInfo.availablePorts()  # 找到所有可打开的串口
        com_list_2 = QSerialPortInfo.availablePorts()  # 找到所有可打开的串口
        # 为可选框1添加item
        for info in com_list_1:
            com1.setPort(info)
            if com1.open(QSerialPort.ReadWrite):
                self.Com_Test_Combo.addItem(info.portName())
        # 为可选框2添加item
        for info in com_list_2:
            com2.setPort(info)
            if com2.open(QSerialPort.ReadWrite):
                self.Com_Test_Combo_2.addItem(info.portName())

    # 串口接收数据
    def Com_Receive_Data(self):
        if self.curState == State.IDLE:  # 如果当前状态为IDLE，则停止进行接收
            return
        else:
            if self.isTimeOut:
                print("超时了")
                # 直接计算rssi和丢包率
                rssi = self.totalRSSI / self.receivePacketNum
                lossRate = (100 - self.receivePacketNum) / 100
                print("rssi:" + str(rssi) + ", loss:" + str(lossRate))
                self.curState = State.IDLE
                self.totalRSSI = 0
                self.receivePacketNum = 0
                self.curPacketNum = -1
                self.isTimeOut = False
                return
            serial_num, curRSSI, rxData = 0, 0, ""
            try:
                # 处理接收到的数据
                if self.curState == State.RECEIVING:
                    rxData = bytes(self.com1.read(PACKET_SIZE))  # 从com1接收16字节数据
                elif self.curState == State.SENDING:
                    rxData = bytes(self.com2.read(PACKET_SIZE))  # 从com2接收16字节数据
                if len(rxData) == 16 and rxData.decode('ascii').startswith('AT+TESTDATA='):  # 如果接收到RSSI数据包
                    # 取出序号和RSSI
                    serial_num = int8_from_unsigned(int(rxData.decode('ascii')[12:14], 16))
                    curRSSI = int8_from_unsigned(int(rxData.decode('ascii')[14:16], 16))
                    self.curPacketNum = serial_num  # 更新当前数据包号
                    self.totalRSSI += curRSSI  # 加入总RSSI，用于计算平均RSSI
                    self.receivePacketNum += 1
                    if not self.hexShowing_checkBox.isChecked():  # 如果不以16进制显示
                        try:
                            print(rxData.decode('ascii'))
                            self.TextEdit_Receive.insertPlainText(
                                "接收到第" + str(serial_num + 1) + "个包" + '\r')  # 这里+1是为了让序号从1开始
                            self.TextEdit_Receive.insertPlainText("信号强度为:" + str(curRSSI) + '\r\n')
                            if self.curPacketNum == 99 and (100 - self.receivePacketNum) / 100 < 0.05:
                                lossRate = (100 - self.receivePacketNum) / 100 * 100
                                if self.curState == State.RECEIVING:  # 如果是接收测试
                                    self.TextEdit_Receive.insertPlainText("接收测试通过,丢包率为:" + str(lossRate)
                                                                          + "%, 平均信号强度:" + str(
                                        self.totalRSSI / self.receivePacketNum) + '\r\n')
                                    self.com1.readAll()
                                elif self.curState == State.SENDING:  # 如果是发送测试
                                    self.TextEdit_Receive.insertPlainText("发送测试通过,丢包率为:" + str(lossRate)
                                                                          + "%, 平均信号强度:" + str(
                                        self.totalRSSI / self.receivePacketNum) + '\r\n')
                                    self.com2.readAll()
                                # 重置
                                self.timer.stop()   # 关闭定时器
                                self.curState = State.IDLE  # 进入空闲状态
                                self.totalRSSI = 0
                                self.receivePacketNum = 0
                                self.curPacketNum = -1
                                self.isTimeOut = False
                                # 重新启用被禁用的按钮
                                self.Com_Close_Button.setEnabled(True)
                                self.Com_Open_Button.setEnabled(True)
                                self.Com_Reset_Button.setEnabled(True)
                                self.ClearButton.setEnabled(True)
                                self.Com_TX_Set_Button.setEnabled(True)
                                self.Com_RX_Set_Button.setEnabled(True)
                        except Exception as e:
                            pass
                        finally:
                            self.TextEdit_Receive.insertPlainText("\n")
                    else:
                        Data = binascii.b2a_hex(rxData).decode('ascii')
                        # re 正则表达式 (.{2}) 匹配两个字母
                        hexStr = ' 0x'.join(re.findall('(.{2})', Data))
                        # 补齐第一个 0x
                        hexStr = '0x' + hexStr
                        self.TextEdit_Receive.insertPlainText(hexStr)
                        self.TextEdit_Receive.insertPlainText(' ')

            except Exception as e:
                QMessageBox.critical(self, 'Error', '串口接收数据错误：{}'.format(e))

    # 保存日志
    def saveLog(self):
        # 使用文件对话框选择保存位置
        fileName, _ = QFileDialog.getSaveFileName(self, "保存日志", "", "文本文件 (*.txt)")
        if fileName:
            # 将日志内容写入文件
            with open(fileName, 'w', encoding='utf-8') as file:
                file.write(self.TextEdit_Receive.toPlainText())

    # 开启线程
    def start(self):
        self.my_thread.start()

    # 16进制显示勾选
    def hexShowingClicked(self):
        if self.hexShowing_checkBox.isChecked():
            # 接收区换行
            self.TextEdit_Receive.insertPlainText('\n')

    # 16进制发送勾选
    def hexSendingClicked(self):
        if self.hexSending_checkBox.isChecked():
            pass

    # 关闭事件
    def closeEvent(self, event: QCloseEvent):
        self.my_thread.requestInterruption()
        # self.my_thread.wait()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyleSheet("QPushButton { background-color: #ffffff; color: white; border-style: outset;"
    #                   " border-width: 1px; border-radius: 10px; border-color: #000000; padding: 6px; }")
    myWin = MyMainWindow()
    # myWin.start()
    # myWin.timer.start(TotalPacketNum * SendingInterval + 5000)
    myWin.show()
    sys.exit(app.exec_())
