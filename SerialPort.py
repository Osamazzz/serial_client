# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SerialPort.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ModelTestHelper(object):
    def setupUi(self, ModelTestHelper):
        ModelTestHelper.setObjectName("ModelTestHelper")
        ModelTestHelper.setWindowModality(QtCore.Qt.NonModal)
        ModelTestHelper.resize(755, 652)
        ModelTestHelper.setMinimumSize(QtCore.QSize(755, 652))
        ModelTestHelper.setMaximumSize(QtCore.QSize(755, 652))
        font = QtGui.QFont()
        font.setFamily("方正兰亭中黑_GBK")
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        ModelTestHelper.setFont(font)
        ModelTestHelper.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        ModelTestHelper.setMouseTracking(False)
        ModelTestHelper.setStyleSheet("color: rgb(0, 0, 0);\n"
                                      "                background-color: rgb(255, 255, 255);\n"
                                      "                font: 9pt \"方正兰亭中黑_GBK\";\n"
                                      "            ")
        self.label = QtWidgets.QLabel(ModelTestHelper)
        self.label.setGeometry(QtCore.QRect(50, 40, 41, 21))
        self.label.setObjectName("label")
        self.ClearButton = QtWidgets.QPushButton(ModelTestHelper)
        self.ClearButton.setGeometry(QtCore.QRect(330, 32, 81, 31))
        self.ClearButton.setObjectName("ClearButton")
        self.TextEdit_Receive = QtWidgets.QTextEdit(ModelTestHelper)
        self.TextEdit_Receive.setGeometry(QtCore.QRect(50, 70, 361, 501))
        self.TextEdit_Receive.setAutoFillBackground(False)
        self.TextEdit_Receive.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                            "color: rgb(0, 0, 0);")
        self.TextEdit_Receive.setLineWidth(1)
        self.TextEdit_Receive.setObjectName("TextEdit_Receive")
        self.hexShowing_checkBox = QtWidgets.QCheckBox(ModelTestHelper)
        self.hexShowing_checkBox.setGeometry(QtCore.QRect(240, 39, 81, 21))
        self.hexShowing_checkBox.setObjectName("hexShowing_checkBox")
        self.Button_Sava_Log = QtWidgets.QPushButton(ModelTestHelper)
        self.Button_Sava_Log.setGeometry(QtCore.QRect(50, 580, 75, 31))
        self.Button_Sava_Log.setObjectName("Button_Sava_Log")
        self.frame = QtWidgets.QFrame(ModelTestHelper)
        self.frame.setGeometry(QtCore.QRect(460, 70, 241, 341))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(1)
        self.frame.setMidLineWidth(0)
        self.frame.setObjectName("frame")
        self.gridLayoutWidget = QtWidgets.QWidget(self.frame)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 221, 321))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.Com_Baud_Combo = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.Com_Baud_Combo.setEditable(True)
        self.Com_Baud_Combo.setDuplicatesEnabled(False)
        self.Com_Baud_Combo.setModelColumn(0)
        self.Com_Baud_Combo.setObjectName("Com_Baud_Combo")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.Com_Baud_Combo.addItem("")
        self.gridLayout.addWidget(self.Com_Baud_Combo, 1, 1, 1, 1)
        self.Com_Test_Combo_2 = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.Com_Test_Combo_2.setObjectName("Com_Test_Combo_2")
        self.gridLayout.addWidget(self.Com_Test_Combo_2, 3, 1, 1, 1)
        self.Com_Baud_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_Baud_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_Baud_Label.setObjectName("Com_Baud_Label")
        self.gridLayout.addWidget(self.Com_Baud_Label, 1, 0, 1, 1)
        self.Com_Open_Button = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.Com_Open_Button.setObjectName("Com_Open_Button")
        self.gridLayout.addWidget(self.Com_Open_Button, 4, 1, 1, 1)
        self.Com_State_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_State_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_State_Label.setObjectName("Com_State_Label")
        self.gridLayout.addWidget(self.Com_State_Label, 4, 0, 1, 1)
        self.Com_Close_Button = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.Com_Close_Button.setDefault(False)
        self.Com_Close_Button.setObjectName("Com_Close_Button")
        self.gridLayout.addWidget(self.Com_Close_Button, 5, 1, 1, 1)
        self.Com_Test_Label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_Test_Label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_Test_Label_2.setObjectName("Com_Test_Label_2")
        self.gridLayout.addWidget(self.Com_Test_Label_2, 3, 0, 1, 1)
        self.Com_Test_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_Test_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_Test_Label.setObjectName("Com_Test_Label")
        self.gridLayout.addWidget(self.Com_Test_Label, 2, 0, 1, 1)
        self.Com_isOpenOrNot_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_isOpenOrNot_Label.setText("")
        self.Com_isOpenOrNot_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_isOpenOrNot_Label.setObjectName("Com_isOpenOrNot_Label")
        self.gridLayout.addWidget(self.Com_isOpenOrNot_Label, 5, 0, 1, 1)
        self.Com_Refresh_Button = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.Com_Refresh_Button.setObjectName("Com_Refresh_Button")
        self.gridLayout.addWidget(self.Com_Refresh_Button, 0, 1, 1, 1)
        self.Com_Test_Combo = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.Com_Test_Combo.setObjectName("Com_Test_Combo")
        self.gridLayout.addWidget(self.Com_Test_Combo, 2, 1, 1, 1)
        self.Com_Refresh_Label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.Com_Refresh_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_Refresh_Label.setObjectName("Com_Refresh_Label")
        self.gridLayout.addWidget(self.Com_Refresh_Label, 0, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(ModelTestHelper)
        self.frame_2.setGeometry(QtCore.QRect(460, 420, 241, 131))
        self.frame_2.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setLineWidth(1)
        self.frame_2.setMidLineWidth(0)
        self.frame_2.setObjectName("frame_2")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.frame_2)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 222, 111))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.Com_RX_Set_Button = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.Com_RX_Set_Button.setObjectName("Com_RX_Set_Button")
        self.gridLayout_2.addWidget(self.Com_RX_Set_Button, 2, 1, 1, 1)
        self.Com_Model_Set_Label = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.Com_Model_Set_Label.setMaximumSize(QtCore.QSize(220, 40))
        font = QtGui.QFont()
        font.setFamily("方正兰亭中黑_GBK")
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.Com_Model_Set_Label.setFont(font)
        self.Com_Model_Set_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Com_Model_Set_Label.setObjectName("Com_Model_Set_Label")
        self.gridLayout_2.addWidget(self.Com_Model_Set_Label, 0, 0, 1, 2)
        self.Com_TX_Set_Button = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.Com_TX_Set_Button.setObjectName("Com_TX_Set_Button")
        self.gridLayout_2.addWidget(self.Com_TX_Set_Button, 2, 0, 1, 1)
        self.Com_Reset_Button = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.Com_Reset_Button.setObjectName("Com_Reset_Button")
        self.gridLayout_2.addWidget(self.Com_Reset_Button, 3, 0, 1, 2)
        self.hexSending_checkBox = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.hexSending_checkBox.setObjectName("hexSending_checkBox")
        self.gridLayout_2.addWidget(self.hexSending_checkBox, 1, 0, 1, 2)

        self.retranslateUi(ModelTestHelper)
        self.ClearButton.clicked.connect(self.TextEdit_Receive.clear)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(ModelTestHelper)

    def retranslateUi(self, ModelTestHelper):
        _translate = QtCore.QCoreApplication.translate
        ModelTestHelper.setWindowTitle(_translate("ModelTestHelper", "模组测试工具"))
        self.label.setText(_translate("ModelTestHelper", "接收区"))
        self.ClearButton.setText(_translate("ModelTestHelper", "清除"))
        self.TextEdit_Receive.setHtml(_translate("ModelTestHelper",
                                                 "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                                 "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                                 "p, li { white-space: pre-wrap; }\n"
                                                 "</style></head><body style=\" font-family:\'方正兰亭中黑_GBK\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                                                 "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.hexShowing_checkBox.setText(_translate("ModelTestHelper", "16进制显示"))
        self.Button_Sava_Log.setText(_translate("ModelTestHelper", "保存日志"))
        self.Com_Baud_Combo.setCurrentText(_translate("ModelTestHelper", "1200"))
        self.Com_Baud_Combo.setItemText(0, _translate("ModelTestHelper", "1200"))
        self.Com_Baud_Combo.setItemText(1, _translate("ModelTestHelper", "2400"))
        self.Com_Baud_Combo.setItemText(2, _translate("ModelTestHelper", "4800"))
        self.Com_Baud_Combo.setItemText(3, _translate("ModelTestHelper", "9600"))
        self.Com_Baud_Combo.setItemText(4, _translate("ModelTestHelper", "14400"))
        self.Com_Baud_Combo.setItemText(5, _translate("ModelTestHelper", "19200"))
        self.Com_Baud_Combo.setItemText(6, _translate("ModelTestHelper", "38400"))
        self.Com_Baud_Combo.setItemText(7, _translate("ModelTestHelper", "43000"))
        self.Com_Baud_Combo.setItemText(8, _translate("ModelTestHelper", "57600"))
        self.Com_Baud_Combo.setItemText(9, _translate("ModelTestHelper", "76800"))
        self.Com_Baud_Combo.setItemText(10, _translate("ModelTestHelper", "115200"))
        self.Com_Baud_Combo.setItemText(11, _translate("ModelTestHelper", "128000"))
        self.Com_Baud_Combo.setItemText(12, _translate("ModelTestHelper", "230400"))
        self.Com_Baud_Combo.setItemText(13, _translate("ModelTestHelper", "256000"))
        self.Com_Baud_Combo.setItemText(14, _translate("ModelTestHelper", "460800"))
        self.Com_Baud_Combo.setItemText(15, _translate("ModelTestHelper", "921600"))
        self.Com_Baud_Combo.setItemText(16, _translate("ModelTestHelper", "1382400"))
        self.Com_Baud_Label.setText(_translate("ModelTestHelper", "波特率"))
        self.Com_Open_Button.setText(_translate("ModelTestHelper", "Open"))
        self.Com_State_Label.setText(_translate("ModelTestHelper", "串口操作"))
        self.Com_Close_Button.setText(_translate("ModelTestHelper", "Close"))
        self.Com_Test_Label_2.setText(_translate("ModelTestHelper", "陪测设备串口"))
        self.Com_Test_Label.setText(_translate("ModelTestHelper", "待测设备串口"))
        self.Com_Refresh_Button.setText(_translate("ModelTestHelper", "刷新"))
        self.Com_Refresh_Label.setText(_translate("ModelTestHelper", "串口搜索"))
        self.Com_RX_Set_Button.setText(_translate("ModelTestHelper", "接收功能测试"))
        self.Com_Model_Set_Label.setText(_translate("ModelTestHelper", "模块功能设置"))
        self.Com_TX_Set_Button.setText(_translate("ModelTestHelper", "发射功能测试"))
        self.Com_Reset_Button.setText(_translate("ModelTestHelper", "复位"))
        self.hexSending_checkBox.setText(_translate("ModelTestHelper", "16进制发送"))
