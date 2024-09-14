import queue
from enum import Enum

from PyQt5.QtGui import QValidator

recPacQueue = queue.Queue(maxsize=100)  # 定义一个大小为1的队列


class State(Enum):
    IDLE = 0  # 客户端空闲状态
    RECEIVING = 1  # 客户端接收状态
    SENDING = 2  # 客户端发送状态


def int8_from_unsigned(value: int) -> int:
    # 取出符号位
    if value & 0x80:  # 最高位为1
        return -(256 - value)
    else:
        return value


# RSSI值修正类
class RSSIValidator(QValidator):
    def __init__(self):
        super().__init__()

    def validate(self, input_str: str, pos):
        # 允许空输入
        if input_str == '':
            return QValidator.Intermediate, input_str, pos
        # 允许输入-
        if input_str == '-':
            return QValidator.Intermediate, input_str, pos
        # 允许单个0
        if input_str == '0':
            return QValidator.Acceptable, input_str, pos
        # 避免输入多个0开头的数字
        if input_str.startswith('0') and len(input_str) > 1:
            return QValidator.Invalid, input_str, pos
        try:
            value = int(input_str)
        except ValueError:
            return QValidator.Invalid, input_str, pos
        if value <= 0:
            return QValidator.Acceptable, input_str, pos
        else:
            return QValidator.Invalid, input_str, pos

    def fixup(self, input_str):
        try:
            value = int(input_str)
            if value > 0:
                return '0'
            return input_str
        except ValueError:
            return '0'


# 丢包率修正类
class LossRateValidator(QValidator):
    def __init__(self):
        super().__init__()

    def validate(self, input_str: str, pos):
        if input_str == '':
            return QValidator.Intermediate, input_str, pos
        if input_str == '0':
            return QValidator.Acceptable, input_str, pos
        # 避免输入多个0开头
        if input_str.startswith('0') and len(input_str) > 1:
            return QValidator.Invalid, input_str, pos
        try:
            value = int(input_str)
        except ValueError:
            return QValidator.Invalid, input_str, pos
        if value >= 0:
            return QValidator.Acceptable, input_str, pos
        else:
            return QValidator.Invalid, input_str, pos

    def fixup(self, input_str):
        try:
            value = int(input_str)
            if value < 0:
                return '0'
            return input_str
        except ValueError:
            return '0'
