import queue
from enum import Enum

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
