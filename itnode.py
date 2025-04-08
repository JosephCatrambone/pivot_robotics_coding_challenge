"""
3. ItNode
  - Waits for synchronization confirmation before starting.
  - Listen to move updates from all NotIt nodes and keep track of the global state. 
  - Choose a move strategically, chasing NotIt nodes using any simple heuristic/algorithm of your choice.
  - Publish move updates to GameNode every 0.5 seconds.
"""
import threading
import time
import random

from channels import Channels
from messages import begin_t, freeze_t, gameover_t, moved_t, report_ready_t
from notitnode import NotItNode


class ItNode(NotItNode):
    def __init__(self, node_id: int, start_position: tuple[int, int], board_shape: tuple[int, int], move_frequency: float):
        super().__init__(
            node_id=node_id, 
            start_position=start_position, 
            board_shape=board_shape, 
            move_frequency=move_frequency
        )
