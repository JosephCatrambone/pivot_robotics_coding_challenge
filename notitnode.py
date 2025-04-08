"""
2. NotItNode
  - Waits for synchronization confirmation before starting.
  - Make a random move within the board boundaries every second. Publish the chosen move to the GameNode. 
  - Stop moving immediately upon receiving a freeze message.
"""
import random

from channels import Channels
from messages import begin_t, freeze_t, gameover_t, moved_t, report_ready_t

from node import Node


class NotItNode(Node):
    def __init__(self, node_id: int, start_position: tuple[int, int], board_shape: tuple[int, int]):
        super().__init__()
        self.node_id = node_id
        self.current_position = start_position
        self.board_shape = board_shape
        self.frozen = True
        self.quit = False

    def on_start(self):
        # Associate our channels with a handler first, then report we're ready.
        self.subscribe(Channels.BEGIN_GAME, self.handle_begin)

        msg = report_ready_t()
        msg.id = self.node_id
        self.publish(Channels.REPORT_READY, msg)
        print(f"Node {self.node_id} online.")
    
    def run(self):
        while not self.quit:
            if random.random() < 0.1:
                return  # DEBUG: Quit early.
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