"""
2. NotItNode
  - Waits for synchronization confirmation before starting.
  - Make a random move within the board boundaries every second. Publish the chosen move to the GameNode. 
  - Stop moving immediately upon receiving a freeze message.
"""
import random
import time
from logging import getLogger

from channels import Channels
from messages import freeze_t, moved_t, report_ready_t, report_status_t

from node import Node


NODE_SYNC_FREQUENCY = 5.0  # This does not need to be frequent. It's a sanity check to see if we missed messages.
GAME_START_POLL_FREQUENCY = 0.1
logger = getLogger()


class NotItNode(Node):

    def __init__(self, node_id: int, start_position: tuple[int, int], board_shape: tuple[int, int], move_frequency: float):
        super().__init__()
        self.node_id = node_id
        self.current_position = start_position
        self.board_shape = board_shape
        self.move_frequency = move_frequency
        self.sync_frequency = NODE_SYNC_FREQUENCY
        self.last_node_sync = 0
        # It's tempting to put all of these into an enumeration of FSM like we have for the game node.
        # The reason we're not doing that is IT might not get the game start message and we don't want a rebroadcast
        # to flip all of the seekers from frozen to unfrozen, restarting the game.
        self.game_started = False
        self.frozen = False
        self.game_over = False

    def position_in_bound(self, pos: tuple[int, int]) -> bool:
        return pos[0] >= 0 and pos[0] < self.board_shape[0] and pos[1] >= 0 and pos[1] < self.board_shape[1]

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
        logger.info(f"Node {self.node_id} online at {self.current_position}")
    
    def run(self):
        while not self.game_started:
            time.sleep(GAME_START_POLL_FREQUENCY)
            self.send_sync()

        self.frozen = False  # Unfreeze as we start the game.

        while not self.game_over:
            time.sleep(self.move_frequency)
            self.tick()
            if not self.frozen:
                new_place = self.choose_move()
                self.move_to(new_place)
            self.send_sync()
    
    def tick(self):
        """Called once per loop inside the run cycle.  Called even if frozen."""
        pass

    def choose_move(self) -> tuple[int, int]:
        """
        Returns the next position that this node should assume.
        This is not the DELTA of the position but the absolute world position.
        """
        next_position = self.current_position
        candidate_moves = list()
        for (dx, dy) in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            next_x = self.current_position[0] + dx
            next_y = self.current_position[1] + dy
            candidate = (next_x, next_y)
            if self.position_in_bound(candidate):
                candidate_moves.append(candidate)
        if len(candidate_moves) == 0:
            # If the board is too small we may have no options.
            logger.warning(f"Candidate moves list is empty for node id {self.node_id}! "
                           f"Pos: {self.current_position}  Board shape: {self.board_shape}")
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
        logger.info(f"Got start message: {self.node_id}")
        self.game_started = True
        # We do NOT set unfrozen here.
        # The node will unfreeze itself as the game starts, but it's possible a message will get dropped and we'll
        # need to re-broadcast the start game, so we don't want to unfreeze the tagged elements.
        # self.frozen = False

    def handle_gameover(self, channel, data):
        self.game_over = True

    def handle_freeze(self, channel, data):
        msg = freeze_t.decode(data)
        if msg.id == self.node_id:
            self.frozen = True

    def send_sync(self):
        # Randomly broadcast status so that we can sanity check our system state.
        now = time.time()
        if now - self.last_node_sync > self.sync_frequency:
            logger.info(f"Node ID {self.node_id} reporting status update.")
            msg = report_status_t()
            msg.id = self.node_id
            msg.position = self.current_position
            msg.frozen = self.frozen
            msg.game_started = self.game_started
            self.publish(Channels.REPORT_STATUS, msg)
            self.last_node_sync = now