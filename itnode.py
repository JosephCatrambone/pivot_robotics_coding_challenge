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
from node import Node


class ItNode(Node):
    def __init__(self, node_id: int, start_position: tuple[int, int], board_shape: tuple[int, int]):
        super().__init__()
        self.node_id = node_id
        self.current_position = start_position
        self.board_shape = board_shape
        self.frozen = True  # This will freeze if the game hasn't begun.
        self.quit = False

    def on_start(self):
        # Associate our channels with a handler first, then report we're ready.
        self.subscribe(Channels.BEGIN_GAME, self.handle_begin)
        self.subscribe(Channels.FREEZE, self.handle_freeze)
        self.subscribe(Channels.STOP_GAME, self.handle_gameover)

        msg = report_ready_t()
        msg.id = self.node_id
        self.publish(Channels.REPORT_READY, msg)
        print(f"Node {self.node_id} online.")
    
    def run(self):
        while not self.quit:
            if self.frozen:
                continue
            pass
    
    def on_stop(self):
        pass

    def handle_begin(self, channel, data):
        self.frozen = False

    def handle_gameover(self, channel, data):
        self.quit = True

    def handle_freeze(self, channel, data):
        self.frozen = True