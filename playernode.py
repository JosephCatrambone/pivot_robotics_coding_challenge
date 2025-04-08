"""
2. NotItNode
  - Waits for synchronization confirmation before starting.
  - Make a random move within the board boundaries every second. Publish the chosen move to the GameNode. 
  - Stop moving immediately upon receiving a freeze message.
"""
import random
import time
from abc import abstractmethod, ABC

from channels import Channels
from messages import begin_t, freeze_t, gameover_t, moved_t, report_ready_t

from node import Node


class PlayerNode(Node, ABC):

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
        super().on_start()
        self.subscribe(Channels.BEGIN_GAME, self.handle_begin)
        self.subscribe(Channels.FREEZE, self.handle_freeze)
        self.subscribe(Channels.STOP_GAME, self.handle_gameover)

        msg = report_ready_t()
        msg.id = self.node_id
        msg.position = self.current_position
        self.publish(Channels.REPORT_READY, msg)
        print(f"Node {self.node_id} online at {self.current_position}")
    
    def run(self):
        while not self.quit:
            time.sleep(self.move_frequency)
            self.tick()
            if not self.frozen:
                new_place = self.choose_move()
                self.move_to(new_place)
    
    @abstractmethod
    def tick(self):
        """Called once per loop inside the run cycle.  Called even if frozen."""
        ...

    @abstractmethod
    def choose_move(self) -> tuple[int, int]:
        """
        Returns the next position that this node should assume.
        This is not the DELTA of the position but the absolute world position.
        """
        ...

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