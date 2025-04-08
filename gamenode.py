"""
1. GameNode 
  - Listens to position updates from It and NotIt nodes. Keeps track of the global states in a NxM board.
  - If the It node and NotIt node are in the same square, send a message to the NotIt node to freeze. 
  - Visually represents the game state using a simple GUI.
  - Keep track of the number of NotIt nodes which have been frozen. If all NotIt nodes are frozen, then end the game. 
"""

import time
from enum import Enum
from logging import getLogger

from channels import Channels
from messages import begin_t, freeze_t, gameover_t, report_ready_t, report_status_t
from movement_monitor import MovementMonitor
from node import Node


MIN_SLEEP_TIME = 0.0001  # Chosen for compatibility. A time of zero doesn't always yield.
UI_REDRAW_DELAY = 0.1  # Time in seconds between drawing the TUI.
logger = getLogger()


class GameState(Enum):
    STARTING = 0
    RUNNING = 1
    COMPLETE = 2
    ERROR = 3


class GameNode(Node):
    def __init__(self, board_shape: tuple[int, int], node_count: int, it_id: int):
        super().__init__()
        assert board_shape[0] > 0 and board_shape[1] > 0
        self.board_shape = board_shape
        self.movement_monitor = MovementMonitor()
        self.node_count = node_count  # Includes the 'it' node.
        self.node_reports = 0  # Have all the workers chimed in?
        self.it_id = it_id  # Used to check when "it" has tagged a node.
        self.untagged_nodes = set()
        self.ui_draw_delay = UI_REDRAW_DELAY
        self.last_ui_draw = 0
        self.game_state = GameState.STARTING

    def on_start(self):
        self.subscribe(Channels.REPORT_READY, self.process_ready_report)
        self.subscribe(Channels.REPORT_STATUS, self.process_status_update)
        self.movement_monitor.register_listeners(self.lc)
        self.node_reports = 0
    
    def run(self):
        while self.game_state == GameState.STARTING:
            # Wait for nodes to come online:
            time.sleep(MIN_SLEEP_TIME)

        # Main game loop:
        while self.game_state == GameState.RUNNING:
            time.sleep(MIN_SLEEP_TIME)
            self.process_freezing()
            self.render_tui()
            self.check_gameover()
        
        # On-stop will be called automatically when we exit from the 'run' function.
        if self.game_state == GameState.COMPLETE:
            print("Game Complete")
    
    def on_stop(self):
        # We could make this the last step in the run.
        # Do we want to reserve 'on stop' for other kinds of cleanup?
        msg = gameover_t()
        self.publish(Channels.STOP_GAME, msg)
            
    def process_freezing(self):
        it_position = self.movement_monitor.get_node_position(self.it_id)
        # Since we wait for 'it' to register itself, position should never be none:
        assert it_position

        # Find other nodes tagged by it.
        newly_tagged_nodes = self.movement_monitor.get_nodes_at_position(it_position)
        for t in newly_tagged_nodes:
            if t != self.it_id and t in self.untagged_nodes:
                self.send_freeze(t)
                self.untagged_nodes.remove(t)
                print(f"{t} was tagged at {it_position}")
    
    def render_tui(self, force_draw_now: bool = False):
        """Redraw UI if it has been sufficiently long since the last output.
        Can call many times in quick succession and it will automatically discard attempts to redraw.
        Override and draw now with `force_draw_now = True`.
        """
        if len(self.movement_monitor.get_last_movers()) == 0 and not force_draw_now:
            return

        if time.time() - self.last_ui_draw > self.ui_draw_delay or force_draw_now:
            self.last_ui_draw = time.time()
        else:
            return

        it_position = self.movement_monitor.get_node_position(self.it_id)
        if it_position is None:
            print("Awaiting 'it' to register.")
            return

        print("-"*20)
        for y in range(0, self.board_shape[1]):
            for x in range(0, self.board_shape[0]):
                if x == it_position[0] and y == it_position[1]:
                    print("X", end = " ")
                else:
                    count = len(self.movement_monitor.get_nodes_at_position((x, y)))
                    if count == 0:
                        print("_", end = " ")
                    else:
                        print(count, end=" ")
            print()
        print("-"*20)
        print(f"Untagged: {self.untagged_nodes}")

    # IPC Methods:

    def send_freeze(self, node_id):
        msg = freeze_t()
        msg.id = node_id
        self.publish(Channels.FREEZE, msg)

    def process_ready_report(self, channel, data):
        msg = report_ready_t.decode(data)
        self.node_reports += 1

        # Track everyone's start positions.
        self.movement_monitor.set_node_position(msg.id, msg.position, clear_previous=False)
        
        # The 'it' doesn't need to be tagged:
        if msg.id != self.it_id:
            self.untagged_nodes.add(msg.id)
        
        # Check if we're ready.
        if self.node_reports == self.node_count+1:  # Plus one because we have the 'NotIt' count and the 'It'.
            self.game_state = GameState.RUNNING
            logger.info(f"All {self.node_reports} nodes ({self.untagged_nodes}) and the 'it' node have reported -- starting game.")
            print("Game Start")
            msg = begin_t()
            self.publish(Channels.BEGIN_GAME, msg)

    def check_gameover(self):
        if len(self.untagged_nodes) == 0 and self.game_state == GameState.RUNNING:
            self.game_state = GameState.COMPLETE

    def send_start_message(self):
        msg = begin_t()
        self.publish(Channels.BEGIN_GAME, msg)

    def process_status_update(self, channel, data):
        msg = report_status_t.decode(data)
        # Perhaps we missed the message saying the game started:
        if self.game_state == GameState.RUNNING and not msg.game_started:
            logger.warning(f"Node ID {msg.id} missed the game start message.  Rebroadcasting.")
            self.send_start_message()
        # Or the node didn't get a freeze command:
        if msg.frozen and msg.id in self.untagged_nodes:
            # This should not be possible but we want to monitor for odd message issues.
            logger.warning(f"Node ID {msg.id} incorrectly detected itself as tagged.  Recovering.")
            self.send_freeze(msg.id)
            self.untagged_nodes.remove(msg.id)
        elif not msg.frozen and msg.id not in self.untagged_nodes:
            logger.warning(f"Node ID {msg.id} did not receive the freeze message.  Resending.")
            self.send_freeze(msg.id)
