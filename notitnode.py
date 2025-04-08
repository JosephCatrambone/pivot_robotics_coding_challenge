"""
2. NotItNode
  - Waits for synchronization confirmation before starting.
  - Make a random move within the board boundaries every second. Publish the chosen move to the GameNode. 
  - Stop moving immediately upon receiving a freeze message.
"""
import random
import time

from channels import Channels
from messages import begin_t, freeze_t, gameover_t, moved_t, report_ready_t

from node import Node


class NotItNode(Node):

    def __init__(self, node_id: int, start_position: tuple[int, int], board_shape: tuple[int, int], move_frequency: float):
        super().__init__()
        self.node_id = node_id
        self.current_position = start_position
        self.board_shape = board_shape
        self.frozen = True
        self.quit = False
        self.move_frequency = move_frequency

    def on_start(self):
        # Associate our channels with a handler first, then report we're ready.
        self.subscribe(Channels.BEGIN_GAME, self.handle_begin)
        self.subscribe(Channels.FREEZE, self.handle_freeze)
        self.subscribe(Channels.STOP_GAME, self.handle_gameover)

        msg = report_ready_t()
        msg.id = self.node_id
        self.publish(Channels.REPORT_READY, msg)
        print(f"Node {self.node_id} online at {self.current_position}")
    
    def run(self):
        while not self.quit:
            time.sleep(self.move_frequency)
            if not self.frozen:
                new_place = self.choose_move()
                self.move_to(new_place)
    
    def choose_move(self) -> tuple[int, int]:
        candidate_moves = list()
        for (dx, dy) in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            next_x = self.current_position[0] + dx
            next_y = self.current_position[1] + dy
            if (next_x >= 0 and next_x < self.board_shape[0] and 
                    next_y >= 0 and next_y < self.board_shape[1]):
                candidate_moves.append((next_x, next_y))
        if len(candidate_moves) == 0:
            # If the board is too small we may have no options.
            print(f"Candidate moves list is empty for node id {self.node_id}.  Pos: {self.current_position}  Board shape: {self.board_shape}")
            next_position = self.current_position
        else:
            next_position = random.choice(candidate_moves)
        return next_position

    def move_to(self, new_position: tuple[int, int]):
        msg = moved_t()
        msg.id = self.node_id
        msg.new_position = new_position
        self.publish(Channels.REPORT_MOVE, msg)
        self.current_position = new_position
    
    def on_stop(self):
        pass

    def handle_begin(self, channel, data):
        self.frozen = False

    def handle_gameover(self, channel, data):
        self.quit = True

    def handle_freeze(self, channel, data):
        msg = freeze_t.decode(data)
        if msg.id == self.node_id:
            self.frozen = True