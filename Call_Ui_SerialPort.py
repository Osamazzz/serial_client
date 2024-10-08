# 逻辑文件
import os
import re
import threading
import time
from datetime import datetime

from PyQt5.QtCore import QTimer, Qt, QThread
from PyQt5.QtGui import QIntValidator
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow

from Client_Util import LossRateValidator
from Client_Util import RSSIValidator
from Client_Util import State
from Client_Util import int8_from_unsigned
from SerialPort import Ui_ModelTestHelper

PACKET_SIZE = 16  # AT指令包大小
TotalPacketNum = 100  # 每轮测试应该发送的包为100个，用于丢包率测试
SendingInterval = 100  # 发送间隔(ms)



# 主页面类
class MyMainWindow(QMainWindow, Ui_ModelTestHelper):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.com1 = QSerialPort()  # 设置Qt串口类实例1 -> 待测设备
        self.com2 = QSerialPort()  # 设置Qt串口类实例2 -> 陪测设备
        self.curState = State.IDLE  # 客户端状态
        self.timer = QTimer(parent=self)  # 设置定时器
        self.onekey_timer = QTimer(parent=self) # 设置一键测试用的定时器
        self.receivePacketNum = 0  # 初始化实际收到的包数,用于计算丢包率
        self.totalRSSI = 0  # 总的RSSI，用于计算平均RSSI
        self.curPacketNum = -1  # 当前包序号
        self.isTimeOut = False  # 超时标志
        self.isPass = False  # 测试通过标志
        self.isComOpen = False
        self.receiveBuffer = ""  # 接收缓冲区
        self.consumer_thread = None  # 存储消费者线程
        self.recFlag = False

        # 测试通过指标
        self.passLossRate = 0.05
        self.passRecNum = (1 - self.passLossRate) * TotalPacketNum
        self.passRSSI = -50

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
        self.OneKey_Button.clicked.connect(self.OneKey_Button_Clicked)
        self.Com_Reset_Button.clicked.connect(self.Com_Reset_Button_Clicked)  # 注册重置按钮，发送重置AT指令
        self.Button_Sava_Log.clicked.connect(self.saveLog)  # 注册保存日志按钮
        self.Button_Param_Setting.clicked.connect(self.openParamSettingDialog)  # 参数设置按钮
        self.Button_Param_Setting_2.clicked.connect(self.openPowerSettingDialog)
        self.Com_Baud_Combo.setCurrentIndex(10)  # 设置默认波特率为115200

        # 接收数据
        self.com1.readyRead.connect(self.Com_Receive_Data)
        self.com2.readyRead.connect(self.Com_Receive_Data)
        # 超时处理
        self.timer.timeout.connect(self.timer_timeout)
        self.onekey_timer.timeout.connect(self.onekey_timeout)

        self.TextEdit_Receive.setReadOnly(True)
        self.TextEdit_Receive.setTextInteractionFlags(Qt.NoTextInteraction)

    # 清空接收缓冲区
    def clearText(self):
        self.TextEdit_Receive.clear()

    # 打开功率设置窗口
    def openPowerSettingDialog(self):
        if not self.isComOpen:
            QMessageBox.warning(self, 'Warning', '请打开串口')
            return
        dialog = PowerConfigurationDialog()
        if dialog.exec_() == QDialog.Accepted:
            power = int(dialog.getParam())   # 0-31
            if 0 <= power <= 9:
                power = '0' + str(power)
            else:
                power = str(power)
            # 发送AT指令
            self.Com_Send_Data(self.com1, 'AT+SET=TXPARM'+ power +'\r\n')
            self.Com_Send_Data(self.com2, 'AT+SET=TXPARM' + power + '\r\n')
        else:
            print('取消设置参数')


    # 打开参数设置窗口
    def openParamSettingDialog(self):
        dialog = ParamSettingDialog()
        if dialog.exec_() == QDialog.Accepted:
            RSSI, LossRate = dialog.getParam()
            # 重新设置新的参数值
            self.passRSSI = int(RSSI)
            self.passLossRate = int(LossRate) / 100
            self.passRecNum = int((1 - self.passLossRate) * TotalPacketNum)
            self.TextEdit_Receive.insertPlainText(
                f'设置成功, RSSI: {self.passRSSI}, 丢包率: {self.passLossRate}, 测试通过的最少收包数:{self.passRecNum}\n')
        else:
            print('取消设置参数')

    def onekey_timeout(self):
        self.Com_RX_Set_Button_Clicked()
        self.onekey_timer.stop()

    # 定时器超时方法
    def timer_timeout(self):
        if not self.isPass:
            self.TextEdit_Receive.insertPlainText("超时,测试失败" + "\r\n")
            # 测试失败，直接终止一键测试timer
            if self.onekey_timer.isActive():
                self.onekey_timer.stop()

            # 直接计算rssi和丢包率
            if self.receivePacketNum == 0:
                self.TextEdit_Receive.insertPlainText(
                    time.strftime('%Y-%m-%d %H:%M:%S,', time.localtime()) + "目前丢包率为:100%,请检查设备是否正常！\n")
            else:
                rssi = self.totalRSSI / self.receivePacketNum
                lossRate = (100 - self.receivePacketNum)
                print("rssi:" + str(rssi) + ", loss:" + str(lossRate))
                self.TextEdit_Receive.insertPlainText(
                    time.strftime('%Y-%m-%d %H:%M:%S,', time.localtime()) + "目前平均信号强度为:{:.2f}".format(
                        rssi) + ", 丢包率为:" + str(lossRate) + "%\n")
        else:
            lossRate = (100 - self.receivePacketNum)
            if self.curState == State.RECEIVING:  # 如果是接收测试
                (self.TextEdit_Receive
                 .insertPlainText(time.strftime(
                    '%Y-%m-%d %H:%M:%S ', time.localtime())
                                  + "接收测试通过,丢包率为:{:.2f}".format(lossRate)
                                  + "%, 平均信号强度:{:.2f}".format(
                    self.totalRSSI / self.receivePacketNum) + '\r\n'))
                self.com1.readAll()
            elif self.curState == State.SENDING:  # 如果是发送测试
                (self.TextEdit_Receive
                 .insertPlainText(time.strftime(
                    '%Y-%m-%d %H:%M:%S ', time.localtime())
                                  + "发送测试通过,丢包率为:{:.2f}".format(lossRate)
                                  + "%, 平均信号强度:{:.2f}".format(
                    self.totalRSSI / self.receivePacketNum) + '\r\n'))
                self.com2.readAll()
        self.curState = State.IDLE
        self.totalRSSI = 0
        self.receivePacketNum = 0
        self.curPacketNum = -1
        self.timer.stop()
        self.stop_consumer()

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
        self.isComOpen = True
        # self.Com_Close_Button.setEnabled(True)
        # self.Com_Open_Button.setEnabled(False)
        # self.Com_Refresh_Button.setEnabled(False)
        # self.Com_Test_Combo.setEnabled(False)
        # self.Com_Test_Combo_2.setEnabled(False)
        # self.Com_Baud_Combo.setEnabled(False)
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
        self.isComOpen = False
        # self.Com_Close_Button.setEnabled(False)
        # self.Com_Open_Button.setEnabled(True)
        # self.Com_Refresh_Button.setEnabled(True)
        # self.Com_Test_Combo.setEnabled(True)
        # self.Com_Test_Combo_2.setEnabled(True)
        # self.Com_Baud_Combo.setEnabled(True)
        self.Com_isOpenOrNot_Label.setText("已关闭")
        pass

    # 通用串口发送函数
    def Com_Send_Data(self, com: QSerialPort, txData: str):
        if len(txData) == 0:
            return
        com.write(txData.encode('ascii'))

    # 在进行测试的时候，除复位和清除键位，其他键位不能使用

    # 发射功能测试
    def Com_TX_Set_Button_Clicked(self):
        if not self.isComOpen:  # 串口未打开
            QMessageBox.critical(self, 'Error', '串口未打开')
            return
        # 重置客户端模式，设置为发送测试模式，重置丢包率和信号强度统计
        # 先清空串口缓冲区
        self.com1.readAll()
        self.com2.readAll()
        self.receiveBuffer = ""
        self.curState = State.SENDING
        self.totalRSSI = 0
        self.receivePacketNum = 0
        self.isPass = False
        self.TextEdit_Receive.insertPlainText("开始进行发送测试..\n")
        self.Com_Send_Data(self.com1, "AT+SET=TESTTX\r\n")  # 向待测设备串口发送->发送模式AT指令
        self.Com_Send_Data(self.com2, "AT+SET=TESTRX\r\n")  # 向陪测设备串口发送->接收模式AT指令
        self.timer.start(TotalPacketNum * SendingInterval + 3000)  # 开启定时器
        self.com2.close()
        self.com2.open(QSerialPort.ReadWrite)
        self.start_consumer()

    # 接收功能测试
    def Com_RX_Set_Button_Clicked(self):
        if not self.isComOpen:  # 串口未打开
            QMessageBox.critical(self, 'Error', '串口未打开')
            return
        # 重置客户端模式，设置为接收测试模式，重置丢包率和信号强度统计
        # 先清空串口缓冲区，以免发生错误
        self.com1.readAll()
        self.com2.readAll()
        self.receiveBuffer = ""
        self.curState = State.RECEIVING
        self.totalRSSI = 0
        self.receivePacketNum = 0
        self.isPass = False
        self.TextEdit_Receive.insertPlainText("开始进行接收测试..\n")
        self.Com_Send_Data(self.com1, "AT+SET=TESTRX\r\n")  # 向待测设备串口发送->接收模式AT指令
        self.Com_Send_Data(self.com2, "AT+SET=TESTTX\r\n")  # 向陪测设备串口发送->发送模式AT指令
        self.timer.start(TotalPacketNum * SendingInterval + 3000)  # 开启定时器
        self.com1.close()
        self.com1.open(QSerialPort.ReadWrite)
        self.start_consumer()


    # 连续进行两次测试
    def OneKey_Button_Clicked(self):
        self.Com_TX_Set_Button_Clicked()
        self.onekey_timer.start(TotalPacketNum * SendingInterval + 4000)


    # 发送复位AT指令，使两个设备进入IDLE状态
    def Com_Reset_Button_Clicked(self):
        if not self.isComOpen:  # 串口未打开
            QMessageBox.critical(self, 'Error', '串口未打开')
            return
        # 重置客户端模式，设置为IDLE模式，重置丢包率和信号强度统计
        # 先清空串口缓冲区，以免发生错误
        self.com1.readAll()
        self.com2.readAll()
        self.receiveBuffer = ""
        self.curState = State.IDLE
        self.totalRSSI = 0
        self.receivePacketNum = 0
        self.isPass = False
        self.curPacketNum = -1  # 当前包序号
        self.isTimeOut = False  # 超时标志
        self.TextEdit_Receive.insertPlainText("进入空闲状态..\n")
        self.Com_Send_Data(self.com1, "AT+SET=RESET\r\n")
        self.Com_Send_Data(self.com2, "AT+SET=RESET\r\n")
        # self.clearText()
        self.timer.stop()
        self.Com_RX_Set_Button.setEnabled(True)
        self.Com_TX_Set_Button.setEnabled(True)
        self.stop_consumer()

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
                com1.close()
        # 为可选框2添加item
        for info in com_list_2:
            com2.setPort(info)
            if com2.open(QSerialPort.ReadWrite):
                self.Com_Test_Combo_2.addItem(info.portName())
                com2.close()

    # 生产者方法，从串口接收数据
    def Com_Receive_Data(self):
        if self.curState == State.IDLE:  # 如果当前状态为IDLE，则停止进行接收
            return
        else:
            rxData = ""
            try:
                # 处理接收到的数据
                if self.curState == State.RECEIVING:
                    rxData = bytes(self.com1.readAll())  # 从com1接收16字节数据
                elif self.curState == State.SENDING:
                    rxData = bytes(self.com2.readAll())  # 从com2接收16字节数据
                # print(f"接收到的数据: {rxData}")
                # 累加到缓冲区中
                self.receiveBuffer += rxData.decode('ascii')
            except Exception as e:
                QMessageBox.critical(self, 'Error', '串口接收数据错误：{}'.format(e))

    # 消费者方法，用于解析缓冲区数据
    def parseData(self):
        # 循环查找缓冲区中完整的AT+TESTDATA=XXXX
        while self.recFlag:
            # print('我一直在运行')
            match = re.search(r'AT\+TESTDATA=[0-9A-F]{4}', self.receiveBuffer)
            # print(self.receiveBuffer)
            if not match:
                # time.sleep(0.1)
                continue
            # 取出序号和RSSI
            packet = match.group(0)
            # print(packet)
            serial_num = int8_from_unsigned(int(packet[12:14], 16))
            curRSSI = int8_from_unsigned(int(packet[14:16], 16))

            self.curPacketNum = serial_num  # 更新当前数据包号
            self.totalRSSI += curRSSI  # 加入总RSSI，用于计算平均RSSI
            self.receivePacketNum += 1
            com_rev = "待测设备" if self.curState == State.RECEIVING else "陪测设备"
            self.TextEdit_Receive.insertPlainText(
                time.strftime('%Y-%m-%d %H:%M:%S ', time.localtime()) + com_rev +
                "接收到第" + str(serial_num + 1) + "个包,")  # 这里+1是为了让序号从1开始
            self.TextEdit_Receive.insertPlainText("信号强度为:" + str(curRSSI) + '\r\n')

            # 不能单纯的以序号作为判断的依据
            if self.receivePacketNum > self.passRecNum and self.passRSSI < self.totalRSSI / self.receivePacketNum:
                self.isPass = True  # 让本次测试通过
            if self.curPacketNum == 99:
                # 可以停止测了
                if not self.isPass:
                    self.TextEdit_Receive.insertPlainText("测试失败" + "\r\n")
                    # 直接计算rssi和丢包率
                    rssi = self.totalRSSI / self.receivePacketNum
                    lossRate = (100 - self.receivePacketNum)
                    print("rssi:" + str(rssi) + ", loss:" + str(lossRate))
                    self.TextEdit_Receive.insertPlainText(
                        time.strftime('%Y-%m-%d %H:%M:%S,',
                                      time.localtime()) + "目前平均信号强度为:{:.2f}".format(
                            rssi) + ", 丢包率为:" + str(lossRate) + "%\n")
                else:  # 测试通过了
                    lossRate = 100 - self.receivePacketNum
                    if self.curState == State.RECEIVING:  # 如果是接收测试
                        self.TextEdit_Receive.insertPlainText(time.strftime(
                            '%Y-%m-%d %H:%M:%S ', time.localtime())
                                                              + "接收测试通过,丢包率为:{:.2f}".format(
                            lossRate)
                                                              + "%, 平均信号强度:{:.2f}".format(
                            self.totalRSSI / self.receivePacketNum) + '\r\n')
                        self.com1.readAll()
                    elif self.curState == State.SENDING:  # 如果是发送测试
                        self.TextEdit_Receive.insertPlainText(time.strftime(
                            '%Y-%m-%d %H:%M:%S ', time.localtime())
                                                              + "发送测试通过,丢包率为:{:.2f}".format(
                            lossRate)
                                                              + "%, 平均信号强度:{:.2f}".format(
                            self.totalRSSI / self.receivePacketNum) + '\r\n')
                        self.com2.readAll()
                # 重置
                self.timer.stop()  # 关闭定时器
                self.curState = State.IDLE  # 进入空闲状态
                self.totalRSSI = 0
                self.receivePacketNum = 0
                self.curPacketNum = -1
                self.isTimeOut = False
                self.Com_Close_Button.setEnabled(True)
                self.Com_Open_Button.setEnabled(True)
                self.Com_Reset_Button.setEnabled(True)
                self.ClearButton.setEnabled(True)
                self.Com_TX_Set_Button.setEnabled(True)
                self.Com_RX_Set_Button.setEnabled(True)
                self.recFlag = False
            # 清理已处理的数据
            end_index = match.end()
            self.receiveBuffer = self.receiveBuffer[end_index:]

    # 开启消费者线程
    def start_consumer(self):
        if self.consumer_thread is None or not self.consumer_thread.isRunning():
            print('none' if self.consumer_thread is None else 'not running')
            self.recFlag = True
            self.consumer_thread = WorkerThread(mainWindow=self)
            self.consumer_thread.start()

    # 关闭消费者线程
    def stop_consumer(self):
        self.recFlag = False
        if self.consumer_thread is not None:
            self.consumer_thread.quit()
            self.consumer_thread.wait()  # 等待线程结束
            self.consumer_thread = None

    # 保存日志
    def saveLog(self):
        # 生成当前时间的时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fileName = os.path.join(os.getcwd(), f"product_log_{timestamp}.txt")

        # 将日志内容写入文件
        with open(fileName, 'a', encoding='utf-8') as file:
            file.write(self.TextEdit_Receive.toPlainText() + "\n")

# 消费者线程
class WorkerThread(QThread):
    def __init__(self, mainWindow: MyMainWindow, parent=None, ):
        self.mainWindow = mainWindow
        super(WorkerThread, self).__init__(parent)

    def run(self):
        self.mainWindow.parseData()

# 参数设置窗口类
class ParamSettingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('请输入参数')
        self.setWindowFlags(self.windowFlags() | Qt.WindowContextHelpButtonHint)
        self.setFixedSize(300, 200)
        layout = QVBoxLayout()
        # 第一个参数输入
        self.param1_edit = QLineEdit(self)
        self.param1_edit.setPlaceholderText('请输入允许的最小RSSI值(负整数),默认为-50')
        self.param1_edit.setValidator(RSSIValidator())  # 只允许输入0和负数
        layout.addWidget(QLabel('RSSI:'))
        layout.addWidget(self.param1_edit)
        # 第二个参数输入
        self.param2_edit = QLineEdit(self)
        self.param2_edit.setPlaceholderText('请输入允许的最大丢包率(%),默认为5')
        self.param2_edit.setValidator(LossRateValidator())
        layout.addWidget(QLabel('丢包率:'))
        layout.addWidget(self.param2_edit)

        # 确认和取消
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.myAccept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def getParam(self):
        RSSI = self.param1_edit.text()
        LossRate = self.param2_edit.text()
        return RSSI, LossRate

    def myAccept(self):
        # 检查是否输入参数
        if not self.param1_edit.text() or not self.param2_edit.text():
            QMessageBox.warning(self, 'Warning', '请完整填写两个参数')
        else:
            self.accept()

# 功率设置窗口
class PowerConfigurationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('请输入参数')
        self.setWindowFlags(self.windowFlags() | Qt.WindowContextHelpButtonHint)
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()
        # 功率设置
        self.param_edit = QLineEdit(self)
        self.param_edit.setPlaceholderText('请输入0~31之间的数字,默认为31')
        self.param_edit.setValidator(QIntValidator(0, 31, self))
        layout.addWidget(QLabel('功率:'))
        layout.addWidget(self.param_edit)

        # 确认和取消
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.myAccept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def getParam(self):
        return self.param_edit.text()

    def myAccept(self):
        if not self.param_edit.text():
            QMessageBox.warning(self, 'Warning', '请填写参数')
        else:
            # 进行功率设置
            self.accept()