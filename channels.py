from enum import StrEnum


class Channels(StrEnum):
    # Workers -> GameNode
    REPORT_READY = "REPORT_READY"
    REPORT_MOVE = "REPORT_MOVE"
    REPORT_STATUS = "REPORT_STATUS"

    # GameNode -> Workers
    BEGIN_GAME = "BEGIN_GAME"
    FREEZE = "FREEZE"
    STOP_GAME = "STOP_GAME"
